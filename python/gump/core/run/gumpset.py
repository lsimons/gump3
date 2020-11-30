#!/usr/bin/python


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

 A gump set (lists and sequences)
 
"""

import os.path
import os
import sys
import fnmatch

from gump import log
from gump.core.config import dir, default, basicConfig
from gump.core.run.gumpenv import GumpEnvironment

import gump.util
import gump.util.work
import gump.util.note

from gump.core.model.workspace import Workspace
from gump.core.model.module import Module
from gump.core.model.project import Project
from gump.core.model.depend import  ProjectDependency
from gump.core.model.state import *
    
###############################################################################
# Init
###############################################################################

SEPARATOR='-------------------------------------------------------------'

###############################################################################
# Classes
###############################################################################

class GumpSet:
    """ 
    
    Contains the primary works sets -- to save recalculating and
    passing so many individual things around.
    
    First, a project expression (list of * or all or wildcarded) is matched 
    against the projects in the workspace, and a like of projects is found.
    That list of projects is expanded to includes all their dependencies, in
    build order, and this is store as the projectSequence.
    
    Second, the project list and projectSequence are converted to the same,
    but for modules. 
    
    As such the gumpset identifies what work needs to be done.
    
    Additionally there are list of what entities have been completed (e.g.
    modules updated, projects built).
    
    """
    def __init__(self, workspace, pexpr=None, \
                        projects=None, projectSequence=None, \
                        modules=None, moduleSequence=None, \
                        repositories=None ):
        self.workspace=workspace
        if not self.workspace:
            raise RuntimeError('A non-None workspace is require')
            
        self.projectexpression=pexpr
        if not pexpr:
            self.projectexpression='*'
        
        # Requested Projects
        if not projects:
            self.projects=self.getProjectsForProjectExpression(pexpr)
        else:
            self.projects=projects
        
        # Project Build Sequence
        if not projectSequence:
            self.projectSequence=self.getBuildSequenceForProjects(self.projects)
        else:
            self.projectSequence=projectSequence
            
        # Module List
        if not modules:
            self.modules=self.getModulesForProjectList(self.projects)
        else:
            self.modules=modules 
        
        # Module Sequence
        if not moduleSequence:
            self.moduleSequence=self.getModulesForProjectList(self.projectSequence)
        else:
            self.moduleSequence=moduleSequence
        
        # Repository List
        if not repositories:
            self.repositories=self.getRepositoriesForModuleList(self.moduleSequence)
        else:
            self.repositories=repositories
            
        self.completedModules=[]
        self.completedProjects=[]
                
        self.validate()
        
    # Validate a decent run
    def validate(self):
        if self.isEmpty():
            raise RuntimeError('No projects match [' + self.projectexpression + ']')
        
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
        
    def getCompletedModules(self):
        return self.completedModules
        
    def setCompletedModule(self,module):
        self.completedModules.append(module)
            
    def inModuleSequence(self,module):
        # Optimization
        if self.isFull(): return True
        # Go look
        return module in self.moduleSequence
        
    def getRepositories(self):
        """ The list of repositories encountered by the module sequence """
        return self.repositories
            
    def inRepositories(self,repository):
        return repository in self.repositories
        
    def getProjects(self):
        return self.projects
              
    def inProjects(self,project):
        """
        Is this project one of the requested projects?
        """
        return project in self.projects
      
    def getProjectExpression(self):
        """
        Return the user provided project list/expression
        """
        return self.projectexpression
        
    def getCompletedProjects(self):
        """
        The projects completed so far
        """
        return self.completedProjects
        
    def setCompletedProject(self,project):
        """
        This project has become completed.
        """
        self.completedProjects.append(project)
        
    def getProjectSequence(self):
        """
        The full (with dependencies) project sequence
        """
        return self.projectSequence    

    def inProjectSequence(self,project):
        """
        Is this project within the main seuqence?
        """
        # Optimization ('all' means, of course...)
        if self.isFull(): return True    
        # Go look...
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
        
        moduleIndex=0
        
        for project in projects:
            
            # Some projects are outside of sequence
            if project.inModule():
                # Get the module this project is in
                module = project.getModule()
                if not module in sequence: 
                    sequence.append(module)
                  
                    # Identify the index within overall sequence
                    moduleIndex+=1
                    module.setPosition(moduleIndex)

        # Identify the size of overall sequence
        moduleTotal=len(sequence)
        for module in sequence:
            module.setTotal(moduleTotal)               
            log.debug('Identify ' + module.getName() + ' at position #' + repr(module.getPosition()))     
          
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
        
        log.debug('Extract projects for expression ['+repr(expr)+']')
        for project in self.workspace.getProjects():
            #log.debug('Evaluate ['+project.getName()+']')
            try:
                # does this name match
                for pattern in expr.split(','):
                    try:
                        if pattern=="all": pattern='*'
                        if fnmatch.fnmatch(project.getName(),pattern): break                    
                    except Exception as detail:
                        log.error('Failed to regexp: ' + pattern + '. Details: ' + str(detail))
                        continue
                else:
                    # no match, advance to the next name
                    continue
                log.debug('Matched ['+project.getName()+'] using ['+pattern+']')
                projects.append(project)
            except Exception as detail:
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
        
        # These are the projects we are going to
        for project in projects:
            log.debug('Evaluate Seq for ['+project.getName()+']')                
            self.addToTodoList(project,todo)
            
        projectIndex=0
            
        while todo:
            # one by one, remove the first ready project and append 
            # it to the sequence
            foundSome=0
            for todoProject in todo:
                if self.isReady(todoProject,todo):
                    todo.remove(todoProject)
                    if not todoProject in sequence:
                        sequence.append(todoProject)
                        projectIndex += 1
                        todoProject.setPosition(projectIndex)
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
                        raise RuntimeError("Circular Dependency Loop: " + str(loop)) 
                        
                        
        # Identify the size of overall sequence
        projectTotal=len(sequence)
        for project in sequence:
            project.setTotal(projectTotal)               
            log.debug('Identify ' + project.getName() + ' at position #' + repr(project.getPosition()))     
                       
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
        i=gump.util.getIndent(indent)
        output.write(i+'Expression: ' + self.getProjectExpression() + '\n')   
        
        self.dumpList(self.projects,'Projects :',indent+1,output)
        self.dumpList(self.projectSequence,'Project Sequence :',indent+1,output)
        self.dumpList(self.modules,'Modules :',indent+1,output)
        self.dumpList(self.moduleSequence,'Module Sequence :',indent+1,output)
        self.dumpList(self.repositories,'Repositories :',indent+1,output)
            
    def dumpList(self,list,title,indent=0,output=sys.stdout):
        """ Display a single list """  
        i=gump.util.getIndent(indent)              
        output.write(SEPARATOR)          
        output.write('\n')
        output.write(i + title + '[' + str(len(list)) + '] : \n') 
        idx=0  
        for object in list:
            idx+=1
            output.write(i+str(idx)+': '+object.getName() + '\n') 
