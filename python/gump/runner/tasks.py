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






        # OBSOLETE MODULE LEFT HERE FOR SPARE PARTS













































import os.path
import sys

from gump import log

from gump.run.gumprun import *
from gump.runner.runner import *
from gump.core.config import dir, default, basicConfig

from gump.utils import dump, display, getIndent, logResourceUtilization, \
                            invokeGarbageCollection
from gump.utils.note import Annotatable
from gump.utils.work import *

from gump.utils.tools import *

from gump.model.workspace import *
from gump.model.state import *


from gump.document.text.documenter import TextDocumenter
from gump.document.xdocs.documenter import XDocDocumenter

from gump.results.resulter import gatherResults,generateResults
from gump.syndication.syndicator import syndicate


###############################################################################
# Classes
###############################################################################

class SequentialTaskRunner(GumpRunner):

    def __init__(self,run):
        GumpRunner.__init__(self,run)

    ###########################################
        
    def performUpdate(self):
        return self.perform(GumpTaskList(['update','document']) )
    
    def performBuild(self):
        return self.perform(GumpTaskList(['build','document']) )
    
    def performDebug(self):
        return self.perform(GumpTaskList(['update','build','document']) )
    
    def performIntegrate(self):
        return self.perform(\
                GumpTaskList(['update','build','syndicate','generateResults','document','notify']) )
        
    def performCheck(self):
        return self.perform(GumpTaskList(['check','document']) )
        
    ###########################################
    
        
    # A few proxies...
    
    def build(self): self.builder.build()
    def update(self): self.updater.update()
    
    
        
    """
    
        ******************************************************************
        
           CHECK WORKSPACE
        
        ******************************************************************
    
    """
    
    def checkWorkspace(self):
        """ Check a GumpRun's Projects """
        workspace=self.run.getWorkspace()

        log.debug('--- Building work directories with sources')
        
        # :TODO: Check the workspace?
        
        self.checkModules()
        self.checkProjects()
        
    def checkModules(self):
        # Check all the modules
        list=self.run.getGumpSet().getModuleSequence()
        moduleCount=len(list)
        moduleNo=1
        for module in list:      
        
            log.info(' ------ Check Module: #[' + `moduleNo` + '] of [' + `moduleCount` + '] : ' + module.getName())
                        
            module.changeState(STATE_SUCCESS)        
            moduleNo+=1

    def checkProjects(self):
        list=self.run.getGumpSet().getProjects()
        # Check all projects
                
        projectCount=len(list)
        projectNo=1
        for project in list:  
        
            log.info(' ------ Check Project: #[' + `projectNo` + '] of [' + `projectCount` + '] : ' + project.getName())
            
            # :TODO: Do some actualy checking...
        
            if project.okToPerformWork():        
                # For now, things are going good...
                project.changeState(STATE_SUCCESS)
        
            if not project.okToPerformWork():
                log.warn('Failed to check project #[' + `projectNo` + '] [' + project.getName() + '], state:' \
                        + project.getStateDescription())
            
            projectNo+=1
                                   
    """
    
        ******************************************************************
        
            THE DOCUMENTATION INTERFACE
        
        ******************************************************************
    
    """

    def prepareDocumentation(self):
        
        logResourceUtilization('Before document preparation')
        
        # Prepare for documentation        
        #documenter=self.run.getOptions().getDocumenter()        
        #if documenter :
        #    documenter.prepare(self.run)            
            
    def document(self):
        
        #   
        # Build HTML Result (via Forrest or ...)
        #
        logResourceUtilization('Before document')
        
        #documenter=self.run.getOptions().getDocumenter()        
        #if documenter :
        #    documenter.document(self.run)
                              
                
    """
    
        ******************************************************************
        
           MISC STUFF
        
        ******************************************************************
    
    """
 
        
    def gatherResults(self):
        #
        # Gather results.xml from other servers/workspaces
        #
        logResourceUtilization('Before gather results')
        gatherResults(self.run)
        
    def generateResults(self):
            
        logResourceUtilization('Before generate results')
        # Update Statistics/Results on full self.runs            
        if self.run.getGumpSet().isFull():
            
            #
            # Generate results.xml for this self.run, on this server/workspace
            #
            logResourceUtilization('Before generate results')
            generateResults(self.run)
            
        
    def syndicate(self):
        logResourceUtilization('Before syndicate')
        #
        # Provide a news feed (or few)
        #
        if self.run.getOptions().isOfficial():
            syndicate(self.run)
                
    def loadStatistics(self):   
        """ Load Statistics into the self.run (to get current values) """
        logResourceUtilization('Before load statistics')
        self.processStatistics(1)
         
    def updateStatistics(self):        
        """ Update Statistics into the self.run (to set current values) """
        logResourceUtilization('Before update statistics')
        self.processStatistics(0)
        
    def processStatistics(self,load):
    
        if load:
            log.debug('--- Loading Project Statistics')
        else:
            log.debug('--- Updating Project Statistics')
    
        from gump.stats.statsdb import StatisticsDB
        db=StatisticsDB()   
        
        workspace=self.run.getWorkspace()        
        
        if not load:
            #
            # Update stats (and stash onto projects)
            #
            db.updateStatistics(workspace)
            
            db.sync()
        else:
            #
            # Load stats (and stash onto projects)
            #    
            db.loadStatistics(workspace)            
    
    
    ###########################################
    
    def perform(self,taskList):     
    
        # Bind this list to these methods (on this engine)
        taskList.bind(self)
        
        # Run the method sequence...
        self.performTasks(taskList)      
                
        # Return an exit code based off success
        # :TODO: Move onto run
        if self.run.getWorkspace().isSuccess():
            result = EXIT_CODE_SUCCESS 
        else: 
            result = EXIT_CODE_FAILED
        
        return result  
    
    def performTasks(self,taskList):
        for task in taskList:
            # Perform tasks sequentially
            log.info('Perform task [' + task.getName() + ']')
            task.invoke()
            
            # Seems a nice place to clean up...    
            invokeGarbageCollection('Task ' + task.getName())
   
