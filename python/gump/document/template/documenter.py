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
   Text documentation...
   
"""

import socket
import time
import os
import sys
import logging

from gump import log

from gump.utils.work import *

from gump.model.state import *

from gump.document.documenter import Documenter
from gump.document.resolver import *
from gump.document.template.resolver import TemplateResolver

class TemplateDocumenter(Documenter):
    
    def __init__(self,output=sys.stdout, dirBase='.', urlBase='.'):
        Documenter.__init__(self)
        self.output=output
        
        # Hack, ought return a non-hierarchical one
        self.resolver=TemplateResolver(dirBase,urlBase)
        
    def getResolverForRun(self,run):
        return self.resolver
    
    def documentRun(self, run):    
        indent=' '
        
        workspace = run.getWorkspace()
        gumpSet = run.getGumpSet()
        gumpEnv = run.getEnvironment()
        
        #
        #
        #
        quick=run.getOptions().isQuick()
        verbose=run.getOptions().isVerbose()
        debug=run.getOptions().isDebug()
        
        #
        # Where to write this.
        #
        output=self.output
            
        # Pretty sorting...
        sortedModuleList=createOrderedList(gumpSet.getModuleSequence())
        sortedProjectList=createOrderedList(gumpSet.getProjectSequence())
        sortedRepositoryList=createOrderedList(gumpSet.getRepositories())        
        sortedServerList=createOrderedList(workspace.getServers())     
        sortedTrackerList=createOrderedList(workspace.getTrackers())
        
        output.write(indent + "Workspace State : " + workspace.getStateDescription() + "\n")
        output.write(indent + "Workspace Secs : " + str(workspace.getElapsedSecs()) + "\n")
    
        self.documentEnvironment(indent,gumpEnv,debug,verbose)    
    
        output.write(indent + "Modules: " + str(len(workspace.getModules())) + "\n")
    
        self.documentAnnotations(indent,workspace)
        self.documentWork(indent,workspace)
            
        indent += ' '
        for module in sortedModuleList:
            if quick:
                if not gumpSet.inModules(module): continue       
            else:
                if not gumpSet.inModuleSequence(module): continue       
            
            output.write(indent + "Module [" + module.getName() + "] State: " + module.getStateDescription() + "\n")
            output.write(indent + "Projects: " + str(len(module.getProjects())) + "\n")

            self.documentWork(indent,module)
        
            #
            # Document all the annotations
            #
            self.documentAnnotations(indent,module)
                    
            for project in module.getProjects():                
                if quick:
                    if not gumpSet.inProjects(project): continue
                else:
                    if not gumpSet.inProjectSequence(project): continue
            
                self.documentProject(indent,project,debug,verbose)
                
    def documentEnvironment(self, indent, environment, debug, verbose):
        indent += ' '
        output=self.output    
        output.write(indent + "Gump Environment\n")
        
        self.documentAnnotations(indent,environment)
        self.documentWork(indent,environment)
                 
    def documentProject(self, indent, project, debug, verbose):
        indent += ' '
        output=self.output    
        output.write(indent + "Project [" + project.getName() 	\
                    + "] State: " + project.getStateDescription() + "\n")
        
        if verbose:
            self.documentDependenciesList(indent, "Project Dependees",		\
                    project.getDirectDependees(), 1, project)
            
            self.documentDependenciesList(indent, "Project Dependencies",	\
                    project.getDirectDependencies(), 0, project)
        
        self.documentAnnotations(indent,project)
        self.documentWork(indent,project)

    def documentWork(self, indent, workable):
        
        if not workable or not workable.worklist: return
        
        indent += ' '
        output=self.output    
        output.write(indent+"Work [" + str(len(workable.worklist)) \
                + "] [" + str(workable.getElapsedSecs()) + "] secs."  + "\n")
    
        for work in workable.worklist:
            output.write(indent+"Work : " + stateDescription(work.state) + "\n")
            if isinstance(work,CommandWorkItem):
                output.write(indent+"Work Name : " + work.command.name + "\n")
                output.write(indent+"Work Cmd  : " + work.command.formatCommandLine() + "\n")
                if work.command.cwd:
                    output.write(indent+"Work Cwd  : " + work.command.cwd + "\n")
                if work.result.signal:
                    output.write(indent+"Work Signal  : " + `work.result.signal` + "\n")
                output.write(indent+"Work Exit : " + str(work.result.exit_code) + "\n")
        

    def documentAnnotations(self, indent, annotatable): 
        indent += ' '
        output=self.output       
        for note in annotatable.getAnnotations():
            output.write(indent+" - " + str(note) + "\n")
        
        
    def documentDependenciesList(self,indent,title,dependencies,dependees,referencingObject):
      if dependencies:
            indent += ' '    
            output=self.output       
            output.write(indent+title+'\n')            
            indent += ' '    
            for depend in dependencies:
                
                # Project/Owner
                if not dependees:
                    project=depend.getProject()
                else:
                    project=depend.getOwnerProject()
                output.write(indent+project.getName())

                # Type
                type=''
                if depend.isRuntime():
                    if type: type += ' '    
                    type+='Runtime'              
                if depend.isOptional():
                    if type: type += ' '
                    type+='Optional'                
                output.write('   '+type)
                
                # Inheritence
                output.write('   '+depend.getInheritenceDescription())
                
                # Ids
                ids = depend.getIds() or 'All'
                output.write('   '+ids)
                
                # State Icon
                output.write('   '+referencingObject.getStateDescription()+'\n')
                
                self.documentAnnotations(indent,depend)                    
        