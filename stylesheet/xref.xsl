<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:template match="workspace">

    <xref>

      <!-- =============================================================== -->
      <!--       Produce a cross reference of project dependencies         -->
      <!-- =============================================================== -->

      <html log="{@logdir}/xref.html"
        banner-image="{@banner-image}" banner-link="{@banner-link}">

        <title>Dependency Cross Reference</title>

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

        <menu>
          <xsl:text>Workspace: </xsl:text>
          <a href="workspace.html">definition</a>
          <a href="cvs_index.html">cvs logs</a>
          <a href="index.html">build logs</a>
          <br/>
          <xsl:text>Cross reference: </xsl:text>
          <a href="modxref.html">modules by repository</a>
          <a href="packages.html">installed packages</a>
          <a href="cvsjars.html">jars by module</a>
        </menu>

        <content>
          <table border="1">
            <tr>
              <th>Project</th>
              <th>Referenced by</th>
            </tr>

            <xsl:for-each select="/workspace/project">
              <xsl:sort select="@name"/>
              <xsl:variable name="project" select="@name"/>

              <tr>
                <td>
                  <a href="module_{@module}.html">
                    <xsl:value-of select="@name"/>
                  </a>
                </td>

                <td>

                  <!-- add a link for each project which depends on this one -->

                  <xsl:for-each select="/workspace/project
                      [depend[@project=$project] | option[@project=$project]]">
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

      <!-- =============================================================== -->
      <!--        Produce a listing of modules sorted by repository        -->
      <!-- =============================================================== -->

      <html log="{@logdir}/modxref.html"
        banner-image="{@banner-image}" banner-link="{@banner-link}">

        <title>List of modules, sorted by repository</title>

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
          <a href="cvs_index.html">cvs logs</a>
          <a href="index.html">build logs</a>
          <br/>
          <xsl:text>Cross reference: </xsl:text>
          <a href="xref.html">dependencies</a>
          <a href="packages.html">installed packages</a>
          <a href="cvsjars.html">jars by module</a>
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
                          <xsl:apply-templates select="description"/>
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

      <!-- =============================================================== -->
      <!--             Produce a listing of installed packages             -->
      <!-- =============================================================== -->

      <html log="{@logdir}/packages.html"
        banner-image="{@banner-image}" banner-link="{@banner-link}">

        <title>List of installed packages</title>

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

        <menu>
          <xsl:text>Workspace: </xsl:text>
          <a href="workspace.html">definition</a>
          <a href="cvs_index.html">cvs logs</a>
          <a href="index.html">build logs</a>
          <br/>
          <xsl:text>Cross reference: </xsl:text>
          <a href="xref.html">dependencies</a>
          <a href="modxref.html">modules by repository</a>
          <a href="cvsjars.html">jars by module</a>
        </menu>

        <content>

          <blockquote>
             <table class="content">
               <tr>
                 <th class="content">Package</th>
                 <th class="content">Version</th>
                 <th class="content">Description</th>
               </tr>

               <xsl:for-each select="/workspace/project[@package]">
                 <xsl:sort select="@name"/>
                 <xsl:variable name="project" select="@name"/>
                 <xsl:variable name="package" select="@package"/>
                 <xsl:variable name="module" select="@module"/>

                 <xsl:for-each select="/workspace/module[@name=$module]">
                   <tr>
                     <td class="content">
                       <xsl:if test="url/@href">
                         <a href="{url/@href}">
                           <xsl:value-of select="$project"/>
                         </a>
                       </xsl:if>
                       <xsl:if test="not(url/@href)">
                         <xsl:value-of select="$project"/>
                       </xsl:if>
                     </td>
                     <td class="content">
                       <xsl:value-of select="$package"/>
                     </td>
                     <td class="content">
                       <xsl:apply-templates select="description"/>
                     </td>
                   </tr>
                 </xsl:for-each>

               </xsl:for-each>

             </table>
          </blockquote>

        </content>

      </html>

      <!-- =============================================================== -->
      <!--              Produce a list of jars used from cvs               -->
      <!-- =============================================================== -->

      <html log="{@logdir}/cvsjars.html"
        banner-image="{@banner-image}" banner-link="{@banner-link}">

        <title>List of jars used from cvs</title>

        <sidebar>
          <strong><a href="index.html">Cvs logs</a></strong>
          <ul>
            <xsl:for-each select="module">
              <xsl:sort select="@name"/>
              <li>
                <a href="cvs_{@name}.html"><xsl:value-of select="@name"/></a>
              </li>
            </xsl:for-each>
          </ul>
        </sidebar>

        <menu>
          <xsl:text>Workspace: </xsl:text>
          <a href="workspace.html">definition</a>
          <a href="cvs_index.html">cvs logs</a>
          <a href="index.html">build logs</a>
          <br/>
          <xsl:text>Cross reference: </xsl:text>
          <a href="xref.html">dependencies</a>
          <a href="modxref.html">modules by repository</a>
          <a href="packages.html">installed packages</a>
        </menu>

        <content>

          <blockquote>
             <table class="content">
               <tr>
                 <th class="content">Package</th>
                 <th class="content">Module</th>
                 <th class="content">Description</th>
               </tr>

               <xsl:for-each select="/workspace/project
                 [jar and not(depend|script) and not(@package)]">

                 <xsl:sort select="@name"/>

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
                     <xsl:value-of select="@module"/>
                   </td>
                   <td class="content">
                     <xsl:apply-templates select="description"/>
                   </td>
                 </tr>

               </xsl:for-each>

             </table>
          </blockquote>
        </content>

      </html>
    </xref>

  </xsl:template>

  <xsl:template match="description">
    <xsl:copy-of select="* | text()"/>
  </xsl:template>

</xsl:stylesheet>
