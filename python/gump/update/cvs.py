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

from gump.integration.cvs import *


###############################################################################
# Classes
###############################################################################

class CvsUpdater(RunSpecific):
    
    def __init__(self,run):
        RunSpecific.__init__(self,run)

        #
        # A stash of known logins.
        #
        self.logins=readLogins()

    def updateModule(self,module):
        """
        
            Perform a CVS update on a module
            
        """
            
        log.info('Perform CVS Update on #[' + `module.getPosition()` + \
                        '] : ' + module.getName())
    
        # Did we 'CVS checkout' already?
        exists	=	os.path.exists(module.getSourceControlStagingDirectory())
       
        # Doesn't tell us much...
        #if exists:
        #    self.performStatus(module)
                
        self.performUpdate(module,exists)        
        
        return module.okToPerformWork()      
        
    def performStatus(self,module):
        #  Get the Update Command
        (repository, root, cmd ) = self.getUpdateCommand(module, True, True)
                
        # Provide CVS logins, if not already there
        loginToRepositoryOnDemand(repository,root,self.logins)
               
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
                
        log.debug("CVS Update Module " + module.getName() + \
                       ", Repository Name: " + str(module.repository.getName()))
                                        
        log.debug("CVS Root " + root + " on Repository: " + module.repository.getName())
        
        # Provide CVS logins, if not already there
        loginToRepositoryOnDemand(repository,root,self.logins)
               
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
            
            # We run CVS as -q (quiet) so any output means
            # updates occured...
            if cmdResult.hasOutput():                       
                log.info('Update(s) received via CVS on #[' \
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
            Format a commandline for doing the CVS update            
        """
        
        if nowork and not exists:
            raise RuntimeException('Not coded for this combo.')            
        
        root=module.cvs.getCvsRoot()
    
        # Prepare CVS checkout/update command...
        prefix='update'
        directory=module.getWorkspace().getSourceControlStagingDirectory()
        if exists:     
            directory=module.getSourceControlStagingDirectory()            
        if nowork:
            prefix='status'       
                
        cmd=Cmd(	'cvs',
                    prefix+'_'+module.getName(),
                    directory)
          
        # Be 'quiet' (but not silent) unless requested otherwise.
        if 	not module.isDebug() 	\
            and not module.isVerbose() \
            and not module.cvs.isDebug()	\
            and not module.cvs.isVerbose():    
            cmd.addParameter('-q')
        
        if nowork:
            cmd.addParameter('-n')
          
        # Allow trace for debug
        if module.isDebug():
            cmd.addParameter('-t')
          
        # Request compression
        cmd.addParameter('-z3')
          
        # Set the CVS root
        cmd.addParameter('-d', root)
    
        # Determine if a tag is set, on <cvs or on <module
        tag=None
        if module.cvs.hasTag():
            tag=module.cvs.getTag()
        elif module.hasTag():
            tag=module.getTag()
            
        if exists:

            # Do a cvs update
            cmd.addParameter('update')
            cmd.addParameter('-P')
            cmd.addParameter('-d')
            if tag:
                cmd.addParameter('-r',tag,' ')
            else:
                cmd.addParameter('-A')
            #cmd.addParameter(module.getName())

        else:

            # do a cvs checkout
            cmd.addParameter('checkout')
            cmd.addParameter('-P')
            if tag:
                cmd.addParameter('-r',tag,' ')

            if 	not module.cvs.hasModule() or \
                not module.cvs.getModule() == module.getName(): 
                    cmd.addParameter('-d',module.getName(),' ')
                    
            if module.cvs.hasModule():
                cmd.addParameter(module.cvs.getModule())
            else:
                cmd.addParameter(module.getName())            
        
        return (module.repository, root, cmd)
    