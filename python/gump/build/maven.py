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

from gump.utils import dump, display, getIndent, logResourceUtilization, \
                            invokeGarbageCollection
from gump.utils.note import Annotatable
from gump.utils.work import *

from gump.utils.tools import *

from gump.model.workspace import *
from gump.model.module import Module
from gump.model.project import Project
from gump.model.depend import  ProjectDependency
from gump.model.stats import *
from gump.model.state import *


###############################################################################
# Classes
###############################################################################

class MavenBuilder(AbstractJavaBuilder):
    
    def __init__(self,run):
        AbstractJavaBuilder.__init__(self,run)


    def buildProject(self,project,stats)
        
        workspace=self.run.getWorkspace()
                 
        log.info(' Project: #[' + `project.getPosition()` + '] of [' + `projectCount` + '] : ' + project.getName())
                    
        # Extract stats (in case we want to do conditional processing)            
        stats=None
        if project.hasStats():
            stats=project.getStats()
            
        if project.isPackaged():             
            self.performProjectPackageProcessing(project, stats)
            continue
                
        # Do this even if not ok
        self.performPreBuild(project, stats)

        wasBuilt=0
        if project.okToPerformWork():        
            log.debug(' ------ Building: [' + `projectNo` + '] ' + project.getName())

            # Turn on --verbose or --debug if failing ...
            if stats:
                if (not STATE_SUCCESS == stats.currentState) and \
                        not project.isVerboseOrDebug():
                    if stats.sequenceInState > INSIGNIFICANT_DURATION:
                        project.addInfo('Enable "debug" output, due to a sequence of %s previous errors.' % stats.sequenceInState)
                        project.setDebug(1)
                    else:
                        project.addInfo('Enable "verbose" output, due to %s previous error(s).' % stats.sequenceInState)    
                        project.setVerbose(1)

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
                        
                    if not project.isDebug():
                        # Display...
                        project.addInfo('Enable "debug" output, due to build failure.')
                        project.setDebug(1)
                        
                else:                         
                    # For now, things are going good...
                    project.changeState(STATE_SUCCESS)
  
    #
    # Build an ANT command for this project
    #        
    def getMavenCommand(self):
        maven=self.maven
        mavenxml=self.xml.maven
    
        # The ant goal (or none == ant default goal)
        goal=maven.getGoal()
    
        # Optional 'verbose' or 'debug'
        verbose=mavenxml.verbose
        debug=mavenxml.debug
    
        #
        # Where to run this:
        #
        basedir = maven.getBaseDirectory() or self.getBaseDirectory()
    
        #
        # Build a classpath (based upon dependencies)
        #
        (classpath,bootclasspath)=self.getClasspaths()
    
        #
        # Get properties
        #
        #jvmargs=self.getJVMArgs()
   
        #
        # Run Maven...
        #
        cmd=Cmd('maven','build_'+self.getModule().getName()+'_'+self.getName(),\
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
        if self.getWorkspace().isDebug() or self.isDebug() or debug: 
            cmd.addParameter('--debug')  
        if self.getWorkspace().isVerbose()  or self.isVerbose() or verbose: 
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
  
 
    # The propertiesFile parameter is primarily for testing.
    def generateMavenProperties(self,propertiesFile=None):
        """Set properties/overrides for a Maven project"""
        
        #:TODO: Does Maven have the idea of system properties?
        
        #
        # Where to put this:
        #
        basedir = self.maven.getBaseDirectory() or self.getBaseDirectory()
        if not propertiesFile: 
            propertiesFile=os.path.abspath(os.path.join(	\
                    basedir,'build.properties'))
        
        if os.path.exists(propertiesFile):
            self.addWarning('Overriding Maven properties: ['+propertiesFile+']')
    
        
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
""")	%	(self.getName(), time.strftime('%Y-%m-%d %H:%M:%S')) )
        
        #
        # Output basic properties
        #
        for property in self.getWorkspace().getProperties()+self.getMaven().getProperties():
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
        
        (classpath,bootclasspath)=self.getClasspathObjects()
        
        # :TODO: write...
        for annotatedPath in classpath.getPathParts():
            if isinstance(annotatedPath,AnnotatedPath):
                props.write(('# Contributor: %s\nmaven.jar.%s=%s\n') % \
                    (	annotatedPath.getContributor(),	\
                        annotatedPath.getId(),	\
                        annotatedPath.getPath()))

        return propertiesFile
      
    def locateMavenLog(self):
        """Return Maven log location"""  
        basedir = self.maven.getBaseDirectory() or self.getBaseDirectory()
        return os.path.abspath(os.path.join(basedir,'maven.log'))
      
    def locateMavenProjectPropertiesFile(self):
        """Return Maven project properties file location""" 
        basedir = self.maven.getBaseDirectory() or self.getBaseDirectory()
        return os.path.abspath(os.path.join(basedir,'project.properties'))
        
    def locateMavenProjectFile(self):
        """Return Maven project file location"""      
        basedir = self.maven.getBaseDirectory() or self.getBaseDirectory()
        return os.path.abspath(os.path.join(basedir,'project.xml'))  