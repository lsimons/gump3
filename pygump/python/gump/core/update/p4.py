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

class P4Updater(RunSpecific):
    
    def __init__(self,run):
        RunSpecific.__init__(self,run)

        #
        # A stash of known logins.
        #
        #self.logins=readLogins()

    def updateModule(self,module):
        """
        
            Perform a P4 sync on a module
            
        """
            
        #log.info('Perform P4 Sync on #[' + `module.getPosition()` + \
        #                '] : ' + module.getName())
    
        ## Did we 'P4 checkout' already?
        exists	=	os.path.exists(module.getSourceControlStagingDirectory())
       
        # Doesn't tell us much...
        if exists:
            self.performStatus(module)
                
        self.performUpdate(module,exists)        
        
        return module.okToPerformWork()      
        
    def performStatus(self,module):
        #  Get the Update Command
        (repository, root, cmd ) = self.getUpdateCommand(module, True, True)
                
        ## Provide P4 logins, if not already there
        #loginToRepositoryOnDemand(repository,root,self.logins)
               
        # Execute the command and capture results        
        cmdResult=execute(cmd, module.getWorkspace().tmpdir)
      
        #
        # Store this as work, on both the module and (cloned) on the repo
        #
        work=CommandWorkItem(WORK_TYPE_UPDATE,cmd,cmdResult)
        module.performedWork(work)  
     
        if not cmdResult.isOk():              
            log.error('Failed to checkout/update module: ' + module.name)   
                                  
    def performUpdate(self,module,exists):
        """
            Update this module (checking out if needed)
        """
        #  Get the Update Command
        (repository, root, cmd ) = self.getUpdateCommand(module, exists)
                
        #log.debug("P4 Sync Module " + module.getName() + \
        #               ", Repository Name: " + str(module.repository.getName()))
                                        
        ## Provide P4 logins, if not already there
        #loginToRepositoryOnDemand(repository,root,self.logins)
               
        # Execute the command and capture results        
        cmdResult=execute(cmd, module.getWorkspace().tmpdir)
      
        #
        # Store this as work, on both the module and (cloned) on the repo
        #
        work=CommandWorkItem(WORK_TYPE_UPDATE,cmd,cmdResult)
        module.performedWork(work)  
        repository.performedWork(work.clone())
      
        # Update Context w/ Results  
        if not cmdResult.isOk():              
            log.error('Failed w/ P4 Root ' + root + ' for %s on Repository %s.' \
                % (module.name, module.repository.getName())) 
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
            
            # We run P4 so any output means updates occured...
            if cmdResult.hasOutput():                       
                log.info('Update(s) received via P4 on #[' \
                                + `module.getPosition()` + \
                                '] : ' + module.getName())
                                 
    def preview(self,module):
                
        (repository, root, command ) = self.getUpdateCommand(module,False)
        command.dump()
        
        # Doesn't tell us much...
        #(repository, root, command ) = self.getUpdateCommand(module,True,True)
        #command.dump()
            
        (repository, root, command ) = self.getUpdateCommand(module,True)
        command.dump()                       
        
    
    def getUpdateCommand(self,module,exists=False,nowork=False):
        """        
            Format a commandline for doing the P4 update            
        """
        if nowork and not exists:
            raise RuntimeException('Not coded for this combo.')            
        
        root=module.p4.getClientspec()
        # Prepare P4 sync command...
        prefix='update'
        directory=module.getWorkspace().getSourceControlStagingDirectory()
        #if exists:     
        #    directory=module.getSourceControlStagingDirectory()            
        if nowork:
            prefix='status'
                
        cmd=Cmd(	'p4',
                    prefix+'_'+module.getName(),
                    directory)
          
        ## Allow trace for debug
        #if module.isDebug():
        #    cmd.addParameter('-t')
          
        ## Request compression
        #cmd.addParameter('-z3')
          
        # Determine if a tag is set, on <p4 or on <module
        tag=None
        if module.p4.hasTag():
            tag=module.p4.getTag()
        elif module.hasTag():
            tag=module.getTag()
        
        # Do a p4 sync
        cmd.addParameter('-p',module.p4.getPort())
        cmd.addParameter('-u',module.p4.getUser())
        cmd.addParameter('-P',module.p4.getPassword())
        cmd.addParameter('-c',root)
        cmd.addParameter('sync')
        if nowork:
            cmd.addParameter('-n')
        if tag:
            cmd.addParameter(module.getName()+'/...@',tag,' ')
        else:
            cmd.addParameter(module.getName()+'/...')
        #cmd.addParameter(module.getName())

        return (module.repository, root, cmd)
    
