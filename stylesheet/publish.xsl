<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output indent="yes"/>

  <!-- =================================================================== -->
  <!-- provide support for specifying desired projects on the command line -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">

    <publish>

      <html banner-image="{@banner-image}" banner-link="{@banner-link}">
        <title>
          <xsl:text>Source: </xsl:text>
          <code><arg/></code>
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
          <sed script="map.sed"/>
        </content>

      </html>
    </publish>

  </xsl:template>

</xsl:stylesheet>
