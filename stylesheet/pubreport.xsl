<?xml version="1.0" ?>
<!--
  Copyright 2003-2004 The Apache Software Foundation

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->
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

  <xsl:template match="junitreport/description[@dest]">
    <data>
      "<xsl:value-of select="@source"/>" =&gt;
        "<xsl:value-of select="@dest"/>",</data>
  </xsl:template>

  <xsl:template match="*">
    <xsl:apply-templates select="*"/>
  </xsl:template>

</xsl:stylesheet>
