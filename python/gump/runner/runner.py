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



from gump.core.misc import *
from gump.update.updater import *
from gump.build.builder import *


###############################################################################
# Classes
###############################################################################


class GumpRunner(RunSpecific):

    def __init__(self, run):
        
        #
        RunSpecific.__init__(self, run)
        
        # Main players
        self.misc=GumpMiscellaneous(run)            
        self.updater=GumpUpdater(run)
        self.builder=GumpBuilder(run)
        
    def initialize(self,exitOnError=1):
        
        logResourceUtilization('Before initialize')
        
        #
        # Perform start-up logic 
        #
        workspace = self.run.getWorkspace()
                
        #
        #
        #
        if not self.run.getOptions().isQuick():
            logResourceUtilization('Before check environment')            
            self.run.getEnvironment().checkEnvironment(exitOnError)
            logResourceUtilization('After check environment')
        
        #
        # Modify the log location on the fly, if --dated
        #
        if self.run.getOptions().isDated():
            workspace.setDatedDirectories()
        
        #
        # Use Forrest if available & not overridden...
        #
        documenter=None
        if self.run.getEnvironment().noForrest \
            or self.run.getOptions().isText() :
            documenter=TextDocumenter(self.run)
        else:
            documenter=XDocDocumenter(	self.run,	\
                                        workspace.getBaseDirectory(), \
                                        workspace.getLogUrl())                        
        self.run.registerActor(documenter)
                    
        # Check the workspace
        if not workspace.getVersion() >= setting.ws_version:
            message='Workspace version ['+str(workspace.getVersion())+'] below preferred [' + setting.ws_version + ']'
            workspace.addWarning(message)
            log.warn(message)   
            
        # Check the workspace
        if not workspace.getVersion() >= setting.ws_minimum_version:
            message='Workspace version ['+str(workspace.getVersion())+'] below minimum [' + setting.ws_minimum_version + ']'
            workspace.addError(message)
            log.error(message)   
            
        # Write workspace to a 'merge' file        
        if not self.run.getOptions().isQuick():
            workspace.writeXMLToFile(default.merge)
            workspace.setMergeFile(default.merge)
                 
        # :TODO: Put this somewhere else, and/or make it depend upon something...
        workspace.changeState(STATE_SUCCESS)
 
        # Let's get going...
        self.run.dispatchEvent(InitializeRunEvent())
                    
    def finalize(self):            
        # About to shutdown...
        self.run.dispatchEvent(FinalizeRunEvent())
        
    def setEndTime(self):
        logResourceUtilization('Set End Time')
        # :TODO: Move this to run
        self.run.getWorkspace().setEndTime()

def getRunner(run):
    #from gump.runner.tasks import SequentialTaskRunner
    #return SequentialTaskRunner(run)
    
    from gump.runner.demand import OnDemandRunner
    return OnDemandRunner(run)
