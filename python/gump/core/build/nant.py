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
	A NAnt builder (uses nant to build projects)
"""

import os.path
import sys

from gump import log
from gump.core.run.gumprun import *
from gump.core.config import dir, default, basicConfig

from gump.util.note import Annotatable
from gump.util.work import *

from gump.util.tools import *

from gump.core.model.workspace import *
from gump.core.model.module import Module
from gump.core.model.project import Project
from gump.core.model.depend import  ProjectDependency
from gump.core.model.stats import *
from gump.core.model.state import *

class NAntBuilder(gump.core.run.gumprun.RunSpecific):
    
    def __init__(self,run):
        """
        	The NAnt Builder is a Java Builder
    	""" 
        gump.core.run.gumprun.RunSpecific.__init__(self,run)

    def buildProject(self,project,language,stats):
        """
        	Build a project using NAnt, based off the <nant metadata.
        	
        	Note: switch on -verbose|-debug based of the stats for this
        	project, i.e. how long in a state of failure.
        """
        
        workspace=self.run.getWorkspace()
                 
        log.info('Run NAnt on Project: #[' + `project.getPosition()` + '] : ' + project.getName())
    
        # Get the appropriate build command...
        cmd=self.getNAntCommand(project, language)

        if cmd:
            # Execute the command ....
            cmdResult=execute(cmd,workspace.tmpdir)
    
            # Update context with the fact that this work was done
            work=CommandWorkItem(WORK_TYPE_BUILD,cmd,cmdResult)
            project.performedWork(work)
            project.setBuilt(True)
                    
            # Update context state based of the result  
            if not cmdResult.state==CMD_STATE_SUCCESS:
                reason=REASON_BUILD_FAILED
                if cmdResult.state==CMD_STATE_TIMED_OUT:
                    reason=REASON_BUILD_TIMEDOUT
                project.changeState(STATE_FAILED,reason)                        
            else:                         
                # For now, things are going good...
                project.changeState(STATE_SUCCESS)
    
    def getNAntCommand(self,project,languageHelper):
        """
        	Build an ANT command for this project, based on the <nant metadata
   			select targets and build files as appropriate.     	
        """
        
        # The original model information...
        nant=project.nant
        # The nant target (or none == nant default target)
        target= nant.getTarget()
    
        # The nant build file (or none == build.xml)
        buildfile = nant.getBuildFile()
    
        # Optional 'verbose' or 'debug'
        verbose=nant.isVerbose()
        debug=nant.isDebug()
    
        # Where to run this:
        basedir = nant.getBaseDirectory() or project.getBaseDirectory()
    
        # Build a classpath (based upon dependencies)
        #(classpath,bootclasspath)=language.getClasspaths(project)
    
        # Get properties
        properties=self.getNAntProperties(project)
   
        # Get system properties
        sysproperties=self.getNAntSysProperties(project)
        
        # Library Path
        libpath=languageHelper.getAssemblyPath(project)
        
        # Run java on apache NAnt...
        cmd=Cmd('NAnt.exe','build_'+project.getModule().getName()+'_'+project.getName(),
            basedir,{'DEVPATH':libpath})
        
        # Launch with specified framework (e.g. mono-1.0.1) if
        # required.
        workspace=self.run.getWorkspace()
        if workspace.hasDotNetInformation():
            dotnetInfo=workspace.getDotNetInformation()
            if dotnetInfo.hasFramework():                
                cmd.addParameter('-t:',dotnetInfo.getFramework(),'')
   
        # These are workspace + project system properties
        cmd.addNamedParameters(sysproperties)
        
        # Get/set JVM properties
        #jvmargs=language.getJVMArgs(project)
        #if jvmargs:
        #    cmd.addParameters(jvmargs)
       
        # Allow ant-level debugging...
        if project.getWorkspace().isDebug() or project.isDebug() or debug: 
            cmd.addParameter('-debug')  
        if project.getWorkspace().isVerbose()  or project.isVerbose() or verbose: 
            cmd.addParameter('-verbose')  
    
        # Some builds might wish for this information
        # :TODO: Grant greater access to Gump variables from
        # within.
        mergeFile=project.getWorkspace().getMergeFile()
        if mergeFile:
            cmd.addPrefixedParameter('-D:','gump.merge',str(mergeFile),'=')        
    
        # These are from the project and/or workspace
        # These are 'normal' properties.
        cmd.addNamedParameters(properties)
    
        # Pass the buildfile
        if buildfile: cmd.addParameter('-buildfile',buildfile, ':')
    
        # End with the target (or targets)...
        if target: 
            for targetParam in target.split(','):
                cmd.addParameter(targetParam)
    
        return cmd
  
    def getNAntProperties(self,project):
        """ Get properties for a project """
        properties=Parameters()
        for property in project.getWorkspace().getProperties()+project.getNAnt().getProperties():
            properties.addPrefixedNamedParameter('-D:',property.name,property.value,'=')
        return properties

    def getNAntSysProperties(self,project):
        """ Get sysproperties for a project """
        properties=Parameters()
        for property in project.getWorkspace().getSysProperties()+project.getNAnt().getSysProperties():
            properties.addPrefixedNamedParameter('-D:',property.name,property.value,'=')
        return properties
                
    def preview(self,project,language,stats):        
        """
        	Preview what an NAnt build would look like.
        """
        command=self.getNAntCommand(project,language) 
        command.dump()
 
