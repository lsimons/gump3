<?xml version="1.0" ?>
<!--
  Copyright 2001-2004 The Apache Software Foundation

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

  <xsl:output indent="yes"/>

  <xsl:template match="*|@*">
    <xsl:copy>
      <xsl:apply-templates select="*|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:variable name="basedir" select="/workspace/@basedir"/>
  <xsl:variable name="cvsdir"  select="/workspace/@cvsdir"/>
  <xsl:variable name="logdir"  select="/workspace/@logdir"/>

  <xsl:variable name="banner-link"  select="/workspace/@banner-link"/>
  <xsl:variable name="banner-image" select="/workspace/@banner-image"/>

  <!-- =================================================================== -->
  <!-- provide support for specifying desired projects on the command line -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">

    <build sync="{@sync}" basedir="{$basedir}" >

      <scorecard file="{$logdir}/results.txt"/>

      <chdir dir="{$basedir}"/>
      <mkdir dir="{$logdir}"/>
      <delete dir="build"/>
      <delete dir="dist"/>

      <!-- restore up old build directories -->
      <project name="clean">
        <html log="{$logdir}/clean.html"
          banner-image="{$banner-image}" banner-link="{$banner-link}">
          <title>
            <xsl:text>Synchronization status - </xsl:text>
            <date/>
          </title>
          <content>
            <logic name="clean">
              <xsl:for-each select="module[cvs]">
                <xsl:if test="not(/workspace/@sync)">
                  <delete dir="{@srcdir}"/>
                  <copy fromdir="{$cvsdir}/{@name}" todir="{@srcdir}"/>
                </xsl:if>
                <xsl:if test="/workspace/@sync">
                  <sync fromdir="{$cvsdir}/{@name}" todir="{@srcdir}"/>
                </xsl:if>
              </xsl:for-each>
              <xsl:if test="@jardir">
                <delete dir="{@jardir}"/>
              </xsl:if>
            </logic>
          </content>
        </html>
      </project>

      <output file="{$logdir}/buildlog.list">
        <strong><a href="index.html">Build logs</a></strong>
        <ul>
          <xsl:for-each select="project[ant|script]">
            <xsl:sort select="@name"/>
            <li>
              <a href="{@name}.html"><xsl:value-of select="@name"/></a>
            </li>
          </xsl:for-each>
        </ul>
      </output>

      <html log="{$logdir}/index.html"
        banner-image="{$banner-image}" banner-link="{$banner-link}">

        <title>
          <xsl:text>Build status - </xsl:text>
          <date/>
        </title>

        <sidebar>
          <include file="{$logdir}/buildlog.list"/>
        </sidebar>

        <menu>
          <xsl:text>Workspace: </xsl:text>
          <a href="workspace.html">definition</a>
          <a href="xref.html">cross reference</a>
          <a href="cvs_index.html">cvs logs</a>
        </menu>

        <content>

          <table border="1">
            <tr>
              <th>Start time</th>
              <th>Project</th>
              <th>Status</th>
            </tr>

            <xsl:apply-templates select="project"/>
          </table>
        </content>
      </html>

    </build>

  </xsl:template>

  <xsl:template match="project">
    <xsl:copy>
      <xsl:copy-of select="@*"/>

      <html log="{$logdir}/{@name}.html"
        banner-image="{$banner-image}" banner-link="{$banner-link}">

        <title>
          <xsl:text>Build </xsl:text>
          <xsl:value-of select="@name"/>
          <xsl:if test="description">
            <xsl:text> - </xsl:text>
            <xsl:value-of select="normalize-space(description)"/>
          </xsl:if>
        </title>

        <xsl:copy-of select="note"/>

        <sidebar>
          <include file="{$logdir}/buildlog.list"/>
        </sidebar>

        <menu>
          <date-time/>
          <br/>

          <xsl:text>Module: </xsl:text>

          <a href="module_{@defined-in}.html">definition</a>

          <xsl:if test="url">
            <a href="{url/@href}">home</a>
          </xsl:if>

          <a href="cvs_{@module}.html">cvs</a>

          <!-- dependencies -->

          <br/>
          <xsl:text>Dependencies: </xsl:text>
          <xsl:for-each select="depend|option">
            <xsl:choose>
              <xsl:when test="ant|script">
                <a href="{@project}.html">
                  <xsl:value-of select="@project"/>
                </a>
              </xsl:when>
              <xsl:when test="@defined-in">
                <a href="module_{@defined-in}.html">
                  <xsl:value-of select="@project"/>
                </a>
              </xsl:when>
            </xsl:choose>
          </xsl:for-each>
        </menu>

        <content>

          <!-- prereq check -->

          <xsl:for-each select="depend[not(noclasspath)]">
            <prereq project="{@project}">
              <xsl:for-each select="jar">
                <file path="{../@home}/{@name}"/>
              </xsl:for-each>
            </prereq>
          </xsl:for-each>

          <logic name="{@name}">
            <xsl:variable name="srcdir" select="@srcdir"/>
            <initdir dir="{$srcdir}" basedon="{$cvsdir}/{@module}"/>
            <chdir dir="{$srcdir}"/>

            <xsl:copy-of select="delete"/>
            <xsl:copy-of select="mkdir"/>

            <classpath>

              <xsl:for-each select="work">
                <xsl:choose>
                  <xsl:when test="@parent">
                    <pathelement location="{$basedir}/{@parent}"/>
                  </xsl:when>
                  <xsl:when test="@nested">
                    <pathelement location="{$srcdir}/{@nested}"/>
                  </xsl:when>
                  <xsl:otherwise>
                    <pathelement location="{$srcdir}"/>
                  </xsl:otherwise>
                </xsl:choose>
                <xsl:text>&#10;</xsl:text>
              </xsl:for-each>

              <xsl:for-each select="depend[not(noclasspath)]|option[not(noclasspath)]">
                <xsl:for-each select="jar">
                  <pathelement location="{../@home}/{@name}">
                    <xsl:copy-of select="@type"/>
                  </pathelement>
                </xsl:for-each>
              </xsl:for-each>
            </classpath>

            <xsl:apply-templates select="ant|script"/>

            <!-- Optionally save any jars produced -->
            <xsl:if test="@redistributable and /workspace/@jardir">
              <xsl:variable name="jardir" select="/workspace/@jardir"/>
              <xsl:variable name="home" select="@home"/>
              <xsl:variable name="module" select="@module"/>
              <xsl:variable name="srcdir" select="@srcdir"/>
              <xsl:for-each select="jar">
                <copy file="{$home}/{@name}" todir="{$jardir}/{$module}"/>
              </xsl:for-each>
              <xsl:for-each select="license">
                <copy file="{$srcdir}/{@name}" todir="{$jardir}/{$module}"/>
              </xsl:for-each>
            </xsl:if>

            <chdir dir="{$basedir}"/>
          </logic>
        </content>
      </html>

      <tr>
        <td>
          <start-time/>
        </td>
        <td class="status">
          <a href="{@name}.html"><xsl:value-of select="@name"/></a>
        </td>
        <td class="status">
          <status/>
        </td>
      </tr>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="project[not(ant) and not(script)]"/>

  <xsl:template match="ant">

    <xsl:if test="@basedir">
      <chdir dir="{ancestor::project/@srcdir}/{@basedir}"/>
    </xsl:if>

    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="/workspace/sysproperty"/>
      <xsl:apply-templates select="/workspace/property"/>
      <xsl:apply-templates select="*"/>

      <xsl:if test="/workspace[not(@bootclass='no')]">
        <xsl:for-each select="../depend | ../option">
          <xsl:for-each select="jar[@type='boot']">
            <bootclass location="{../@home}/{@name}"/>
          </xsl:for-each>
        </xsl:for-each>
     </xsl:if>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
