<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output indent="yes"/>

  <xsl:template match="*|@*">
    <xsl:copy>
      <xsl:apply-templates select="*|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:variable name="basedir" select="/workspace/@basedir"/>
  <xsl:variable name="cvsdir"  select="/workspace/@cvsdir"/>
  <xsl:variable name="logdir"  select="/workspace/@logdir"/>

  <xsl:variable name="banner-link"  select="/workspace/@banner-link"/>
  <xsl:variable name="banner-image" select="/workspace/@banner-image"/>

  <xsl:variable name="build-sequence" select="/workspace/@build-sequence"/>

  <!-- =================================================================== -->
  <!-- provide support for specifying desired projects on the command line -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">

    <build build-sequence="{$build-sequence}">

      <chdir dir="{$basedir}"/>
      <mkdir dir="{$logdir}"/>
      <delete dir="build"/>
      <delete dir="dist"/>

      <xsl:if test="$build-sequence = 'bulk'">
        <xsl:for-each select="module[cvs]">
          <delete dir="{@srcdir}"/>
          <copy fromdir="{$cvsdir}/{@name}" todir="{@srcdir}"/>
        </xsl:for-each>
      </xsl:if>

      <html log="{$logdir}/index.html"
        banner-image="{$banner-image}" banner-link="{$banner-link}">

        <title>
          <xsl:text>Build status - </xsl:text>
          <date/>
        </title>

        <sidebar>
          <strong><a href="index.html">Build logs</a></strong>
          <ul>
            <xsl:for-each select="project[ant|script]">
              <xsl:sort select="@name"/>
              <li>
                <a href="{@name}.html"><xsl:value-of select="@name"/></a>
              </li>
            </xsl:for-each>
          </ul>
        </sidebar>

        <menu>
          <xsl:text>Workspace: </xsl:text>
          <a href="workspace.html">definition</a>
          <a href="xref.html">cross reference</a>
          <a href="cvs_index.html">cvs logs</a>
        </menu>

        <content>

          <table border="1">
            <tr>
              <th>Start time</th>
              <th>Project</th>
              <th>Status</th>
            </tr>
            <xsl:apply-templates select="project"/>
          </table>
        </content>
      </html>

    </build>

  </xsl:template>

  <xsl:template match="project">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:variable name="module" select="@module"/>
      <xsl:variable name="srcdir" select="../module[@name=$module]/@srcdir"/>

      <html log="{$logdir}/{@name}.html"
        banner-image="{$banner-image}" banner-link="{$banner-link}">

        <title>
          <xsl:text>Build </xsl:text>
          <xsl:value-of select="@name"/>
          <xsl:choose>
            <xsl:when test="description">
              <xsl:text> - </xsl:text>
              <xsl:value-of select="normalize-space(description)"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:for-each select="../module[@name=$module]/description">
                <xsl:text> - </xsl:text>
                <xsl:value-of select="normalize-space(.)"/>
              </xsl:for-each>
            </xsl:otherwise>
          </xsl:choose>
        </title>

        <xsl:copy-of select="note"/>

        <sidebar>
          <strong><a href="index.html">Build logs</a></strong>
          <ul>
            <xsl:for-each select="../project[ant|script]">
              <xsl:sort select="@name"/>
              <li>
                <a href="{@name}.html"><xsl:value-of select="@name"/></a>
              </li>
            </xsl:for-each>
          </ul>
        </sidebar>

        <menu>
          <date-time/>
          <br/>

          <xsl:text>Project: </xsl:text>
          <xsl:if test="url">
            <a href="{url/@href}">home</a>
          </xsl:if>

          <a href="project_{@defined-in}.html">definition</a>

          <xsl:for-each select="/workspace/project[cvs and @module=$module]">
            <a href="cvs_{@name}.html">cvs</a>
          </xsl:for-each>

          <!-- dependencies -->

          <br/>
          <xsl:text>Dependencies: </xsl:text>
          <xsl:for-each select="depend|option">
            <xsl:variable name="dependent" select="@project"/>
            <xsl:for-each select="/workspace/project[@name=$dependent]">
              <xsl:choose>
                <xsl:when test="ant|script">
                  <a href="{@name}.html">
                    <xsl:value-of select="$dependent"/>
                  </a>
                </xsl:when>
                <xsl:otherwise>
                  <a href="project_{@module}.html">
                    <xsl:value-of select="$dependent"/>
                  </a>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:for-each>
          </xsl:for-each>
        </menu>

        <content>

          <!-- prereq check -->

          <xsl:for-each select="depend">
            <xsl:variable name="dependent" select="@project"/>
            <prereq project="{@project}">
              <xsl:for-each select="/workspace/project[@name=$dependent]">
                <xsl:for-each select="jar">
                  <file path="{../home}/{@name}"/>
                </xsl:for-each>
              </xsl:for-each>
            </prereq>
          </xsl:for-each>

          <logic name="{@name}">
            <initdir dir="{$srcdir}" basedon="{$cvsdir}/{$module}"/>
            <chdir dir="{$srcdir}"/>

            <xsl:copy-of select="mkdir"/>

            <classpath>

              <xsl:for-each select="work">
                <xsl:choose>
                  <xsl:when test="@parent">
                    <pathelement location="{$basedir}/{@parent}"/>
                  </xsl:when>
                  <xsl:when test="@nested">
                    <pathelement location="{$srcdir}/{@nested}"/>
                  </xsl:when>
                  <xsl:otherwise>
                    <pathelement location="{$srcdir}"/>
                  </xsl:otherwise>
                </xsl:choose>
                <xsl:text>&#10;</xsl:text>
              </xsl:for-each>

              <xsl:for-each select="depend[not(noclasspath)]|option">
                <xsl:variable name="dependent" select="@project"/>
                <xsl:for-each select="/workspace/project[@name=$dependent]">
                  <xsl:for-each select="jar">
                    <pathelement location="{../home}/{@name}"/>
                  </xsl:for-each>
                </xsl:for-each>
              </xsl:for-each>
            </classpath>

            <xsl:apply-templates select="ant|script"/>

            <chdir dir="{$basedir}"/>
          </logic>
        </content>
      </html>

      <tr>
        <td>
          <start-time/>
        </td>
        <td class="status">
          <a href="{@name}.html"><xsl:value-of select="@name"/></a>
        </td>
        <td class="status">
          <status/>
        </td>
      </tr>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="project[not(ant) and not(script)]"/>

  <xsl:template match="ant">
    <xsl:variable name="module" select="ancestor::project/@module"/>
    <xsl:variable name="srcdir" select="/workspace/module[@name=$module]/@srcdir"/>

    <xsl:if test="@basedir">
      <chdir dir="{$srcdir}/{@basedir}"/>
    </xsl:if>

    <xsl:copy>
      <xsl:choose>
        <xsl:when test="ancestor::project/@target">
          <xsl:attribute name="target">
            <xsl:value-of select="ancestor::project/@target"/>
          </xsl:attribute>
        </xsl:when>
        <xsl:when test="@target">
          <xsl:copy-of select="@target"/>
        </xsl:when>
      </xsl:choose>

      <xsl:apply-templates select="@*[name()!='target']"/>
      <xsl:apply-templates select="*[name()!='property']"/>

      <xsl:for-each select="/workspace/property|property">
        <xsl:variable name="name" select="@name"/>
        <xsl:choose>
          <xsl:when test="@reference='home'">
            <xsl:variable name="project" select="@project"/>
            <xsl:for-each select="/workspace/project[@name=$project]">
              <property name="{$name}" value="{home}" type="path"/>
            </xsl:for-each>
          </xsl:when>

          <xsl:when test="@reference='jar'">
            <xsl:variable name="project" select="@project"/>
            <xsl:if test="@id">
              <xsl:variable name="id" select="@id"/>
              <xsl:for-each select="/workspace/project[@name=$project]">
                <property name="{$name}" value="{jar[@id=$id]/@name}"/>
              </xsl:for-each>
            </xsl:if>
            <xsl:if test="not(@id)">
              <xsl:for-each select="/workspace/project[@name=$project]/jar">
                <property name="{$name}" value="{@name}"/>
              </xsl:for-each>
            </xsl:if>
          </xsl:when>

          <xsl:when test="@reference='jarpath'">
            <xsl:variable name="project" select="@project"/>
            <xsl:if test="@id">
              <xsl:variable name="id" select="@id"/>
              <xsl:for-each select="/workspace/project[@name=$project]">
                <property name="{$name}" value="{home}/{jar[@id=$id]/@name}" type="path"/>
              </xsl:for-each>
            </xsl:if>
            <xsl:if test="not(@id)">
              <xsl:for-each select="/workspace/project[@name=$project]/jar">
                <property name="{$name}" value="{../home}/{@name}" type="path"/>
              </xsl:for-each>
            </xsl:if>
          </xsl:when>

          <xsl:when test="@reference='srcdir'">
            <xsl:variable name="project" select="@project"/>
            <xsl:for-each select="/workspace/project[@name=$project]">
              <property name="{$name}" value="{$srcdir}" type="path"/>
            </xsl:for-each>
          </xsl:when>

          <xsl:when test="@path">
            <property name="{$name}" value="{$srcdir}/{@path}" type="path"/>
          </xsl:when>

          <xsl:otherwise>
            <property name="{$name}" value="{@value}"/>
          </xsl:otherwise>
        </xsl:choose>

      </xsl:for-each>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
