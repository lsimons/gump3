<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:variable name="basedir" select="/workspace/@basedir"/>
  <xsl:variable name="logdir"  select="/workspace/@logdir"/>

  <xsl:variable name="banner-link"  select="/workspace/@banner-link"/>
  <xsl:variable name="banner-image" select="/workspace/@banner-image"/>

  <xsl:template match="*|@*">
    <xsl:copy>
      <xsl:apply-templates select="*|@*"/>
    </xsl:copy>
  </xsl:template>

  <!-- =================================================================== -->
  <!-- provide support for specifying desired modules on the command line  -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">

    <update>
      <xsl:copy-of select="@*"/>

      <mkdir dir="{$basedir}"/>
      <mkdir dir="{$logdir}"/>
      <mkdir dir="{@cvsdir}"/>

      <output file="{$logdir}/cvslog.list">
        <strong><a href="index.html">Cvs logs</a></strong>
        <ul>
          <xsl:for-each select="module">
            <xsl:sort select="@name"/>
            <li>
              <a href="cvs_{@name}.html"><xsl:value-of select="@name"/></a>
            </li>
          </xsl:for-each>
        </ul>
      </output>

      <html log="{$logdir}/cvs_index.html"
        banner-image="{$banner-image}" banner-link="{$banner-link}">

        <title>
          <xsl:text>CVS update - </xsl:text>
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
          <a href="modxref.html">cross reference</a>
          <a href="index.html">build logs</a>
        </menu>

        <content>

          <table border="1">
            <tr>
              <th>Start time</th>
              <th>Module</th>
              <th>Status</th>
            </tr>

            <xsl:apply-templates select="module">
              <xsl:sort select="@name"/>
            </xsl:apply-templates>
          </table>
        </content>
      </html>

      <chdir dir="{$basedir}"/>
    </update>

  </xsl:template>

  <xsl:template match="module">

    <xsl:copy>
      <xsl:copy-of select="@*"/>

      <html log="{$logdir}/cvs_{@name}.html"
        banner-image="{$banner-image}" banner-link="{$banner-link}">

        <title>
          <xsl:text>cvs update </xsl:text>
          <xsl:value-of select="@name"/>
        </title>

        <sidebar>
          <include file="{$logdir}/cvslog.list"/>
        </sidebar>

        <menu>
          <date-time/>

          <br/>
          <xsl:text>Module: </xsl:text>
          <a href="module_{@name}.html">definition</a>
          <a href="modxref.html">cross reference</a>

          <xsl:variable name="module" select="@name"/>
          <xsl:if test="/workspace/project[@module=$module and (ant|script)]">
            <br/>
            <xsl:text>Project: </xsl:text>
          </xsl:if>

          <xsl:for-each select="/workspace/project[@module=$module]">
            <xsl:sort select="@name"/>
            <xsl:if test="ant|script">
              <a href="{@name}.html"><xsl:value-of select="@name"/></a>
            </xsl:if>
          </xsl:for-each>

        </menu>

        <content>
          <logic name="{@name}">
            <xsl:apply-templates select="cvs"/>
          </logic>
        </content>
      </html>

      <tr>
        <td>
          <start-time/>
        </td>
        <td class="status">
          <a href="cvs_{@name}.html"><xsl:value-of select="@name"/></a>
        </td>
        <td class="status">
          <status/>
        </td>
      </tr>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="module[not(cvs)]"/>

</xsl:stylesheet>
