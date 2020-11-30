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

from time import localtime, strftime, tzname

from gump.util.work import *
from gump.util.tools import *

from gump.core.model.state import *
from gump.core.model.object import NamedModelObject
from gump.core.model.project import Project
from gump.util.note import transferAnnotations, Annotatable
from gump.util.domutils import *


class Profile(NamedModelObject):
    """Gump Profile"""
    def __init__(self,name,dom,workspace):
    	NamedModelObject.__init__(self,name,dom,workspace) 

    def resolve(self):
        
        owner=self.getOwner()
        
        for pdom in self.getDomChildIterator('project'):
            if hasDomAttribute(pdom,'name'):
                name=getDomAttributeValue(pdom,'name')
                
                if owner.hasProject(name):
                    project=owner.getProject(name)
                    project.splice(pdom)             
                    if not self.hasProject(name):
                        self.addProject(project)
                else:
                    project=Project(name,pdom,self)
                    self.addProject(project)
                        	
    def complete(self,workspace):        
        if self.isComplete(): return
        
        # Copy over any XML errors/warnings
        # :TODO:#1: transferAnnotations(self.xml, workspace)  
        
        # :TODO: Until we document the profile
        # add these to workspace transferAnnotations(self.xml, self)  
                
        self.setComplete(1)  
        
    def getObjectForTag(self,tag,dom,name=None):
        return self.getOwner().getObjectForTag(tag,dom,name)
                      
    def addModule(self,module):
        self.getOwner().addModule(module)
                      
    def hasProject(self,name):
        return self.getOwner().hasProject(name)
            
    def getProject(self,name):
        return self.getOwner().getProject(name)
        
    def addProject(self,project):
        self.getOwner().addProject(project)
    
    def dump(self, indent=0, output=sys.stdout):
        output.write(getIndent(indent)+'Profile : ' + self.name + '\n')   
        NamedModelObject.dump(self, indent+1, output)
