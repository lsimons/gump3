<!-- ===================================================================== -->
<!--      replace references to projects with their actual definition      -->
<!-- ===================================================================== -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output indent="yes"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match="*|@*">
    <xsl:copy>
      <xsl:apply-templates select="* | @* | text()"/>
    </xsl:copy>
  </xsl:template>

  <!-- =================================================================== -->
  <!--           process all projects referenced in a workspace            -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">
    <xsl:variable name="version">0.2</xsl:variable>
    <xsl:if test="not(@version)">
      <xsl:message terminate="yes">
Cannot find version number, should be &lt;workspace version="<xsl:value-of select="$version"/>"&gt;
      </xsl:message>
    </xsl:if>
    <xsl:if test="not(@version=$version)">
      <xsl:message terminate="yes">
Hmm, looks like the wrong version <xsl:value-of select="@version"/>, expecting <xsl:value-of select="$version"/>
      </xsl:message>
    </xsl:if>
    <xsl:variable name="basedir" select="@basedir"/>
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

      <!-- default build style, if not present -->
      <xsl:if test="not(@build-sequence)">
        <xsl:attribute name="build-sequence">
          <xsl:text>bulk</xsl:text>
        </xsl:attribute>
      </xsl:if>

      <xsl:copy-of select="@*"/>

      <!-- Drop pre-processing versions of project and repository -->
      <xsl:copy-of select="*[not(self::project|self::repository)]"/>

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
        <xsl:variable name="tag" select="@tag"/>
        <xsl:for-each select="$file/project">
          <xsl:call-template name="project">
            <xsl:with-param name="home" select="$home"/>
            <xsl:with-param name="basedir" select="$basedir"/>
            <xsl:with-param name="tag" select="$tag"/>
            <xsl:with-param name="defined-in" select="$defined-in"/>
          </xsl:call-template>
        </xsl:for-each>

      </xsl:for-each>

      <!-- Process repositories -->
      <xsl:for-each select="repository[@href]">
        <xsl:text>&#10;&#10;</xsl:text>

        <!-- is the file found? -->

        <xsl:variable name="file" select="document(@href,.)"/>
        <xsl:if test="not($file/repository)">
          <xsl:message terminate="yes">
            <xsl:text>Unable to open </xsl:text>
            <xsl:value-of select="@href"/>
          </xsl:message>
        </xsl:if>

        <!-- process it -->

        <xsl:copy-of select="$file[not(self::home|self::project)] |@*| text()"/>


      </xsl:for-each>

    </xsl:copy>
  </xsl:template>

  <!-- =================================================================== -->
  <!--      resolve paths and add implicit dependencies to a project       -->
  <!-- =================================================================== -->

  <xsl:template name="project">
    <xsl:param name="home"/>
    <xsl:param name="basedir"/>
    <xsl:param name="tag"/>
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
      <xsl:apply-templates select="@*[name()!='srcdir']"/>

      <xsl:if test="$defined-in">
        <xsl:attribute name="defined-in">
          <xsl:value-of select="$defined-in"/>
        </xsl:attribute>
      </xsl:if>

      <xsl:attribute name="srcdir">
        <xsl:value-of select="$srcdir"/>
      </xsl:attribute>

      <xsl:attribute name="tag">
        <xsl:value-of select="$tag"/>
      </xsl:attribute>

      <xsl:apply-templates select="*[not(self::home|self::project)] | text()"/>

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

  <!-- =================================================================== -->
  <!--                         resolve buildpath                           -->
  <!-- =================================================================== -->

  <xsl:template match="ant">
    <xsl:copy>
      <xsl:attribute name="buildpath">
        <xsl:if test="@basedir">
          <xsl:value-of select="@basedir"/>
          <xsl:text>/</xsl:text>
        </xsl:if>

        <xsl:if test="@buildfile">
          <xsl:value-of select="@buildfile"/>
        </xsl:if>
        <xsl:if test="not(@buildfile)">
          <xsl:text>build.xml</xsl:text>
        </xsl:if>
      </xsl:attribute>

      <xsl:copy-of select="@* | * | text()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
