<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output indent="yes"/>

  <xsl:template match="text()|@*" />

  <xsl:template match="workspace">
    <movefiles>
      <xsl:apply-templates/>
    </movefiles>
  </xsl:template>

  <xsl:template match="*[@cache-as]">
    <move todir="{@cache-as}" file="work/{@extern-prefix}{@name}.xml"/>
  </xsl:template>
</xsl:stylesheet>