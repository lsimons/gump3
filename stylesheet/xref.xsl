<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:variable name="basedir"
    select="translate(/workspace/@basedir, '\', '/')"/>

	<xsl:variable name="logdir">
		<xsl:choose>
			<xsl:when test="/workspace/@logdir"><xsl:value-of
				select="translate(/workspace/@logdir, '\', '/')"/></xsl:when>
			<xsl:otherwise><xsl:value-of select="$basedir"/>
				<xsl:text>/log</xsl:text>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:variable>

  <!-- =================================================================== -->
  <!--         Produce a cross reference of project dependencies           -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">

    <xref>

      <html log="{$logdir}/xref.html">
        <title>Cross Reference</title>

        <sidebar>
          <strong><a href="index.html">Build logs</a></strong>
          <ul>
            <xsl:for-each select="project[ant|script]">
              <xsl:sort select="@name"/>
              <li>
                <a href="{@name}.html"><xsl:value-of select="@name"/></a>
              </li>
            </xsl:for-each>
          </ul>
        </sidebar>

        <menu/>

        <content>
          <table border="1">
            <tr>
              <th>Project</th>
              <th>Referenced by</th>
            </tr>

            <xsl:for-each select="//project">
              <xsl:sort select="@name"/>
              <xsl:variable name="project" select="@name"/>

              <tr>
                <td>
                  <a href="source_{@srcdir}.html">
                    <xsl:value-of select="@name"/>
                  </a>
                </td>

                <td>

                  <!-- add a link for each project which depends on this one -->

                  <xsl:for-each select="//project[depend[@project=$project] |
                                                  option[@project=$project]]">
                    <xsl:sort select="@name"/>

                    <!-- "decorate open" link based on type of dependency -->
                      <xsl:if test="not(depend[@project=$project])">
                        <xsl:text>[</xsl:text>
                      </xsl:if>

                      <xsl:if test="depend[@project=$project]/noclasspath">
                        <xsl:text>${</xsl:text>
                      </xsl:if>
                    <!-- end "decoration" -->

                    <!-- the link itself -->
                    <a href="{@name}.html">
                      <xsl:value-of select="@name"/>
                    </a>

                    <!-- "decorate close" link based on type of dependency -->
                      <xsl:if test="depend[@project=$project]/noclasspath">
                        <xsl:text>}</xsl:text>
                      </xsl:if>

                      <xsl:if test="not(depend[@project=$project])">
                        <xsl:text>]</xsl:text>
                      </xsl:if>
                    <!-- end "decoration" -->
                  </xsl:for-each>
                </td>
              </tr>
            </xsl:for-each>
          </table>

          <br/> Legend:
          <blockquote>
            [] : optional dependency
            <br/> ${} : property reference
          </blockquote>
        </content>

      </html>
    </xref>

  </xsl:template>

</xsl:stylesheet>
