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
    This module contains information on
"""

from gump.core.model.state import *
from gump.core.model.object import NamedModelObject

from gump.util.note import *
from gump.util import getIndent
from gump.util.domutils import *

# Inheritence
INHERIT_NONE=0
INHERIT_OUTPUTS=1
INHERIT_JARS=INHERIT_OUTPUTS # Deprecated term, use outputs not jars
INHERIT_RUNTIME=2
INHERIT_ALL=3
INHERIT_HARD=4

inheritDescriptions = { INHERIT_NONE : "None",
           INHERIT_RUNTIME : "Runtime",
           INHERIT_OUTPUTS : "Outputs",
           INHERIT_ALL : "All",
           INHERIT_HARD : "Hard" }

def inheritDescription(inherit):
    return inheritDescriptions.get(inherit,'Unknown Inherit:' + str(inherit))
           
def importDomDependency(ownerProject,dependProject,ddom,optional):
        
    # Is this a runtime dependency?
    runtime = hasDomAttribute(ddom,'runtime')
        
    # Inheritence
    inherit=INHERIT_NONE
    if hasDomAttribute(ddom,'inherit'):
        inherit=getDomAttributeValue(ddom,'inherit')
        if 'runtime' == inherit:
            inherit=INHERIT_RUNTIME
        elif 'all' == inherit:
            inherit=INHERIT_ALL
        elif 'hard' == inherit:
            inherit=INHERIT_HARD
        elif 'jars' == inherit:
            inherit=INHERIT_JARS
        elif 'none' == inherit:
            inherit=INHERIT_NONE
        
    ids	=	getDomAttributeValue(ddom,'ids','')
    
    annotation = None # 'Expressed Dependency'
    
    noclasspath=hasDomChild(ddom,'noclasspath')    
        
    # Construct the dependency
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
    def __init__(self,owner,project,inherit,
                    runtime=False,optional=False,ids=None,
                    noclasspath=False,annotation=None):
        
        Annotatable.__init__(self)
        
        self.owner=owner
        self.project=project
        self.inherit=inherit
        self.runtime=runtime
        self.optional=optional
        self.ids=ids
        self.noclasspath=noclasspath
        self.valid=True
        if annotation:	self.addInfo(annotation)
        
    def __del__(self):
        
        Annotatable.__init__(self)    
        
        self.owner=None
        self.project=None
        
    def __hash__(self):
        return hash(self.owner) + hash(self.project)
    
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
        
    def hasInheritence(self):
        return self.inherit <> INHERIT_NONE
        
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
                
    def dump(self, indent=0, output=sys.stdout,dependee=False):
        """ Display the contents of this object """
        
        i=getIndent(indent)
        i1=getIndent(indent+1)
        
        if dependee:
            output.write(i+'Depend: ' + self.owner.getName() + '\n')        
        else:
            output.write(i+'Depend: ' + self.project.getName() + '\n')        
        if self.hasInheritence():
            output.write(i1+'Inherit: ' + self.getInheritenceDescription() + '\n')            
        if self.isNoClasspath():
            output.write(i1+'*NoClasspath*\n')
        if self.ids:
            output.write(i1+'Ids: ' + self.ids + '\n')        
        Annotatable.dump(self,indent+1,output)
                
    #
    # Return the outputs for the dependent project (matching
    # ids, etc.)
    #
    def outputs(self):
        """ Return the outputs reference by this dependency """
        result=[]
        
        #
		# Wants the dependency, but not the JARS
		#
        if not self.isNoClasspath():
        
            #
            # IDs is a space separated list of output ids. If specified
            # then return those that are listed, else all.
            #
            ids=(self.ids or '').split(' ')
            try:
                for output in self.project.getOutputs():
                    if (not self.ids) or (output.id in ids): result.append(output)
            except:
                log.warn('Failed to access outputs in dependency project [' + self.project + ']')
        
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
        
    def removeDepend(self, depend):
        # :TODO: Ought remove more (or never delete,
        # but never let 'bad' (i.e. circular) get in
        # here in the first place.
        self.depends.remove(depend)
        
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
        
    def getUniqueProjectDependList(self):
        return self.projectMap.keys()
        
    def getUniqueProjectDependCount(self):
        return len(self.projectMap)
                
    def dump(self, indent=0, output=sys.stdout):
        if self.depends:
            if self.dependees:
                output.write(getIndent(indent)+'Dependees Set\n')    
            else:
                output.write(getIndent(indent)+'Dependancy Set\n')    
                
            for dep in self.depends:
                dep.dump(indent+1,output,self.dependees)
    	
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
        
    def __del__(self):
        self.directDependencies=None
        self.directDependees=None
        self.fullDependencies=None
        self.fullDependees=None
        
    #
    # Dependencies
    # 
    def addDependency(self,depend):
        self.directDependencies.addDepend(depend)
        
    def removeDependency(self,depend):
        self.directDependencies.removeDepend(depend)
            
    def getDirectDependencies(self):
        return self.directDependencies.getDepends()
        
    def getFullDependencies(self):
        if self.fullDependencies: return self.fullDependencies.getDepends()
        
        # Build (once) upon demand
        self.fullDependencies=DependSet()       
        self.resolveDependencies(self.getDirectDependencies())
        
        return self.fullDependencies.getDepends()
        
    def resolveDependencies(self,dependList):
                
        for depend in dependList:
            # Have we travelled here before?
            dependProject=depend.getProject()
            if not self.fullDependencies.containsProject(dependProject):
                    
                # Add it now, so we don't cover this again
                self.fullDependencies.addDepend(depend)
                
                self.resolveDependencies(dependProject.getDirectDependencies())
            else:
                self.fullDependencies.addDepend(depend)    
                                            
    def getDependencyCount(self):
        return self.directDependencies.getUniqueProjectDependCount()
        
    def getFullDependencyCount(self):
        self.getFullDependencies()
        return self.fullDependencies.getUniqueProjectDependCount()       
        
    def getFullDependencyProjectList(self):
        self.getFullDependencies()
        return self.fullDependencies.getUniqueProjectDependList()        
        
    #
    # Depth
    #
    def getDependencyDepth(self):
        if self.depth: return self.depth
        maxDepth=0
        for depend in self.directDependencies.getDepends():
            dependencyDepth=depend.getProject().getDependencyDepth() + 1
            if maxDepth < dependencyDepth:
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
        
        # Build (once) upon demand
        self.fullDependees=DependSet(True)
        self.resolveDependees(self.getDirectDependees())             
        return self.fullDependees.getDepends()
        
    def resolveDependees(self,dependList):
                
        for depend in dependList:
            # Have we travelled here before?
            dependProject=depend.getOwnerProject()
            if not self.fullDependees.containsProject(dependProject):
                    
                # Add it now, so we don't cover this again
                self.fullDependees.addDepend(depend)
                
                self.resolveDependees(dependProject.getDirectDependees())
            else:
                self.fullDependees.addDepend(depend)   
                
    def getDependeeCount(self):
        return self.directDependees.getUniqueProjectDependCount()
                
    def getFullDependeeCount(self):
        self.getFullDependees()
        return self.fullDependees.getUniqueProjectDependCount()
        
    def getFullDependeeProjectList(self):
        self.getFullDependees()
        return self.fullDependees.getUniqueProjectDependList()        
        
    def buildDependenciesMap(self,workspace):        
        
        # Provide backwards links  [Note: ant|maven might have added some
        # dependencies, so this is done here & not just with the direct
        # xml depend/option elements]
        for dependency in self.getDirectDependencies():
            dependProject=dependency.getProject()
            # Add us as a dependee on them
            dependProject.addDependee(dependency)  
                                                        
    # 
    def hasFullDependencyOnNamedProject(self,name):
        for dependency in self.getDirectDependencies():
            if dependency.getProject().getName()==name	\
                and not dependency.isNoClasspath() :
                return True            
        return False

    # determine if this project is a prereq of any project on the todo list
    def hasDirectDependencyOn(self,project):
        """ Does this project exist as a dependency """    
        for dependency in self.getDirectDependencies():
            if dependency.getProject()==project: return True
    
    # determine if this project is a prereq of any project on the todo sequence
    def hasDependencyOn(self,project):
        """ Does this project exist as any dependency """        
        for dependency in self.getFullDependencies():
            if dependency.getProject()==project: return True
    
    def hasDirectDependee(self,project):
        """ Does this project exist as a direct dependee """    
        for dependee in self.getDirectDependees():
            if dependee.getOwnerProject()==project: return True
            
    def hasDependee(self,project):
        """ Does this project exist as any dependee """
        for dependee in self.getFullDependees():
            if dependee.getOwnerProject()==project: return True
                        
    def dump(self, indent=0, output=sys.stdout):
        self.directDependencies.dump(indent+1,output)
        self.directDependees.dump(indent+1,output)
