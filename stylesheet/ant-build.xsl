<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <!--
       This generates an ant build.xml file - to serve the same purpose as the build.sh/bat.
       It requires an existing build of ant - but it doesn't use it ( it will fork the new ant
       as soon as it is built ).

       The main challenge is the content generation. To avoid mixing too much content in the
       generated build file, we'll use some form of post-processing. 

       The scoreboard is used to keep track of the projects status. It is a simple properties file.
       Each project will have the output generated in log/PROJECT_NAME.log
       We'll use some templates ( velocity or just ant replace ? ) to generate the html for each
       file.
      
  -->
  <xsl:output method="XML" indent="yes"/>

  <xsl:template match="*|@*">
    <xsl:copy>
      <xsl:apply-templates select="*|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:variable name="basedir" select="/workspace/@basedir"/>
  <xsl:variable name="cvsdir"  select="/workspace/@cvsdir"/>
  <xsl:variable name="logdir"  select="/workspace/@logdir"/>

  <!-- ============================== Top level Ant Template ============================== -->

  <xsl:template match="workspace">
    <project name="gump-build" default="message" >
      <property name="sync" value="{@sync}" />
      <property name="scorecard" location="{$logdir}/results.txt" />
      <xsl:text>
        
      </xsl:text>
      <property name="basedir" location="{$basedir}" />
      <xsl:text>
        
      </xsl:text>
      <xsl:comment>========== Generic targets ==========</xsl:comment>
      <xsl:text>
        
      </xsl:text>
      <target name="init" >
        <mkdir dir="{$logdir}" />
        <delete dir="build" />
        <delete dir="dist" />
      </target>
      <xsl:text>
        
      </xsl:text>
      <target name="message" >
        <echo>TODO: help</echo>
      </target>
      <xsl:text>
        
      </xsl:text>
      <target name="all" >
        <xsl:foreach select="project">
          <antcall target="{project}" />
        </xsl:foreach>
      </target>
      <xsl:text>
        
      </xsl:text>
      <target name="initdir" >
        <copy fromdir="${{module}}" todir="${{dir}}"/>
        <!--<xsl:if test="not(/workspace/@sync)">
             <delete dir="{@srcdir}"/>
             <copy fromdir="{$cvsdir}/{@name}" todir="{@srcdir}"/>
           </xsl:if>
           <xsl:if test="/workspace/@sync">
             <sync fromdir="{$cvsdir}/{@name}" todir="{@srcdir}"/>
           </xsl:if>
           -->
         </target>
         <xsl:text>
           
         </xsl:text>
         <target name="depend-error" >
           
         </target>
         <xsl:text>
           
         </xsl:text>
         <target name="check-depend" >
           
      </target>
      <xsl:text>
        
      </xsl:text>
      <xsl:comment>========== restore up old build directories ==========</xsl:comment>
      <xsl:text>
        
      </xsl:text>
      <target name="clean">
      </target>
      <xsl:text>
        
      </xsl:text>
      <xsl:comment>========== Generated build  ==========</xsl:comment> 
      <xsl:comment>For each project we generate 2 targets: PROJECT_NAME and all_PROJECT_NAME</xsl:comment> 
      <xsl:comment>The "all_PROJECT_NAME" target will first build all dependencies</xsl:comment> 
      <xsl:text>
        
      </xsl:text>
      <xsl:apply-templates select="project"/>
      <xsl:text>
        
      </xsl:text>
    </project>
  </xsl:template>
  
  <!-- ============================== Project Template ============================== -->
  
  <xsl:template match="project">
    <xsl:variable name="project-name" select="@name" />
    
    <target name="all-{@name}" >
      <xsl:for-each select="depend">
        <antcall target="project"/>
      </xsl:for-each>
      <antcall target="{@name}" />
    </target>
    <xsl:text>
      
    </xsl:text>
    <target name="{@name}-env" >
      <xsl:comment>Set the paths for this project</xsl:comment>
      <fileset name="{@name}.jars" base="${{{@name}.home}}">
        <xsl:for-each select="jar">
          <include name="{@name}"/>
        </xsl:for-each>
      </fileset>
    </target>
    <xsl:text>

    </xsl:text>
    <target name="{@name}-check-depends" >
      <!-- Check dependencies -->
      <condition property="{$project-name}-depends-exist">
        <and>
          <xsl:for-each select="depend">
            <xsl:for-each select="jar">
              <!-- Make a standalone task to do this automatically -->
              <available file="{../@home}/{@name}" />
            </xsl:for-each>
          </xsl:for-each>
        </and>
      </condition>
    </target>
    <xsl:text>
      
    </xsl:text>
    <target name="{@name}" depends="{@name}-check-depends" >

      <xsl:variable name="srcdir" select="@srcdir"/>
          
      <antcall target="initdir">
        <param name="dir" value="{$srcdir}" />
        <param name="module" value="{$cvsdir}/{@module}"/>      
      </antcall>

      <xsl:copy-of select="mkdir"/>
      
      <!-- Set classpath -->
      <path id="{$project-name}-boot-classpath">
        <xsl:for-each select="depend/jar[ @type='boot' ] | option/jar[@type='boot']">
          <pathelement location="{../@home}/{@name}" />
        </xsl:for-each>
      </path>

      <path id="{$project-name}-classpath">
        <xsl:for-each select="depend/jar[ not( @type ) ] | depend/jar[ not( @type='boot' )]">
            <pathelement location="{../@home}/{@name}">
              <xsl:copy-of select="@type"/>
            </pathelement>
        </xsl:for-each>
      </path>

      <path id="{$project-name}-optional-classpath">
        <xsl:for-each select="option/jar[not(@type)] | option/jar[ not( @type = 'boot') ]">
          <pathelement location="{../@home}/{@name}"/>
        </xsl:for-each>
      </path>

      <path id="{$project-name}-work">
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
        </xsl:for-each>
      </path>
    
      <!-- building -->
      <xsl:choose>
        <xsl:when test="ant">
          <!-- Ant-based build. TODO: use java fork-->
          <java fork="true" classname="org.apache.tools.ant.Main" >
            <xsl:if test="ant/@basedir">
              <xsl:attribute name="basedir"><xsl:value-of select="@srcdir"/>/<xsl:value-of select="ant/@basedir"/></xsl:attribute>
            </xsl:if>
            <classpath refid="{$project-name}-boot-classpath" />
            <classpath refid="{$project-name}-optional-classpath" />
            <classpath refid="{$project-name}-classpath" />

            <xsl:if test="ant/@target" >
              <arg value="{ant/@target}"/>  
            </xsl:if>

            <xsl:for-each select="ant/property">
              <arg value="-D{@name}={@value}"/>
            </xsl:for-each>
            <xsl:for-each select="/workspace/property">
              <arg value="-D{@name}={@value}"/>
            </xsl:for-each>
          </java>
        </xsl:when>
        <xsl:when test="script">
          <xsl:choose>
            <xsl:when test="script/@name" >
              <exec executable="{script/@name}" dir="{@srcdir}" />
            </xsl:when>
            <xsl:otherwise>
              <exec executable="build.sh" dir="{@srcdir}" />
            </xsl:otherwise>
          </xsl:choose>
        </xsl:when>
        <xsl:otherwise>
          <!-- Add check for existence, message -->
          <echo message="This is a binary package, URL: {url/@href}" />
        </xsl:otherwise>
      </xsl:choose>

      
      <!-- Optionally save any jars produced -->
      <xsl:if test="/workspace/@jardir">
        <xsl:variable name="jardir" select="/workspace/@jardir"/>
        <xsl:variable name="home" select="@home"/>
        <xsl:variable name="module" select="@module"/>
        <xsl:for-each select="jar">
          <copy file="{$home}/{@name}" todir="{$jardir}/{$module}"/>
        </xsl:for-each>
      </xsl:if>
      
      <chdir dir="{$basedir}"/>
    </target>
  </xsl:template>

</xsl:stylesheet>
