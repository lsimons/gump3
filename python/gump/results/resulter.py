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
    Results (XML document containing states/dates/etc.)
"""

import socket
import time
import os
import sys
import logging

from string import lower, capitalize

from gump import log
from gump.model.object import NamedModelObject
from gump.model.workspace import *
from gump.model.module import *
from gump.model.project import *
from gump.results.model import *
from gump.results.loader import *

class ResultsSet(dict):
    def __init__(self):
        dict.__init__(self)
        
        self.calculated=0
        self.differences=0
        
    def hasDifferences(self):
        if self.calculated: return self.differences
        
        lastPair=None
        for result in self.values():
            statePair=result.getStatePair()            
            if lastPair:
                if lastPair <> statePair:
                    self.differeces=1
            lastPair=statePair
            
        self.calculated=1
        return self.differences
                    
class Resulter:
    
    def __init__(self,run):        
        self.run = run
        self.workspace=run.getWorkspace()
        self.gumpSet=run.getGumpSet()
        
        self.serverResults = {}
        self.serversLoaded = 0
        
    def getServerResultFor(sefl, server, object):
        results=self.getResultsForAllServers(object)
        if results.has_key(server):
            return results[server]
        
    def getResultsForAllServers(self, object):
        results = ResultsSet()
        
        # Load on demand
        if not self.serversLoaded:
            self.loadResultsForServers()
            
        # For all servers, extract any result
        for server in self.workspace.getServers():
            result=None
            if self.serverResults.has_key(server):
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
                except Exception, details:
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
        
        workspaceResults.writeXMLToFile(where)

    def constructResults(self):
        """
        Construct result objects from tree of states
        """
        
        if self.workspace.hasResults():
            return self.workspace.getResults()
        
        # Create
        workspaceResults = WorkspaceResult(self.workspace.getName())
    
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
    