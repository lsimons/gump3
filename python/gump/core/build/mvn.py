#!/usr/bin/python


# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__revision__  = "$Rev: 36667 $"
__date__      = "$Date: 2004-08-20 08:55:45 -0600 (Fri, 20 Aug 2004) $"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"


"""

"""

import os.path
import sys

from gump import log
from gump.core.run.gumprun import *
from gump.core.config import dir, default, basicConfig

from gump.util import dump, display, getIndent, logResourceUtilization, \
                            invokeGarbageCollection
from gump.util.note import Annotatable
from gump.util.work import *

from gump.util.tools import *

from gump.core.model.workspace import *
from gump.core.model.module import Module
from gump.core.model.project import Project
from gump.core.model.depend import  ProjectDependency
from gump.core.model.stats import *
from gump.core.model.state import *


###############################################################################
# Classes
###############################################################################

class Maven2Builder(gump.core.run.gumprun.RunSpecific):
    
    def __init__(self,run):
        gump.core.run.gumprun.RunSpecific.__init__(self,run)

    def buildProject(self,project,languageHelper,stats):
        """
        Build a Maven2 project
        """
        
        workspace=self.run.getWorkspace()
                
        log.debug('Run Maven2 on Project: #[' + `project.getPosition()` + '] ' + project.getName())
        
        self.performPreBuild(project, languageHelper, stats)
          
        if project.okToPerformWork():

            #
            # Get the appropriate build command...
            #
            cmd=self.getMavenCommand(project,languageHelper)

            if cmd:
                # Execute the command ....
                cmdResult=execute(cmd,workspace.tmpdir)
    
                # Update Context    
                work=CommandWorkItem(WORK_TYPE_BUILD,cmd,cmdResult)
                project.performedWork(work)
                project.setBuilt(True)
                    
                # Update Context w/ Results  
                if not cmdResult.state==CMD_STATE_SUCCESS:
                    reason=REASON_BUILD_FAILED
                    if cmdResult.state==CMD_STATE_TIMED_OUT:
                        reason=REASON_BUILD_TIMEDOUT
                    project.changeState(STATE_FAILED,reason)                        
                else:                         
                    # For now, things are going good...
                    project.changeState(STATE_SUCCESS)
                    
        if project.wasBuilt():
            pomFile=self.locateMavenProjectFile(project) 
            if os.path.exists(pomFile):                               
                project.addDebug('Maven POM in: ' + pomFile) 
                catFileToFileHolder(project, pomFile, FILE_TYPE_CONFIG) 
                    
            projpFile=self.locateMavenProjectPropertiesFile(project) 
            if os.path.exists(projpFile):                                                
                project.addDebug('Maven project properties in: ' + projpFile)                
                catFileToFileHolder(project, projpFile, FILE_TYPE_CONFIG)                           
  
    #
    # Build an Maven command for this project
    #        
    def getMavenCommand(self,project,languageHelper):
        maven=project.mvn
    
        # The maven goal (or none == maven default goal)
        goal=maven.getGoal()
    
        # Optional 'verbose' or 'debug'
        verbose=maven.isVerbose()
        debug=maven.isDebug()
    
        #
        # Where to run this:
        #
        basedir = maven.getBaseDirectory() or project.getBaseDirectory()
    
        #
        # Build a classpath (based upon dependencies)
        #
        (classpath,bootclasspath)=languageHelper.getClasspaths(project)
    
        # Run Maven...
        cmd=Cmd('mvn','build_'+project.getModule().getName()+'_'+project.getName(),\
            basedir,{'CLASSPATH':classpath})
            
        # Set this as a system property. Setting it here helps JDK1.4+
        # AWT implementations cope w/o an X11 server running (e.g. on
        # Linux)
        # cmd.addPrefixedParameter('-D','java.awt.headless','true','=')
    
        #
        # Add BOOTCLASSPATH
        #
        #if bootclasspath:
        #    cmd.addPrefixedParameter('-X','bootclasspath/p',bootclasspath,':')
            
        #if jvmargs:
        #    cmd.addParameters(jvmargs)
            
        # cmd.addParameter('org.apache.maven.cli.App')  
    
        #
        # Allow maven-level debugging...
        #
        if project.getWorkspace().isDebug() or project.isDebug() or debug: 
            cmd.addParameter('--debug')  
        if project.getWorkspace().isVerbose()  or project.isVerbose() or verbose: 
            cmd.addParameter('--exception') 
        
        #
        # Suppress downloads
        #          

        # As long as we don't know how to pass our local artifacts to
        # mvn there is no point in using the offline mode
        #
        # cmd.addParameter('--offline')  
        
        #
        #	This sets the *defaults*, a workspace could override them.
        #
        #cmd.addPrefixedParameter('-D','build.sysclasspath','only','=')
    
        # End with the goal...
        if goal: 
            for goalParam in goal.split(','):
                cmd.addParameter(goalParam)
    
        return cmd
  
        # Do this even if not ok
    def performPreBuild(self, project, languageHelper, stats):
                   
        # Maven requires a build.properties to be generated...
        if project.okToPerformWork():
            try:
                propertiesFile=self.generateMavenProperties(project,languageHelper)                                
                project.addDebug('(Gump generated) Maven Properties in: ' + propertiesFile)
                
                try:
                    catFileToFileHolder(project,propertiesFile,
                        FILE_TYPE_CONFIG,
                        os.path.basename(propertiesFile))
                except:
                    log.error('Display Properties [ ' + propertiesFile + '] Failed', exc_info=1)   
               
            except Exception, details:
                message='Generate Maven Properties Failed:' + str(details)
                log.error(message, exc_info=1)
                project.addError(message)    
                project.changeState(STATE_FAILED,REASON_PREBUILD_FAILED)
 
    # The propertiesFile parameter is primarily for testing.
    def generateMavenProperties(self,project,languageHelper,propertiesFile=None):
        """Set properties/overrides for a Maven project"""
        
        #:TODO: Does Maven have the idea of system properties?
        
        #
        # Where to put this:
        #
        basedir = project.mvn.getBaseDirectory() or project.getBaseDirectory()
        if not propertiesFile: 
            propertiesFile=os.path.abspath(os.path.join(basedir,'profiles.xml'))
            
        # Ensure containing directory exists, or make it.
        propsdir=os.path.dirname(propertiesFile)
        if not os.path.exists(propsdir):
            project.addInfo('Making directory for Maven properties: ['+propsdir+']')
            os.makedirs(propsdir)
        
        if os.path.exists(propertiesFile):
            project.addWarning('Overriding Maven properties: ['+propertiesFile+']')
    
        
        props=open(propertiesFile,'w')
        
        props.write('<?xml version="1.0"?>\n')
        props.write(("""<!-- 
# DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT 
#
# File Automatically Generated by Gump, see http://gump.apache.org/
#
# Generated For : %s
# Generated At  : %s
#
#
# DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT
# 
-->\n""")	%	(project.getName(), time.strftime('%Y-%m-%d %H:%M:%S')) )
        props.write("<profiles>\n")
        props.write("  <profile>\n")
        props.write("   <id>Gump</id>\n")
        props.write("   <activation><activeByDefault/></activation>\n")
        (classpath,bootclasspath)=languageHelper.getClasspathObjects(project)
        
        # :TODO: write...
        props.write("   <properties>\n")
        for annotatedPath in classpath.getPathParts()+bootclasspath.getPathParts():
            if isinstance(annotatedPath,gump.core.language.path.AnnotatedPath):
                # Sort of punting here
                props.write("<!-- Contributor: %s -->\n" % \
                    ( annotatedPath.getContributor() ))
                props.write("     <maven.jar.%s>%s</maven.jar.%s>\n" % \
                             (annotatedPath.getId(), \
                              annotatedPath.getPath(), \
                              annotatedPath.getId()))
        #
        # Output basic properties
        #
        for property in project.getWorkspace().getProperties()+project.getMvn().getProperties():
            # build.sysclasspath makes Maven sick.
            if not 'build.sysclasspath' == property.name:
                props.write(('<%s>%s</%s>\n') % \
                   (property.name,property.value,property.name))            
        
        #
        # Output classpath properties
        #
        props.write("""<!--
# 
# M A V E N  J A R  O V E R R I D E
# 
-->
<maven.jar.override>on</maven.jar.override>
""")
        
        props.write("   </properties>\n")
        props.write("</profile></profiles>\n")
        return propertiesFile
      
    def locateMavenProjectPropertiesFile(self,project):
        """Return Maven project properties file location""" 
        basedir = project.mvn.getBaseDirectory() or project.getBaseDirectory()
        return os.path.abspath(os.path.join(basedir,'project.properties'))
        
    def locateMavenProjectFile(self,project):
        """Return Maven project file location"""      
        basedir = project.mvn.getBaseDirectory() or project.getBaseDirectory()
        return os.path.abspath(os.path.join(basedir,'pom.xml'))  
        
    def preview(self,project,languageHelper,stats):        
        command=self.getMavenCommand(project,languageHelper) 
        command.dump()
            
