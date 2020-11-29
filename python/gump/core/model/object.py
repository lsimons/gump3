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

    This module contains the base model objects (plain and Named)
    
"""

from time import localtime, strftime, tzname

from gump.util.note import *
from gump.util.work import *
from gump.util.file import *
from gump.util.owner import *
from gump.util.domutils import *

from gump.core.model.state import *
from gump.core.model.propagation import *

class ModelObject(Annotatable,Workable,FileHolder,Propogatable,Ownable):
        
    """Base model object for a single entity"""
    def __init__(self,dom,owner=None):
                
        # Can scribble on this thing...
        Annotatable.__init__(self)
        
        # Holds work (with state)
        Workable.__init__(self)
        
        # Holds file references
        FileHolder.__init__(self)
        
        # Can propogate states
        Propogatable.__init__(self)

        # Can propogate states
        Ownable.__init__(self,owner)

        # The DOM model
        self.dom=dom
        if dom.nodeType==xml.dom.Node.DOCUMENT_NODE:
            self.element=dom.documentElement
        else:
            self.element=self.dom
        
        self.spliced=False
        
        self.debug=False
        self.verbose=False
        self.metadata=None
        
        self.resolutionPerformed=False
        self.completionPerformed=False
            
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        return self.__class__.__name__
        
    def __del__(self):
        Annotatable.__del__(self)
        Workable.__del__(self)
        #FileHolder.__del__(self)
        #Propogatable.__del__(self)
        Ownable.__del__(self)
        
        # No longer need this...
        self.dom=None
       
    def shutdownDom(self): 
        """       
            Shut this object's DOM down, to conserve memory after it is 'done with'.
        """
        if self.dom:            
            if self.element:
                if not self.element is self.dom:
                    self.element.unlink()
                self.element=None
                
            self.dom.unlink()
            self.dom=None
            
    def shutdown(self):
        """       
            Shut this object down to the bare minimim,
            to conserve memory after it is 'done with'.           
        """
     
            
        self.shutdownWork() 
    
    def isResolved(self):
        return self.resolutionPerformed
        
    def setResolved(self,resolved=True):
       self.resolutionPerformed=resolved
       
    def isComplete(self):
        return self.completionPerformed
        
    def setComplete(self,complete=True):
        self.completionPerformed=complete
       
    def setDebug(self,debug=True):
        self.debug=debug
       
    def isDebug(self):
        return self.debug
        
    def setVerbose(self,verbose=True):
        self.verbose=verbose
       
    def isVerbose(self):
        return self.verbose
         
    def isVerboseOrDebug(self):
        return self.isVerbose() or self.isDebug()
        
    def hasMatadataLocation(self):
        if self.metadata: return True
        return False
    
    def setMetadataLocation(self,metadata):
        self.metadata=metadata
        
    def getMetadataLocation(self):
        return self.metadata
    
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        # output.write(getIndent(indent)+'Class: ' + self.__class__.__name__ + '\n')
        if self.hasOwner():
            output.write(getIndent(indent)+'Owner: ' + repr(self.getOwner()) + '\n')
        output.write(getIndent(indent)+'Id: ' + repr(id(self)) + '\n')
        #output.write(getIndent(indent)+'Id DOM: ' + `id(self.dom)` + '\n')
        #output.write(getIndent(indent)+'Id Element: ' + `id(self.element)` + '\n')
        if self.isSpliced():
            output.write(getIndent(indent)+'Was *Spliced*\n')
        Annotatable.dump(self,indent,output)
    
    # Helper methods
    def domAttributeIsTrue(self,name):
        return domAttributeIsTrue(self.element,name)
        
    def hasDomAttribute(self,name):
        return hasDomAttribute(self.element,name)
    
    def getDomAttributeValue(self,name,default=None):
        return self.expandVariables(
                    getDomAttributeValue(self.element,name,default))
        
    def expandVariables(self,value):    
        """
        
            Return a copy of the value with any Gump
            variables expanded.
            
        """
        if not value: return value
        
        # Right now just one supported
        return value.replace('@@DATE@@',default.date_s)
    
        
    def hasDomChild(self,name):
        if hasDomChild(self.element,name): return True
        return False  
        
    def getDomChild(self,name):
        return getDomChild(self.element,name)
        
    def getDomChildValue(self,name,default=None):
        return self.expandVariables(
                    getDomChildValue(self.element,name,default))
        
    def getDomChildIterator(self,name):
        return getDomChildIterator(self.element,name)
   
    # Serialization:
    def writeXml(self,stream,indent='    ',newl='\n') :
        self.dom.writexml(stream,indent=indent,newl=newl) 
        
    def getXml(self,indent='    ',newl='\n'):
        return self.dom.toprettyxml(indent=indent,newl=newl)
        
    # Misc..
    
    def getDomValue(self,name,default=None):
        return getDomValue(self.element,name,default)
    
    def hasXmlData(self):
        return hasattr(self,'xmldata')
        
    def getXmlData(self):
        if not self.hasXmlData():
            self.xmldata=self.getXml()    
        return self.xmldata
        
    def writeXmlToFile(self, outputFile):
        try:            
            f=open(outputFile, 'w')
            self.writeXml(f)
        finally:
            # Since we may exit via an exception, close explicitly.
            if f: f.close()    
        
    # Somewhat bogus...
    
    def getElapsedSecs(self):
        elapsedSecs=self.worklist.getElapsedSecs()
        if hasattr(self,'getChildren'):
            for object in self.getChildren():
                elapsedSecs += object.getElapsedSecs()
        return int(round(elapsedSecs,0))
    
    def aggregateStates(self, states=None):
        if not states: states=[]
        
        pair=self.getStatePair()
        # Add state, if not already there
        if not pair.isUnset() and not pair in states: \
            states.append(pair)
        
        return self.getSubbordinateStates(states);
        
    def getSubbordinateStates(self, states=None):
        if not states: states=[]
        
        # Subbordinates
        if hasattr(self,'getChildren'):
            for object in self.getChildren():
                object.aggregateStates(states)
            
        return states
        
    def getObjectForTag(self,tag,dom,name=None):
        pass
        
    def resolve(self): 
        pass
                         
    # Splice in attributes (other) from 'overrides', e.g. 
    # setting a project packagfe (in the workspace).
    
    def isSpliced(self):
        return self.spliced
    
    def setSpliced(self,spliced):
        self.spliced=spliced
        
    def splice(self,dom): 
        if self.isComplete():
            raise RuntimeError("Can't splice a completed entity: " + repr(self))
        # log.debug("Splice: " + `dom`) 
        spliceDom(self.element,dom)
        self.setSpliced(True) 
                                
    def complete(self):
        if self.isComplete(): return    
        
        # Import overrides from DOM
        transferDomInfo( self.element, self, {})    
        
        # Done, don't redo
        self.setComplete(True)    
        
class NamedModelObject(ModelObject):
    """Context for a single entity"""
    def __init__(self,name,dom,owner=None):
                
        ModelObject.__init__(self,dom,owner)
        
        
        
        # Named
        self.name=name
        if not name:
            raise RuntimeError(self.__class__.__name__ + ' needs a name.')
            
        self.hash=0
        
        from threading import RLock
        self.lock=RLock()
      
    #
    # Same if same type, and same name
    # i.e project context X is not equals to module context X
    def __eq__(self,other):
        return self.__class__ == other.__class__ and self.name == other.name
        
    def __cmp__(self,other):
        return cmp(self.name,other.name)
        
    def __hash__(self):
        if self.hash: return self.hash
        self.hash=hash(self.name)
        return self.hash        
        
    def __str__(self):
        return self.__class__.__name__+':'+self.name

    def getName(self):
        return self.name
        
    def getLock(self):
        return self.lock
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        output.write(getIndent(indent)+'Name: ' + self.name + '\n')
        ModelObject.dump(self,indent+1,output)
