<?xml version="1.0" ?>
<!--
  Copyright 2003-2004 The Apache Software Foundation

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
  <xsl:strip-space elements="*"/>
  <xsl:output method="text" omit-xml-declaration="yes"/>

  <!-- =================================================================== -->
  <!--                               build                                 -->
  <!-- =================================================================== -->

  <xsl:template match="scorecard">
  </xsl:template>

  <xsl:template match="build">
    <xsl:text>@echo off&#10;</xsl:text>
    <xsl:text>@if "%GUMP_ECHO%" == "on" echo %GUMP_ECHO%&#10;</xsl:text>
    <xsl:text>SETLOCAL&#10;</xsl:text>
    <xsl:text>SET CP=%CLASSPATH%&#10;</xsl:text>
    <xsl:text>if "%1"=="all" goto header&#10;</xsl:text>
    <xsl:text>SET TARGET=%2 %3 %4 %5 %6 %7 %8 %9&#10;</xsl:text>

    <xsl:for-each select=".//project">
      <xsl:text>if "%1"=="</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>" goto </xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>&#10;</xsl:text>
    </xsl:for-each>

    <xsl:text>if not "%1"=="" echo Unknown project: %1&#10;</xsl:text>
    <xsl:text>echo Usage: build all ^| clean ^| </xsl:text>
    <xsl:text>project [target...]&#10;</xsl:text>
    <xsl:text>goto eoj&#10;</xsl:text>
    <xsl:text>&#10;:header&#10;</xsl:text>

    <xsl:apply-templates/>

    <xsl:text>&#10;:eoj&#10;</xsl:text>
    <xsl:text>ENDLOCAL&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="build//project">
    <xsl:choose>
      <xsl:when test="@name='clean'">
        <xsl:text>&#10;echo Restoring build directories&#10;</xsl:text>
      </xsl:when>

      <xsl:otherwise>
        <xsl:text>&#10;echo Building </xsl:text>
        <xsl:value-of select="@name"/>
        <xsl:text>&#10;</xsl:text>
      </xsl:otherwise>
    </xsl:choose>

    <xsl:if test="count(.//ant)=1">
      <xsl:text>SET TARGET=</xsl:text>
      <xsl:value-of select=".//ant/@target"/>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>

    <xsl:apply-templates/>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                             cvs update                              -->
  <!-- =================================================================== -->

  <xsl:template match="update">
    <xsl:text>@echo off&#10;</xsl:text>
    <xsl:text>@if "%GUMP_ECHO%" == "on" echo %GUMP_ECHO%&#10;</xsl:text>
    <xsl:text>SETLOCAL&#10;</xsl:text>

    <xsl:text>chdir /d </xsl:text>
    <xsl:value-of select="translate(@cvsdir,'/','\')"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>if "%1"=="all" goto header&#10;</xsl:text>
    <xsl:text>:top&#10;</xsl:text>

    <xsl:for-each select=".//module">
      <xsl:text>if "%1"=="</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>" goto </xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>&#10;</xsl:text>
    </xsl:for-each>

    <xsl:text>if not "%1"=="" echo Unknown module: %1&#10;</xsl:text>
    <xsl:text>echo Usage: update all ^| module...&#10;</xsl:text>
    <xsl:text>goto eoj&#10;</xsl:text>
    <xsl:text>&#10;:header&#10;</xsl:text>

    <xsl:apply-templates/>

    <xsl:text>&#10;:eoj&#10;</xsl:text>
    <xsl:text>shift&#10;</xsl:text>
    <xsl:text>if not "%1"=="" goto top&#10;</xsl:text>

    <xsl:text>chdir /d </xsl:text>
    <xsl:value-of select="translate(@basedir,'/','\')"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>ENDLOCAL&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="update//module">
    <xsl:text>&#10;echo Updating </xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:apply-templates/>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                          cross reference                            -->
  <!-- =================================================================== -->

  <xsl:template match="xref">
    <xsl:text>@echo off&#10;</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                       publish an xml source                         -->
  <!-- =================================================================== -->

  <xsl:template match="publish">
    <xsl:text>@echo off&#10;</xsl:text>
    <xsl:text>@if "%GUMP_ECHO%" == "on" echo %GUMP_ECHO%&#10;</xsl:text>
    <xsl:text>echo - %1&#10;</xsl:text>
    <xsl:text>SET OUT=^&gt;^&gt;%2&#10;</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="publish//arg">
    <xsl:text>echo %1 %OUT%&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="sed">
    <xsl:text>perl </xsl:text>
    <xsl:value-of select="@script"/>
    <xsl:text> %1 %OUT%&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                      publish all xml sources                        -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">
    <xsl:variable name="basedir" select="translate(@basedir, '/', '\')"/>
    <xsl:variable name="cvsdir"  select="translate(@cvsdir,  '/', '\')"/>
    <xsl:variable name="logdir"  select="translate(@logdir,  '/', '\')"/>

    <xsl:text>@echo off&#10;</xsl:text>
    <xsl:text>@if "%GUMP_ECHO%" == "on" echo %GUMP_ECHO%&#10;</xsl:text>

    <xsl:text>if not exist </xsl:text>
    <xsl:value-of select="$basedir"/>
    <xsl:text> mkdir </xsl:text>
    <xsl:value-of select="$basedir"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>if not exist </xsl:text>
    <xsl:value-of select="$logdir"/>
    <xsl:text>  mkdir </xsl:text>
    <xsl:value-of select="$logdir"/>
    <xsl:text> &#10;</xsl:text>

    <xsl:text>if not exist </xsl:text>
    <xsl:value-of select="$cvsdir"/>
    <xsl:text>  mkdir </xsl:text>
    <xsl:value-of select="$cvsdir"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>call publish.bat %1 </xsl:text>
    <xsl:value-of select="$logdir"/>
    <xsl:text>\workspace.html&#10;</xsl:text>

    <xsl:for-each select="project">
      <xsl:sort select="@defined-in"/>
      <xsl:if test="@defined-in">
        <xsl:variable name="defined-in" select="@defined-in"/>
        <xsl:if test="not(preceding::project[@defined-in=$defined-in])">
          <xsl:text>call publish </xsl:text>
          <xsl:if test="not(@extern-prefix)">
            <xsl:text>..\project\</xsl:text>
          </xsl:if>
          <xsl:value-of select="@extern-prefix"/>
          <xsl:value-of select="@defined-in"/>
          <xsl:text>.xml </xsl:text>
          <xsl:value-of select="$logdir"/>
          <xsl:text>\module_</xsl:text>
          <xsl:value-of select="@defined-in"/>
          <xsl:text>.html&#10;</xsl:text>
        </xsl:if>
      </xsl:if>
    </xsl:for-each>

    <xsl:for-each select="repository">
      <xsl:sort select="defined-in"/>
      <xsl:variable name="defined-in" select="@defined-in"/>
      <xsl:if test="not(preceding::project[@defined-in=$defined-in])">
        <xsl:text>call publish </xsl:text>
        <xsl:if test="not(@extern-prefix)">
          <xsl:text>..\repository\</xsl:text>
        </xsl:if>
        <xsl:value-of select="@extern-prefix"/>
        <xsl:value-of select="@defined-in"/>
        <xsl:text>.xml </xsl:text>
        <xsl:value-of select="$logdir"/>
        <xsl:text>\repository_</xsl:text>
        <xsl:value-of select="@defined-in"/>
        <xsl:text>.html&#10;</xsl:text>
      </xsl:if>
    </xsl:for-each>

    <xsl:for-each select="profile">
      <xsl:sort select="defined-in"/>

      <xsl:text>call publish </xsl:text>
      <xsl:if test="not(@extern-prefix)">
        <xsl:text>..\profile\</xsl:text>
      </xsl:if>
      <xsl:value-of select="@extern-prefix"/>
      <xsl:value-of select="@defined-in"/>
      <xsl:text>.xml </xsl:text>
      <xsl:value-of select="$logdir"/>
      <xsl:text>\profile_</xsl:text>
      <xsl:value-of select="@defined-in"/>
      <xsl:text>.html&#10;</xsl:text>
    </xsl:for-each>

    <xsl:for-each select="server">
      <xsl:sort select="defined-in"/>
      <xsl:variable name="defined-in" select="@defined-in"/>
      <xsl:if test="not(preceding::server[@defined-in=$defined-in])">
        <xsl:text>call publish </xsl:text>
        <xsl:if test="not(@extern-prefix)">
        <xsl:text>..\server\</xsl:text>
        </xsl:if>
        <xsl:value-of select="@extern-prefix"/>
        <xsl:value-of select="@defined-in"/>
        <xsl:text>.xml </xsl:text>
        <xsl:value-of select="$logdir"/>
        <xsl:text>\server_</xsl:text>
        <xsl:value-of select="@defined-in"/>
        <xsl:text>.html&#10;</xsl:text>
      </xsl:if>
    </xsl:for-each>

    <xsl:text>for %%i in (..\stylesheet\*.xsl) do </xsl:text>
    <xsl:text>call publish </xsl:text>
    <xsl:if test="not(@extern-prefix)">
      <xsl:text>..\stylesheet\</xsl:text>
    </xsl:if>
    <xsl:value-of select="@extern-prefix"/>
    <xsl:text>%%~nxi </xsl:text>
    <xsl:value-of select="$logdir"/>
    <xsl:text>\code_%%~ni.html&#10;</xsl:text>

    <xsl:text>call xref.bat&#10;</xsl:text>

    <xsl:text>copy update.bat </xsl:text>
    <xsl:value-of select="$basedir"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>copy build.bat </xsl:text>
    <xsl:value-of select="$basedir"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>echo.&#10;</xsl:text>
    <xsl:text>goto :eof&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                      core logic for a project                       -->
  <!-- =================================================================== -->

  <xsl:template match="logic">
    <xsl:text>echo ^&lt;XMP^&gt; %OUT%&#10;</xsl:text>

    <xsl:text>:</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:apply-templates/>

    <xsl:text>if not "%1"=="all" goto eoj&#10;</xsl:text>
    <xsl:text>echo ^&lt;/XMP^&gt; %OUT%&#10;</xsl:text>

    <xsl:text>:end_</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                         status information                          -->
  <!-- =================================================================== -->

  <xsl:template match="start-time">
    <xsl:text>echo %START:~0,8% %OUT%&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="status">
    <xsl:text>echo %STATUS% %OUT%&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="date">
    <xsl:text>date /t %OUT%&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="date-time">
    <xsl:text>SET START=%TIME%&#10;</xsl:text>
    <xsl:text>date /t %OUT%&#10;</xsl:text>
    <xsl:text>echo at %START:~0,8% %OUT%&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="td[@class='status']">
    <xsl:text>SET STYLE= class="warn"&#10;</xsl:text>
    <xsl:text>IF "%STATUS%"=="SUCCESS" SET STYLE=&#10;</xsl:text>
    <xsl:text>IF "%STATUS%"=="FAILED" </xsl:text>
    <xsl:text>SET STYLE= class="fail"&#10;</xsl:text>
    <xsl:text>echo ^&lt;td%STYLE%^&gt; %OUT%&#10;</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>echo ^&lt;/td^&gt; %OUT%&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                         check for prereqs                           -->
  <!-- =================================================================== -->

  <xsl:template match="prereq">
    <xsl:variable name="project" select="ancestor::project/@name"/>
    <xsl:text>SET STATUS=PREQ FAILURE - </xsl:text>
    <xsl:value-of select="@project"/>
    <xsl:text>&#10;</xsl:text>
    <xsl:for-each select="file">
      <xsl:text>IF NOT EXIST </xsl:text>
      <xsl:value-of select="translate(@path,'/','\')"/>
      <xsl:text> goto end_</xsl:text>
      <xsl:value-of select="$project"/>
      <xsl:text>&#10;</xsl:text>
    </xsl:for-each>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                        create the classpath                         -->
  <!-- =================================================================== -->

  <xsl:template match="classpath">
    <xsl:text>SET CLASSPATH=%CP%;%JAVA_HOME%\lib\tools.jar&#10;</xsl:text>
    <xsl:for-each select="pathelement">
      <xsl:text>SET CLASSPATH=%CLASSPATH%;</xsl:text>
      <xsl:value-of select="translate(@location,'/','\')"/>
      <xsl:text>&#10;</xsl:text>
    </xsl:for-each>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                      process Ant based builds                       -->
  <!-- =================================================================== -->

  <xsl:template match="ant">

    <xsl:text>SET STATUS=SUCCESS&#10;</xsl:text>
    <xsl:text>java</xsl:text>

    <xsl:if test="bootclass">
      <xsl:text> -Xbootclasspath/p:</xsl:text>
      <xsl:for-each select="bootclass">
        <xsl:if test="position()!=1">
          <xsl:text>;</xsl:text>
        </xsl:if>
        <xsl:value-of select="translate(@location,'\','/')"/>
      </xsl:for-each>
    </xsl:if>

    <xsl:for-each select="jvmarg">
      <xsl:text> </xsl:text>
      <xsl:value-of select="@value"/>
    </xsl:for-each>

    <xsl:text> org.apache.tools.ant.Main</xsl:text>

    <xsl:if test="@buildfile">
      <xsl:text> -buildfile </xsl:text>
      <xsl:value-of select="translate(@buildfile,'/','\')"/>
    </xsl:if>

    <xsl:for-each select="property">
      <xsl:text> -D</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>=</xsl:text>
      <xsl:choose>
        <xsl:when test="@type='path'">
          <xsl:value-of select="translate(@value,'/','\')"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="@value"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>

    <xsl:choose>
      <xsl:when test="count(../ant)=1">
        <xsl:text> %TARGET%</xsl:text>
      </xsl:when>
      <xsl:when test="@target">
        <xsl:text> </xsl:text>
        <xsl:value-of select="@target"/>
      </xsl:when>
    </xsl:choose>

    <xsl:text> &lt;nul %OUT% 2&gt;&amp;1&#10;</xsl:text>
    <xsl:text>if errorlevel 1 SET STATUS=FAILED&#10;</xsl:text>

  </xsl:template>

  <!-- =================================================================== -->
  <!--                          make directories                           -->
  <!-- =================================================================== -->

  <xsl:template match="mkdir">
    <xsl:text>if not exist </xsl:text>
    <xsl:value-of select="translate(@dir,'/','\')"/>
    <xsl:text> mkdir </xsl:text>
    <xsl:value-of select="translate(@dir,'/','\')"/>
    <xsl:text> %OUT% 2&gt;&amp;1&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                         change directories                          -->
  <!-- =================================================================== -->

  <xsl:template match="chdir">
    <xsl:text>chdir /d </xsl:text>
    <xsl:value-of select="translate(@dir,'/','\')"/>
    <xsl:text> %OUT% 2&gt;&amp;1&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                         remove directories                          -->
  <!-- =================================================================== -->

  <xsl:template match="delete">
    <xsl:text>if exist </xsl:text>
    <xsl:value-of select="translate(@dir,'/','\')"/>
    <xsl:text> rmdir /s /q </xsl:text>
    <xsl:value-of select="translate(@dir,'/','\')"/>
    <xsl:text> %OUT% 2&gt;&amp;1&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                          copy directories                           -->
  <!-- =================================================================== -->

  <xsl:template match="copy">
    <xsl:if test="@fromdir">
      <xsl:text>xcopy /E /I /Q /R /K </xsl:text>
      <xsl:value-of select="translate(@fromdir,'/','\')"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="translate(@todir,'/','\')"/>
      <xsl:text> %OUT% 2&gt;&amp;1&#10;</xsl:text>
    </xsl:if>

    <xsl:if test="@file">
      <xsl:text>if exist </xsl:text>
      <xsl:value-of select="translate(@file,'/','\')"/>
      <xsl:text> if not exist </xsl:text>
      <xsl:value-of select="translate(@todir,'/','\')"/>
      <xsl:text> mkdir </xsl:text>
      <xsl:value-of select="translate(@todir,'/','\')"/>
      <xsl:text> %OUT% 2&gt;&amp;1&#10;</xsl:text>

      <xsl:text>if exist </xsl:text>
      <xsl:value-of select="translate(@file,'/','\')"/>
      <xsl:text> copy /Y </xsl:text>
      <xsl:value-of select="translate(@file,'/','\')"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="translate(@todir,'/','\')"/>
      <xsl:text> %OUT% 2&gt;&amp;1&#10;</xsl:text>
    </xsl:if>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                      Move a file or directory                       -->
  <!-- =================================================================== -->

  <xsl:template match="move">
    <xsl:if test="@quiet">
      <xsl:text>if exist </xsl:text>
      <xsl:value-of select="translate(@file,'/','\')"/>
      <xsl:text> </xsl:text>
    </xsl:if>
    <xsl:text>move </xsl:text>
    <xsl:value-of select="translate(@file,'/','\')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="translate(@todir,'/','\')"/>
    <xsl:text>&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                         Synch a directory                           -->
  <!-- =================================================================== -->

  <xsl:template match="sync">
    <xsl:value-of select="/build/@sync"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="translate(@fromdir,'/','\')"/>
    <xsl:text>\ </xsl:text>
    <xsl:value-of select="translate(@todir,'/','\')"/>
    <xsl:text> $OUT 2&gt;&amp;1"&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--       initialize a directory if it does not currently exist         -->
  <!-- =================================================================== -->

  <xsl:template match="initdir">
    <xsl:text>if not exist </xsl:text>
    <xsl:value-of select="translate(@dir,'/','\')"/>
    <xsl:text> xcopy /E /I /Q /R /K </xsl:text>
    <xsl:value-of select="translate(@basedon,'/','\')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="translate(@dir,'/','\')"/>
    <xsl:text>&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                     batch file / shell scripts                      -->
  <!-- =================================================================== -->

  <xsl:template match="script">
    <xsl:text>SET STATUS=SUCCESS&#10;</xsl:text>
    <xsl:text>call .\</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.bat %OUT% 2&gt;&amp;1&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                            java compile                             -->
  <!-- =================================================================== -->

  <xsl:template match="javac">
    <xsl:text>javac </xsl:text>

    <xsl:if test="@sourcedir">
      <xsl:text>-sourcepath </xsl:text>
      <xsl:value-of select="javac/@sourcedir"/>
      <xsl:text> </xsl:text>
    </xsl:if>

    <xsl:if test="javac/@destdir">
      <xsl:text>-d </xsl:text>
      <xsl:value-of select="@destdir"/>
      <xsl:text> </xsl:text>
    </xsl:if>

    <xsl:if test="javac/@sourcedir">
      <xsl:text>-sourcepath </xsl:text>
      <xsl:value-of select="@sourcedir"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="@sourcedir"/>
      <xsl:text>/</xsl:text>
    </xsl:if>

    <xsl:value-of select="javac/@file"/>
    <xsl:text>&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                             cvs update                              -->
  <!-- =================================================================== -->

  <xsl:template match="cvs[@srcdir]">
    <xsl:text>SET STATUS=SUCCESS&#10;</xsl:text>

    <!-- update -->

    <xsl:text>if exist </xsl:text>
    <xsl:value-of select="translate(@srcdir,'/','\')"/>
    <xsl:text> SET CMD=cvs </xsl:text>
    <xsl:value-of select="@compress"/>
    <xsl:text> -d </xsl:text>
    <xsl:value-of select="@cvsroot"/>

    <xsl:text> update -P -d</xsl:text>

    <xsl:if test="@tag">
      <xsl:text> -r </xsl:text>
      <xsl:value-of select="@tag"/>
    </xsl:if>
    <xsl:if test="not(@tag)">
      <xsl:text> -A</xsl:text>
    </xsl:if>

    <xsl:text> </xsl:text>
    <xsl:value-of select="@srcdir"/>
    <xsl:text>&#10;</xsl:text>

    <!-- checkout -->

    <xsl:text>if not exist </xsl:text>
    <xsl:value-of select="translate(@srcdir,'/','\')"/>

    <xsl:text> SET CMD=cvs </xsl:text>
    <xsl:value-of select="@compress"/>
    <xsl:text> -d </xsl:text>
    <xsl:value-of select="@cvsroot"/>

    <xsl:text> checkout -P</xsl:text>

    <xsl:if test="@tag">
      <xsl:text> -r </xsl:text>
      <xsl:value-of select="@tag"/>
    </xsl:if>

    <xsl:if test="@module!=@srcdir">
      <xsl:text> -d </xsl:text>
      <xsl:value-of select="@srcdir"/>
    </xsl:if>

    <xsl:text> </xsl:text>
    <xsl:value-of select="@module"/>
    <xsl:text>&#10;</xsl:text>

    <!-- execute -->

    <xsl:text>@echo %CMD% %OUT%&#10;</xsl:text>
    <xsl:text>@echo. %OUT%&#10;</xsl:text>
    <xsl:text>%CMD% %OUT% 2&gt;&amp;1&#10;</xsl:text>
    <xsl:text>if errorlevel 1 SET STATUS=FAILED&#10;</xsl:text>
    <xsl:text>if not "%1"=="all" goto eoj&#10;</xsl:text>

  </xsl:template>

  <!-- =================================================================== -->
  <!--                             svn update                              -->
  <!-- =================================================================== -->

  <xsl:template match="svn">
    <xsl:text>SET STATUS=SUCCESS&#10;</xsl:text>

    <!-- update -->

    <xsl:text>if exist </xsl:text>
    <xsl:value-of select="translate(@srcdir,'/','\')"/>
    <xsl:text> SET CMD=svn update </xsl:text>
    <xsl:value-of select="@srcdir"/>
    <xsl:text>&#10;</xsl:text>

    <!-- checkout -->

    <xsl:text>if not exist </xsl:text>
    <xsl:value-of select="translate(@srcdir,'/','\')"/>

    <xsl:text> SET CMD=svn checkout </xsl:text>
    <xsl:value-of select="@url"/>
    <xsl:text> -d </xsl:text>
    <xsl:value-of select="@srcdir"/>
    <xsl:text>&#10;</xsl:text>

    <!-- execute -->

    <xsl:text>@echo %CMD% %OUT%&#10;</xsl:text>
    <xsl:text>@echo. %OUT%&#10;</xsl:text>
    <xsl:text>%CMD% %OUT% 2&gt;&amp;1&#10;</xsl:text>
    <xsl:text>if errorlevel 1 SET STATUS=FAILED&#10;</xsl:text>
    <xsl:text>if not "%1"=="all" goto eoj&#10;</xsl:text>

  </xsl:template>

  <!-- =================================================================== -->
  <!--          support for capturing and including static text            --> 
  <!-- =================================================================== -->

  <xsl:template match="output">
    <xsl:text>SET OUT=^&gt;^&gt;</xsl:text>
    <xsl:value-of select="translate(@file,'/','\')"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>echo ^&lt;!-- </xsl:text>
    <xsl:value-of select="translate(@file,'/','\')"/>
    <xsl:text> --^%OUT%&#10;</xsl:text>

    <xsl:apply-templates/>

    <xsl:text>echo ^&lt;/!-- </xsl:text>
    <xsl:value-of select="translate(@file,'/','\')"/>
    <xsl:text> --^&gt; %OUT%&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="include">
    <xsl:text>type </xsl:text>
    <xsl:value-of select="translate(@file,'/','\')"/>
    <xsl:text> %OUT%&#10;</xsl:text>

    <xsl:apply-templates/>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                 default catchers for html and text                  -->
  <!-- =================================================================== -->

  <xsl:template match="html">
    <xsl:if test="@log">
      <xsl:text>SET OUT=^&gt;^&gt;</xsl:text>
      <xsl:value-of select="translate(@log,'/','\')"/>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>

    <xsl:text>echo ^&lt;html^%OUT%&#10;</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>echo ^&lt;/html^&gt; %OUT%&#10;</xsl:text>

    <xsl:if test="ancestor::html/@log">
      <xsl:text>SET OUT=^&gt;^&gt;</xsl:text>
      <xsl:value-of select="translate(ancestor::html/@log,'/','\')"/>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="a[count(*)=0 and count(@*)=1]">
    <xsl:text>echo ^&lt;a href="</xsl:text>
    <xsl:value-of select="@href"/>
    <xsl:text>"^&gt;</xsl:text>
    <xsl:value-of select="."/>
    <xsl:text>^&lt;/a^&gt; %OUT%&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="*">
    <xsl:text>echo ^&lt;</xsl:text>
    <xsl:value-of select="name()"/>

    <xsl:for-each select="@*">
      <xsl:text> </xsl:text>
      <xsl:value-of select="name()"/>
      <xsl:text>="</xsl:text>
      <xsl:call-template name="escape">
         <xsl:with-param name="string">
           <xsl:value-of select="normalize-space(.)"/>
         </xsl:with-param>
       </xsl:call-template>
      <xsl:text>"</xsl:text>
    </xsl:for-each>

    <xsl:choose>
      <xsl:when test="count(*|text())=0">
        <!-- note: to accomodate old browsers, a space before the slash -->
        <xsl:text> /^&gt; %OUT%&#10;</xsl:text>
      </xsl:when>
      <xsl:when test="count(*)=0">
        <!-- put entire tag on one line -->
        <xsl:text>^&gt;</xsl:text>
        <xsl:call-template name="escape">
          <xsl:with-param name="string">
            <xsl:value-of select="normalize-space(.)"/>
          </xsl:with-param>
        </xsl:call-template>
        <xsl:text>^&lt;/</xsl:text>
        <xsl:value-of select="name()"/>
        <xsl:text>^&gt; %OUT%&#10;</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>^&gt; %OUT%&#10;</xsl:text>

        <xsl:apply-templates select="*|text()"/>

        <xsl:text>echo ^&lt;/</xsl:text>
        <xsl:value-of select="name()"/>
        <xsl:text>^&gt; %OUT%&#10;</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="text()">
    <xsl:text>echo </xsl:text>
    <xsl:value-of select="normalize-space(.)"/>
    <xsl:text> %OUT%&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--               escaping strings for the command line                 -->
  <!-- =================================================================== -->

  <xsl:template name="escape">
    <xsl:param name="string"/>

    <xsl:variable name="special"><![CDATA[%&]]></xsl:variable>
    <xsl:variable name="work" select="translate($string,$special,'%%')"/>

    <xsl:choose>
      <xsl:when test="contains($work,'%')">

        <xsl:variable name="pre" select="substring-before($work, '%')"/>
        <xsl:variable name="char"
           select="substring($string, string-length($pre)+1,1)"/>

        <xsl:value-of select="$pre"/>

        <xsl:choose>
          <xsl:when test="$char='%'">
            <xsl:text>%%</xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text>^&amp;</xsl:text>
          </xsl:otherwise>
        </xsl:choose>

        <xsl:call-template name="escape">
           <xsl:with-param name="string">
             <xsl:value-of select="substring-after($string, $char)"/>
           </xsl:with-param>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$string"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- =================================================================== -->
  <!--          Generate the move script for the cached files              -->
  <!-- =================================================================== -->

  <xsl:template match="movefiles">
    <xsl:text>@echo off&#10;</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>
