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

from gump.update.cvs import CvsUpdater

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

class GumpUpdater(Runnable):
    
    def __init__(self,run):
        Runnable.__init__(self, run)
        
        self.cvs=CvsUpdater(run)
        #self.svn=SvnUpdater(run)
        #self.jars=JarsUpdater(run)

    """
    
        ******************************************************************
        
            THE UPDATE INTERFACE
        
        ******************************************************************
    
    """
    def update(self):        
        logResourceUtilization('Before update')
        
        #
        # Doing a full build?
        #
        all=not self.run.getOptions().isQuick()
        
        if all:
            modules=self.run.getGumpSet().getModuleSequence()
        else:
            modules=self.run.getGumpSet().getModules()
        
        #
        # Checkout from source code repositories
        #
        self.updateModules(modules)
  
        # Return an exit code based off success
        # :TODO: Move onto self.run
        if self.run.getWorkspace().isSuccess():
            result = EXIT_CODE_SUCCESS 
        else: 
            result = EXIT_CODE_FAILED
        
        return result
  
    def updateModules(self, list):    
    
        workspace = self.run.getWorkspace()
        
        # :TODO: A tad bogus to move here
        os.chdir(workspace.getCvsDirectory())
        log.debug("Workspace CVS Directory: " + workspace.getCvsDirectory())

        #log.debug('Modules to update:') 
    
        moduleCount=len(list)
        moduleNo=0     
        # Update all the modules that have CVS repositories
        for module in list: 
            moduleNo+=1
            module.setPosition(moduleNo)
            self.updateModule(module)
        
    def updateModule(self,module):
    
    #        if module.isPackaged(): 
    #            # Not sure we have anything to do right now
    #            # self.performModulePackageProcessing(module)
    #            continue
    #        
    #        if not module.isUpdatable(): continue
            
        log.info('Perform Update on #[' + `module.getPosition()` + \
                        '] : ' + module.getName())

        # Do the appropriate...
        if module.okToPerformWork():                                
            ok = 0
                
            if module.hasCvs():
                ok =self.cvs.updateModule(module)
            #elif module.hasSvn():
            #    ok=self.svn.updateModule(module)
            #elif module.hasJars():
            #    ok=self.jars.updateModule(module)        
            else:
                # :TODO: Now what?
                pass
                   
            # Synchronize the files...
            if ok:
                self.syncModule(module)     
                    
        # Incremental documentation...
        documenter=self.run.getOptions().getDocumenter()        
        if documenter :
            documenter.entity(module,self.run)      

    
    def syncModule(self,module):
        """
            
            Synchronize the storage area with the build area
                
        """
        workspace = module.getWorkspace()
        
        sourcedir = os.path.abspath(	\
                            os.path.join(	workspace.getCvsDirectory(), \
                                                module.name)) # todo allow override
        destdir = module.getSourceDirectory()
                
        # Perform the sync...
        try:
            # Store changes next to updates log
            changesFile = os.path.abspath(	\
                                os.path.join(	\
                                    workspace.tmpdir,	\
                                    'changes_to_'+gumpSafeName(module.getName())+'.txt'))
                    
            # Perform the operation.
            modified=syncDirectories(sourcedir,destdir,module,changesFile)
                    
            # We are good to go...
            module.changeState(STATE_SUCCESS)
                    
            # Were the contents of the repository modified?                                        
            if modified:
                module.setModified(1)                        
                log.info('Update(s) received via CVS/SVN/Jars on #[' \
                                + `module.getPosition()` + \
                                '] of [' + `moduleCount` + ']: ' + module.getName())
                                
                # Log of changes...
                if os.path.exists(changesFile):                               
                    catFileToFileHolder(module, changesFile, FILE_TYPE_LOG) 
                        
        except Exception, details:
            module.changeState(STATE_FAILED,REASON_SYNC_FAILED)
            log.error('Synchronize Failed ' + str(details), exc_info=1)
           
        return module.okToPerformWork()

     
    def getSvnUpdateCommand(self,exists=0):
        
        log.debug("SubVersion Update Module " + self.getName() + \
                       ", Repository Name: " + str(self.repository.getName()))
                                        
        url=self.svn.getRootUrl()
      
        log.debug("SVN URL: [" + url + "] on Repository: " + self.repository.getName())
     
        #
        # Prepare SVN checkout/update command...
        # 
        cmd=Cmd('svn', 'update_'+self.getName(), self.getWorkspace().cvsdir)
       
        #
        # Be 'quiet' (but not silent) unless requested otherwise.
        #
        if 	not self.isDebug() 	\
            and not self.isVerbose() \
            and not self.svn.isDebug()	\
            and not self.svn.isVerbose():    
            cmd.addParameter('--quiet')
                  
        #
        # Allow trace for debug
        #
        # SVN complains about -v|--verbose, don't ask me why
        #
        # if self.isDebug() or  self.svn.isDebug():
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
        if self.svn.hasDir():
            if not self.svn.getDir() == self.getName():
                cmd.addParameter(self.getName())
        

        return (self.repository, url, cmd)
         
     
    def getJarsUpdateCommand(self,exists=0):
        
        log.debug("Jars Update Module " + self.getName() + \
                       ", Repository Name: " + str(self.repository.getName()))

        url=self.jars.getRootUrl()
      
        log.debug("Jars URL: [" + url + "] on Repository: " + self.repository.getName())
     
        #
        # Prepare Jars checkout/update command...
        # 
        cmd=Cmd('update.py',	\
                'update_'+self.getName(),	\
                self.getWorkspace().cvsdir)
    
        cmd.addParameter(url)
          
        #
        # Be 'quiet' (but not silent) unless requested otherwise.
        #
        if 	not self.isDebug() 	\
            and not self.isVerbose() \
            and not self.jars.isDebug()	\
            and not self.jars.isVerbose():    
            cmd.addParameter('-q')

        return (self.repository, url, cmd)
     
