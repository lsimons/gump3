#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/results/resulter.py,v 1.4 2004/02/28 00:24:32 ajack Exp $
# $Revision: 1.4 $
# $Date: 2004/02/28 00:24:32 $
#
# ====================================================================
#
# The Apache Software License, Version 1.1
#
# Copyright (c) 2003 The Apache Software Foundation.  All rights
# reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. The end-user documentation included with the redistribution, if
#    any, must include the following acknowlegement:
#       "This product includes software developed by the
#        Apache Software Foundation (http://www.apache.org/)."
#    Alternately, this acknowlegement may appear in the software itself,
#    if and wherever such third-party acknowlegements normally appear.
#
# 4. The names "The Jakarta Project", "Alexandria", and "Apache Software
#    Foundation" must not be used to endorse or promote products derived
#    from this software without prior written permission. For written
#    permission, please contact apache@apache.org.
#
# 5. Products derived from this software may not be called "Apache"
#    nor may "Apache" appear in their names without prior written
#    permission of the Apache Group.
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
# ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# ====================================================================
#
# This software consists of voluntary contributions made by many
# individuals on behalf of the Apache Software Foundation.  For more
# information on the Apache Software Foundation, please see
# <http://www.apache.org/>.

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
from gump.results.model import *
from gump.results.loader import *

class Resulter:
    
    def __init__(self,run):        
        self.run = run
        self.workspace=run.getWorkspace()
        self.gumpSet=run.getGumpSet()
        
        self.serverResults = {}
        
    #def getResultsFor(self, object):
    #    for server in self.workspace.getServers():
            
        
    def loadResultsForServers(self):
        for server in self.workspace.getServers():       
            if not server in self.serverResults:
                results=None
                try:
                    results=loadResultsForServer(server)            
                except:
                    pass
                if results:
                    self.serverResults(server, results)
            
    def loadResultsForServer(self, server):
        return loadResults(server.getUrl() + '/results.xml')
        
    def loadResults(self, url):    
        loader =  WorkspaceResultLoader()        
        return loader.loadFromUrl(url)
        
    def generateResults(self,where=None):
        """
        Generate a results file
        """
        
        workspaceResults = self.constructResults()
        
        # If not told where to stick it, contstruct...
        if not where: where=workspaceResults.getName()+'.xml'
        
        workspaceResults.writeXMLToFile(where)
        
    def constructResults(self):
        """
        Generate a results file
        """
        # Create
        workspaceResults = WorkspaceResult(self.workspace.getName())
    
        # For all modules...
        for module in self.workspace.getModules():        
                if not self.gumpSet.inModules(module): continue
                
                #
                # Generate results for this module, and
                # add all projects.
                #
                moduleResults = ModuleResult(module.getName())

                # Set attributes:
                # Stats?
                moduleResults.setStatePair(module.getStatePair())
                
                # Add projects
                for project in module.getProjects():
                    if not self.gumpSet.inSequence(project): continue    
                    
                    #
                    # Add a project
                    #
                    projectResults = ProjectResult(project.getName())
                    
                    # Set attributes:
                    projectResults.setStatePair(project.getStatePair())
                
                    # Stash on moduleResult
                    moduleResults.setProjectResult(projectResults)
                    
                    # Stash on workspaceResult also
                    workspaceResults.setProjectResult(projectResults)                    
                    
                # Stash moduleResult on workspaceResult
                workspaceResults.setModuleResult(moduleResults)
                
        return workspaceResults
            
    
def generateResults(run):
    
    # Generate results around this run...
    resulter=Resulter(run)
    
    where=run.getOptions().getResolver().getFile(run.getWorkspace(),'results','.xml',1)
    
    # Generate the output...
    resulter.generateResults(where)
    