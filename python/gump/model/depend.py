#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/depend.py,v 1.14 2004/03/09 21:19:09 ajack Exp $
# $Revision: 1.14 $
# $Date: 2004/03/09 21:19:09 $
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
    This module contains information on
"""

from gump.model.state import *
from gump.model.object import NamedModelObject
from gump.model.property import Property, PropertyContainer


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
    
    #
    # Construct the dependency
    #        
    return ProjectDependency( 	ownerProject,	\
                                dependProject,	\
                                inherit,		\
                                runtime,		\
                                optional,		\
                                ids,			\
                                annotation)
                

class ProjectDependency(Annotatable):
    """ A dependency from one project to another """
    def __init__(self,owner,project,inherit,runtime=0,optional=0,ids=None,annotation=None):
        
        Annotatable.__init__(self)
        
        self.owner=owner
        self.project=project
        self.inherit=inherit
        self.runtime=runtime
        self.optional=optional
        self.ids=ids
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
                
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        output.write(getIndent(indent)+'Depend: ' + self.project.getName() + '\n')
        output.write(getIndent(indent)+'Inherit: ' + self.getInheritenceDescription() + '\n')
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
                
class Dependable:
    
    """ Direct and Full Dependencies """
    def __init__(self):
        
        # Direct & Full Dependencies
        self.directDependencies=DependSet()
        self.fullDependencies=None
        
        # Direct & Full Dependees
        self.directDependees=DependSet(1)
        self.fullDependees=None
        
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
                self.fullDependencies.addDepend(depend)
                
                dependProject=depend.getProject()
                if not self.fullDependencies.containsProject(dependProject):
                    # Get Sub Dependencies
                    for subdepend in dependProject.getFullDependencies():
                        if not self.fullDependencies.containsDepend(subdepend):
                            self.fullDependencies.addDepend(depend)
            
        return self.fullDependencies.getDepends()
                
    def getDependencyCount(self):
        return self.directDependencies.getUniqueProjectDependCount()
        
    def getFullDependencyCount(self):
        self.getFullDependencies()
        return self.fullDependencies.getUniqueProjectDependCount()
                
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
                self.fullDependees.addDepend(depend)
                
                dependProject=depend.getOwnerProject()
                if not self.fullDependees.containsProject(dependProject):
                    # Get Sub Dependees
                    for subdepend in dependProject.getFullDependees():
                        if not self.fullDependees.containsDepend(subdepend):    
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
            if dependency.getProject().getName()==name: 
                return 1
                
# :TODO:        
#           and not dependency.noclasspath: return 1
#:TODO: noclasspath????

        return 0

    # determine if this project is a prereq of any project on the todo list
    def hasDirectDependencyOn(self,project):
        for dependency in self.dependencies:
            if dependency.getProject()==project: return 1
    
    def hasDirectDependee(self,project):
        for dependee in self.dependees:
            if dependee.getOwnerProject()==project: return 1
            
    def hasDependee(self,project):
        for dependee in self.getFullDependees():
            if dependee.getOwnerProject()==project: return 1
                    
        
        
        