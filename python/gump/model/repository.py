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
from gump.model.stats import *

from gump.model.object import NamedModelObject

from gump.utils import getIndent

class Repository(NamedModelObject, Statable):
    """A named repository"""
    def __init__(self,xml,workspace):
    	NamedModelObject.__init__(self,xml.getName(),xml,workspace)
            
        if 'cvs'==xml.type:
            self.type='CVS'
            if hasattr(xml,'root'):
                self.method=xml.root.transfer('method')  
                self.user=xml.root.transfer('user')
                self.password=xml.root.transfer('password')
                self.path=xml.root.transfer('path')
                self.hostname=xml.root.transfer('hostname')
                self.web=xml.transfer('cvsweb') or \
                        xml.transfer('web')
            else:
                raise RuntimeError, 'No XML <root on repository: ' + self.getName()
        elif 'svn'==xml.type:  
            self.type='Subversion'
            if hasattr(xml,'url'):
                self.url=str(xml.url)
            else:
                raise RuntimeError, 'No URL on SVN repository: ' + self.getName()
            self.web=xml.transfer('web')
        elif 'artefact'==xml.type:
            self.type='Java Archives'
            if hasattr(xml,'url'):
                self.url=str(xml.url)
            else:
                raise RuntimeError, 'No URL on Jars repository: ' + self.getName()                
            self.web=xml.transfer('web')
        else:
            raise RuntimeError, 'Invalid Repository Type:' + str(xml.type)         
            
        # Modules referencing this repository
        self.modules=[]
            
    def complete(self,workspace):
        pass
                     
    def check(self,workspace):
        if not self.hasModules():
            self.addWarning('Unused Repository (not referenced by modules)')
    
    def hasModules(self):
        if self.modules: return 1
        return 0
    
    def hasType(self):
        if self.type: return 1
        return 0            
           
    def getType(self):
        return self.type
            
    def getModules(self):
        return self.modules
    
    def dump(self, indent=0, output=sys.stdout):
        output.write(getIndent(indent)+'Repository : ' + self.name + '\n')   
        NamedModelObject.dump(self,indent+1,output)
        
    def hasTitle(self): 
        return hasattr(self.xml,'title') and self.xml.title
        
    def hasHomePage(self): 
        return hasattr(self.xml,'home-page') and getattr(self.xml,'home-page')
        
    def hasWeb(self): 
        return self.web

    def isRedistributable(self):
        # Existence means 'true'
        return hasattr(self.xml,'redistributable')
        
    def hasUser(self): return hasattr(self,'user')
    def hasPassword(self): return hasattr(self,'password')
    def hasPath(self): return hasattr(self,'path')
    def hasMethod(self): return hasattr(self,'method')
    def hasHostname(self): return hasattr(self,'hostname')   
    
    
    def getTitle(self): return self.xml.transfer('title')
    def getHomePage(self): return self.xml.transfer('home-page')
    def getWeb(self): return self.web
    
    def getUser(self): return str(self.user)
    def getPassword(self): return str(self.password)
    def getPath(self): return str(self.path)
    def getMethod(self): return str(self.method)
    def getHostname(self): return str(self.hostname)
    
    def hasUrl(self): return hasattr(self,'url')
    def getUrl(self): return str(self.url)
    
    def addModule(self,module):
        self.modules.append(module)
        
    def getModules(self): 
        return self.modules    
        
class RepositoryStatistics(Statistics):
    """Statistics Holder"""
    def __init__(self,repositoryName):
        Statistics.__init__(self,repositoryName)

    def getKeyBase(self):
        return 'repository:'+ self.name        
        
    