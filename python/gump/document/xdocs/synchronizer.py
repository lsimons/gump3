#!/usr/bin/env python

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
    XDOC generation.
"""

from gump import log

from gump.utils.tools import syncDirectories,copyDirectories,wipeDirectoryTree
from gump.run.gumprun import *
import gump.run.actor
    
class Synchronizer(gump.run.actor.AbstractRunActor):
    
    def __init__(self, run, documenter):
        gump.run.actor.AbstractRunActor.__init__(self, run)            
        self.documenter=documenter
        
    def processOtherEvent(self,event):
            
        workspace=self.run.getWorkspace()        
        
        if isinstance(event,FinalizeRunEvent):
            self.synchronizeRun()
                
    def synchronizeRun(self):
    
        log.debug('--- Synchronize Results')

        # Synchronize xdocs...
        return self.syncXDocs()
        
    def syncXDocs(self):
        
        # The move contents/xdocs from work directory to log
        xdocWorkDir=self.documenter.getXDocWorkDirectory()
        logDirectory=self.documenter.getXDocLogDirectory()
        
        log.info('Synchronize work->log, and clean-up...')
            
        success=True
        try:
            
            if self.run.getOptions().isOfficial():
                # Sync over public pages...
                syncDirectories(xdocWorkDir,logDirectory)
            else:
                # Copy over public pages...
                copyDirectories(xdocWorkDir,logDirectory)
            
            cleanUp=True       
            if cleanUp:
                # Clean-up work area
                wipeDirectoryTree(xdocWorkDir)
            
        except:        
            log.error('--- Failed to work->log sync and/or clean-up', exc_info=1)
            success=False
        
        return success
   