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

from gump.update.updater import *
from gump.build.builder import *

from gump.document.text.documenter import TextDocumenter
from gump.document.xdocs.documenter import XDocDocumenter

from gump.timing.keeper import TimeKeeper
from gump.stats.statistician import Statistician
from gump.repository.publisher import RepositoryPublisher
from gump.notify.notifier import Notifier
from gump.results.resulter import Resulter
from gump.syndication.syndicator import Syndicator

###############################################################################
# Classes
###############################################################################


class GumpRunner(RunSpecific):

    def __init__(self, run):
        
        #
        RunSpecific.__init__(self, run)
        
        # Main players (soon we ought make
        # them into actors, like the others).         
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
            workspace.writeXmlToFile(default.merge)
            workspace.setMergeFile(default.merge)
                 
        # :TODO: Put this somewhere else, and/or make it depend upon something...
        workspace.changeState(STATE_SUCCESS)
 
        # Initialize Actors
        self.initializeActors()             
 
        # Let's get going...
        self.run.dispatchEvent(InitializeRunEvent(self.run))
    
    def initializeActors(self):
        
        # Stamp times
        self.run.registerActor(TimeKeeper(self.run))
        
        # Update statistics
        self.run.registerActor(Statistician(self.run))
        
        # Generate results
        self.run.registerActor(Resulter(self.run))            
              
        # Document..
        # Use XDOCS if not overridden...
        #
        documenter=None
        if self.run.getOptions().isText() :
            documenter=TextDocumenter(self.run)
        else:
            documenter=XDocDocumenter(	self.run,	\
                                        self.run.getWorkspace().getBaseDirectory(), \
                                        self.run.getWorkspace().getLogUrl())  
        self.run.getOptions().setResolver(documenter.getResolver())                                                  
        self.run.registerActor(documenter)    
        
        
        # Syndicate once documented
        self.run.registerActor(Syndicator(self.run))   
            
        # Notify last
        if self.run.getOptions().isNotify():
            self.run.registerActor(Notifier(self.run))         
                    
    def finalize(self):            
        # About to shutdown...
        self.run.dispatchEvent(FinalizeRunEvent(self.run))
        
    def getUpdater(self):
        return self.updater
        
    def getBuilder(self):
        return self.builder
        
        
    #
    # Call a method called 'documentRun(run)'
    #
    def perform(self):
        if not hasattr(self,'performRun'):
            raise RuntimeError, \
                    'Class [' + `self.__class__` + '] needs a performRun(self,run)'
        
        if not callable(self.performRun):
            raise RuntimeError, \
                    'Class [' + `self.__class__` + '] needs a callable performRun(self,run)'
        
        log.debug('Perform run using [' + `self` + ']')
        
        self.performRun()

def getRunner(run):
    from gump.runner.demand import OnDemandRunner
    return OnDemandRunner(run)
