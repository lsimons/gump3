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

from gump.run.gumprun import *
from gump.core.config import dir, default, basicConfig

from gump.update.cvs import CvsUpdater
from gump.update.svn import SvnUpdater
from gump.update.artifact import ArtifactUpdater

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

class GumpUpdater(RunSpecific):
    
    def __init__(self,run):
        RunSpecific.__init__(self, run)
        
        self.cvs=CvsUpdater(run)
        self.svn=SvnUpdater(run)
        self.artifact=ArtifactUpdater(run)

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
        
        log.debug("Workspace CVS|SVN|artifacts Directory: " + workspace.getSourceControlStagingDirectory())

        # Update all the modules that have CVS repositories
        for module in list: 
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
                ok=self.cvs.updateModule(module)
            elif module.hasSvn():
                ok=self.svn.updateModule(module)
            elif module.hasArtifacts():
                ok=self.artifact.updateModule(module)        
            else:
                # :TODO: Now what?
                pass
                   
            # Synchronize the files...
            if ok:
                self.syncModule(module)     
                    

    
    def syncModule(self,module):
        """
            
            Synchronize the storage area with the build area
                
        """
        workspace = module.getWorkspace()
        
        sourcedir = module.getSourceControlStagingDirectory() 
        destdir = module.getWorkingDirectory()
                
        # Perform the sync...
        try:
            # Store changes next to updates log
            changesFile = os.path.abspath(	\
                                os.path.join(	\
                                    workspace.tmpdir,	\
                                    'changes_to_'+gumpSafeName(module.getName())+'.txt'))
                    
            # Perform the operation.
            (actions,modified,cleaned)=syncDirectories(sourcedir,destdir,module,changesFile)
                    
            # We are good to go...
            module.changeState(STATE_SUCCESS)
                    
            # Were the contents of the repository modified?                                        
            if modified: 
            
                #
                # Use 'incoming changes' to note that the module
                # was modified.
                #
                module.setModified(True)                                  
                log.info('Update(s) received via on #[' \
                                + `module.getPosition()` + \
                                '] : ' + module.getName())
                                
                if os.path.exists(changesFile):  
                    catFileToFileHolder(module, changesFile, FILE_TYPE_LOG) 
                        
        except Exception, details:
            module.changeState(STATE_FAILED,REASON_SYNC_FAILED)
            log.error('Synchronize Failed ' + str(details), exc_info=1)
           
        return module.okToPerformWork()
        

    def preview(self,module):
        """
        
            Preview what ought occur for this
            
        """
        
        if module.hasCvs():
            ok=self.cvs.preview(module)
        elif module.hasSvn():
            ok=self.svn.preview(module)
        elif module.hasArtifacts():
            ok=self.artifact.preview(module)        
        else:
            print 'No updater for module: ' + module.getName()            