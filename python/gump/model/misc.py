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

    This module contains miscellaneous model objects
    
"""

from time import localtime, strftime, tzname
from string import lower, capitalize

#from gump.utils.note import *
#from gump.utils.work import *
#from gump.utils.file import *
#from gump.utils.owner import *
from gump.utils.domutils import *
from gump.model.object import *

class Positioned:
    def __init__(self): 
        self.posn=-1
        self.total=-1
        
    def setPosition(self,posn):
        self.posn=posn
        
    def setTotal(self,total):
        self.total=total

    def getPosition(self):
        if -1 != self.total:
            return (self.posn,self.total)
        if -1 != self.posn:
            return self.posn
            
    def getPositionIndex(self):
        return self.posn
          
class Resultable:
    def __init__(self): 
        pass
    
    # Stats are loaded separately and cached on here,
    # hence they may exist on an object at all times.
    def hasServerResults(self):
        return hasattr(self,'serverResults')
        
    def setServerResults(self,serverResults):
        self.serverResults=serverResults
        
    def getServerResults(self):
        if not self.hasServerResults():
            raise RuntimeError, "ServerResults not available [yet]: " \
                    + self.getName()
        return self.serverResults
        
    
    # Stats are loaded separately and cached on here,
    # hence they may exist on an object at all times.
    def hasResults(self):
        return hasattr(self,'results')
        
    def setResults(self,results):
        self.results=results
        
    def getResults(self):
        if not self.hasResults():
            raise RuntimeError, "Results not available [yet]: " \
                    + self.getName()
        return self.results
        
        
        
# represents a <nag/> element
class Nag(ModelObject):
    def __init__(self,toaddr,fromaddr):
    	ModelObject.__init__(self,xml,workspace)

# represents a <javadoc/> element
class Javadoc(ModelObject): pass
      
# represents a <description/> element
class Description(ModelObject): pass

# represents a <home/> element
class Home(ModelObject): pass

# represents a <jar/> element
class Jar(NamedModelObject):
    def __init__(self,name,dom,owner):
    	NamedModelObject.__init__(self,name,dom,owner)
    	self.id=''
    	self.type=''
    	
    def setPath(self,path):
        self.path=path
    
    def getPath(self):
        return self.path;
        
    def hasId(self):
        if self.id: return True
        return False
        
    def setId(self,id):
        self.id = id
        
    def getId(self):
        return self.id
        
    def getType(self):
        return self.type

class Resolvable(ModelObject):
    def __init__(self,dom,owner):
        ModelObject.__init__(self,dom,owner)                
        
    def getResolvedPath(self):  
        path=None
        
        if self.hasDomAttribute('nested'):
            path=os.path.abspath(	\
                    os.path.join(	self.owner.getModule().getWorkingDirectory(),	\
                                    self.getDomAttributeValue('nested')))
        elif self.hasDomAttribute('parent'):
            path=os.path.abspath(	\
                    os.path.join(self.owner.getWorkspace().getBaseDirectory(),	\
                                 self.getDomAttributeValue('parent')))
                                 
        return path
              
# represents a <junitreport/> element
class JunitReport(Resolvable):
    def __init__(self,dom,owner):
        Resolvable.__init__(self,dom,owner)    
    
# represents a <mkdir/> element
class Mkdir(Resolvable):
    def __init__(self,dom,owner):
        Resolvable.__init__(self,dom,owner)    

# represents a <delete/> element
class Delete(Resolvable): 
    def __init__(self,dom,owner):
        Resolvable.__init__(self,dom,owner)    

# represents a <work/> element
class Work(Resolvable): 
    def __init__(self,dom,owner):
        Resolvable.__init__(self,dom,owner)    
        
        
class AddressPair:
    def __init__(self,toAddr,fromAddr):
        self.toAddr=toAddr
        self.fromAddr=fromAddr
        
    def __str__(self):
        return '[To:' + self.toAddr + ', From:' + self.fromAddr + ']'
        
    def getToAddress(self):
        return self.toAddr
        
    def getFromAddress(self):
        return self.fromAddr
        
        