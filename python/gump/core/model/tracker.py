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
from gump.util.domutils import *

class Tracker(NamedModelObject):
    """A named Tracker"""
    def __init__(self,name,xml,workspace):
        NamedModelObject.__init__(self,name,xml,workspace)
        
        self.resolver=None
            
    def complete(self,workspace):      
        pass
                     
    def check(self,workspace):
        pass
        
    def hasType(self):
        return self.hasDomAttribute('type')
           
    def getType(self):
        return self.getDomAttributeValue('type')
        
    def hasSite(self):
        return self.hasDomAttribute('site')
           
    def getSite(self):
        return self.getDomAttributeValue('site')
        
    def hasUrl(self):
        return self.hasDomAttribute('url')
           
    def getUrl(self):
        return self.getDomAttributeValue('url')
        
    def hasTitle(self): 
        return self.hasDomAttribute('title')
        
    def getTitle(self): 
        return self.getDomAttributeValue('title')
        
    def hasResolver(self): 
        if self.resolver: return True
        return False
        
    def getResolver(self): 
        return self.resolver            
    
    def dump(self, indent=0, output=sys.stdout):
        output.write(getIndent(indent)+'Tracker : ' + self.name + '\n')   
        NamedModelObject.dump(self,indent+1,output)

    
