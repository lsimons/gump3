<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="page">

<html lang="en" xml:lang="en">
<head>
 <title><xsl:value-of select="title"/></title>
 <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
 <link rel="stylesheet" type="text/css" href="/styles/print.css" media="print"/> <link rel="stylesheet" type="text/css" href="/styles/base/content.css" media="all"/> <link rel="stylesheet" type="text/css" href="/styles/cavendish/content.css" title="Cavendish" media="all"/> <link rel="stylesheet" type="text/css" href="/styles/base/template.css" media="screen"/> <link rel="stylesheet" type="text/css" href="/styles/cavendish/template.css" title="Cavendish" media="screen"/>
 <link rel="icon" href="/images/icon.png" type="image/png"/>
 <xsl:apply-templates select="style"/>
 <script src="/scripts/search.js" type="text/javascript">//</script>
</head>

<body>

<div id="top">
 <ul class="path">
  <xsl:apply-templates select="path"/>
 </ul>
</div>

<div id="center">

<div id="header">
 <h1><a href="/" title="Apache Gump" accesskey="1">Apache Gump</a></h1>
 <ul>
  <xsl:apply-templates select="tabs"/>
 </ul>
 <div class="searchbox">
   <label> </label>
   <!--input type="text" width="10" onkeyup="act(event)"/-->
 </div>
</div>

<xsl:if test="sidebar">
<div id="side" class="left">	
  <div id="menubar">
    <ul id="nav">
      <xsl:apply-templates select="sidebar"/>
	</ul>
  </div>
</div>
</xsl:if>

<div id="body">
  <xsl:if test="sidebar">
   <xsl:attribute name="class">withside</xsl:attribute>
  </xsl:if>
  <xsl:apply-templates select="content"/>
</div>

</div>

<div id="bottom">
  <div id="footer">
    <p>Copyright (c) 2000-2004 The Apache Software Foundation and its licensors. Some rights reserved.</p>
  </div>
</div>

</body>
</html>  
</xsl:template>

<xsl:template match="item">
  <li><a href="{@url}" title="{@name}"><xsl:value-of select="@name"/></a></li>
</xsl:template>

<xsl:template match="current">
  <li class="current"><span><xsl:value-of select="@name"/></span></li>
</xsl:template>

<xsl:template match="content">
 <xsl:apply-templates/>
</xsl:template>

<xsl:template match="sidebar/item">
  <li>
    <a href="{@url}"><strong><xsl:value-of select="@name"/></strong>
     <xsl:if test="description"><br/><span class="description"><xsl:value-of select="description"/></span></xsl:if>
    </a>
  </li>
</xsl:template>

<xsl:template match="sidebar/current">
  <li>
    <span><strong><xsl:value-of select="@name"/></strong>
     <xsl:if test="description"><br/><span class="description"><xsl:value-of select="description"/></span></xsl:if>
    </span>
  </li>
</xsl:template>

<xsl:template match="*|@*|text()">
 <xsl:copy>
   <xsl:apply-templates select="*|@*|text()"/>
 </xsl:copy>
</xsl:template>

</xsl:stylesheet>
