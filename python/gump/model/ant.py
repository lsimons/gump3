#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/Attic/ant.py,v 1.8 2003/12/01 17:34:07 ajack Exp $
# $Revision: 1.8 $
# $Date: 2003/12/01 17:34:07 $
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

from time import localtime, strftime, tzname

from gump.utils.work import *
from gump.utils.note import *

from gump.model.state import *
from gump.model.object import *
from gump.model.depend import *
from gump.model.property import *

from gump.model.rawmodel import XMLProperty
       

# represents an <ant/> element
class AntBuilder(ModelObject, PropertyContainer):
    """ An Ant command (within a project)"""
    def __init__(self,xml,project):
    	ModelObject.__init__(self,xml,project)
    	PropertyContainer.__init__(self)
        	    
    	    
        # Store owning project
        self.project=project
    	
    	
    #
    # expand properties - in other words, do everything to complete the
    # entry that does NOT require referencing another project
    #
    def expand(self,project,workspace):
        self.expandProperties(project,workspace)
        self.expandDependencies(project,workspace)
        
    def expandProperties(self,project,workspace):
        #
        # convert Ant property elements which reference a project 
        # into dependencies
        #
        for property in self.xml.property:
            self.expandProperty(property,project,workspace)        
    
    def expandProperty(self,property,project,workspace):
            
        # Check if the property comes from another project
        if not property.project: return      
        # If that project is the one we have in hand
        if property.project==project.getName(): return
        # If the property is not as simple as srcdir
        if property.reference=="srcdir": return
        # If it isn't already a classpath dependency
        if project.hasFullDependencyOnNamedProject(property.project): return
            
        # If there are IDs specified
        ids=''
        if property.id: ids= property.id

        # Runtime?
        runtime=0
        if property.runtime: property.runtime=1
   
        projectName=property.project
        if workspace.hasProject(projectName): 
            # Add a dependency (to bring property)
            dependency=ProjectDependency(project, 	\
                            workspace.getProject(property.project),	\
                            INHERIT_ALL,	\
                            runtime,
                            0,	\
                            ids)
                            
            dependency.addInfo("Property Based Dependency " + `property`)
            
            # :TODOs:
            # if not property.classpath: depend['noclasspath']=Single({})
            
            
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
            property=XMLProperty(depend.__dict__)
            property['reference']='jarpath'
      
            # Name the property...
            if depend.property:
                property['name']=depend.property
            elif not hasattr(property,'name') or not property['name']:
                # :TODO: Reconsider later, but default to project name for now...
                property['name']=depend.project
                project.addWarning('Unnamed property for [' + project.name + '] in depend on: ' + depend.project )
        
            # :TODO: AJ added this, no idea if it is right/needed.
            if depend.id: property['ids']= depend.id
            # Store it
            self.expandProperty(property,project,workspace)      

        
    #
    # complete the definition - it is safe to reference other projects
    # at this point
    #
    def complete(self,project,workspace):
        if self.isComplete(): return
        
        # Import the properties..
    	PropertyContainer.importProperties(self,self.xml)
    	
    	# Compelte them all
        self.completeProperties(workspace)
                
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
 
 
       

# represents an <ant/> element
class Ant(AntBuilder):
    """ An Ant command (within a project)"""
    def __init__(self,xml,project):
    	AntBuilder.__init__(self,xml,project)
      
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
class Maven(AntBuilder):
    """ A Maven command (within a project)"""
    def __init__(self,xml,project):
    	AntBuilder.__init__(self,xml,project)
    	
        # Import the goal
    	self.goal='gump'
    	if xml.goal:
    	    self.goal=xml.goal
            	    
    def getGoal(self):
        return self.goal
    	