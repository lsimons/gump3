<!-- ===================================================================== -->
<!-- Produce naglist                                                       -->
<!-- ===================================================================== -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:strip-space elements="*"/>
  <xsl:output method="text" omit-xml-declaration="yes" 
              encoding="ISO-8859-1"/>

  <xsl:template match="text()|@*" />

  <xsl:template match="nag">
    <xsl:if test="not(preceding::nag)">
      <xsl:text>--------&#10;</xsl:text>
    </xsl:if>

    <xsl:text>Project: </xsl:text>
    <xsl:value-of select="../@name" />
    <xsl:text>&#10;</xsl:text>

    <xsl:for-each select="regexp">
      <xsl:text>To: </xsl:text>
      <xsl:value-of select="@to" />
      <xsl:text>&#10;</xsl:text>
      <xsl:text>From: </xsl:text>
      <xsl:value-of select="@from" />
      <xsl:text>&#10;</xsl:text>
      <xsl:text>Subject: </xsl:text>
      <xsl:value-of select="@subject" />
      <xsl:text>&#10;</xsl:text>
      <xsl:text>Regex: </xsl:text>
      <xsl:value-of select="@pattern" />
      <xsl:text>&#10;</xsl:text>
    </xsl:for-each>

    <xsl:text>--------&#10;</xsl:text>
  </xsl:template>
</xsl:stylesheet>
