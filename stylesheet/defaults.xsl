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
  <!--           process all projects referenced in a workspace            -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">
    <xsl:variable name="basedir" select="@basedir"/>
    <xsl:variable name="version">0.3</xsl:variable>

    <xsl:if test="not(@version)">
      <xsl:message terminate="yes">
        <xsl:text>Cannot find version number, should be </xsl:text>
        <xsl:text>&lt;workspace version="</xsl:text>
        <xsl:value-of select="$version"/>
        <xsl:text>"&gt;</xsl:text>
      </xsl:message>
    </xsl:if>

    <xsl:if test="not(@version=$version)">
      <xsl:message terminate="yes">
        <xsl:text>Hmm, looks like the wrong version </xsl:text>
        <xsl:value-of select="@version"/>
        <xsl:text>, expecting </xsl:text>
        <xsl:value-of select="$version"/>
      </xsl:message>
    </xsl:if>

    <xsl:copy>

      <!-- default banner-image, if not present -->
      <xsl:if test="not(@banner-image)">
        <xsl:attribute name="banner-image">
          <xsl:text>http://jakarta.apache.org/images/jakarta-logo.gif</xsl:text>
        </xsl:attribute>
      </xsl:if>

      <!-- default banner-link, if not present -->
      <xsl:if test="not(@banner-link)">
        <xsl:attribute name="banner-link">
          <xsl:text>http://jakarta.apache.org</xsl:text>
        </xsl:attribute>
      </xsl:if>

      <!-- default log directory, if not present -->
      <xsl:if test="not(@logdir)">
        <xsl:attribute name="logdir">
          <xsl:value-of select="$basedir"/>
          <xsl:text>/log</xsl:text>
        </xsl:attribute>
      </xsl:if>

      <!-- default cvs directory, if not present -->
      <xsl:if test="not(@cvsdir)">
        <xsl:attribute name="cvsdir">
          <xsl:value-of select="$basedir"/>
          <xsl:text>/cvs</xsl:text>
        </xsl:attribute>
      </xsl:if>

      <!-- default build style, if not present -->
      <xsl:if test="not(@build-sequence)">
        <xsl:attribute name="build-sequence">
          <xsl:text>bulk</xsl:text>
        </xsl:attribute>
      </xsl:if>

      <!-- copy the rest -->
      <xsl:apply-templates select="* | @* | text()"/>

    </xsl:copy>

  </xsl:template>

  <!-- =================================================================== -->
  <!--      resolve paths and add implicit dependencies to a project       -->
  <!-- =================================================================== -->

  <xsl:template match="project">

    <xsl:variable name="basedir" select="../@basedir"/>
    <xsl:variable name="project" select="@name"/>

    <!-- determine the name of the source directory -->

    <xsl:variable name="srcdir">
      <xsl:choose>
        <xsl:when test="@srcdir">
          <xsl:value-of select="@srcdir"/>
        </xsl:when>
        <xsl:when test="@defined-in">
          <xsl:value-of select="@defined-in"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="@name"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:copy>
      <xsl:apply-templates select="@*[name()!='srcdir']"/>

      <xsl:attribute name="srcdir">
        <xsl:value-of select="$srcdir"/>
      </xsl:attribute>

      <xsl:apply-templates select="*[not(self::home|self::project)] | text()"/>

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
             <xsl:value-of select="$basedir"/>
             <xsl:text>/</xsl:text>
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
             <xsl:value-of select="$basedir"/>
             <xsl:text>/</xsl:text>
             <xsl:value-of select="$srcdir"/>
          </xsl:otherwise>
        </xsl:choose>
      </home>
      <xsl:text>&#10;</xsl:text>

      <!-- Generate additional dependency entries, as needed -->

      <xsl:for-each select="ant/property[@project!=$project and 
                                         not(@reference='srcdir')]">

        <xsl:variable name="dependency" select="@project"/>
        <xsl:if test="not(../../depend[@project=$dependency])">

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
