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
  <!-- provide support for specifying desired projects on the command line -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">

    <update>
      <xsl:copy-of select="@*"/>

      <mkdir dir="{$basedir}"/>
      <mkdir dir="{$logdir}"/>
      <mkdir dir="{@cvsdir}"/>

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

        <menu/>

        <content>

          <table border="1">
            <tr>
              <th>Start time</th>
              <th>Project</th>
              <th>Status</th>
            </tr>

            <xsl:apply-templates select="project">
              <xsl:sort select="@name"/>
            </xsl:apply-templates>
          </table>
        </content>
      </html>

      <chdir dir="{$basedir}"/>
    </update>

  </xsl:template>

  <xsl:template match="project">

    <xsl:copy>
      <xsl:copy-of select="@*"/>

      <html log="{$logdir}/cvs_{@name}.html" 
        banner-image="{$banner-image}" banner-link="{$banner-link}">

        <title>
          <xsl:text>cvs update </xsl:text>
          <xsl:value-of select="@name"/>
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
        </menu>

        <content>
          <logic>
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

  <xsl:template match="project[not(cvs)]"/>

  <!-- =================================================================== -->
  <!-- pre-resolve repository for later convenience                        -->
  <!-- =================================================================== -->

  <xsl:template match="cvs">
    <xsl:variable name="repository" select="@repository"/>
    <cvs srcdir="{ancestor::project/@srcdir}">

      <xsl:attribute name="repository">
        <xsl:value-of select="//cvs-repository/tree[@name=$repository]/@root"/>
        <xsl:if test="@dir">
          <xsl:text>/</xsl:text>
          <xsl:value-of select="@dir"/>
        </xsl:if>
      </xsl:attribute>

      <xsl:apply-templates select="@*[not(name()='repository')]"/>

      <xsl:if test="not(@module)">
        <xsl:attribute name="module">
          <xsl:value-of select="ancestor::project/@name"/>
        </xsl:attribute>
      </xsl:if>
    </cvs>
  </xsl:template>

</xsl:stylesheet>
