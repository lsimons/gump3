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

__revision__  = "$Rev: 36667 $"
__date__      = "$Date: 2004-08-20 08:55:45 -0600 (Fri, 20 Aug 2004) $"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"


"""

"""

import os.path
import sys

from gump import log
from gump.run.gumprun import *
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

class ScriptBuilder(gump.run.gumprun.RunSpecific):
    
    def __init__(self,run):
        """
        A script 'builder'
        """
        gump.run.gumprun.RunSpecific.__init__(self,run)

    def buildProject(self,project,languageHelper,stats):
        """
        Run a project's script (a .bat or a .sh as appropriate)
        """
        
        workspace=self.run.getWorkspace()
                 
        log.info('Run Project (as a script): #[' + `project.getPosition()` + '] : ' + project.getName())
                
        #
        # Get the appropriate build command...
        #
        cmd=self.getScriptCommand(project,languageHelper)

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
   
    def getScriptCommand(self,project,languageHelper):
        """ Return the command object for a <script entry """
        script=project.script
           
        # Where to run this:
        basedir = script.getBaseDirectory() or project.getBaseDirectory()

        scriptfullname=script.getName()
        if not os.path.exists(os.path.join(basedir, scriptfullname)):
            # Add .sh  or .bat as appropriate to platform
            if not os.name == 'dos' and not os.name == 'nt':
                scriptfullname += '.sh'
            else:
                scriptfullname += '.bat'
  
        # The script
        scriptfile=os.path.abspath(os.path.join(basedir, scriptfullname))
        
        # Needed for (at least) a compiler...
        (classpath,bootclasspath)=languageHelper.getClasspaths(project)

        cmd=Cmd(scriptfile,'buildscript_'+project.getModule().getName()+'_'+project.getName(),\
            basedir,{'CLASSPATH':classpath})    
        
        return cmd
        
        
    def preview(self,project,languageHelper,stats):        
        """
        Preview what this would do
        """
        command=self.getScriptCommand(project,languageHelper) 
        command.dump()
