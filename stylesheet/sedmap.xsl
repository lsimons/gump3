<!-- ===================================================================== -->
<!-- sort a list of projects into dependency order.                        -->
<!-- ===================================================================== -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:template match="workspace">

    <xsl:text>s/&amp;/\&amp;amp;/g&#10;</xsl:text>
    <xsl:text>s/&lt;/\&amp;lt;/g&#10;</xsl:text>
    <xsl:text>s/&gt;/\&amp;gt;/g&#10;</xsl:text>

    <xsl:text>s/&amp;lt;!--.*--&amp;gt;/</xsl:text>
    <xsl:text>&lt;font color="green"&gt;</xsl:text>
    <xsl:text>&amp;&lt;\/font&gt;/g&#10;</xsl:text>

    <xsl:text>s/repository *href="\(.*\)\/\(.*\).xml"/</xsl:text>
    <xsl:text>repository href="&lt;a href="repository_\2.html"&gt;</xsl:text>
    <xsl:text>\1\/\2.xml&lt;\/a&gt;"/g&#10;</xsl:text>

    <xsl:text>s/profile *href="\(.*\)\/\(.*\).xml"/</xsl:text>
    <xsl:text>profile href="&lt;a href="profile_\2.html"&gt;</xsl:text>
    <xsl:text>\1\/\2.xml&lt;\/a&gt;"/g&#10;</xsl:text>

    <xsl:text>s/project *href="\(.*\)\/\(.*\).xml"/</xsl:text>
    <xsl:text>project href="&lt;a href="project_\2.html"&gt;</xsl:text>
    <xsl:text>\1\/\2.xml&lt;\/a&gt;"/g&#10;</xsl:text>

    <xsl:text>s/home-page&amp;gt;\(.*\)&amp;lt;/</xsl:text>
    <xsl:text>home-page&gt;&lt;a href="\1"&gt;</xsl:text>
    <xsl:text>\1&lt;\/a&gt;\&amp;lt;/g&#10;</xsl:text>

    <xsl:text>s/cvs-web&amp;gt;\(.*\)&amp;lt;/</xsl:text>
    <xsl:text>cvs-web&gt;&lt;a href="\1"&gt;</xsl:text>
    <xsl:text>\1&lt;\/a&gt;\&amp;lt;/g&#10;</xsl:text>

    <xsl:text>s/url *href="\(.*\)"/</xsl:text>
    <xsl:text>url href="&lt;a href="\1"&gt;\1&lt;\/a&gt;"/g&#10;</xsl:text>

    <xsl:text>s/project *name="\([^ ]*\)"/</xsl:text>
    <xsl:text>project name="&lt;font color="red"&gt;</xsl:text>
    <xsl:text>\1&lt;\/font&gt;"/g&#10;</xsl:text>

    <xsl:for-each select="*[@defined-in]">

      <xsl:text>s/ project="</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>"/ project="&lt;a href="</xsl:text>
      <xsl:value-of select="name()"/>
      <xsl:text>_</xsl:text>
      <xsl:value-of select="@defined-in"/>
      <xsl:text>.html"&gt;</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>&lt;\/a&gt;"/g&#10;</xsl:text>

    </xsl:for-each>

    <xsl:text>1i\&#10;</xsl:text>
    <xsl:text>&lt;PRE&gt;&#10;</xsl:text>
    <xsl:text>$a\&#10;</xsl:text>
    <xsl:text>&lt;/PRE&gt;&#10;</xsl:text>

  </xsl:template>

</xsl:stylesheet>
