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
        <style type="text/css">
          body {
            background-color: #ffffff;
            color: #000000;
            font-family: arial, helvetica, sanserif }
          :link { color: #525D76 }
          div.copyright {
            color: #525D76;
            font-size: 80%;
            text-align: center;
            font-weight: bold; }
          td.title {
            background-color: #525D76;
            color: #ffffff;
            font-weight: bold; }
          a.title { font-weight: bold; }
        </style>
      </head>

      <body>

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
                  <td class="title">
                    <xsl:apply-templates select="title/*|title/text()"/>
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
              <div align="center" class="copyright">
                Copyright &amp;#169; 2001, Apache Software Foundation
              </div>
            </td>
          </tr>
        </table>
      </body>

    </html>
  </xsl:template>
</xsl:stylesheet>
