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

from gump.model.object import *

# represents a <property/> element
class Property(NamedModelObject):
    
    def __init__(self,xml,parent):
    	NamedModelObject.__init__(self,xml.getName(),xml,parent)
    	self.value=xml.value or '*Unset*' 
    	
    def setValue(self,value):
        self.value = value
        
    def getValue(self):
        return self.value
        
    # provide default elements when not defined in xml
    def complete(self,parent,workspace):
        if self.isComplete(): return
    
        # Properties are either on the workspace, or on
        # an ant entry within a project. Pick workspace or project.
        responsibleParty=workspace
        if not parent==workspace: responsibleParty=parent.getOwner()
        
        if self.xml.reference=='home':
            if not workspace.hasProject(self.xml.project):
                responsibleParty.addError('Cannot resolve homedir of *unknown* [' + self.xml.project + ']')                
            else:
                self.setValue(workspace.getProject(self.xml.project).getHomeDirectory())
                
        elif self.xml.reference=='srcdir':
            if not workspace.hasProject(self.xml.project):
                responsibleParty.addError('Cannot resolve srcdir of *unknown* [' + self.xml.project + ']')
            else:
                self.setValue(workspace.getProject(self.xml.project).getModule().getSourceDirectory())
                
        elif self.xml.reference=='jarpath' or self.xml.reference=='jar':            
            if not workspace.hasProject(self.xml.project):
                responsibleParty.addError('Cannot resolve jar/jarpath of *unknown* [' \
                        + self.xml.project + ']')
            else:
                targetProject=workspace.getProject(self.xml.project)
                
                if self.xml.id:
                    # Find the referenced id
                    for jar in targetProject.getJars():
                        if jar.getId()==self.xml.id:
                            if self.xml.reference=='jarpath':
                                self.setValue(jar.getPath())
                            else:
                                self.setValue(jar.getName())
                            break
                    else:
                        responsibleParty.addError(	\
                            ("jar with id %s was not found in project %s ") % \
                            (self.xml.id, targetProject.getName()))
                elif targetProject.getJarCount()==1:
                    # There is only one, so pick it...
                    self.setValue(targetProject.getJars()[0].getPath())
                elif  targetProject.getJarCount()>1:
                    # Don't know which....
                    responsibleParty.addError(	\
                        ("Multiple jars defined by project %s; " + \
                        "an id attribute is required to select the one you want") % \
                          (targetProject.getName()))
                else:
                    responsibleParty.addError(	\
                        ('Project %s defines no jars as output') % \
                        (targetProject.getName()))      
                                
        elif self.xml.path:
            #
            # If a property on a project..
            #
            if not parent==workspace: 
                relativeProject=None
                # If on a referenced project
                if self.xml.project:
                    if not workspace.hasProject(self.xml.project):
                        responsibleParty.addError('Cannot resolve relative to *unknown* [' + self.xml.project + '] for ' + \
                                    self.getName())                
                    else:    
                        # Relative to referenced project
                        relativeProject=workspace.getProject(self.xml.project)
                else:
                    # Relative to this project...
                    relativeProject=responsibleParty
                
                if relativeProject:                        
                    #
                    # Path relative to module's srcdir (doesn't work in workspace)
                    #        
                    self.value=os.path.abspath(os.path.join(	\
                            relativeProject.getModule().getSourceDirectory(),	\
                            self.xml.path))
            else:
                responsibleParty.addError('Can\'t have path on property on workspace: ' + \
                    + self.getName())
        
        if not hasattr(self,'value'):
            responsibleParty.addError('Unhandled Property: ' + self.getName() + ' on: ' + \
                    str(parent))
                
        self.setComplete(1)
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the property """
        output.write(getIndent(indent)+'Property: ' + self.getName() + ' ' + self.getValue()+ '\n')

class PropertySet(Ownable):
    """ Can hold properties """
    def __init__(self,owner,properties=None):
        
        Ownable.__init__(self,owner)
        
        self.properties={}
        
        # Any starting properties..
        if properties:
            self.properties=properties
            
    def addProperty(self,property):
        self.properties[property.getName()]=property
        
    def setProperty(self,name,value):
        self.properties[name]=Property(name,value)
        
    def getPropertyValue(self,name):
        return self.properties[name].getValue()
        
    def getProperty(self,name):
        return self.properties[name]
        
    def hasProperties(self):
        if self.properties: return 1
        return 0
        
    def getProperties(self):
        return self.properties.values()
            
    def importProperty(self,xmlproperty):
        self.addProperty(Property(xmlproperty,self.getOwner()))
            
    def completeProperties(self,workspace):   
        for property in self.getProperties(): 
            property.complete(self.getOwner(),workspace)
                        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the properties """
        for property in self.getProperties():
            property.dump(indent+1,output)

class PropertyContainer:
    """ 
    
    Can hold two sets of properties (normal and system)
    
    Note: This depends upon the 'user' class being 'Ownable'.
    
    """
    def __init__(self,properties=None,sysproperties=None):
        self.properties=PropertySet(self, properties)    
        self.sysproperties=PropertySet(self, sysproperties)
        
    def hasProperties(self):
        if self.properties: return 1
        return 0
                
    def getProperties(self):
        return self.properties.getProperties()
        
    def hasSysProperties(self):
        if self.sysproperties: return 1
        return 0                
        
    def getSysProperties(self):
        return self.sysproperties.getProperties()
        
    def importProperty(self,xmlproperty):
        self.properties.importProperty(xmlproperty)
        
    def importSysProperty(self,xmlproperty):
        self.sysproperties.importProperty(xmlproperty)
                
    def importProperties(self,xml):
        """ Import all properties (from XML to model). """
        if xml.property:
            for xmlproperty in xml.property:
                self.importProperty(xmlproperty)
                
        if xml.sysproperty:
            for xmlproperty in xml.sysproperty:
                self.importSysProperty(xmlproperty)
            
    def completeProperties(self,workspace=None):        
        # The only entity not to pass the workspace,
        # can be the workspace itself.
        if not workspace: workspace=self
        # Import normal and system
        self.properties.completeProperties(workspace)
        self.sysproperties.completeProperties(workspace)
                        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the properties """
        self.properties.dump(self,indent,output)
        self.sysproperties.dump(self,indent,output)
        
