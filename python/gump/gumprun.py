#!/usr/bin/python
"""

 A gump run (not 'run gump')
 
"""

import os.path
import os
import sys
from fnmatch import fnmatch

from gump import log
from gump.config import dir, default, basicConfig


from gump.utils.work import *
from gump.utils import dump, display, getIndent
from gump.utils.note import Annotatable

from gump.model.workspace import Workspace
from gump.model.module import Module
from gump.model.project import Project
from gump.model.depend import  ProjectDependency
from gump.model.state import *

from gump.document.text import TextDocumenter

from gump.output.statsdb import *
from gump.output.repository import JarRepository

    
###############################################################################
# Functions
###############################################################################
def isAllProjects(pexpr):
    return pexpr=='all' or pexpr=='*'

###############################################################################
# Classes
###############################################################################

    
# :TODO: Migrate more code to this
class GumpSet:
    """ Contains the primary works sets -- to save recalculating and
    passing so many individual things around """
    def __init__(self, workspace, pexpr=None, \
                        projects=None, sequence=None, \
                        modules=None, repositories=None ):
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
        if not sequence:
            self.sequence=self.getBuildSequenceForProjects(self.projects)
        else:
            self.sequence=sequence
            
        #
        # Module List
        #
        if not modules:
            self.modules=self.getModulesForProjectList(self.sequence)
        else:
            self.modules=modules 
        
        #
        # Repository List
        #
        if not repositories:
            self.repositories=self.getRepositoriesForModuleList(self.modules)
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
        return isAllProjects(self.projectexpression)
        
#  if not projects:
#    print
#    print "The project expresion '"+expr+"' does not match the workspace's projects."
#    print "Available projects:"
#    for p in Project.list:
#            print "  - " + p
#        return 1        

    def getWorkspace(self):
        return self.workspace
        
    def getModules(self):
        return self.modules
            
    def inModules(self,module):
        return module in self.modules
        
    def getRepositories(self):
        return self.repositories
            
    def inRepositories(self,repository):
        return repository in self.repositories
        
    def getProjects(self):
        return self.projects
              
    def inProjects(self,project):
        return project in self.projects
      
    def getProjectExpression(self):
        return self.projectexpression
        
    def getSequence(self):
        return self.sequence    

    def inSequence(self,project):
        return project in self.sequence
    
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
        modules=[]
        for project in projects:
            
            # Some projects are outside of modules
            if project.inModule():
                # Get the module this project is in
                module = project.getModule()
                if not module in modules: 
                    modules.append(module)

        modules.sort()
        return modules
  
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
        result=[]
        for project in projects:
            log.debug('Evaluate Seq for ['+project.getName()+']')                
            self.addToTodoList(project,todo)
            log.debug('TODOS ['+`len(todo)`+']')
            
        while todo:
            # one by one, remove the first ready project and append 
            # it to the result
            foundSome=0
            for todoProject in todo:
                if self.isReady(todoProject,todo):
                    todo.remove(todoProject)
                    if not todoProject in result:
                        log.debug('New Result ['+todoProject.getName()+']')     
                        result.append(todoProject)
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
        return result

                
    #
    # Determine if this project has any unsatisfied dependencies left
    # on the todo list.
    #
    def isReady(self,project,todo):
        for dependency in project.getDependencies():
            if dependency.getProject() in todo: return 0
        return 1

    # add this element and all of it's dependencies to a todo list
    def addToTodoList(self,project,todo):
        # Add the project first
        if not project in todo:
            todo.append(project)
            
        for dependency in project.getDependencies():
            # Add all dependencies
            dependProject=dependency.getProject()
            if not dependProject in todo: 
                self.addToTodoList(dependProject,todo)    

    # determine if this project is a prereq of any project on the todo list
    def isPrereq(self,project,todo):
        for todoProject in todo:
            for dependency in todoProject.getDependencies():
                if dependency.getProject().getName()==project.getName(): return 1

    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        output.write(getIndent(indent)+'GumpSet: ' + self.getProjectExpression() + '\n')        

class GumpRunOptions:
    def __init__(self):
        self.optimize=0
 
        self.debug=0	
        self.verbose=0	
        self.dated=0	# Defaults to NOT dated.
        
        # Default is Text        
        self.documenter=TextDocumenter()

    def setDocumenter(self, documenter):
        self.documenter = documenter
    
    def getDocumenter(self):
        return self.documenter

    # Different Documenter have different resolvers 'cos
    # they may vary the layout
    def getResolver(self):
        return self.getDocumenter().getResolver(self)
        
    def isDated(self):
        return self.dated
        
    def setDated(self,dated):
        self.dated=dated
        
class GumpRun(Workable,Annotatable,Stateful):
    def __init__(self,workspace,expr=None,options=None):
        #
        # The workspace being worked upon
        #
        self.workspace=workspace
        
        #
        # The set of 
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
        # A repository interface...
        #
        self.outputsRepository=JarRepository(workspace.jardir)
        
    def getWorkspace(self):
        return self.workspace

    def getOptions(self):
        return self.options
        
    def getGumpSet(self):
        return self.gumpSet
        
    def getOutputsRepository(self):
        return self.outputsRepository
