#!/usr/bin/python


# Copyright 2003-2004 The Apache Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

"""

import os.path
import sys

from gump import log
from gump.core.gumprun import *
from gump.core.config import dir, default, basicConfig

from gump.build.abstract import AbstractJavaBuilder

from gump.utils import dump, display, getIndent, logResourceUtilization, \
                            invokeGarbageCollection
from gump.utils.note import Annotatable
from gump.utils.work import *

from gump.utils.tools import *

from gump.model.workspace import *
from gump.model.module import Module
from gump.model.project import Project,AnnotatedPath
from gump.model.depend import  ProjectDependency
from gump.model.stats import *
from gump.model.state import *


###############################################################################
# Classes
###############################################################################

class MavenBuilder(AbstractJavaBuilder):
    
    def __init__(self,run):
        AbstractJavaBuilder.__init__(self,run)

    def buildProject(self,project,stats):
        
        workspace=self.run.getWorkspace()
                
        log.debug(' ------ Maven-ing: #[' + `project.getPosition()` + '] ' + project.getName())
        
        self.performPreBuild(project, stats)
          
        wasBuilt=0
        if project.okToPerformWork():

            #
            # Get the appropriate build command...
            #
            cmd=project.getBuildCommand(self.run.getEnvironment().getJavaCommand())

            if cmd:
                # Execute the command ....
                cmdResult=execute(cmd,workspace.tmpdir)
    
                # Update Context    
                work=CommandWorkItem(WORK_TYPE_BUILD,cmd,cmdResult)
                project.performedWork(work)
                wasBuilt=1
                    
                # Update Context w/ Results  
                if not cmdResult.state==CMD_STATE_SUCCESS:
                    reason=REASON_BUILD_FAILED
                    if cmdResult.state==CMD_STATE_TIMED_OUT:
                        reason=REASON_BUILD_TIMEDOUT
                    project.changeState(STATE_FAILED,reason)                        
                else:                         
                    # For now, things are going good...
                    project.changeState(STATE_SUCCESS)
                    
        if wasBuilt:
            pomFile=self.locateMavenProjectFile(project) 
            if os.path.exists(pomFile):                               
                project.addDebug('Maven POM in: ' + pomFile) 
                catFileToFileHolder(project, pomFile, FILE_TYPE_CONFIG) 
                    
            projpFile=self.locateMavenProjectPropertiesFile(project) 
            if os.path.exists(projpFile):                                                
                project.addDebug('Maven project properties in: ' + projpFile)                
                catFileToFileHolder(project, pomFile, FILE_TYPE_CONFIG) 
            
            logFile=self.locateMavenLog(project)
            if os.path.exists(logFile):
                project.addDebug('Maven Log in: ' + logFile)                
                catFileToFileHolder(project, logFile, FILE_TYPE_LOG)                                
  
    #
    # Build an ANT command for this project
    #        
    def getMavenCommand(self,project):
        maven=project.maven
        mavenxml=project.xml.maven
    
        # The ant goal (or none == ant default goal)
        goal=maven.getGoal()
    
        # Optional 'verbose' or 'debug'
        verbose=mavenxml.verbose
        debug=mavenxml.debug
    
        #
        # Where to run this:
        #
        basedir = maven.getBaseDirectory() or project.getBaseDirectory()
    
        #
        # Build a classpath (based upon dependencies)
        #
        (classpath,bootclasspath)=project.getClasspaths()
    
        #
        # Get properties
        #
        #jvmargs=project.getJVMArgs()
   
        #
        # Run Maven...
        #
        cmd=Cmd('maven','build_'+project.getModule().getName()+'_'+project.getName(),\
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
        cmd.addParameter('--offline')  
        
        #
        #	This sets the *defaults*, a workspace could override them.
        #
        #cmd.addPrefixedParameter('-D','build.sysclasspath','only','=')
    
        # End with the goal...
        cmd.addParameter(goal)
    
        return cmd
  
        # Do this even if not ok
    def performPreBuild(self, project, stats):
                   
        # Maven requires a build.properties to be generated...
        if project.okToPerformWork():
            try:
                propertiesFile=self.generateMavenProperties(project)                                
                project.addDebug('Maven Properties in: ' + propertiesFile)
                
                try:
                    catFileToFileHolder(project,propertiesFile,	\
                        FILE_TYPE_CONFIG,	\
                        os.path.basename(propertiesFile))
                except:
                    log.error('Display Properties [ ' + propertiesFile + '] Failed', exc_info=1)   
                
            except:
                log.error('Generate Maven Properties Failed', exc_info=1)    
                project.changeState(STATE_FAILED,REASON_PREBUILD_FAILED)
 
    # The propertiesFile parameter is primarily for testing.
    def generateMavenProperties(self,project,propertiesFile=None):
        """Set properties/overrides for a Maven project"""
        
        #:TODO: Does Maven have the idea of system properties?
        
        #
        # Where to put this:
        #
        basedir = project.maven.getBaseDirectory() or project.getBaseDirectory()
        if not propertiesFile: 
            propertiesFile=os.path.abspath(os.path.join(	\
                    basedir,'build.properties'))
        
        if os.path.exists(propertiesFile):
            project.addWarning('Overriding Maven properties: ['+propertiesFile+']')
    
        
        props=open(propertiesFile,'w')
        
        props.write(("""# ------------------------------------------------------------------------
# DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT 
#
# File Automatically Generated by Gump, see http://gump.apache.org/
#
# Generated For : %s
# Generated At  : %s
#
#
# DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT
# ------------------------------------------------------------------------
""")	%	(project.getName(), time.strftime('%Y-%m-%d %H:%M:%S')) )
        
        #
        # Output basic properties
        #
        for property in project.getWorkspace().getProperties()+project.getMaven().getProperties():
            # build.sysclasspath makes Maven sick.
            if not 'build.sysclasspath' == property.name:
                props.write(('%s=%s\n') % (property.name,property.value))            
        
        #
        # Output classpath properties
        #
        props.write("""
# ------------------------------------------------------------------------
# M A V E N  J A R  O V E R R I D E
# ------------------------------------------------------------------------
maven.jar.override = on

# ------------------------------------------------------------------------
# Jars set explicity by path.
# ------------------------------------------------------------------------
""")
        
        (classpath,bootclasspath)=project.getClasspathObjects()
        
        # :TODO: write...
        for annotatedPath in classpath.getPathParts():
            if isinstance(annotatedPath,AnnotatedPath):
                props.write(('# Contributor: %s\nmaven.jar.%s=%s\n') % \
                    (	annotatedPath.getContributor(),	\
                        annotatedPath.getId(),	\
                        annotatedPath.getPath()))

        return propertiesFile
      
    def locateMavenLog(self,project):
        """Return Maven log location"""  
        basedir = project.maven.getBaseDirectory() or project.getBaseDirectory()
        return os.path.abspath(os.path.join(basedir,'maven.log'))
      
    def locateMavenProjectPropertiesFile(self,project):
        """Return Maven project properties file location""" 
        basedir = project.maven.getBaseDirectory() or project.getBaseDirectory()
        return os.path.abspath(os.path.join(basedir,'project.properties'))
        
    def locateMavenProjectFile(self,project):
        """Return Maven project file location"""      
        basedir = project.maven.getBaseDirectory() or project.getBaseDirectory()
        return os.path.abspath(os.path.join(basedir,'project.xml'))  