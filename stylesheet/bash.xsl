<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:strip-space elements="*"/>
  <xsl:output method="text" omit-xml-declaration="yes"/>

  <xsl:param name="cmd-prefix"/>
  <xsl:param name="os-type"/>

  <xsl:variable name="cygwin">
    <xsl:choose>
      <xsl:when test="$os-type='cygwin'">1</xsl:when>
      <xsl:when test="$os-type='cygwin32'">1</xsl:when>
      <xsl:otherwise>0</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <!-- =================================================================== -->
  <!--             parse command line option for project name              -->
  <!-- =================================================================== -->

  <xsl:template name="select">
    <xsl:param name="usage"/>

    <xsl:text>case $1 in&#10;</xsl:text>
    <xsl:for-each select=".//project | .//module">
      <xsl:value-of select="@name"/>
      <xsl:text>) export </xsl:text>
      <xsl:value-of select="translate(@name,'-.','__')"/>
      <xsl:text>=1;;&#10;</xsl:text>
    </xsl:for-each>

    <xsl:text>all)&#10;</xsl:text>
    <xsl:text>  export all=1&#10;</xsl:text>
    <xsl:for-each select=".//project | .//module">
      <xsl:text>  export </xsl:text>
      <xsl:value-of select="translate(@name,'-.','__')"/>
      <xsl:text>=1&#10;</xsl:text>
    </xsl:for-each>

    <xsl:text>  ;;&#10;</xsl:text>
    <xsl:text>*)&#10;</xsl:text>
    <xsl:text>  test -n $1 &amp;&amp; echo Unknown project: $1&#10;</xsl:text>

    <xsl:text>  echo </xsl:text>
    <xsl:value-of select="normalize-space($usage)"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>  exit 1;;&#10;</xsl:text>
    <xsl:text>esac&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                               build                                 -->
  <!-- =================================================================== -->

  <xsl:template match="build">
    <xsl:text>#!/bin/bash&#10;</xsl:text>

    <xsl:if test="$cygwin=1">
      <xsl:text>export CP=`cygpath --path --unix "$CLASSPATH"`&#10;</xsl:text>
    </xsl:if>

    <xsl:if test="$cygwin=0">
      <xsl:text>export CP=$CLASSPATH&#10;</xsl:text>
    </xsl:if>

    <xsl:call-template name="select">
      <xsl:with-param name="usage">
        Usage: build all \| clean \| project [target...]
      </xsl:with-param>
    </xsl:call-template>

    <xsl:text>shift&#10;</xsl:text>
    <xsl:text>export TARGET=$*&#10;</xsl:text>
    <xsl:text>export STATUS=SUCCESS&#10;</xsl:text>

    <xsl:text>if test $all; then&#10;</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>fi&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="build//project">
    <xsl:choose>
      <xsl:when test="@name='clean'">
        <xsl:text>echo Restoring build directories&#10;</xsl:text>
      </xsl:when>

      <xsl:otherwise>
        <xsl:text>echo Building </xsl:text>
        <xsl:value-of select="@name"/>
        <xsl:text>&#10;</xsl:text>
      </xsl:otherwise>
    </xsl:choose>

    <xsl:if test="count(.//ant)=1">
      <xsl:text>export TARGET="</xsl:text>
      <xsl:value-of select=".//ant/@target"/>
      <xsl:text>"&#10;</xsl:text>
    </xsl:if>

    <xsl:apply-templates/>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                             cvs update                              -->
  <!-- =================================================================== -->

  <xsl:template match="update">
    <xsl:text>#!/bin/bash&#10;</xsl:text>

    <xsl:text>cd </xsl:text>
    <xsl:value-of select="translate(@cvsdir,'\','/')"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>while test $1; do&#10;</xsl:text>

    <xsl:call-template name="select">
      <xsl:with-param name="usage">
        Usage: update all \| module...
      </xsl:with-param>
    </xsl:call-template>

    <xsl:text>shift&#10;</xsl:text>
    <xsl:text>done&#10;</xsl:text>

    <xsl:text>if test $all; then&#10;</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>fi&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="update//module">
    <xsl:text>echo Updating </xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:apply-templates/>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                          cross reference                            -->
  <!-- =================================================================== -->

  <xsl:template match="xref">
    <xsl:text>#!/bin/bash&#10;</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                       publish an xml source                         -->
  <!-- =================================================================== -->

  <xsl:template match="publish">
    <xsl:text>#!/bin/bash&#10;</xsl:text>
    <xsl:text>echo - $1&#10;</xsl:text>
    <xsl:text>export OUT=\&gt;\&gt;$2&#10;</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="publish//arg">
    <xsl:text>eval "echo $1 $OUT"&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="sed">
    <xsl:text>eval "perl </xsl:text>
    <xsl:value-of select="@script"/>
    <xsl:text> ../$1 $OUT"&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                      publish all xml sources                        -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">
    <xsl:variable name="basedir" select="translate(@basedir, '\', '/')"/>
    <xsl:variable name="cvsdir"  select="translate(@cvsdir,  '\', '/')"/>
    <xsl:variable name="logdir"  select="translate(@logdir,  '\', '/')"/>

    <xsl:text>#!/bin/bash&#10;</xsl:text>

    <xsl:text>test -d </xsl:text>
    <xsl:value-of select="$basedir"/>
    <xsl:text> || mkdir </xsl:text>
    <xsl:value-of select="$basedir"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>test -d </xsl:text>
    <xsl:value-of select="$logdir"/>
    <xsl:text> || mkdir </xsl:text>
    <xsl:value-of select="$logdir"/>
    <xsl:text> &#10;</xsl:text>

    <xsl:text>test -d </xsl:text>
    <xsl:value-of select="$cvsdir"/>
    <xsl:text> || mkdir </xsl:text>
    <xsl:value-of select="$cvsdir"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>bash publish.sh $1 </xsl:text>
    <xsl:value-of select="$logdir"/>
    <xsl:text>/workspace.html&#10;</xsl:text>

    <xsl:for-each select="project">
      <xsl:sort select="@defined-in"/>
      <xsl:if test="@defined-in">
        <xsl:variable name="defined-in" select="@defined-in"/>
        <xsl:if test="not(preceding::project[@defined-in=$defined-in])">
          <xsl:text>bash publish.sh project/</xsl:text>
          <xsl:value-of select="@defined-in"/>
          <xsl:text>.xml </xsl:text>
          <xsl:value-of select="$logdir"/>
          <xsl:text>/module_</xsl:text>
          <xsl:value-of select="@defined-in"/>
          <xsl:text>.html&#10;</xsl:text>
        </xsl:if>
      </xsl:if>
    </xsl:for-each>

    <xsl:for-each select="repository">
      <xsl:sort select="defined-in"/>
      <xsl:variable name="defined-in" select="@defined-in"/>
      <xsl:if test="not(preceding::project[@defined-in=$defined-in])">
        <xsl:text>bash publish.sh repository/</xsl:text>
        <xsl:value-of select="@defined-in"/>
        <xsl:text>.xml </xsl:text>
        <xsl:value-of select="$logdir"/>
        <xsl:text>/repository_</xsl:text>
        <xsl:value-of select="@defined-in"/>
        <xsl:text>.html&#10;</xsl:text>
      </xsl:if>
    </xsl:for-each>

    <xsl:for-each select="profile">
      <xsl:sort select="defined-in"/>

      <xsl:text>bash publish.sh profile/</xsl:text>
      <xsl:value-of select="@defined-in"/>
      <xsl:text>.xml </xsl:text>
      <xsl:value-of select="$logdir"/>
      <xsl:text>/profile_</xsl:text>
      <xsl:value-of select="@defined-in"/>
      <xsl:text>.html&#10;</xsl:text>
    </xsl:for-each>

    <xsl:text>for i in ../stylesheet/*.xsl; do&#10;</xsl:text>
    <xsl:text>  bash publish.sh stylesheet/`basename $i` </xsl:text>
    <xsl:value-of select="$logdir"/>
    <xsl:text>/code_`basename $i .xsl`.html&#10;</xsl:text>
    <xsl:text>done&#10;</xsl:text>

    <xsl:text>bash xref.sh&#10;</xsl:text>

    <xsl:text>cp update.sh </xsl:text>
    <xsl:value-of select="$basedir"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>cp build.sh </xsl:text>
    <xsl:value-of select="$basedir"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>echo&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                      core logic for a project                       -->
  <!-- =================================================================== -->

  <xsl:template match="logic">
    <xsl:text>eval "echo \&lt;XMP\&gt; $OUT"&#10;</xsl:text>

    <xsl:text>fi&#10;</xsl:text>
    <xsl:text>&#10;if test $</xsl:text>
    <xsl:value-of select="translate(@name,'-.','__')"/>
    <xsl:text>; then&#10;</xsl:text>

    <xsl:apply-templates/>

    <xsl:text>fi&#10;</xsl:text>
    <xsl:text>&#10;if test $all; then&#10;</xsl:text>
    <xsl:text>eval "echo \&lt;/XMP\&gt; $OUT"&#10;</xsl:text>

  </xsl:template>

  <!-- =================================================================== -->
  <!--                         status information                          -->
  <!-- =================================================================== -->

  <xsl:template match="start-time">
    <xsl:text>eval "echo $START $OUT"&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="status">
    <xsl:text>eval "echo $STATUS $OUT"&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="date">
    <xsl:text>eval "date \"+%a %x\" $OUT"&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="date-time">
    <xsl:text>export STATUS=SUCCESS&#10;</xsl:text>
    <xsl:text>export START=`date "+%T"`&#10;</xsl:text>
    <xsl:text>eval "date $OUT"&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="td[@class='status']">
    <xsl:text>case $STATUS in &#10;</xsl:text>
    <xsl:text> SUCCESS) eval "echo \&lt;td\&gt; $OUT" ;;&#10;</xsl:text>
    <xsl:text> FAILED) eval</xsl:text>
    <xsl:text> "echo \&lt;td class="fail"\&gt; $OUT" ;;&#10;</xsl:text>
    <xsl:text> *) eval "echo \&lt;td class="warn"\&gt;$OUT" ;;&#10;</xsl:text>
    <xsl:text>esac&#10;</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>eval "echo \&lt;/td\&gt; $OUT"&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                         check for prereqs                           -->
  <!-- =================================================================== -->

  <xsl:template match="prereq">
    <xsl:variable name="project" select="@project"/>
    <xsl:for-each select="file">
      <xsl:text>if test ! -e </xsl:text>
      <xsl:value-of select="translate(@path,'\','/')"/>
      <xsl:text>; then&#10;</xsl:text>

      <xsl:text>  export STATUS="PREREQ FAILURE - </xsl:text>
      <xsl:value-of select="$project"/>
      <xsl:text>"&#10;</xsl:text>

      <xsl:text>  eval echo "\&lt;p\&gt;Missing prereq \&lt;code\&gt;</xsl:text>
      <xsl:value-of select="translate(@path,'\','/')"/>
      <xsl:text>\&lt;/code\&gt; from \&lt;a href=\\\"</xsl:text>
      <xsl:value-of select="$project"/>
      <xsl:text>.html\\\"\&gt;</xsl:text>
      <xsl:value-of select="$project"/>
      <xsl:text>\&lt;/a\&gt;\&lt;/p\&gt; $OUT"&#10;</xsl:text>

      <xsl:text>fi&#10;</xsl:text>
    </xsl:for-each>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                        create the claspath                          -->
  <!-- =================================================================== -->

  <xsl:template match="classpath">
    <xsl:text>export CLASSPATH=$CP:$JAVA_HOME/lib/tools.jar&#10;</xsl:text>
    <xsl:for-each select="pathelement">
      <xsl:if test="not(@type='boot')">
        <xsl:text>export CLASSPATH=$CLASSPATH:</xsl:text>
        <xsl:value-of select="translate(@location,'\','/')"/>
        <xsl:text>&#10;</xsl:text>
      </xsl:if>
      <xsl:if test="@type='boot'">
        <xsl:text>export CLASSPATH=</xsl:text>
        <xsl:value-of select="translate(@location,'\','/')"/>
        <xsl:text>:$CLASSPATH&#10;</xsl:text>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                      process Ant based builds                       -->
  <!-- =================================================================== -->

  <xsl:template match="ant">

    <xsl:text>if test "$STATUS" = "SUCCESS"; then \&#10;</xsl:text>

    <xsl:if test="$cygwin=1">
      <xsl:text>export CLASSPATH=</xsl:text>
      <xsl:text>`cygpath --path --windows "$CLASSPATH"`&#10;</xsl:text>
    </xsl:if>

    <xsl:text>eval </xsl:text>
    <xsl:if test="$cmd-prefix">
       <xsl:text>"</xsl:text>
       <xsl:value-of select="$cmd-prefix"/>
       <xsl:text>" </xsl:text>
    </xsl:if>
    <xsl:text>"java</xsl:text>

    <xsl:if test="bootclass">
      <xsl:text> -Xbootclasspath/p:</xsl:text>
      <xsl:for-each select="bootclass">
        <xsl:if test="position()!=1">
          <xsl:text>:</xsl:text>
        </xsl:if>
        <xsl:value-of select="translate(@location,'\','/')"/>
      </xsl:for-each>
    </xsl:if>

    <xsl:text> org.apache.tools.ant.Main</xsl:text>

    <xsl:if test="@buildfile">
      <xsl:text> -buildfile </xsl:text>
      <xsl:value-of select="translate(@buildfile,'\','/')"/>
    </xsl:if>

    <xsl:for-each select="property">
      <xsl:text> -D</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>=</xsl:text>
      <xsl:choose>
        <xsl:when test="@type = 'path' and $cygwin = 1">
          <xsl:text>'`cygpath --path --windows "</xsl:text>
          <xsl:value-of select="@value"/>
          <xsl:text>"`'</xsl:text>
        </xsl:when>
        <xsl:otherwise><xsl:value-of select="@value"/></xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>

    <xsl:choose>
      <xsl:when test="count(../ant)=1">
        <xsl:text> $TARGET</xsl:text>
      </xsl:when>
      <xsl:when test="@target">
        <xsl:text> </xsl:text>
        <xsl:value-of select="@target"/>
      </xsl:when>
    </xsl:choose>

    <xsl:text> $OUT 2&gt;&amp;1"&#10;</xsl:text>
    <xsl:text>test $? -ge 1 &amp;&amp; </xsl:text>
    <xsl:text>export STATUS="FAILED"&#10;</xsl:text>
    <xsl:text>fi&#10;</xsl:text>

  </xsl:template>

  <!-- =================================================================== -->
  <!--                          make directories                           -->
  <!-- =================================================================== -->

  <xsl:template match="mkdir">
    <xsl:text>test ! -d </xsl:text>
    <xsl:value-of select="translate(@dir,'\','/')"/>
    <xsl:text> &amp;&amp; eval "mkdir </xsl:text>
    <xsl:value-of select="translate(@dir,'\','/')"/>
    <xsl:text> $OUT 2&gt;&amp;1"&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                         change directories                          -->
  <!-- =================================================================== -->

  <xsl:template match="chdir">
    <xsl:text>eval "cd </xsl:text>
    <xsl:value-of select="translate(@dir,'\','/')"/>
    <xsl:text> $OUT 2&gt;&amp;1"&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                         remove directories                          -->
  <!-- =================================================================== -->

  <xsl:template match="delete">
    <xsl:text>eval "rm -rf </xsl:text>
    <xsl:value-of select="translate(@dir,'\','/')"/>
    <xsl:text> $OUT 2&gt;&amp;1"&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                          copy directories                           -->
  <!-- =================================================================== -->

  <xsl:template match="copy">
    <xsl:text>eval "cp -r </xsl:text>
    <xsl:value-of select="translate(@fromdir,'\','/')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="translate(@todir,'\','/')"/>
    <xsl:text> $OUT 2&gt;&amp;1"&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                      Move a file or directory                       -->
  <!-- =================================================================== -->

  <xsl:template match="move">
    <xsl:if test="@quiet">
      <xsl:text>test -d </xsl:text>
      <xsl:value-of select="translate(@file,'\','/')"/>
      <xsl:text> &amp;&amp; </xsl:text>
    </xsl:if>
    <xsl:text>eval "mv </xsl:text>
    <xsl:value-of select="translate(@file,'\','/')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="translate(@todir,'\','/')"/>
    <xsl:text> $OUT 2&gt;&amp;1"&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                         Synch a directory                           -->
  <!-- =================================================================== -->

  <xsl:template match="sync">
    <xsl:text>eval "</xsl:text>
    <xsl:value-of select="/build/@sync"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="translate(@fromdir,'\','/')"/>
    <xsl:text>/ </xsl:text>
    <xsl:value-of select="translate(@todir,'\','/')"/>
    <xsl:text> $OUT 2&gt;&amp;1"&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--       initialize a directory if it does not currently exist         -->
  <!-- =================================================================== -->

  <xsl:template match="initdir">
    <xsl:variable name="dir" select="translate(@dir,'\','/')"/>
    <xsl:text>test -d </xsl:text>
    <xsl:value-of select="$dir"/>
    <xsl:text> || cp -r </xsl:text>
    <xsl:value-of select="translate(@basedon,'\','/')"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="$dir"/>
    <xsl:text>&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                     batch file / shell scripts                      -->
  <!-- =================================================================== -->

  <xsl:template match="script">
    <xsl:text>eval "./</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>.sh $OUT" 2&gt;&amp;1&#10;</xsl:text>
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

  <xsl:template match="cvs">

    <!-- update -->

    <xsl:text>test -d </xsl:text>
    <xsl:value-of select="translate(@srcdir,'\','/')"/>
    <xsl:text> &amp;&amp; export CMD="cvs -z3 -d </xsl:text>
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
    <xsl:text>"&#10;</xsl:text>

    <!-- checkout -->

    <xsl:text>test -d </xsl:text>
    <xsl:value-of select="translate(@srcdir,'\','/')"/>

    <xsl:text> || export CMD="cvs -z3 -d </xsl:text>
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
    <xsl:text>"&#10;</xsl:text>

    <!-- execute -->

    <xsl:text>eval "echo $CMD $OUT"&#10;</xsl:text>
    <xsl:text>eval "echo $OUT"&#10;</xsl:text>

    <xsl:text>if ! eval </xsl:text>
    <xsl:if test="$cmd-prefix">
       <xsl:text>"</xsl:text>
       <xsl:value-of select="$cmd-prefix"/>
       <xsl:text>" </xsl:text>
    </xsl:if>
    <xsl:text>"$CMD $OUT 2&gt;&amp;1"; then&#10;</xsl:text>

    <xsl:text>sleep 90&#10;</xsl:text>
    <xsl:text>echo Retrying...&#10;</xsl:text>

    <xsl:text>eval </xsl:text>
    <xsl:if test="$cmd-prefix">
       <xsl:text>"</xsl:text>
       <xsl:value-of select="$cmd-prefix"/>
       <xsl:text>" </xsl:text>
    </xsl:if>
    <xsl:text>"$CMD $OUT 2&gt;&amp;1" ||\&#10;</xsl:text>
    <xsl:text>export STATUS=FAILED&#10;</xsl:text>

    <xsl:text>fi&#10;</xsl:text>

  </xsl:template>

  <!-- =================================================================== -->
  <!--          support for capturing and including static text            --> 
  <!-- =================================================================== -->

  <xsl:template match="output">
    <xsl:text>export OUT=\&gt;\&gt;</xsl:text>
    <xsl:value-of select="translate(@file,'\','/')"/>
    <xsl:text>&#10;</xsl:text>

    <xsl:text>eval "echo \&lt;!-- </xsl:text>
    <xsl:value-of select="translate(@file,'\','/')"/>
    <xsl:text> --\\$OUT"&#10;</xsl:text>

    <xsl:apply-templates/>

    <xsl:text>eval "echo \&lt;/!-- </xsl:text>
    <xsl:value-of select="translate(@file,'\','/')"/>
    <xsl:text> --\&gt; $OUT"&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="include">
    <xsl:text>eval "cat </xsl:text>
    <xsl:value-of select="translate(@file,'\','/')"/>
    <xsl:text> $OUT"&#10;</xsl:text>

    <xsl:apply-templates/>
  </xsl:template>

  <!-- =================================================================== -->
  <!--                 default catchers for html and text                  -->
  <!-- =================================================================== -->

  <xsl:template match="html">
    <xsl:if test="@log">
      <xsl:text>export OUT=\&gt;\&gt;</xsl:text>
      <xsl:value-of select="translate(@log,'\','/')"/>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>

    <xsl:text>eval "echo \&lt;html\\$OUT"&#10;</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>eval "echo \&lt;/html\&gt; $OUT"&#10;</xsl:text>

    <xsl:if test="ancestor::html/@log">
      <xsl:text>export OUT=\&gt;\&gt;</xsl:text>
      <xsl:value-of select="translate(ancestor::html/@log,'\','/')"/>
      <xsl:text>&#10;</xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="a[count(*)=0 and count(@*)=1]">
    <xsl:text>eval "echo \&lt;a href=\\\"</xsl:text>
    <xsl:value-of select="@href"/>
    <xsl:text>\\\"\&gt;</xsl:text>
    <xsl:value-of select="."/>
    <xsl:text>\&lt;/a\&gt; $OUT"&#10;</xsl:text>
  </xsl:template>

  <xsl:template match="*">
    <xsl:text>eval "echo \&lt;</xsl:text>
    <xsl:value-of select="name()"/>

    <xsl:for-each select="@*">
      <xsl:text> </xsl:text>
      <xsl:value-of select="name()"/>
      <xsl:text>=\\\"</xsl:text>
      <xsl:call-template name="escape">
         <xsl:with-param name="string">
           <xsl:value-of select="normalize-space(.)"/>
         </xsl:with-param>
       </xsl:call-template>
      <xsl:text>\\\"</xsl:text>
    </xsl:for-each>

    <xsl:choose>
      <xsl:when test="count(*|text())=0">
        <!-- note: to accomodate old browsers, a space before the slash -->
        <xsl:text> /\&gt; $OUT"&#10;</xsl:text>
      </xsl:when>
      <xsl:when test="count(*)=0">
        <!-- put entire tag on one line -->
        <xsl:text>\&gt;</xsl:text>
        <xsl:call-template name="escape">
          <xsl:with-param name="string">
            <xsl:value-of select="normalize-space(.)"/>
          </xsl:with-param>
        </xsl:call-template>
        <xsl:text>\&lt;/</xsl:text>
        <xsl:value-of select="name()"/>
        <xsl:text>\&gt; $OUT"&#10;</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>\&gt; $OUT"&#10;</xsl:text>

        <xsl:apply-templates select="*|text()"/>

        <xsl:text>eval "echo \&lt;/</xsl:text>
        <xsl:value-of select="name()"/>
        <xsl:text>\&gt; $OUT"&#10;</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="text()">
    <xsl:text>eval "echo </xsl:text>
    <xsl:call-template name="escape">
      <xsl:with-param name="string">
        <xsl:value-of select="normalize-space(.)"/>
      </xsl:with-param>
    </xsl:call-template>
    <xsl:text> $OUT"&#10;</xsl:text>
  </xsl:template>

  <!-- =================================================================== -->
  <!--               escaping strings for the command line                 -->
  <!-- =================================================================== -->

  <xsl:template name="escape">
    <xsl:param name="string"/>

    <xsl:variable name="special"><![CDATA["#&'(){]]></xsl:variable>
    <xsl:variable name="work" select="translate($string,$special,';;;;;;;')"/>

    <xsl:choose>
      <xsl:when test="contains($work,';')">

        <xsl:variable name="pre" select="substring-before($work, ';')"/>
        <xsl:variable name="char"
           select="substring($string, string-length($pre)+1,1)"/>

        <xsl:value-of select="$pre"/>

        <xsl:choose>
          <xsl:when test="$char='&amp;quot;'">
            <xsl:text>\\\</xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text>\</xsl:text>
          </xsl:otherwise>
        </xsl:choose>

        <xsl:value-of select="$char"/>

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

</xsl:stylesheet>
