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
    This module contains information on
"""

from gump.model.state import *
from gump.model.object import NamedModelObject
from gump.model.property import Property


from gump.utils.note import *
from gump.utils import getIndent

# Inheritence
INHERIT_NONE=0
INHERIT_JARS=1
INHERIT_RUNTIME=2
INHERIT_ALL=3
INHERIT_HARD=4

inheritDescriptions = { INHERIT_NONE : "None",
           INHERIT_RUNTIME : "Runtime",
           INHERIT_JARS : "Jars",
           INHERIT_ALL : "All",
           INHERIT_HARD : "Hard" }

def inheritDescription(inherit):
    return inheritDescriptions.get(inherit,'Unknown Inherit:' + str(inherit))
           
def importXMLDependency(ownerProject,dependProject,xmldepend,optional):
        
    # Is this a runtime dependency?
    runtime = 0
    if xmldepend.runtime: runtime = 1
        
    # Inheritence
    inherit=INHERIT_NONE
    if 'runtime' == xmldepend.inherit:
        inherit=INHERIT_RUNTIME
    elif 'all' == xmldepend.inherit:
        inherit=INHERIT_ALL
    elif 'hard' == xmldepend.inherit:
        inherit=INHERIT_HARD
    elif 'jars' == xmldepend.inherit:
        inherit=INHERIT_JARS
    elif 'none' == xmldepend.inherit:
        inherit=INHERIT_NONE
        
    ids	=	xmldepend.ids
    
    annotation = None # 'Expressed Dependency'
        
    noclasspath=0
    if xmldepend.noclasspath: 	noclasspath=1
        
    #
    # Construct the dependency
    #        
    return ProjectDependency( 	ownerProject,	\
                                dependProject,	\
                                inherit,		\
                                runtime,		\
                                optional,		\
                                ids,			\
                                noclasspath,	\
                                annotation)                

class ProjectDependency(Annotatable):
    """ A dependency from one project to another """
    def __init__(self,owner,project,inherit,runtime=0,optional=0,ids=None,noclasspath=0,annotation=None):
        
        Annotatable.__init__(self)
        
        self.owner=owner
        self.project=project
        self.inherit=inherit
        self.runtime=runtime
        self.optional=optional
        self.ids=ids
        self.noclasspath=noclasspath
        if annotation:	self.addInfo(annotation)
    
    # :TODO: if same ids, but different order/spacing, it ought match..
    def __eq__(self,other):
        return 	self.project == other.project \
                and self.owner == other.owner	\
                and self.inherit == other.inherit \
                and self.runtime == other.runtime \
                and self.ids == other.ids
                
    def __cmp__(self,other):
        c = cmp(self.project,other.project)
        if not c: c = cmp(self.owner,other.owner)
        if not c: c = cmp(self.inherit,other.inherit)
        if not c: c = cmp(self.runtime,other.runtime)
        if not c: c = cmp(self.ids,other.ids)
        return c
    
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        output='[owner=\''+ self.owner.getName() + '\'] '
        
        output+='project=\''+ self.project.getName() + '\''
        
        if self.inherit:
            output+=' inherit=\'' + self.getInheritenceDescription() + '\''
        if self.runtime:
            output+=' runtime=\'' + str(self.runtime) + '\''
        if self.ids:
            output+=' ids=\'' + self.ids + '\''
        return output
            
    def getOwnerProject(self):
        return self.owner
        
    def getProject(self):
        return self.project
        
    def getInheritence(self):
        return self.inherit
        
    def getInheritenceDescription(self):
        return inheritDescription(self.inherit)
    
    def isRuntime(self):
        return self.runtime
    
    def isOptional(self):
        return self.optional
        
    def getIds(self):
        return self.ids
        
    def isNoClasspath(self):
    	return self.noclasspath
                
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        output.write(getIndent(indent)+'Depend: ' + self.project.getName() + '\n')
        output.write(getIndent(indent)+'Inherit: ' + self.getInheritenceDescription() + '\n')
        if self.isNoClasspath():
            output.write(getIndent(indent)+'*NoClasspath*\n')
        if self.ids:
            output.write(getIndent(indent)+'Ids: ' + self.ids + '\n')
        
        Annotatable.dump(self,indent+1,output)
                
    #
    # Return the jars for the dependent project (matching
    # ids, etc.)
    #
    def jars(self):
        """ Return the jars reference by this dependency """
        result=[]
        
        #
		# Wants the dependency, but not the JARS
		#
        if not self.isNoClasspath():
        
            #
            # IDs is a space separated list of jar ids. If specified
            # then return those that are listed, else all.
            #
            ids=(self.ids or '').split(' ')
            try:
                for jar in self.project.getJars():
                    if (not self.ids) or (jar.id in ids): result.append(jar)
            except:
                log.warn('Failed to access jars in dependency project [' + self.project + ']')
        
        return result
        
class DependSet:

    """ A dependency set contains dependencies between projects """
    def __init__(self, dependees=0):
        
        # A list of all dependencies
        self.depends=[]
        
        # A map by project -> dependencies list
        self.projectMap={}
        
        # Which direction (to or from?)
        self.dependees=dependees
        
    def addDepend(self, depend):
        
        #
        # Add to total list
        #
        self.depends.append(depend)
                
        #
        # Store depend by project key
        #
        dependProject=None
        if self.dependees:
            dependProject = depend.getOwnerProject()
        else:
            dependProject = depend.getProject()        
        if not self.projectMap.has_key(dependProject):
            self.projectMap[dependProject] = []            
        self.projectMap[dependProject] = depend
        
    def containsDepend(self, depend):
        return (depend in self.depends)
        
    def containsProject(self, project):
        return self.projectMap.has_key(project)
        
    def getDepends(self):
        return self.depends
        
    def getUniqueProjectDependCount(self):
        return len(self.projectMap)
    	
class DependencyPath(list):
    """ 'Path' of dependencies between two points """
    def __init__(self,startDependable,endDependable):
        self.startDependable=startDependable
        self.endDependable=endDependable
        
    def appendDepend(self,depend):
        self.append(depend)
        self.endDependable=depend.getProject()
    
    def getStart(self):
        return self.startDependable
        
    def getEnd(self):
        return self.endDependable
                
class Dependable:
    
    """ Direct and Full Dependencies """
    def __init__(self):
        
        # Direct & Full Dependencies
        self.directDependencies=DependSet()
        self.fullDependencies=None
        
        # Direct & Full Dependees
        self.directDependees=DependSet(1)
        self.fullDependees=None
    
        # Depth
        self.depth=0
        self.totalDepth=0
        
    #
    # Dependencies
    # 
    def addDependency(self,depend):
        self.directDependencies.addDepend(depend)
            
    def getDirectDependencies(self):
        return self.directDependencies.getDepends()
        
    def getFullDependencies(self):
        if self.fullDependencies: return self.fullDependencies.getDepends()
        
        #
        # Build (once) upon demand
        #
        self.fullDependencies=DependSet()
        for depend in self.directDependencies.getDepends():
            if not self.fullDependencies.containsDepend(depend):
                
                dependProject=depend.getProject()
                if not self.fullDependencies.containsProject(dependProject):
                    # Get Sub Dependencies
                    for subdepend in dependProject.getFullDependencies():
                        if not self.fullDependencies.containsDepend(subdepend):   
                            self.fullDependencies.addDepend(subdepend)
                                            
                self.fullDependencies.addDepend(depend)
            
        return self.fullDependencies.getDepends()
                
    def getDependencyCount(self):
        return self.directDependencies.getUniqueProjectDependCount()
        
    def getFullDependencyCount(self):
        self.getFullDependencies()
        return self.fullDependencies.getUniqueProjectDependCount()

    #
    # Depth
    #
    def getDependencyDepth(self):
        if self.depth: return self.depth
        maxDepth=1
        for depend in self.directDependencies.getDepends():
            dependencyDepth=depend.getProject().getDependencyDepth() + 1
            if maxDepth <  dependencyDepth:
                maxDepth=dependencyDepth
        self.depth=maxDepth
        return self.depth
     
     
    #
    # Total Depth
    #
    def getTotalDependencyDepth(self):
        if self.totalDepth: return self.totalDepth
        for depend in self.directDependencies.getDepends():
            dependencyDepth=depend.getProject().getDependencyDepth()
            self.totalDepth += dependencyDepth
        return self.totalDepth
        
    #
    # Dependency Paths (None, One, Some).
    #
    def getDependencyPaths(self, dependable):
        paths=[]
        # Determine the dependency paths for any direct dependencies
        # and 
        for depend in self.directDependencies.getDepends():
            directDependable=depend.getProject()
            if dependable == directDependable:
                # A simple path
                path=DependencyPath(dependable,self)
                path.appendDepend(depend)
                paths.append(path)
            elif directDependable.hasDependencyOn(dependable):
                # Clearly there is at least one path (maybe more)
                for path in directDependable.getDependencyPaths(dependable):
                    # Take each path and extend it...
                    path.appendDepend(depend)
                    paths.append(path)
        return paths
        
    #
    # Dependees
    # 
    def addDependee(self,depend):
        self.directDependees.addDepend(depend)
            
    def getDirectDependees(self):
        return self.directDependees.getDepends()
        
        
    def getFullDependees(self):
        if self.fullDependees: return self.fullDependees.getDepends()
        
        #
        # Build (once) upon demand
        #
        self.fullDependees=DependSet(1)
        
        for depend in self.directDependees.getDepends():
            if not self.fullDependees.containsDepend(depend):  
                
                dependProject=depend.getOwnerProject()
                if not self.fullDependees.containsProject(dependProject):
                    # Get Sub Dependees
                    for subdepend in dependProject.getFullDependees():
                        if not self.fullDependees.containsDepend(subdepend):    
                            self.fullDependees.addDepend(subdepend)
                                              
                self.fullDependees.addDepend(depend)
            
        return self.fullDependees.getDepends()
        
    def getDependeeCount(self):
        return self.directDependees.getUniqueProjectDependCount()
                
    def getFullDependeeCount(self):
        self.getFullDependees()
        return self.fullDependees.getUniqueProjectDependCount()
        
        
    def buildDependenciesMap(self,workspace):        
        
        #
        # Provide backwards links  [Note: ant|maven might have added some
        # dependencies, so this is done here * not just with the direct
        # xml depend/option elements]
        #
        for dependency in self.getDirectDependencies():
            dependProject=dependency.getProject()
            # Add us as a dependee on them
            dependProject.addDependee(dependency)  
                                                        
    # 
    def hasFullDependencyOnNamedProject(self,name):
        for dependency in self.getDirectDependencies():
            if dependency.getProject().getName()==name	\
                and not dependency.isNoClasspath() :
                return 1            
        return 0

    # determine if this project is a prereq of any project on the todo list
    def hasDirectDependencyOn(self,project):
        """ Does this project exist as a dependency """    
        for dependency in self.getDirectDependencies():
            if dependency.getProject()==project: return 1
    
    # determine if this project is a prereq of any project on the todo sequence
    def hasDependencyOn(self,project):
        """ Does this project exist as any dependency """        
        for dependency in self.getFullDependencies():
            if dependency.getProject()==project: return 1
    
    def hasDirectDependee(self,project):
        """ Does this project exist as a direct dependee """    
        for dependee in self.getDirectDependees():
            if dependee.getOwnerProject()==project: return 1
            
    def hasDependee(self,project):
        """ Does this project exist as any dependee """
        for dependee in self.getFullDependees():
            if dependee.getOwnerProject()==project: return 1