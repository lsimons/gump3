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

    <xsl:variable name="basedir" select="../@basedir"/>
    <xsl:variable name="project" select="@name"/>

    <!-- determine the name of the module -->

    <xsl:variable name="module">
      <xsl:choose>
        <xsl:when test="@module">
          <xsl:value-of select="@module"/>
        </xsl:when>
        <xsl:when test="@defined-in">
          <xsl:value-of select="@defined-in"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="@name"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:variable name="srcdir" select="../module[@name=$module]/@srcdir"/>

    <xsl:copy>
      <xsl:apply-templates select="@*[name()!='module']"/>

      <xsl:attribute name="module">
        <xsl:value-of select="$module"/>
      </xsl:attribute>

      <xsl:apply-templates select="*[not(self::home)] | text()"/>

      <!-- Compute fully qualified home directory -->

      <home>
        <xsl:choose>
          <xsl:when test="@home">
             <xsl:value-of select="@home"/>
          </xsl:when>
          <xsl:when test="home/@parent">
             <xsl:value-of select="$basedir"/>
             <xsl:text>/</xsl:text>
             <xsl:value-of select="home/@parent"/>
          </xsl:when>
          <xsl:when test="home/@nested">
             <xsl:value-of select="$srcdir"/>
             <xsl:text>/</xsl:text>
             <xsl:value-of select="home/@nested"/>
          </xsl:when>
          <xsl:when test="home/@dir">
             <xsl:value-of select="@dir"/>
          </xsl:when>
          <xsl:when test="@package">
             <xsl:value-of select="../@pkgdir"/>
             <xsl:text>/</xsl:text>
             <xsl:value-of select="@package"/>
          </xsl:when>
          <xsl:otherwise>
             <xsl:value-of select="$srcdir"/>
          </xsl:otherwise>
        </xsl:choose>
      </home>
      <xsl:text>&#10;</xsl:text>

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
