<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="text" omit-xml-declaration="yes"/>

  <xsl:template match="workspace">
    <script>#!/usr/bin/perl
    use File::Copy;
    use File::Path;

    my %map = (<xsl:apply-templates select="*"/>);

    foreach $source (sort keys %map) {
      if (-d $source) {
        $dest = $map{$source};
        rmtree $dest, 0, 0;
        mkpath $dest, 0, 0775;
        rmdir $dest;
        system "cp -r $source $dest";
        print "+ $source\n";
      } else {
        print "! $source\n";
      }
    }
    </script>
  </xsl:template>

  <xsl:template match="javadoc/description[@dest]">
    <data>
      "<xsl:value-of select="@source"/>" =&gt;
        "<xsl:value-of select="@dest"/>",</data>
  </xsl:template>

  <xsl:template match="*">
    <xsl:apply-templates select="*"/>
  </xsl:template>

</xsl:stylesheet>
