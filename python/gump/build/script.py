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

class ScriptBuilder(RunSpecific):
    
    def __init__(self,run):
        RunSpecific.__init__(self,run)

    def buildProject(self,project,stats):
        
        workspace=self.run.getWorkspace()
                 
        log.info(' ------ Script-ing: #[' + `project.getPosition()` + '] : ' + project.getName())
                
        #
        # Get the appropriate build command...
        #
        cmd=self.getScriptCommand(project)

        if cmd:
            # Execute the command ....
            cmdResult=execute(cmd,workspace.tmpdir)
    
            # Update Context    
            work=CommandWorkItem(WORK_TYPE_BUILD,cmd,cmdResult)
            project.performedWork(work)
                    
            # Update Context w/ Results  
            if not cmdResult.state==CMD_STATE_SUCCESS:
                reason=REASON_BUILD_FAILED
                if cmdResult.state==CMD_STATE_TIMED_OUT:
                    reason=REASON_BUILD_TIMEDOUT
                project.changeState(STATE_FAILED,reason)
                        
            else:                         
                # For now, things are going good...
                project.changeState(STATE_SUCCESS)
   
    def getScriptCommand(self,project):
        """ Return the command object for a <script entry """
        script=project.script
        scriptxml=project.xml.script 
           
        #
        # Where to run this:
        #
        basedir = script.getBaseDirectory() or project.getBaseDirectory()

        # Add .sh  or .bat as appropriate to platform
        scriptfullname=scriptxml.name
        if not os.name == 'dos' and not os.name == 'nt':
            scriptfullname += '.sh'
        else:
            scriptfullname += '.bat'
      
        # Optional 'verbose' or 'debug'
        # verbose=scriptxml.verbose
        # debug=scriptxml.debug
       
        scriptfile=os.path.abspath(os.path.join(basedir, scriptfullname))
        
        # Not sure this is relevent...
        (classpath,bootclasspath)=project.getClasspaths()

        cmd=Cmd(scriptfile,'buildscript_'+project.getModule().getName()+'_'+project.getName(),\
            basedir,{'CLASSPATH':classpath})    
            
        # Set this as a system property. Setting it here helps JDK1.4+
        # AWT implementations cope w/o an X11 server running (e.g. on
        # Linux)
        #    
        # Per GUMP-48 scripts do not want this.
        # cmd.addPrefixedParameter('-D','java.awt.headless','true','=')
    
        #
        # Add BOOTCLASSPATH
        #
        # Per GUMP-48 scripts do not want this.
        #if bootclasspath:
        #    cmd.addPrefixedParameter('-X','bootclasspath/p',bootclasspath,':')
                    
        #
        # Allow script-level debugging...
        #
        # Per GUMP-48 scripts do not want this.        
        #if project.getWorkspace().isDebug() or project.isDebug() or debug:
        #    cmd.addParameter('-debug')  
        #if project.getWorkspace().isVerbose()  or project.isVerbose() or verbose:
        #    cmd.addParameter('-verbose')  
        
        return cmd
    