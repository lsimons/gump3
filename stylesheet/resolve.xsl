<!-- ===================================================================== -->
<!--      replace references to projects with their actual definition      -->
<!-- ===================================================================== -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!-- =================================================================== -->
  <!--           process all projects referenced in a workspace            -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">
    <xsl:variable name="basedir" select="@basedir"/>
    <xsl:copy>

      <xsl:copy-of select="@*"/>
      <xsl:copy-of select="*[not(self::project)]"/>

      <!-- process any directly nested projects verbatim -->

      <xsl:for-each select="project[not(@href)]">
        <xsl:call-template name="project">
          <xsl:with-param name="home" select="@home"/>
          <xsl:with-param name="basedir" select="$basedir"/>
        </xsl:call-template>
      </xsl:for-each>

      <!-- embed any projects specified by href -->

      <xsl:for-each select="project[@href]">
        <xsl:variable name="home" select="@home"/>
        <xsl:message>
           <xsl:text>  </xsl:text>
           <xsl:value-of select="@href"/>
        </xsl:message>
        <xsl:text>&#10;&#10;</xsl:text>

        <!-- is the href found? -->

        <xsl:variable name="file" select="document(@href,.)"/>
        <xsl:if test="not($file/project)">
           <xsl:message terminate="yes">
              <xsl:text>Unable to open </xsl:text>
              <xsl:value-of select="@href"/>
           </xsl:message>
        </xsl:if>

        <!-- process it -->

        <xsl:variable name="defined-in"
           select="substring-before(substring-after(@href,'/'),'.')"/>
        <xsl:for-each select="$file/project">
          <xsl:call-template name="project">
            <xsl:with-param name="home" select="$home"/>
            <xsl:with-param name="basedir" select="$basedir"/>
            <xsl:with-param name="defined-in" select="$defined-in"/>
          </xsl:call-template>
        </xsl:for-each>

      </xsl:for-each>

    </xsl:copy>
  </xsl:template>

  <!-- =================================================================== -->
  <!--      resolve paths and add implicit dependencies to a project       -->
  <!-- =================================================================== -->

  <xsl:template name="project">
    <xsl:param name="home"/>
    <xsl:param name="basedir"/>
    <xsl:param name="defined-in"/>

    <xsl:variable name="project" select="@name"/>

    <!-- determine the name of the source directory -->

    <xsl:variable name="srcdir">
      <xsl:choose>
        <xsl:when test="@srcdir">
          <xsl:value-of select="@srcdir"/>
        </xsl:when>
        <xsl:when test="../@srcdir">
          <xsl:value-of select="../@srcdir"/>
        </xsl:when>
        <xsl:when test="../@name">
          <xsl:value-of select="../@name"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="@name"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:copy>
      <xsl:copy-of select="@*[name()!='srcdir']"/>

      <xsl:if test="$defined-in">
        <xsl:attribute name="defined-in">
          <xsl:value-of select="$defined-in"/>
        </xsl:attribute>
      </xsl:if>

      <xsl:attribute name="srcdir">
        <xsl:value-of select="$srcdir"/>
      </xsl:attribute>

      <xsl:copy-of select="*[not(self::home|self::project)] | text()"/>

      <!-- Compute fully qualified home directory -->

      <home>
        <xsl:choose>
          <xsl:when test="$home">
             <xsl:value-of select="$home"/>
          </xsl:when>
          <xsl:when test="home/@parent">
             <xsl:value-of select="$basedir"/>
             <xsl:text>/</xsl:text>
             <xsl:value-of select="home/@parent"/>
          </xsl:when>
          <xsl:when test="home/@nested">
             <xsl:value-of select="$basedir"/>
             <xsl:text>/</xsl:text>
             <xsl:value-of select="$srcdir"/>
             <xsl:text>/</xsl:text>
             <xsl:value-of select="home/@nested"/>
          </xsl:when>
          <xsl:when test="home/@dir">
             <xsl:value-of select="@dir"/>
          </xsl:when>
          <xsl:otherwise>
             <xsl:value-of select="$basedir"/>
             <xsl:text>/</xsl:text>
             <xsl:value-of select="$srcdir"/>
          </xsl:otherwise>
        </xsl:choose>
      </home>
      <xsl:text>&#10;</xsl:text>

      <!-- Generate additional dependency entries, as needed -->

      <xsl:for-each select="ant/property[@project!=$project]">

        <xsl:variable name="dependency" select="@project"/>
        <xsl:if test="not(../../depend[@project=$dependency])">

          <xsl:variable name="position" select="position()"/>
          <xsl:if test="not(../property[position() &lt; $position and
                                        @project=$dependency])">
            <depend>
              <xsl:attribute name="project">
                <xsl:value-of select="$dependency"/>
              </xsl:attribute>
              <noclasspath/>
            </depend>
            <xsl:text>&#10;</xsl:text>

          </xsl:if>
        </xsl:if>

      </xsl:for-each>

    </xsl:copy>

    <!-- process nested projects -->

    <xsl:for-each select="project">
      <xsl:text>&#10;&#10;</xsl:text>
      <xsl:call-template name="project">
        <xsl:with-param name="home" select="$home"/>
        <xsl:with-param name="basedir" select="$basedir"/>
        <xsl:with-param name="defined-in" select="$defined-in"/>
      </xsl:call-template>
    </xsl:for-each>

  </xsl:template>

</xsl:stylesheet>
