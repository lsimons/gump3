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
from gump.core.model.stats import *


from gump.core.model.object import NamedModelObject

from gump.util import getIndent

class Server(NamedModelObject):
    """A named server"""
    def __init__(self,name,dom,workspace):
        NamedModelObject.__init__(self,name,dom,workspace)
        
        self.resolver=None

    def __lt__(self, other):
        return self.name < other.name # TEMPORARY
            
    def complete(self,workspace):      
    
        if self.hasType() and self.getType() == 'python':
            if self.hasUrl():
                from gump.actor.document.xdocs.resolver import XDocResolver    
                self.resolver=XDocResolver('bogus', self.getUrl())
                     
    def check(self,workspace):
        pass
        
    def isPython(self):
        return self.hasType() and 'python' == self.getType()
        
    def hasType(self):
        return self.hasDomAttribute('type')
           
    def getType(self):
        return self.getDomAttributeValue('type')
        
    def hasStatus(self):
        return self.hasDomAttribute('status')
           
    def getStatus(self):
        return self.getDomAttributeValue('status')
        
    def isUp(self):
        return self.hasStatus() and 'up' == self.getStatus()
        
    def hasSite(self):
        return self.hasDomChild('site')
           
    def getSite(self):
        return  self.getDomChildValue('site')
        
    def hasUrl(self):
        return self.hasDomChild('url')
           
    def getUrl(self):
        return  self.getDomChildValue('url')
        
    def hasNote(self):
        return self.hasDomChild('note')
           
    def getNote(self):
        return self.getDomChildValue('note')
        
    def hasResultsUrl(self):
        return self.isPython() and self.hasUrl()
        
    def getResultsUrl(self):
        return self.getUrl() + '/results.xml'
        
    def hasResults(self):
        return hasattr(self,'results') and self.results
    
    def setResults(self,results):
        self.results=results
        
    def getResults(self):
        return self.results
        
    def hasTitle(self): 
        return self.hasDomAttribute('title')
        
    def getTitle(self): 
        return self.getDomAttributeValue('title')
        
    def hasResolver(self): 
        if self.resolver: return 1
        return 0
        
    def getResolver(self): 
        return self.resolver            
    
    def dump(self, indent=0, output=sys.stdout):
        output.write(getIndent(indent)+'Server : ' + self.name + '\n')   
        NamedModelObject.dump(self,indent+1,output)

    
