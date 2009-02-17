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

"""

"""

import os.path

from gump import log
from gump.core.model.workspace import catFileToFileHolder, \
    EXIT_CODE_FAILED, EXIT_CODE_SUCCESS, FILE_TYPE_LOG, \
    gumpSafeName, logResourceUtilization, \
    STATE_FAILED, STATE_SUCCESS, syncDirectories, REASON_SYNC_FAILED
from gump.core.run.gumprun import RunSpecific
from gump.core.update.cvs import CvsUpdater
from gump.core.update.git import GitUpdater
from gump.core.update.p4 import P4Updater
from gump.core.update.svn import SvnUpdater

def syncModule(module):
    """
        
        Synchronize the storage area with the build area
            
    """
    workspace = module.getWorkspace()
    
    sourcedir = module.getSourceControlStagingDirectory() 
    destdir = module.getWorkingDirectory()
            
    # Perform the sync...
    try:
        # Store changes next to updates log
        changesFile = os.path.abspath(os.path.join(workspace.tmpdir,
                                                   'changes_to_' + \
                                                       gumpSafeName(module.getName()) + \
                                                       '.txt'))
                
        # Perform the operation.
        (actions, modified, cleaned) = syncDirectories(sourcedir, destdir, \
                                                           module, \
                                                           changesFile)

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
                            
                    
    except Exception, details:
        module.changeState(STATE_FAILED, REASON_SYNC_FAILED)
        message = 'Synchronize Failed: ' + str(details)
        module.addError(message)
        log.error(message, exc_info=1)
        
        
    # Might help even with sync failures.
    if os.path.exists(changesFile):
        catFileToFileHolder(module, changesFile, FILE_TYPE_LOG)

    return module.okToPerformWork()

###############################################################################
# Classes
###############################################################################

class GumpUpdater(RunSpecific):
    
    def __init__(self, run):
        RunSpecific.__init__(self, run)
        
        self.updaters = {'cvs' : CvsUpdater(run), 'svn' : SvnUpdater(run),
                         'p4' : P4Updater(run), 'git' : GitUpdater(run)}


    #    ******************************************************************
    #    
    #        THE UPDATE INTERFACE
    #    
    #    ******************************************************************
    def update(self):        
        logResourceUtilization('Before update')
        
        #
        # Doing a full build?
        #
        all = not self.run.getOptions().isQuick()
        
        if all:
            modules = self.run.getGumpSet().getModuleSequence()
        else:
            modules = self.run.getGumpSet().getModules()
        
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
        
        log.debug("Workspace CVS|SVN|P4|GIT Directory: " \
                      + workspace.getSourceControlStagingDirectory())

        # Update all the modules that have repositories
        for module in list: 
            self.updateModule(module)
        
    def updateModule(self, module):
    
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
                
            scmUpdater = self.getScmUpdater(module)
            if scmUpdater:
                ok = scmUpdater.updateModule(module)
            else:
                # :TODO: Now what?
                pass
                   
            # Synchronize the files...
            if ok:
                syncModule(module)     
                    
    
    def getScmUpdater(self, module):
        """
        Finds the correct SCM updater for a given module
        """
        scm = module.getScm()
        if scm:
            return self.updaters.get(scm.getScmType())
        return None

    def preview(self, module):
        """
        
            Preview what ought occur for this
            
        """
        
        scmUpdater = self.getScmUpdater(module)
        if scmUpdater:
            scmUpdater.preview(module)
        else:
            print 'No updater for module: ' + module.getName()            
