<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output indent="yes"/>

  <xsl:template match="*|@*">
    <xsl:copy>
      <xsl:apply-templates select="*|@*"/>
    </xsl:copy>
  </xsl:template>

  <!-- =================================================================== -->
  <!-- provide support for specifying desired projects on the command line -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">

    <build>

      <chdir dir="{@basedir}"/>
      <mkdir dir="log"/>
      <delete dir="build"/>
      <delete dir="dist"/>

      <xsl:for-each select="project[cvs]">
        <delete dir="{/workspace/@basedir}/{@name}"/>
        <copy fromdir="{/workspace/@cvsdir}/{@name}"
              todir="{/workspace/@basedir}/{@name}"/>
      </xsl:for-each>

      <html log="{/workspace/@basedir}/log/index.html">
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
          <a href="source_index.html">definition</a>
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
      <xsl:variable name="srcdir" select="@srcdir"/>

      <html log="{/workspace/@basedir}/log/{@name}.html">
        <title>
          <xsl:text>Build </xsl:text>
          <xsl:value-of select="@name"/>
          <xsl:if test="description">
            <xsl:text> - </xsl:text>
            <xsl:value-of select="normalize-space(description)"/>
          </xsl:if>
        </title>

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

          <a href="source_{@defined-in}.html">definition</a>

          <xsl:for-each select="//project[cvs and @srcdir=$srcdir]">
            <a href="cvs_{@name}.html">cvs</a>
          </xsl:for-each>

          <!-- dependencies -->

          <br/>
          <xsl:text>Dependencies: </xsl:text>
          <xsl:for-each select="depend|option">
            <xsl:variable name="dependent" select="@project"/>
            <xsl:for-each select="//project[@name=$dependent]">
              <xsl:choose>
                <xsl:when test="ant|script">
                  <a href="{@name}.html">
                    <xsl:value-of select="$dependent"/>
                  </a>
                </xsl:when>
                <xsl:otherwise>
                  <a href="source_{@srcdir}.html">
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
              <xsl:for-each select="//project[@name=$dependent]">
                <xsl:for-each select="jar">
                  <file path="{../home}/{@name}"/>
                </xsl:for-each>
              </xsl:for-each>
            </prereq>
          </xsl:for-each>

          <logic>
            <xsl:variable name="basedir" select="/workspace/@basedir"/>

            <initdir dir="{$basedir}/{$srcdir}"
                     basedon="{/workspace/@cvsdir}/{$srcdir}"/>
            <chdir dir="{$basedir}/{$srcdir}"/>
            <classpath>

              <xsl:for-each select="work">
                <xsl:choose>
                  <xsl:when test="@parent">
                    <pathelement location="{$basedir}/{@parent}"/>
                  </xsl:when>
                  <xsl:when test="@nested">
                    <pathelement location="{$basedir}/{$srcdir}/{@nested}"/>
                  </xsl:when>
                  <xsl:otherwise>
                    <pathelement location="{$basedir}/{$srcdir}"/>
                  </xsl:otherwise>
                </xsl:choose>
                <xsl:text>&#10;</xsl:text>
              </xsl:for-each>

              <xsl:for-each select="depend[not(noclasspath)]|option">
                <xsl:variable name="dependent" select="@project"/>
                <xsl:for-each select="//project[@name=$dependent]">
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
        <td>
          <a href="{@name}.html"><xsl:value-of select="@name"/></a>
        </td>
        <td>
          <status/>
        </td>
      </tr>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="project[not(ant) and not(script)]"/>

  <xsl:template match="ant">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="*[name()!='property']"/>

      <xsl:if test="/workspace/build/@sysclasspath">
        <property name="build.sysclasspath"
          value="{/workspace/build/@sysclasspath}"/>
      </xsl:if>

      <xsl:for-each select="property">
        <xsl:variable name="name" select="@name"/>
        <xsl:choose>
          <xsl:when test="@reference='home'">
            <xsl:variable name="project" select="@project"/>
            <xsl:for-each select="//project[@name=$project]">
              <property name="{$name}" value="{home}"/>
            </xsl:for-each>
          </xsl:when>

          <xsl:when test="@reference='jar'">
            <xsl:variable name="project" select="@project"/>
            <xsl:variable name="id" select="@id"/>
            <xsl:for-each select="//project[@name=$project]">
              <property name="{$name}" value="{jar[@id=$id]/@name}"/>
            </xsl:for-each>
          </xsl:when>

          <xsl:when test="@reference='jarpath'">
            <xsl:variable name="project" select="@project"/>
            <xsl:variable name="id" select="@id"/>
            <xsl:for-each select="//project[@name=$project]">
              <property name="{$name}" value="{home}/{jar[@id=$id]/@name}"/>
            </xsl:for-each>
          </xsl:when>

          <xsl:when test="@path">
            <property name="{$name}" value="{ancestor::workspace/@basedir}/{ancestor::project/@srcdir}/{@path}"/>
          </xsl:when>

          <xsl:otherwise>
            <property name="{$name}" value="{@value}"/>
          </xsl:otherwise>
        </xsl:choose>

      </xsl:for-each>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
