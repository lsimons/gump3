<?xml version="1.0" ?>
<!--
  Copyright 2002,2004 The Apache Software Foundation

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
