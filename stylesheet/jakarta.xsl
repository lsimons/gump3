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
        <xsl:apply-templates select="title"/>
        <meta http-equiv="Content-Type"
              content="text/html; charset=iso-8859-1"/>
        <style type="text/css">
          body {
            background-color: #ffffff;
            color: #000000 }
          :link { color: #525D76 }
          div.copyright {
            color: #525D76;
            font-size: 80%;
            text-align: center;
            font-weight: bold; }
          td.sidebar {
            font-family: arial, helvetica, sanserif }
          td.title {
            background-color: #525D76;
            color: #ffffff;
            font-weight: bold; }
          td.subtitle, a.subtitle:link, a.subtitle:visited {
            background-color: #828DA6;
            color: #ffffff;
            text-decoration: none;
            font-weight: bold; 
            font-family: arial, helvetica, sanserif }
          td.note {
            background-color: #B1B7C1;
            color: #000000;
            font-family: arial, helvetica, sanserif }
          table.content {
            border: 0;
            font-family: arial, helvetica, sanserif }
          th.content {
            margin: 0;
            padding: 2;
            color: #000000;
            background-color: #039acc;
            text-align: left;
            font-weight: bold; 
            font-family: arial, helvetica, sanserif }
          td.content {
            margin: 0;
            padding: 2;
            color: #000000;
            background-color: #a0ddf0;
            font-family: arial, helvetica, sanserif }
          td.fail {
            background-color: red;
            font-weight: bold; }
          td.warn {
            background-color: yellow }
          a.title { font-weight: bold; }
        </style>
      </head>

      <body>

        <table border="0" width="100%" cellspacing="0">
          <tr>
            <td>
              <a href="{@banner-link}">
                <img src="{@banner-image}" align="left" border="0"/>
              </a>
            </td>
            <td>
              <a href="http://jakarta.apache.org/gump/">
                <img src="http://jakarta.apache.org/gump/images/bench.png" 
                  align="right" border="0"/>
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
            <td valign="top" nowrap="true" class="sidebar">
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

              <xsl:if test="note">
                <p/>
                <table border="0" cellspacing="0" cellpadding="2" width="100%">
                  <tr>
                    <td class="note">
                      <strong>
                          Note:
                      </strong>
                      <xsl:apply-templates select="note/text()"/>
                    </td>
                  </tr>
                </table>
              </xsl:if>

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


  <xsl:template match="subsection">
    <table border="0" cellspacing="0" cellpadding="2" width="100%">
      <tr>
        <td class="subtitle">
          <xsl:value-of select="@name"/>
        </td>
      </tr>
      <tr>
        <td>
          <blockquote>
            <xsl:apply-templates/>
          </blockquote>
        </td>
      </tr>
      <tr>
        <td>
          <br/>
        </td>
      </tr>
    </table>
  </xsl:template>

</xsl:stylesheet>
