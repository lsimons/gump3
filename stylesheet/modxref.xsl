<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!-- =================================================================== -->
  <!--         Produce a cross reference of project dependencies           -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">

    <xref>

      <html log="{@logdir}/modxref.html"
        banner-image="{@banner-image}" banner-link="{@banner-link}">

        <title>Repository listing</title>

        <sidebar>
          <strong>Repositories</strong>
          <ul>
            <xsl:for-each select="/workspace/repository">
              <xsl:sort select="@name"/>
              <li>
                <a href="#{@name}"><xsl:value-of select="title"/></a>
              </li>
            </xsl:for-each>
          </ul>
        </sidebar>

        <menu>
          <xsl:text>Workspace: </xsl:text>
          <a href="workspace.html">definition</a>
          <a href="xref.html">cross reference</a>
          <a href="cvs_index.html">cvs logs</a>
          <a href="index.html">build logs</a>
        </menu>

        <content>
          <blockquote>
            <xsl:for-each select="/workspace/module/cvs">
              <xsl:sort select="@repository"/>
              <xsl:variable name="r" select="@repository"/>

              <xsl:if test="not(preceding::cvs[@repository=$r])">
                <p/>

                <table width="100%" cellpadding="2" cellspacing="0" border="0">
                  <tr>
                    <td class="subtitle">
                      <xsl:for-each select="/workspace/repository[@name=$r]">
                        <a class="subtitle" name="{$r}" href="{home-page}">
                          <xsl:value-of select="title"/>
                        </a>
                      </xsl:for-each>
                    </td>
                  </tr>
                </table>

                <blockquote>
                  <table class="content">
                    <tr>
                      <th class="content">Module</th>
                      <th class="content">Description</th>
                    </tr>

                    <xsl:for-each 
                      select="/workspace/module[cvs/@repository=$r]">
                      <tr>
                        <td class="content">
                          <xsl:if test="url/@href">
                            <a href="{url/@href}">
                              <xsl:value-of select="@name"/>
                            </a>
                          </xsl:if>
                          <xsl:if test="not(url/@href)">
                            <xsl:value-of select="@name"/>
                          </xsl:if>
                        </td>
                        <td class="content">
                          <xsl:value-of select="normalize-space(description)"/>
                        </td>
                      </tr>
                    </xsl:for-each>

                  </table>
                </blockquote>

              </xsl:if>
            </xsl:for-each>
          </blockquote>

        </content>

      </html>
    </xref>

  </xsl:template>

</xsl:stylesheet>
