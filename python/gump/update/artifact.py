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
from fnmatch import fnmatch

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

from gump.integration.depot import *

###############################################################################
# Classes
###############################################################################

class ArtifactUpdater(RunSpecific):
    
    def __init__(self,run):
        RunSpecific.__init__(self,run)

    def updateModule(self,module):
        """
        
            Perform an Artifact update on a module
            
        """            
        log.info('Perform Artifact Update on #[' + `module.getPosition()` + \
                        '] : ' + module.getName())
    
        # Did we 'downlaod artifacts' already?
        exists	=	os.path.exists(module.getSourceControlStagingDirectory())
       
        #  Get the Update Command
        cmd = self.getArtifactUpdateCommand(module)
                               
        # Execute the command and capture results        
        cmdResult=execute(cmd, module.getWorkspace().tmpdir)
      
        #
        # Store this as work, on both the module and (cloned) on the repo
        #
        work=CommandWorkItem(WORK_TYPE_UPDATE,cmd,cmdResult)
        module.performedWork(work)  
        module.getRepository().performedWork(work.clone())
      
        # Update Context w/ Results  
        if not cmdResult.isOk():              
            log.error('Failed to checkout/update module: ' + module.name)   
            if not exists:     
                module.changeState(STATE_FAILED,REASON_UPDATE_FAILED)
            else:
                module.addError('*** Failed to update from source control. Stale contents ***')
                        
                # Black mark for this repository
                repository=module.getRepository()
                repository.addError('*** Failed to update %s from source control. Stale contents ***'	\
                                    % module.getName())
                                        
                # Kinda bogus, but better than nowt (for now)
                module.changeState(STATE_SUCCESS,REASON_UPDATE_FAILED)
        else:
            module.changeState(STATE_SUCCESS)       
                
        return module.okToPerformWork()                                                 
         
    def preview(self,module):            
        command = self.getArtifactUpdateCommand(module)
        command.dump()                                            
         
    def getArtifactUpdateCommand(self,module):
        
        log.debug("Artifact Update Module " + module.getName() + \
                       ", Repository Name: " + str(module.repository.getName()))

        url=module.artifacts.getRootUrl()
        group=module.artifacts.getGroup()
      
        log.debug("Artifact URL/Group: [" + `url` + "," + `group` + "] on Repository: " + module.repository.getName())
     
        #
        # Prepare Artifact checkout/update command...
        # 
        cmd=Cmd(getDepotUpdateCmd(),	\
                'update_'+module.getName(),	\
                module.getWorkspace().cvsdir)
        
        # Be 'quiet' (but not silent) unless requested otherwise.
        if 	not module.isDebug() 	\
            and not module.isVerbose() \
            and not module.artifacts.isDebug()	\
            and not module.artifacts.isVerbose():    
            cmd.addParameter('-q')
    
        # The URL (ought be optional)
        if url:
            cmd.addParameter('-r')    
            cmd.addParameter(url)
    
        # Group (mandatory)
        cmd.addParameter('-g')
        cmd.addParameter(group)
        
        # Target
        cmd.addParameter('-t')
        cmd.addParameter(module.getName())  
   
        return cmd
     
