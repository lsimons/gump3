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

from time import localtime, strftime, tzname
from string import lower, capitalize

from gump.utils.note import *
from gump.utils.work import *
from gump.utils.file import *
from gump.utils.owner import *
from gump.utils.xmlutils import xmlize
from gump.utils.domutils import *

from gump.model.state import *
from gump.model.propagation import *

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

        # The XML model
    	self.dom=dom
    	if dom.nodeType==xml.dom.Node.DOCUMENT_NODE:
    	    self.element=dom.documentElement
        else:
            self.element=self.dom
    	
    	self.debug=False
    	self.verbose=False
    	
    	self.completionPerformed=0
    	
    def __del__(self):
        Annotatable.__del__(self)
        Workable.__del__(self)
        #FileHolder.__del__(self)
        #Propogatable.__del__(self)
        Ownable.__del__(self)
        
        # No longer need this...
        self.dom=None
        
    def isComplete(self):
        return self.completionPerformed
        
    def setComplete(self,complete):
       self.completionPerformed=complete
       
    def setDebug(self,debug):
        self.debug=debug
       
    def isDebug(self):
        return self.debug or hasattr(self.dom,'debug')
        
    def setVerbose(self,verbose):
        self.verbose=verbose
       
    def isVerbose(self):
        return self.verbose or hasattr(self.xml,'verbose')
         
    def isVerboseOrDebug(self):
        return self.isVerbose() or self.isDebug()
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        Annotatable.dump(self,indent,output)
    
    def hasXMLData(self):
        return hasattr(self,'xmldata')
        
    def getXMLData(self):
        if not self.hasXMLData():
            stream=StringIO.StringIO() 
            xmlize(self.xml.getTagName(),self.xml,stream)
            stream.seek(0)
            self.xmldata=stream.read()
            stream.close()
    
        return self.xmldata
        
    def writeXMLToFile(self, outputFile):
        try:            
            f=open(outputFile, 'w')
            f.write(self.getXMLData())
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
                                
class NamedModelObject(ModelObject):
    """Context for a single entity"""
    def __init__(self,name,dom,owner=None):
                
    	ModelObject.__init__(self,dom,owner)
    	
    	# Named
    	self.name=name
      
    #
    # Same if same type, and same name
    # i.e project context X is not equals to module context X
    def __eq__(self,other):
        return self.__class__ == other.__class__ and self.name == other.name
        
    def __cmp__(self,other):
        return cmp(self.name,other.name)
        
    def __hash__(self):
        return hash(self.name)
        
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        return self.__class__.__name__+':'+self.name

    def getName(self):
        return self.name
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        output.write(getIndent(indent)+'Name: ' + self.name + '\n')
        ModelObject.dump(self,indent+1,output)

class Positioned:
    def __init__(self): 
        self.posn=-1
        
    def setPosition(self,posn):
        self.posn=posn

    def getPosition(self):
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
    	self.id=None
    	self.type=None
    	
    def complete(self):
        if self.isComplete(): return    
        
        # Import overrides from DOM
        transferInfo( self.element, self, {})    
        
        # Done, don't redo
        self.setComplete(True)    
    	
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
        if self.xml.nested:
            path=os.path.abspath(	\
                    os.path.join(	self.owner.getModule().getWorkingDirectory(),	\
                                    self.xml.nested))
        elif self.xml.parent:
            path=os.path.abspath(	\
                    os.path.join(self.owner.getWorkspace().getBaseDirectory(),	\
                                 self.xml.parent))
                                 
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
        