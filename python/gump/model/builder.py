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
        if hasattr(self.xml,'property'):
            for property in self.xml.property:
                self.expandProperty(property,project,workspace)       
                self.importProperty(property)
            
        #
        # convert Ant sysproperty elements which reference a project 
        # into dependencies
        #
        if hasattr(self.xml,'sysproperty'):
            for sysproperty in self.xml.sysproperty:
                self.expandProperty(sysproperty,project,workspace)       
                self.importSysProperty(sysproperty)
    
    #
    # Expands
    #
    def expandProperty(self,property,project,workspace):
        
        # :TODO: Cleanup this Workaround
        if not hasattr(property,'name') and hasattr(property,'project'):
            property.name=property.project
            
        # Check if the property comes from another project
        if not hasattr(property,'project'): return      
        # If that project is the one we have in hand
        if property.project==project.getName(): return
        # If the property is not as simple as srcdir
        if hasattr(property,'reference') and property.reference=="srcdir": return
        # If it isn't already a classpath dependency
        if project.hasFullDependencyOnNamedProject(property.project): 
            self.addDebug('Dependency on ' + property.project + \
                    ' exists, no need to add for property ' + \
                        property.name + '.')
            return
            
        # If there are IDs specified
        ids=''
        if hasattr(property,'id'): ids= property.id

        # Runtime?
        runtime=hasattr(property,'runtime')
   
        projectName=property.project
        if workspace.hasProject(projectName): 
                        
            # A Property
            noclasspath=not hasattr(property,'classpath')
                        
            # Add a dependency (to bring property)
            dependency=ProjectDependency(project, 	\
                            workspace.getProject(property.project),	\
                            INHERIT_NONE,	\
                            runtime,
                            False,	\
                            ids,
                            noclasspath,
                            'Property Dependency for ' + property.name)
            
            
            # Add depend to project...
            # :TODO: Convert to ModelObject
            project.addDependency(dependency)
        else:
            project.addError('No such project [' + projectName + '] for property')

    def expandDependencies(self,project,workspace):
        if hasattr(self.xml,'depend'):
            #
            # convert all depend elements into property elements, and
            # move the dependency onto the project
            #
            for depend in self.xml.depend:
                # Generate the property
                xmlproperty=XMLProperty(depend.__dict__)
                xmlproperty['reference']='jarpath'
      
                # Name the xmlproperty...
                if hasattr(depend,'property'):
                    xmlproperty['name']=depend.property
                elif not hasattr(xmlproperty,'name') or not xmlproperty['name']:
                    # :TODO: Reconsider later, but default to project name for now...
                    xmlproperty['name']=depend.project
                    project.addWarning('Unnamed property for [' + project.name + '] in depend on: ' + depend.project )
        
                # :TODO: AJ added this, no idea if it is right/needed.
                if hasattr(depend,'id'): xmlproperty['ids']= depend.id
            
                # <depend wants the classpath
                #:TODO:#2: I really hate this code, we ought not be trying
                # to acess the delegate. We do so to check for existence
                # but w/o value.
                if not hasattr(depend,'noclasspath') or None==depend.noclasspath.delegate:
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
        if self.xml.hasAttr('basedir'):
            self.basedir = os.path.abspath(	\
                                os.path.join(	\
                                    self.project.getModule().getWorkingDirectory() or dir.base,	\
                                    self.xml.transfer('basedir')))
        else:
            self.basedir=self.project.getBaseDirectory()
                
        self.setComplete(1)
                    
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        i=getIndent(indent)
        output.write(i+self.__class__.__name__+'\n')
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
        self.target=xml.transfer('target','gump')    	    
        # Import the buildfile
        self.buildfile=xml.transfer('buildfile','build.xml')
    	    
    def getTarget(self):
        return self.target
        
    def getBuildFile(self):
        return self.buildfile
                
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        Builder.dump(self)
        i=getIndent(indent)
        output.write(i+'Ant: ' + self.getTarget() + '\n')
        output.write(i+'BuildFile: ' + self.getBuildFile() + '\n')

# represents an <maven/> element
class Maven(Builder):
    """ A Maven command (within a project)"""
    def __init__(self,xml,project):
    	Builder.__init__(self,xml,project)
    	
        # Import the goal
        self.goal=xml.transfer('goal','jar')
            	    
    def getGoal(self):
        return self.goal
    	
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        Builder.dump(self)
        i=getIndent(indent)
        output.write(i+'Maven: ' + self.getGoal() + '\n')

# represents an <script/> element
class Script(Builder):
    """ A script command (within a project)"""
    def __init__(self,xml,project):
    	Builder.__init__(self,xml,project)
    	
    	# Get the name
    	self.name=xml.transfer('name','unset')
    	
    def getName(self):
        return self.name
    
    	