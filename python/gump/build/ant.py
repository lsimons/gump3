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
from gump.model.project import Project
from gump.model.depend import  ProjectDependency
from gump.model.stats import *
from gump.model.state import *


###############################################################################
# Classes
###############################################################################

class AntBuilder(AbstractJavaBuilder):
    
    def __init__(self,run):
        AbstractJavaBuilder.__init__(self,run)


    def buildProject(self,project,stats):
        
        workspace=self.run.getWorkspace()
                 
        log.info('Run Ant on Project: #[' + `project.getPosition()` + '] : ' + project.getName())
    
        #
        # Get the appropriate build command...
        #
        cmd=self.getAntCommand(project, self.run.getEnvironment().getJavaCommand())

        if cmd:
            # Execute the command ....
            cmdResult=execute(cmd,workspace.tmpdir)
    
            # Update Context    
            work=CommandWorkItem(WORK_TYPE_BUILD,cmd,cmdResult)
            project.performedWork(work)
            project.setBuilt(1)
                    
            # Update Context w/ Results  
            if not cmdResult.state==CMD_STATE_SUCCESS:
                reason=REASON_BUILD_FAILED
                if cmdResult.state==CMD_STATE_TIMED_OUT:
                    reason=REASON_BUILD_TIMEDOUT
                project.changeState(STATE_FAILED,reason)
                        
            else:                         
                # For now, things are going good...
                project.changeState(STATE_SUCCESS)
   
    #
    # Build an ANT command for this project
    #        
    def getAntCommand(self,project,javaCommand='java'):
        
        # The original model information...
        ant=project.ant
        antxml=project.xml.ant
    
        # The ant target (or none == ant default target)
        target= antxml.target or ''
    
        # The ant build file (or none == build.xml)
        buildfile = antxml.buildfile or ''
    
        # Optional 'verbose' or 'debug'
        verbose=antxml.verbose
        debug=antxml.debug
    
        #
        # Where to run this:
        #
        basedir = ant.getBaseDirectory() or project.getBaseDirectory()
    
        #
        # Build a classpath (based upon dependencies)
        #
        (classpath,bootclasspath)=project.getClasspaths()
    
        #
        # Get properties
        #
        properties=self.getAntProperties(project)
   
        #
        # Get properties
        #
        sysproperties=self.getAntSysProperties(project)
   
        #
        # Get properties
        #
        jvmargs=self.getJVMArgs(antxml)
   
        #
        # Run java on apache Ant...
        #
        cmd=Cmd(javaCommand,'build_'+project.getModule().getName()+'_'+project.getName(),\
            basedir,{'CLASSPATH':classpath})
            
        # These are workspace + project system properties
        cmd.addNamedParameters(sysproperties)
        
        
        # :NOTE: Commented out since <sysproperty was implemented.
        #
        # Set this as a system property. Setting it here helps JDK1.4+
        # AWT implementations cope w/o an X11 server running (e.g. on
        # Linux)
        # cmd.addPrefixedParameter('-D','java.awt.headless','true','=')
    
    
        # :NOTE: Commented out since <sysproperty was implemented.
        #
        # This helps ant maintain VM information for sub-VMs it launches.
        #
        # cmd.addPrefixedParameter('-D','build.clonevm','true','=')
        
        #
        # Add BOOTCLASSPATH
        #
        if bootclasspath:
            cmd.addPrefixedParameter('-X','bootclasspath/p',bootclasspath,':')
            
        if jvmargs:
            cmd.addParameters(jvmargs)
            
        cmd.addParameter('org.apache.tools.ant.Main')  
    
        #
        # Allow ant-level debugging...
        #
        if project.getWorkspace().isDebug() or project.isDebug() or debug: 
            cmd.addParameter('-debug')  
        if project.getWorkspace().isVerbose()  or project.isVerbose() or verbose: 
            cmd.addParameter('-verbose')  
        
        #
        #	This sets the *defaults*, a workspace could override them.
        #        
        # :NOTE: Commented out since <property on workspace works.
        # cmd.addPrefixedParameter('-D','build.sysclasspath','only','=')
    
        mergeFile=project.getWorkspace().getMergeFile()
        if mergeFile:
            cmd.addPrefixedParameter('-D','gump.merge',str(mergeFile),'=')        
    
        # These are from the project and/or workspace
        # These are 'normal' properties.
        cmd.addNamedParameters(properties)
    
        # Pass the buildfile
        if buildfile: cmd.addParameter('-f',buildfile)
    
        # End with the target...
        if target: 
            for targetParam in target.split():
                cmd.addParameter(targetParam)
    
        return cmd
  
    def getAntProperties(self,project):
        """Get properties for a project"""
        properties=Parameters()
        for property in project.getWorkspace().getProperties()+project.getAnt().getProperties():
            properties.addPrefixedNamedParameter('-D',property.name,property.value,'=')
        return properties

    def getAntSysProperties(self,project):
        """Get sysproperties for a project"""
        properties=Parameters()
        for property in project.getWorkspace().getSysProperties()+project.getAnt().getSysProperties():
            properties.addPrefixedNamedParameter('-D',property.name,property.value,'=')
        return properties
                
    def preview(self,project,stats):        
        command=self.getAntCommand(project) 
        command.dump()
 