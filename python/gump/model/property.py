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
from gump.utils.domutils import *

# represents a <property/> element
class Property(NamedModelObject):
    
    def __init__(self,name,dom,parent):
    	NamedModelObject.__init__(self,name,dom,parent)
    	self.value=self.getDomAttributeValue('value')
    	
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
            
        project=self.getDomAttributeValue('project')   
            
        reference=self.getDomAttributeValue('reference')
        if reference=='home':         
            if not workspace.hasProject(project):
                responsibleParty.addError('Cannot resolve homedir of *unknown* [' + project + ']')                
            else:
                self.setValue(workspace.getProject(project).getHomeDirectory())
                
        elif reference=='srcdir':
            if not workspace.hasProject(project):
                responsibleParty.addError('Cannot resolve srcdir of *unknown* [' + project + ']')
            else:
                self.setValue(workspace.getProject(project).getModule().getWorkingDirectory())
                
        elif reference=='jarpath' or reference=='jar':            
            if self.hasDomAttribute('project'):
                if not workspace.hasProject(project):
                    responsibleParty.addError('Cannot resolve jar/jarpath of *unknown* [' \
                        + project + ']')
                else:
                    targetProject=workspace.getProject(project)
                
                    if self.hasDomAttribute('id'):
                        id=self.getDomAttributeValue('id')
                        # Find the referenced id
                        for jar in targetProject.getJars():
                            if jar.getId()==id:
                                if reference=='jarpath':
                                    self.setValue(jar.getPath())
                                else:
                                    self.setValue(jar.getName())
                                break
                        else:
                            responsibleParty.addError(	\
                               ("jar with id %s was not found in project %s ") % \
                                (id, targetProject.getName()))
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
            else:
                responsibleParty.addError('No project specified.')      
                                
        elif self.hasDomAttribute('path'):
            # If a property on a project..
            if not parent==workspace: 
                relativeProject=None
                # If on a referenced project
                if self.hasDomAttribute('project'):
                    project=self.getDomAttributeValue('project')
                    if not workspace.hasProject(project):
                        responsibleParty.addError('Cannot resolve relative to *unknown* [' + project + '] for ' + \
                                    self.getName())                
                    else:    
                        # Relative to referenced project
                        relativeProject=workspace.getProject(project)
                else:
                    # Relative to this project...
                    relativeProject=responsibleParty
                
                if relativeProject:                        
                    # Path relative to module's srcdir (doesn't work in workspace)     
                    path=self.getDomAttributeValue('path')
                    self.value=os.path.abspath(os.path.join(	\
                            relativeProject.getModule().getWorkingDirectory(),
                            path))
            else:
                responsibleParty.addError('Can\'t have path on property on workspace: ' + \
                    + self.getName())
        
        if not self.value:
            responsibleParty.addError('Unhandled Property: ' + self.getName() + ' on: ' + \
                    str(parent))
            self.value='*Unset*'
                
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
    	
    def __del__(self):
        Ownable.__del__(self)
        
    def addProperty(self,property):
        self.properties[property.getName()]=property
        
    def setProperty(self,name,value):
        self.properties[name]=Property(name,value)
        
    def getPropertyValue(self,name):
        return self.properties[name].getValue()
        
    def getProperty(self,name):
        return self.properties[name]
        
    def hasProperties(self):
        if self.properties: return True
        return False
        
    def getProperties(self):
        return self.properties.values()
            
    def importProperty(self,pdom):        
        property=None
        
        if hasDomAttribute(pdom,'name'):
            name=getDomAttributeValue(pdom,'name')
            property=Property(name,pdom,self.getOwner())
            self.addProperty(property)
        else:
            self.getOwner().addError('Property without name : ' + pdom.toprettyxml())
            
        return property
            
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
        if self.properties: return True
        return False
                
    def getProperties(self):
        return self.properties.getProperties()
        
    def hasSysProperties(self):
        if self.sysproperties: return True
        return False
        
    def getSysProperties(self):
        return self.sysproperties.getProperties()
        
    def importProperty(self,domproperty):
        self.properties.importProperty(domproperty)
        
    def importSysProperty(self,domproperty):
        self.sysproperties.importProperty(domproperty)
                
    def importProperties(self,dom):
        """ Import all properties (from DOM to model). """
        for element in getDomChildIterator(dom,'property'):
            self.importProperty(element)
                
        for element in getDomChildIterator(dom,'sysproperty'):
            self.importSysProperty(element)
                            
    def completeProperties(self,workspace=None):        
        # The only entity not to pass the workspace,
        # can be the workspace itself.
        if not workspace: workspace=self
        # Import normal and system
        self.properties.completeProperties(workspace)
        self.sysproperties.completeProperties(workspace)
                        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the properties """
        self.properties.dump(indent,output)
        self.sysproperties.dump(indent,output)
        
