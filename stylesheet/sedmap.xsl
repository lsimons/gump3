<!-- ===================================================================== -->
<!-- Produce a Perl script which converts XML into HTML for viewing        -->
<!-- ===================================================================== -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:strip-space elements="*"/>
  <xsl:output method="text" omit-xml-declaration="yes"/>

  <xsl:template match="workspace">

    <xsl:text></xsl:text>
    <xsl:text>print "&lt;PRE&gt;\n";&#10;</xsl:text>
    <xsl:text>while (&lt;&gt;) {&#10;</xsl:text>

    <!-- Escape XML entities -->
    <xsl:text>  s/&amp;/\&amp;amp;/g;&#10;</xsl:text>
    <xsl:text>  s/&lt;/\&amp;lt;/g;&#10;</xsl:text>
    <xsl:text>  s/&gt;/\&amp;gt;/g;&#10;</xsl:text>

    <!-- Make comments green -->
    <xsl:text>  s/(&amp;lt;!--.*--&amp;gt;)/</xsl:text>
    <xsl:text>&lt;font color="green"&gt;</xsl:text>
    <xsl:text>$1&lt;\/font&gt;/g;&#10;</xsl:text>

    <!-- Make project names red -->
    <xsl:text>  s/project *name="(\S*)"/</xsl:text>
    <xsl:text>project name="&lt;font color="red"&gt;</xsl:text>
    <xsl:text>$1&lt;\/font&gt;"/g;&#10;</xsl:text>

    <!-- Make hrefs work -->
    <xsl:text>  s/repository *href="(.*)\/(.*).xml"/</xsl:text>
    <xsl:text>repository href="&lt;a href="repository_$2.html"&gt;</xsl:text>
    <xsl:text>$1\/$2.xml&lt;\/a&gt;"/g;&#10;</xsl:text>

    <xsl:text>  s/profile *href="(.*)\/(.*).xml"/</xsl:text>
    <xsl:text>profile href="&lt;a href="profile_$2.html"&gt;</xsl:text>
    <xsl:text>$1\/$2.xml&lt;\/a&gt;"/g;&#10;</xsl:text>

    <xsl:text>  s/module *href="(.*)\/(.*).xml"/</xsl:text>
    <xsl:text>module href="&lt;a href="module_$2.html"&gt;</xsl:text>
    <xsl:text>$1\/$2.xml&lt;\/a&gt;"/g;&#10;</xsl:text>

    <xsl:text>  s/home-page&amp;gt;(.*)&amp;lt;/</xsl:text>
    <xsl:text>home-page&gt;&lt;a href="$1"&gt;</xsl:text>
    <xsl:text>$1&lt;\/a&gt;\&amp;lt;/g;&#10;</xsl:text>

    <xsl:text>  s/cvs-web&amp;gt;(.*)&amp;lt;/</xsl:text>
    <xsl:text>cvs-web&gt;&lt;a href="$1"&gt;</xsl:text>
    <xsl:text>$1&lt;\/a&gt;\&amp;lt;/g;&#10;</xsl:text>

    <xsl:text>  s/url *href="(.*)"/</xsl:text>
    <xsl:text>url href="&lt;a href="$1"&gt;$1&lt;\/a&gt;"/g;&#10;</xsl:text>

    <!-- Link each referenced project to where it was defined -->
    <xsl:for-each select="project[@defined-in]">
      <xsl:text>  s/ project="</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>"/ project="&lt;a href="</xsl:text>
      <xsl:value-of select="concat(name(),'_',@defined-in,'.html')"/>
      <xsl:text>"&gt;</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>&lt;\/a&gt;"/g;&#10;</xsl:text>
    </xsl:for-each>

    <!-- Link each referenced repository to where it was defined -->
    <xsl:for-each select="repository[@defined-in]">
      <xsl:text>  s/ repository="</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>"/ repository="&lt;a href="</xsl:text>
      <xsl:value-of select="concat(name(),'_',@defined-in,'.html')"/>
      <xsl:text>"&gt;</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>&lt;\/a&gt;"/g;&#10;</xsl:text>
    </xsl:for-each>

    <xsl:text>  print;&#10;</xsl:text>
    <xsl:text>}&#10;</xsl:text>
    <xsl:text>print "&lt;/PRE&gt;\n";&#10;</xsl:text>

  </xsl:template>

</xsl:stylesheet>
