<!-- ===================================================================== -->
<!-- Produce a sh script, which tars together packages that should be      -->
<!-- published and sends them to the servers.                              -->
<!-- ===================================================================== -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:strip-space elements="*"/>
  <xsl:output method="text" omit-xml-declaration="yes"/>

  <xsl:template match="text()|@*" />

  <xsl:template match="site[@username]">
    <xsl:if test="not(preceding::site[@username])">
      <xsl:text>#!/bin/sh&#10;</xsl:text>
      <xsl:text>&#10;</xsl:text>
      <xsl:text>rm -rf </xsl:text>
      <xsl:value-of select="@scratchdir"/>
      <xsl:text>&#10;</xsl:text>
      <xsl:text>mkdir </xsl:text>
      <xsl:value-of select="@scratchdir"/>
      <xsl:text>&#10;</xsl:text>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>

    <xsl:text>cd </xsl:text>
    <xsl:value-of select="@scratchdir"/>
    <xsl:text>&#10;</xsl:text>
    <xsl:text>mkdir </xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>cd </xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>&#10;</xsl:text>

    <xsl:text>echo &quot;#!/bin/sh&quot; &gt; deliver-</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.sh</xsl:text>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>echo &quot;cd </xsl:text>
    <xsl:value-of select="docroot"/>
    <xsl:text>&quot; &gt;&gt; deliver-</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.sh</xsl:text>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>echo &quot;tar xf </xsl:text>
    <xsl:value-of select="@dropdir"/>
    <xsl:text>/</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.tar&quot; &gt;&gt; deliver-</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.sh</xsl:text>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>echo &gt;&gt; deliver-</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.sh</xsl:text>
    <xsl:text>&#10;</xsl:text>

    <xsl:for-each select="deliver">
      <xsl:text>mkdirhier </xsl:text>
      <xsl:value-of select="@todir"/>
      <xsl:text>&#10;</xsl:text>
      <xsl:text>cp </xsl:text>
      <xsl:value-of select="@fromdir"/>
      <xsl:text>/* </xsl:text>
      <xsl:value-of select="@todir"/>
      <xsl:text>&#10;</xsl:text>

      <xsl:text>echo &quot;chgrp -R </xsl:text>
      <xsl:value-of select="../groupid/text()"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="@todir"/>
      <xsl:text>&quot; &gt;&gt; deliver-</xsl:text>
      <xsl:value-of select="../@name"/>
      <xsl:text>.sh</xsl:text>
      <xsl:text>&#10;</xsl:text>

      <xsl:text>echo &quot;chmod -R g+w </xsl:text>
      <xsl:value-of select="@todir"/>
      <xsl:text>&quot; &gt;&gt; deliver-</xsl:text>
      <xsl:value-of select="../@name"/>
      <xsl:text>.sh</xsl:text>
      <xsl:text>&#10;</xsl:text>

    </xsl:for-each>

    <xsl:text>&#10;</xsl:text>

    <xsl:text>tar cf </xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.tar *</xsl:text>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>scp </xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.tar </xsl:text>
    <xsl:value-of select="@username"/>
    <xsl:text>@</xsl:text>
    <xsl:value-of select="@server"/>
    <xsl:text>:</xsl:text>
    <xsl:value-of select="@dropdir"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>scp deliver-</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.sh </xsl:text>
    <xsl:value-of select="@username"/>
    <xsl:text>@</xsl:text>
    <xsl:value-of select="@server"/>
    <xsl:text>:</xsl:text>
    <xsl:value-of select="@dropdir"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>ssh </xsl:text>
    <xsl:value-of select="@username"/>
    <xsl:text>@</xsl:text>
    <xsl:value-of select="@server"/>
    <xsl:text> chmod +x </xsl:text>
    <xsl:value-of select="@dropdir"/>
    <xsl:text>/deliver-</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.sh</xsl:text>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>ssh </xsl:text>
    <xsl:value-of select="@username"/>
    <xsl:text>@</xsl:text>
    <xsl:value-of select="@server"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="@dropdir"/>
    <xsl:text>/deliver-</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.sh</xsl:text>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>ssh </xsl:text>
    <xsl:value-of select="@username"/>
    <xsl:text>@</xsl:text>
    <xsl:value-of select="@server"/>
    <xsl:text> rm -f </xsl:text>
    <xsl:value-of select="@dropdir"/>
    <xsl:text>/</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.tar</xsl:text>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>ssh </xsl:text>
    <xsl:value-of select="@username"/>
    <xsl:text>@</xsl:text>
    <xsl:value-of select="@server"/>
    <xsl:text> rm -f </xsl:text>
    <xsl:value-of select="@dropdir"/>
    <xsl:text>/deliver-</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.sh</xsl:text>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>ssh </xsl:text>
    <xsl:value-of select="@username"/>
    <xsl:text>@</xsl:text>
    <xsl:value-of select="@server"/>
    <xsl:text> rm -f </xsl:text>
    <xsl:value-of select="docroot/text()"/>
    <xsl:text>/deliver-</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.sh</xsl:text>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>&#10;</xsl:text>
  </xsl:template>
</xsl:stylesheet>
