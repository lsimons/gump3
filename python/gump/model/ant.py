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

from time import localtime, strftime, tzname

from gump.utils.work import *
from gump.utils.note import *

from gump.model.state import *
from gump.model.object import *
from gump.model.depend import *
from gump.model.property import *

from gump.model.rawmodel import XMLProperty
       

# represents an <ant/> element
class Builder(ModelObject, PropertyContainer):
    """ An Ant command (within a project)"""
    def __init__(self,xml,project):
    	ModelObject.__init__(self,xml,project)
    	PropertyContainer.__init__(self)
            
        self.basedir=None
        
        # Store owning project
        self.project=project
    	
    #
    # expand properties - in other words, do everything to complete the
    # entry that does NOT require referencing another project
    #
    def expand(self,project,workspace):
        self.expandDependencies(project,workspace)
        self.expandProperties(project,workspace)
        
    def expandProperties(self,project,workspace):
        #
        # convert Ant property elements which reference a project 
        # into dependencies
        #
        for property in self.xml.property:
            self.expandProperty(property,project,workspace)       
            self.importProperty(property)
            
        #
        # convert Ant sysproperty elements which reference a project 
        # into dependencies
        #
        for sysproperty in self.xml.sysproperty:
            self.expandProperty(sysproperty,project,workspace)       
            self.importSysProperty(sysproperty)
    
    #
    # Expands
    #
    def expandProperty(self,property,project,workspace):
        
        # :TODO: Cleanup this Workaround
        if not property.name and property.project:
            property.name=property.project
            
        # Check if the property comes from another project
        if not property.project: return      
        # If that project is the one we have in hand
        if property.project==project.getName(): return
        # If the property is not as simple as srcdir
        if property.reference=="srcdir": return
        # If it isn't already a classpath dependency
        if project.hasFullDependencyOnNamedProject(property.project): 
            self.addInfo('Dependency on ' + property.project + \
                    ' exists, no need to add for property ' + \
                        property.name + '.')
            return
            
        # If there are IDs specified
        ids=''
        if property.id: ids= property.id

        # Runtime?
        runtime=0
        if property.runtime: property.runtime=1
   
        projectName=property.project
        if workspace.hasProject(projectName): 
                        
            # A Property
            noclasspath=1
            if property.classpath:
               noclasspath=0
                        
            # Add a dependency (to bring property)
            dependency=ProjectDependency(project, 	\
                            workspace.getProject(property.project),	\
                            INHERIT_NONE,	\
                            runtime,
                            0,	\
                            ids,
                            noclasspath,
                            'Property Dependency for ' + property.name)
            
            
            # Add depend to project...
            # :TODO: Convert to ModelObject
            project.addDependency(dependency)
        else:
            project.addError('No such project [' + projectName + '] for property')

    def expandDependencies(self,project,workspace):
        #
        # convert all depend elements into property elements, and
        # move the dependency onto the project
        #
        for depend in self.xml.depend:
            # Generate the property
            xmlproperty=XMLProperty(depend.__dict__)
            xmlproperty['reference']='jarpath'
      
            # Name the xmlproperty...
            if depend.property:
                xmlproperty['name']=depend.property
            elif not hasattr(xmlproperty,'name') or not xmlproperty['name']:
                # :TODO: Reconsider later, but default to project name for now...
                xmlproperty['name']=depend.project
                project.addWarning('Unnamed property for [' + project.name + '] in depend on: ' + depend.project )
        
            # :TODO: AJ added this, no idea if it is right/needed.
            if depend.id: xmlproperty['ids']= depend.id
            
            # <depend wants the classpath
            if not xmlproperty.noclasspath:
                xmlproperty['classpath']='add'
            
            # Store it
            self.expandProperty(xmlproperty,project,workspace)            
            self.importProperty(xmlproperty) 

        
    #
    # complete the definition - it is safe to reference other projects
    # at this point
    #
    def complete(self,project,workspace):
        if self.isComplete(): return
        
        # Import the properties..
    	PropertyContainer.importProperties(self,self.xml)
    	
    	# Complete them all
        self.completeProperties(workspace)
        
        # Set this up...
        self.basedir = os.path.abspath(os.path.join(	\
                                self.project.getModule().getSourceDirectory() or dir.base,	\
                                self.xml.basedir or self.project.getBaseDirectory() or ''))
                
        self.setComplete(1)
                    
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        i=getIndent(indent)
        output.write(i+'Ant: ' + self.getTarget() + '\n')
        output.write(i+'BuildFile: ' + self.getBuildFile() + '\n')
        
        #
        # Dump all properties...
        #
        PropertyContainer.dump(self,indent+1,output)

    def getBaseDirectory(self):
         return self.basedir
       

# represents an <ant/> element
class Ant(Builder):
    """ An Ant command (within a project)"""
    def __init__(self,xml,project):
    	Builder.__init__(self,xml,project)
      
        # Import the target
    	self.target='gump'
    	if xml.target:
    	    self.target=xml.target
    	    
        # Import the buildfile
    	self.buildfile='build.xml'
    	if xml.buildfile:
    	    self.buildfile=xml.buildfile    
    	    
    def getTarget(self):
        return self.target
        
    def getBuildFile(self):
        return self.buildfile

# represents an <maven/> element
class Maven(Builder):
    """ A Maven command (within a project)"""
    def __init__(self,xml,project):
    	Builder.__init__(self,xml,project)
    	
        # Import the goal
    	self.goal='jar'
    	if xml.goal:
    	    self.goal=xml.goal
            	    
    def getGoal(self):
        return self.goal
    	

# represents an <script/> element
class Script(Builder):
    """ A script command (within a project)"""
    def __init__(self,xml,project):
    	Builder.__init__(self,xml,project)
    
    	