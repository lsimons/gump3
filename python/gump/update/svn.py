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

###############################################################################
# Classes
###############################################################################

class SvnUpdater(RunSpecific):
    
    def __init__(self,run):
        RunSpecific.__init__(self,run)


    def updateModule(self,module):
        """        
            Perform a SVN update on a module            
        """
            
        log.info('Perform SVN Update on #[' + `module.getPosition()` + \
                        '] : ' + module.getName())
    
        # Did we 'SVN checkout' already?
        exists	=	os.path.exists(module.getSourceControlStagingDirectory())
       
        if exists:
            self.performStatus(module)
            
        self.performUpdate(module, exists)
        
        return module.okToPerformWork()   
              
    def performStatus(self,module):
        """
        
            Do a status comparison between our copy and server
            
        """
        
        #  Get the Update Command
        cmd = self.getStatusCommand(module)
                               
        # Execute the command and capture results        
        cmdResult=execute(cmd, module.getWorkspace().tmpdir)
    
        # Store this as work
        work=CommandWorkItem(WORK_TYPE_UPDATE,cmd,cmdResult)
        module.performedWork(work)  
      
        # Update Context w/ Results  
        if not cmdResult.state==CMD_STATE_SUCCESS:              
            message='Failed to \'status --show-updates\' module: ' + module.getName()
            module.addWarning(message)
            log.error(message)               

    def getStatusCommand(self,module):
        """
        
            Build the 'svn status --show-updates --non-interative' command
            
        """
        log.debug("SubVersion Module Status : " + module.getName() + \
                       ", Repository Name: " + str(module.repository.getName()))
                                        
        url=module.svn.getRootUrl()
      
        log.debug("SVN URL: [" + url + "] on Repository: " + module.repository.getName())
     
        #
        # Prepare SVN checkout/update command...
        # 
        cmd=Cmd('svn', 'status_'+module.getName(), 
                module.getSourceControlStagingDirectory())
       
        #
        # Be 'quiet' (but not silent) unless requested otherwise.
        #
        if 	not module.isDebug() 	\
            and not module.isVerbose() \
            and not module.svn.isDebug()	\
            and not module.svn.isVerbose():    
            cmd.addParameter('--quiet')
                  
        #
        # Allow trace for debug
        #
        # SVN complains about -v|--verbose, don't ask me why
        #
        # if module.isDebug() or  module.svn.isDebug():
        #    cmd.addParameter('--verbose')
            
        # do an SVN status --show-updates
        cmd.addParameter('status')
        cmd.addParameter('--show-updates')
       
        #
        # Request non-interactive
        #
        cmd.addParameter('--non-interactive')

        return cmd

                                                  
    def performUpdate(self,module,exists):
        """
        
            Check-out or Update  from SVN
            
        """
        
        #  Get the Update Command
        (repository, url, cmd ) = self.getUpdateCommand(module, exists)
                
               
        # Execute the command and capture results        
        cmdResult=execute(cmd, module.getWorkspace().tmpdir)
      
        #
        # Store this as work, on both the module and (cloned) on the repo
        #
        work=CommandWorkItem(WORK_TYPE_UPDATE,cmd,cmdResult)
        module.performedWork(work)  
        repository.performedWork(work.clone())
      
        # Update Context w/ Results  
        if not cmdResult.state==CMD_STATE_SUCCESS:              
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
                         
                             
    def preview(self,module):
        (repository, url, command ) = self.getUpdateCommand(module,0)
        command.dump()
            
        (repository, url, command ) = self.getStatusCommand(module)
        command.dump()
            
        (repository, url, command ) = self.getUpdateCommand(module,1)
        command.dump()                                            
    
    def getUpdateCommand(self,module,exists=0):
        """
            Build the appropriate SVN command for checkout/update
        """
        
        log.debug("SubVersion  Module Update : " + module.getName() + \
                       ", Repository Name: " + str(module.repository.getName()))
                                        
        url=module.svn.getRootUrl()
      
        log.debug("SVN URL: [" + url + "] on Repository: " + module.repository.getName())
     
        #
        # Prepare SVN checkout/update command...
        # 
        cmd=Cmd('svn', 'update_'+module.getName(), 
                    module.getWorkspace().getSourceControlStagingDirectory())
       
        #
        # Be 'quiet' (but not silent) unless requested otherwise.
        #
        if 	not module.isDebug() 	\
            and not module.isVerbose() \
            and not module.svn.isDebug()	\
            and not module.svn.isVerbose():    
            cmd.addParameter('--quiet')
                  
        #
        # Allow trace for debug
        #
        # SVN complains about -v|--verbose, don't ask me why
        #
        # if module.isDebug() or  module.svn.isDebug():
        #    cmd.addParameter('--verbose')
            
        if exists:
            # do an SVN update
            cmd.addParameter('update')
        else:
            # do an SVN checkout
            cmd.addParameter('checkout')
            cmd.addParameter(url)
       
        #
        # Request non-interactive
        #
        cmd.addParameter('--non-interactive')

        #
        # If module name != SVN directory, tell SVN to put it into
        # a directory named after our module
        #
        if module.svn.hasDir():
            if not module.svn.getDir() == module.getName():
                cmd.addParameter(module.getName())
        

        return (module.repository, url, cmd)
         
    