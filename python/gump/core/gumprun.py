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

 A gump run (not 'run gump')
 
"""

import os.path
import os
import sys
from fnmatch import fnmatch

from gump import log
from gump.core.config import dir, default, basicConfig
from gump.core.gumpenv import GumpEnvironment


from gump.utils.work import *
from gump.utils import dump, display, getIndent
from gump.utils.note import Annotatable

from gump.model.workspace import Workspace
from gump.model.module import Module
from gump.model.project import Project
from gump.model.depend import  ProjectDependency
from gump.model.state import *
    
###############################################################################
# Functions
###############################################################################

###############################################################################
# Classes
###############################################################################

class GumpSet:
    """ Contains the primary works sets -- to save recalculating and
    passing so many individual things around """
    def __init__(self, workspace, pexpr=None, \
                        projects=None, projectSequence=None, \
                        modules=None, moduleSequence=None, \
                        repositories=None ):
        self.workspace=workspace
        if not self.workspace:
            raise RuntimeError, 'A non-None workspace is require'
            
        self.projectexpression=pexpr
        if not pexpr:
            self.projectexpression='*'
        
        #
        # Requested Projects
        #
        if not projects:
            self.projects=self.getProjectsForProjectExpression(pexpr)
        else:
            self.projects=projects
        
        #
        # Project Build Sequence
        #
        if not projectSequence:
            self.projectSequence=self.getBuildSequenceForProjects(self.projects)
        else:
            self.projectSequence=projectSequence
            
        #
        # Module List
        #
        if not modules:
            self.modules=self.getModulesForProjectList(self.projects)
        else:
            self.modules=modules 
        
        #
        # Module Sequence
        #
        if not moduleSequence:
            self.moduleSequence=self.getModulesForProjectList(self.projectSequence)
        else:
            self.moduleSequence=moduleSequence
        
        #
        # Repository List
        #
        if not repositories:
            self.repositories=self.getRepositoriesForModuleList(self.moduleSequence)
        else:
            self.repositories=repositories
                
        self.validate()
        
    # Validate a decent run
    def validate(self):
        if self.isEmpty():
            raise RuntimeError, 'No projects match [' + self.projectexpression + ']'
        
    # No Projects
    def isEmpty(self):
        return not self.projects
        
    # All Projects
    def isFull(self):
        return self.projectexpression=='all' or self.projectexpression=='*'    
        
#  if not projects:
#    print
#    print "The project expresion '"+expr+"' does not match the workspace's projects."
#    print "Available projects:"
#    for p in Project.list:
#            print "  - " + p
#        return 1        

    def getWorkspace(self):
        return self.workspace
        
    # :TODO: Need ModuleSequence [tree] separate from ModuleList
    def getModules(self):
        return self.modules
            
    def inModules(self,module):
        return module in self.modules
        
    def getModuleSequence(self):
        return self.moduleSequence
            
    def inModuleSequence(self,module):
        return module in self.moduleSequence
        
    def getRepositories(self):
        """ The list of repositories encountered by the module sequence """
        return self.repositories
            
    def inRepositories(self,repository):
        return repository in self.repositories
        
    def getProjects(self):
        return self.projects
              
    def inProjects(self,project):
        return project in self.projects
      
    def getProjectExpression(self):
        return self.projectexpression
        
    def getProjectSequence(self):
        return self.projectSequence    

    def inProjectSequence(self,project):
        return project in self.projectSequence
    
    def getModuleNamesForProjectExpression(self,expr):
        return self.getModuleNamesForProjectList(	\
              self.getProjectsForProjectExpression(expr))
  
    def getModuleNamesForProjectList(self, projects):
        modules=[]
        for module in self.getModulesForProjectList(projects):
            if not module.name in modules: modules.append(module.name)        
        modules.sort()
        return modules

    def getModulesForProjectExpression(self,expr):
        return self.getModulesForProjectList(	\
                self.getProjectsForProjectExpression(expr))
  
    def getModulesForProjectList(self,projects):
        sequence=[]
        for project in projects:
            
            # Some projects are outside of sequence
            if project.inModule():
                # Get the module this project is in
                module = project.getModule()
                if not module in sequence: 
                    sequence.append(module)
                    module.setPosition(len(sequence))

        # Hmm, see if we don't sort ...
        # would be nice to get in same order as
        # projects need 
        # sequence.sort()
        
        return sequence
  
    def getRepositoriesForModuleList(self,modules):
        repositories=[]
        for module in modules:
            
            # Some modules are outside of modules
            if module.hasRepository():
                # Get the module this module is in
                repository = module.getRepository()
                if not repository in repositories: 
                    repositories.append(repository)

        repositories.sort()
        return repositories
  
    def getProjectsForProjectExpression(self,expr):
        """ Return a list of projects matching this expression"""
        projects=[]
        
        if not expr:expr='*'
        
        log.debug('Extract projects for expression ['+`expr`+']')
        for project in self.workspace.getProjects():
            #log.debug('Evaluate ['+project.getName()+']')
            try:
                # does this name match
                for pattern in expr.split(','):
                    try:
                        if pattern=="all": pattern='*'
                        if fnmatch(project.getName(),pattern): break                    
                    except Exception, detail:
                        log.error('Failed to regexp: ' + pattern + '. Details: ' + str(detail))
                        continue
                else:
                    # no match, advance to the next name
                    continue
                log.debug('Matched ['+project.getName()+'] using ['+pattern+']')
                projects.append(project)
            except Exception, detail:
                log.error('Failed to regexp: ' + expr + '. Details: ' + str(detail))
                pass
        projects.sort()
        return projects
  
    def getPackagedProjects(self):
        """ Return a list of projects installed as packages """
        packages=[]
        for project in self.workspace.getProjects():
            if project.isPackaged():                
                packages.append(project)
        return packages
        
    def getBuildSequenceForProjects(self,projects):
        """Determine the build sequence for a given list of projects."""
        todo=[]
        sequence=[]
        for project in projects:
            log.debug('Evaluate Seq for ['+project.getName()+']')                
            self.addToTodoList(project,todo)
            
        while todo:
            # one by one, remove the first ready project and append 
            # it to the sequence
            foundSome=0
            for todoProject in todo:
                if self.isReady(todoProject,todo):
                    todo.remove(todoProject)
                    if not todoProject in sequence:
                        sequence.append(todoProject)
                        todoProject.setPosition(len(sequence))
                        log.debug('#' + `todoProject.getPosition()` + ' -> ' + todoProject.getName())     
                    #else:
                    #    log.debug('Duplicate Result ['+todoProject.getName()+']')    
                    foundSome=1
                    
            if not foundSome:
                # we have a circular dependency, remove all innocent victims
                while todo:
                    for todoProject in todo:
                        if not self.isPrereq(todoProject,todo):
                            todo.remove(todoProject)
                            break
                    else:
                        loop=", ".join([project.getName() for todoProject in todo])
                        raise RuntimeError, "Circular Dependency Loop: " + str(loop)              
        return sequence

                
    #
    # Determine if this project has any unsatisfied dependencies left
    # on the todo list.
    #
    def isReady(self,project,todo):
        for dependency in project.getDirectDependencies():
            if dependency.getProject() in todo: return 0
        return 1

    # add this element and all of its dependencies to a todo list
    def addToTodoList(self,project,todo):
        # Add the project first
        if not project in todo:
            todo.append(project)
            
        for dependency in project.getDirectDependencies():
            # Add all dependencies
            dependProject=dependency.getProject()
            if not dependProject in todo: 
                self.addToTodoList(dependProject,todo)    

    # determine if this project is a prereq of any project on the todo list
    def isPrereq(self,project,todo):
        for todoProject in todo:
            for dependency in todoProject.getDirectDependencies():
                if dependency.getProject().getName()==project.getName(): return 1

    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        i=getIndent(indent)
        output.write(i+'Expression: ' + self.getProjectExpression() + '\n')   
        
        self.dumpList(self.projects,'Projects :',indent+1,output)
        self.dumpList(self.projectSequence,'Project Sequence :',indent+1,output)
        self.dumpList(self.modules,'Modules :',indent+1,output)
        self.dumpList(self.moduleSequence,'Module Sequence :',indent+1,output)
        self.dumpList(self.repositories,'Repositories :',indent+1,output)
            
    def dumpList(self,list,title,indent=0,output=sys.stdout):
        """ Display a single list """  
        i=getIndent(indent)              
        output.write('\n')
        output.write(i + title + '[' + str(len(list)) + '] : \n') 
        idx=0  
        for object in list:
            idx+=1
            output.write(i+str(idx)+': '+object.getName() + '\n')
            
            
class GumpRunOptions:
    """
    
    GumpRunOptions are the 'switches' that dictate the code path
    
    """
    def __init__(self):
        self.optimize=0
 
        self.debug=0	
        self.verbose=0	
        self.cache=1	# Defaults to QUICK
        self.quick=1	# Defaults to CACHE
        self.dated=0	# Defaults to NOT dated.
        self.optimize=0	# Do the least ammount of work...
        self.official=0	# Do a full run (with publishing e-mail)
        
        # Default is Text unless Forrest is in the environment,
        # but can also force text with --text 
        self.text=0        
        
        # If using Forrest, this say leave xdocs, do NOT run
        # the 'forrest' build inlined.
        self.xdocs=0
        
    def isDated(self):
        return self.dated
        
    def setDated(self,dated):
        self.dated=dated
        
    def isOfficial(self):
        return self.official
        
    def setOfficial(self,official):
        self.official=official
        
    def isQuick(self):
        return self.quick
        
    def setQuick(self,quick):
        self.quick=quick
        
    def isText(self):
        return self.text
        
    def setText(self,text):
        self.text=text
        
    def isXDocs(self):
        return self.xdocs
        
    def setXDocs(self,xdocs):
        self.xdocs=xdocs
        
    def isCache(self):
        return self.cache
        
    def setCache(self,cache):
        self.cache=cache
        
    def isDebug(self):
        return self.debug
        
    def setDebug(self,debug):
        self.debug=debug
        
    def isVerbose(self):
        return self.verbose
        
    def setVerbose(self,verbose):
        self.verbose=verbose

    def setResolver(self,resolver):
        self.resolver=resolver        

    def getResolver(self):
        return self.resolver
        
class RunSpecific:
    """
    
        A class that is it specific to an instance of a run
        
    """
    def __init__(self, run):
        self.run	=	run
        
    def getRun(self):
        return self.run


STATE_UNSET=0

class RunEvent(RunSpecific):
    """
        An event to actors (e.g. a project built, a module updated)
    """
            
    def __init__(self, run):
        RunSpecific.__init__(self,run)
        
    def __repr__(self):
        return self.__class__.__name__
        
class InitializeRunEvent(RunEvent): pass
class FinalizeRunEvent(RunEvent): pass
        
class EntityRunEvent(RunEvent):
    """
    
        An event to actors (e.g. a project built, a module updated)
        
    """
            
    def __init__(self, run, entity, realtime=0):
        RunEvent.__init__(self,run)
        
        self.entity=entity
        self.realtime=realtime
            
    def __repr__(self):
        return self.__class__.__name__ + ':' + `self.entity`
        
    def getEntity(self):
        return self.entity 
        
    def isRealtime(self):
        return self.realtime    
        
                
class RunRequest(RunEvent):
    """

    """            
    def __init__(self, run, type):
        RunEvent.__init__(self,run)
        self.type=type
        self.satisfied=0
        
    def getType(self):
        return self.type
        
    def isSatisfied(self):
        return self.satisfied  
        
class EntityRunRequest(RunEvent):
    """

    """
            
    def __init__(self, run, type, entity):
        RunEvent.__init__(self, run, type)
        
        self.entity=entity
        
    def __repr__(self):
        return self.__class__.__name__ + ':' + `self.entity`
        
    def getEntity(self):
        return self.entity 
                
class GumpRun(Workable,Annotatable,Stateful):
    def __init__(self,workspace,expr=None,options=None,env=None):
        
        Workable.__init__(self)
        Annotatable.__init__(self)
        Stateful.__init__(self)
        
        #
        # The workspace being worked upon
        #
        self.workspace=workspace
        
        #
        # The set of modules/projects/repos in use
        #
        self.gumpSet=GumpSet(self.workspace,expr)
        
        #
        # The run options
        #
        if options:
            self.options=options
        else:
            self.options=GumpRunOptions()
        
        #
        # The run options
        #
        if env:
            self.env=env
        else:
            self.env=GumpEnvironment()
        
        #
        # A repository interface...
        #
        from gump.repository.jars import JarRepository
        self.outputsRepository=JarRepository(workspace.jardir)
                  
        # Generate a GUID (or close)
        import md5
        import socket        
        m=md5.new()
        self.guid = `socket.gethostname()`  + ':' + workspace.getName() + ':' + default.datetime
        m.update(self.guid)
        self.hexguid=m.hexdigest().upper()     
        log.debug('Run GUID [' + `self.guid` + '] using [' + `self.hexguid` + ']')    
        
        # Actor Queue
        self.actors=list()

    def getRunGuid(self):
        return self.guid
        
    def getRunHexGuid(self):
        return self.hexguid
        
    def getWorkspace(self):
        return self.workspace

    def setEnvironment(self,env):
        self.env=env

    def getEnvironment(self):
        return self.env

    def getOptions(self):
        return self.options
        
    def getGumpSet(self):
        return self.gumpSet
        
    def getOutputsRepository(self):
        return self.outputsRepository
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        
        i=getIndent(indent)
        #output.write(i+'Expression: ' + self.gumpSet. + '\n')
        output.write(i+'Gump Set:\n')
        self.gumpSet.dump(indent+1,output)
       
    def registerActor(self,actor):
        log.debug('Register Actor : ' + `actor`)
        self.actors.append(actor)
        
    def dispatchEvent(self,event):
        log.debug('Dispatch Event : ' + `event`)        
        for actor in self.actors:
            #log.debug('Dispatch Event : ' + `event` + ' to ' + `actor`)     
            actor._processEvent(event)
        inspectGarbageCollection(`event`)
            
    def dispatchRequest(self,request):
        log.debug('Dispatch Request : ' + `request`)    
        for actor in self.actors:
            log.debug('Dispatch Request : ' + `request` + ' to ' + `actor`)       
            actor._processRequest(request)
        inspectGarbageCollection(`request`)
            
    def generateEvent(self,entity):
        self.dispatchEvent(EntityRunEvent(self, entity))
        
    def generateRequest(self,type):
        self.dispatchRequest(RunRequest(self, type))
                
