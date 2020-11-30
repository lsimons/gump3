#!/usr/bin/env python

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

    Results (XML document containing states/dates/etc.)
    
"""

import socket
import time
import os
import sys
import logging

from gump import log

from gump.core.run.actor import *

from gump.core.model.object import NamedModelObject
from gump.core.model.workspace import *
from gump.core.model.module import *
from gump.core.model.project import *
from gump.actor.results.model import *
from gump.actor.results.loader import *

class Resulter(AbstractRunActor):
    
    def __init__(self,run):        
        AbstractRunActor.__init__(self,run)
        
        self.workspace=run.getWorkspace()
        self.gumpSet=run.getGumpSet()
        
        self.serverResults = {}
        self.serversLoaded = 0
        
        
    def processOtherEvent(self,event):
            
        workspace=self.run.getWorkspace()        
        
        if isinstance(event,InitializeRunEvent):
            
            self.gatherResults()
            
        elif isinstance(event,FinalizeRunEvent):   
            if self.run.getOptions().isResults() :     
                # In the root.
                where=self.run.getOptions().getResolver().getFile(	\
                    self.run.getWorkspace(),'results','.xml',1)    
                # Generate the output...
                self.generateResults(where)
            
    def getServerResultFor(self, server, object):
        results=self.getResultsForAllServers(object)
        if server in results:
            return results[server]
        
    def getResultsForAllServers(self, object):
        results = ResultsSet()
        
        # Load on demand
        if not self.serversLoaded:
            self.loadResultsForServers()
            
        # For all servers, extract any result
        for server in self.workspace.getServers():
            result=None
            if server in self.serverResults:
                serverResults=self.serverResults[server]
                if isinstance(object,NamedModelObject):
                    name=object.getName()
                    if isinstance(object,Workspace):                    
                        result=serverResults
                    elif isinstance(object,Module):                    
                        if serverResults.hasModuleResult(name):
                            result=serverResults.getModuleResult(name)
                    elif isinstance(object,Project):               
                        if serverResults.hasProjectResult(name):    
                            result=serverResults.getProjectResult(name)
                    else:
                        raise RuntimeError('Object [' + object.__class__.__name__ + '] NOT understood for Results')
                
            if result:
                results[server] = result
        
        return results
            
    def loadResultsForServers(self):
                
        if self.serversLoaded: return
            
        for server in self.workspace.getServers():       
            if not server in self.serverResults:
                results=None
                try:
                    if server.isPython():
                        results=self.loadResultsForServer(server)            
                except Exception as details:
                    log.debug('Failed to load results for [' + str(server) + '] : ' \
                            + str(details), exc_info=1)
                            
                if results:
                    log.debug('Loaded results for server [' + str(server) + ']')
                    self.serverResults[server]=results
                    
                    # Probably a hack, but might as well (for now)
                    # just wire the server with iht's latest results
                    server.setResults(results)
                    
        self.serversLoaded=1
            
    def loadResultsForServer(self, server):
        return self.loadResults(server.getResultsUrl())
        
    def loadResults(self, url):    
        loader =  WorkspaceResultLoader()
        log.debug('Load results from URL : [' + url + ']')        
        return loader.loadFromUrl(url)
        
    def gatherResults(self):
        """
        Gather results from servers and set onto workspace/modules/projects
        """
      
        # For all modules...
        for module in self.workspace.getModules():        
                if not self.gumpSet.inModuleSequence(module): continue
                
                #
                # Gather results for this module
                #
                moduleResults = self.getResultsForAllServers(module)

                module.setServerResults(moduleResults)
                
                # Add projects
                for project in module.getProjects():
                    if not self.gumpSet.inProjectSequence(project): continue    
                    
                    #
                    # Gather results for this project
                    #
                    projectResults = self.getResultsForAllServers(project)

                    project.setServerResults(projectResults)
                
    def generateResults(self,where=None):
        """ Generate a results file """
        workspaceResults = self.constructResults()
        
        # If not told where to stick it, contstruct...
        if not where: where=workspaceResults.getName()+'.xml'
        
        workspaceResults.writeXmlToFile(where)

    def constructResults(self):
        """
        Construct result objects from tree of states
        """
        
        if self.workspace.hasResults():
            return self.workspace.getResults()
        
        # Create
        workspaceResults = WorkspaceResult(self.workspace.getName())
        
        # :TODO: Find nicer way to transfer (or just reference)
        workspaceResults.startDateTime=self.run.getStart().getLocal()
        workspaceResults.startDateTimeUtc=self.run.getStart().getUtc()
        workspaceResults.endDateTime=self.run.getEnd().getLocal()
        workspaceResults.endDateTimeUtc=self.run.getEnd().getUtc()
        
        # Take just one string for each.
        (workspaceResults.timezone, dst)=self.run.getEnvironment().getTimezone()
        workspaceResults.timezoneOffset=repr(self.run.getEnvironment().getTimezoneOffset())
    
        # For all modules...
        for module in self.workspace.getModules():        
                if not self.gumpSet.inModuleSequence(module): continue
                
                #
                # Generate results for this module, and
                # add all projects.
                #
                moduleResults = ModuleResult(module.getName())

                # Set attributes:
                # Stats?
                moduleResults.setStatePair(module.getStatePair())
                
                module.setResults(moduleResults)
                
                # Add projects
                for project in module.getProjects():
                    if not self.gumpSet.inProjectSequence(project): continue    
                    
                    #
                    # Add a project
                    #
                    projectResults = ProjectResult(project.getName())
                    
                    # Set attributes:
                    projectResults.setStatePair(project.getStatePair())
                                    
                    # Stash on project
                    project.setResults(projectResults)                
                
                    # Stash on moduleResult
                    moduleResults.setProjectResult(projectResults)
                    
                    # Stash on workspaceResult also
                    workspaceResults.setProjectResult(projectResults)                    
                    
                # Stash moduleResult on workspaceResult
                workspaceResults.setModuleResult(moduleResults)
                
        # Stash on workspace
        self.workspace.setResults(workspaceResults)
                
        return workspaceResults
            
    
def generateResults(run):
    
    # Generate results around this run...
    resulter=Resulter(run)
    
    # In the root.
    where=run.getOptions().getResolver().getFile(run.getWorkspace(),'results','.xml',1)
    
    # Generate the output...
    resulter.generateResults(where)
    
def gatherResults(run):
    
    # Generate results around this run...
    resulter=Resulter(run)
    
    # Generate the output...
    resulter.gatherResults()
    
