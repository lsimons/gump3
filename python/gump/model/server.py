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

class Server(NamedModelObject):
    """A named server"""
    def __init__(self,xml,workspace):
    	NamedModelObject.__init__(self,xml.getName(),xml,workspace)
        
        self.resolver=None
            
    def complete(self,workspace):      
    
        if self.hasType() and self.getType() == 'python':
            if self.hasUrl():
                from gump.document.resolver import Resolver    
                self.resolver=Resolver('bogus', self.getUrl())
                     
    def check(self,workspace):
        pass
        
    def isPython(self):
        return self.hasType() and 'python' == self.getType()
        
    def hasType(self):
        return hasattr(self.xml,'type') and self.xml.type
           
    def getType(self):
        return str(self.xml.type)
        
    def hasSite(self):
        return hasattr(self.xml,'site') and self.xml.site
           
    def getSite(self):
        return str(self.xml.site)
        
    def hasUrl(self):
        return hasattr(self.xml,'url') and self.xml.url
           
    def getUrl(self):
        return str(self.xml.url)
        
    def hasResultsUrl(self):
        return self.hasUrl()
        
    def getResultsUrl(self):
        return self.getUrl() + '/results.xml'
        
    def hasResults(self):
        return hasattr(self,'results') and self.results
    
    def setResults(self,results):
        self.results=results
        
    def getResults(self):
        return self.results
        
    def hasTitle(self): 
        return hasattr(self.xml,'title') and self.xml.title
        
    def getTitle(self): 
        return str(self.xml.title)
        
    def hasResolver(self): 
        if self.resolver: return 1
        return 0
        
    def getResolver(self): 
        return self.resolver            
    
    def dump(self, indent=0, output=sys.stdout):
        output.write(getIndent(indent)+'Server : ' + self.name + '\n')   
        NamedModelObject.dump(self,indent+1,output)

    