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

from gump.net.cvs import *

from gump.document.text.documenter import TextDocumenter
from gump.document.forrest.documenter import ForrestDocumenter

from gump.output.statsdb import *
from gump.output.repository import JarRepository
from gump.output.notify import Notifier
from gump.results.resulter import gatherResults,generateResults
from gump.syndication.syndicator import syndicate


###############################################################################
# Classes
###############################################################################

class GumpMiscellaneous(Runnable):
    
    def __init__(self,run):
        Runnable.__init__(self,run)

    def preprocess(self,exitOnError=1):
        
        logResourceUtilization('Before preprocess')
        
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
        # Use forrest if available & not overridden...
        #
        if self.run.getEnvironment().noForrest \
            or self.run.getOptions().isText() :
            documenter=TextDocumenter()
        else:
            documenter=ForrestDocumenter(workspace.getBaseDirectory(), \
                                         workspace.getLogUrl())                        
        self.run.getOptions().setDocumenter(documenter)
                    
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

                    
    def setEndTime(self):
        
        logResourceUtilization('Set End Time')
        # :TODO: Move this to run
        self.run.getWorkspace().setEndTime()
        
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
        documenter=self.run.getOptions().getDocumenter()        
        if documenter :
            documenter.prepare(self.run)            
            
    def document(self):
        
        #   
        # Build HTML Result (via Forrest or ...)
        #
        logResourceUtilization('Before document')
        documenter=self.run.getOptions().getDocumenter()        
        if documenter :
            documenter.document(self.run)
                              
                
    """
    
        ******************************************************************
        
           MISC STUFF
        
        ******************************************************************
    
    """
    
    def notify(self):
                
        #
        # Only an 'all' is an official build, for them:
        #
        #	Send Naggin E-mails
        #
        if self.run.getOptions().isOfficial() \
            and self.run.getGumpSet().isFull() \
            and self.run.getWorkspace().isNotify():
  
            log.info('Notify about failures... ')            
            
            #
            # Notify about failures
            #
            logResourceUtilization('Before notify')
            notify(self.run)  
        
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
        self.processStatistics(self.run,1)
         
    def updateStatistics(self):        
        """ Update Statistics into the self.run (to set current values) """
        logResourceUtilization('Before update statistics')
        self.processStatistics(self.run,0)
        
    def processStatistics(self,load):
    
        if load:
            log.debug('--- Loading Project Statistics')
        else:
            log.debug('--- Updating Project Statistics')
    
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
