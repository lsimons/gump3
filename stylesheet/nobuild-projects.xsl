<!-- ===================================================================== -->
<!-- Copy a module  removing the "ant" tag.                                -->
<!-- This is usefull for referencing projects with out building them       -->
<!-- ===================================================================== -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  
  <xsl:output method="xml" />

<xsl:template match="@* | node()">
  <xsl:copy>
    <xsl:apply-templates select="@*"/>
    <xsl:apply-templates/>
  </xsl:copy>
</xsl:template>


<xsl:template match="ant | script | nag | javadoc | cvs">
	<xsl:comment>No build</xsl:comment>
</xsl:template>




</xsl:stylesheet>