<?xml version="1.0" ?>
<!--
  Copyright 2001,2004 The Apache Software Foundation

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

  <!-- =================================================================== -->
  <!-- provide support for specifying desired projects on the command line -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">

    <publish>

      <html banner-image="{@banner-image}" banner-link="{@banner-link}">
        <title>
          <xsl:text>Source: </xsl:text>
          <code><arg/></code>
        </title>

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
          <sed script="map.pl"/>
        </content>

      </html>
    </publish>

  </xsl:template>

</xsl:stylesheet>
