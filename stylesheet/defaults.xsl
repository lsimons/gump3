<!-- ===================================================================== -->
<!--      replace references to projects with their actual definition      -->
<!-- ===================================================================== -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:template match="*|@*|text()">
    <xsl:copy>
      <xsl:apply-templates select="* | @* | text()"/>
    </xsl:copy>
  </xsl:template>

  <!-- =================================================================== -->
  <!--      resolve paths and add implicit dependencies to a project       -->
  <!-- =================================================================== -->

  <xsl:template match="project">

    <xsl:variable name="project" select="@name"/>

    <xsl:copy>
      <xsl:apply-templates select="@* | * | text()"/>

      <!-- Generate additional dependency entries, as needed -->

      <xsl:for-each select="ant/property[@project!=$project and 
                                         not(@reference='srcdir')]">

        <xsl:variable name="dependency" select="@project"/>
        <xsl:if test="not(../../depend[@project=$dependency]) and
                      not(../../option[@project=$dependency])">

          <xsl:variable name="position" select="position()"/>
          <xsl:if test="not(../property[position() &lt; $position and
                                        @project=$dependency])">
            <depend project="{$dependency}">
              <xsl:if test="not(@classpath)">
                <noclasspath/>
              </xsl:if>
            </depend>
            <xsl:text>&#10;</xsl:text>

          </xsl:if>
        </xsl:if>

      </xsl:for-each>

    </xsl:copy>

  </xsl:template>

</xsl:stylesheet>
