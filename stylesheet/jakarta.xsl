<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output indent="yes"/>

  <xsl:template match="*|@*|text()">
    <xsl:copy>
      <xsl:apply-templates select="*|@*|text()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html">
    <html>
      <xsl:copy-of select="@*"/>

      <head>
        <title><xsl:value-of select="title/."/></title>
        <meta http-equiv="Content-Type"
              content="text/html; charset=iso-8859-1"/>
      </head>

      <body bgcolor="#ffffff" text="#000000" link="#525D76">

        <table border="0" width="100%" cellspacing="0">
          <tr>
            <td colspan="2">
              <a href="{@banner-link}">
                <img src="{@banner-image}" align="left" border="0"/>
              </a>
            </td>
          </tr>
        </table>

        <table border="0" width="100%" cellspacing="4">
          <tr>
            <td colspan="2">
              <hr noshade="" size="1"/>
            </td>
          </tr>
          <tr>
            <td valign="top" nowrap="true">
              <xsl:apply-templates select="sidebar/*"/>
            </td>
            <td align="left" valign="top">
              <table border="0" cellspacing="0" cellpadding="2" width="100%">
                <tr>
                  <td bgcolor="#525D76">
                    <font color="#ffffff" face="arial,helvetica,sanserif">
                      <strong>
                        <xsl:apply-templates select="title/*|title/text()"/>
                      </strong>
                    </font>
                  </td>
                </tr>
              </table>
              <xsl:apply-templates select="menu/*|menu/text()"/>
              <xsl:apply-templates select="content/*"/>
            </td>
          </tr>
          <tr>
            <td colspan="2">
              <hr noshade="" size="1"/>
            </td>
          </tr>
          <tr>
            <td colspan="2">
              <div align="center">
                <font color="#525D76" size="-1">
                  <em>
                    Copyright &amp;#169; 2001, Apache Software Foundation
                  </em>
                </font>
              </div>
            </td>
          </tr>
        </table>
      </body>

    </html>
  </xsl:template>
</xsl:stylesheet>
