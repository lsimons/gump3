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

    Results (a tree of status)
    
"""

from time import localtime, strftime, tzname
from xml.dom import getDOMImplementation
        
from gump.util.note import *
from gump.util.work import *
from gump.util.owner import *
from gump.util.domutils import *
from gump.core.model.state import *

class ResultModelObject(Annotatable,Ownable,Stateful):
    """Base model object for a single entity"""
    def __init__(self,name,dom=None,owner=None):
                
        # Can scribble on this thing...
        Annotatable.__init__(self)

        # Can be owned
        Ownable.__init__(self,owner)

        # Holds a state
        Stateful.__init__(self)
        
        # Named
        self.name=name
        
        # The DOM model
        if dom: 
            self.dom=dom
            if dom.nodeType==xml.dom.Node.DOCUMENT_NODE:
                self.element=dom.documentElement
            else:
                self.element=self.dom 
        else:
            self.dom=None
            self.element=None
 
        # Internals...
        self.completionPerformed=False
        
    def __del__(self):
        Ownable.__del__(self)
        
    def isComplete(self):
        return self.completionPerformed
        
    def setComplete(self,complete):
       self.completionPerformed=complete
         
    def completeState(self,node=None):
        if not node: node=self.dom
        stateName=node.getAttribute('state')
        reasonName=node.getAttribute('reason')
        self.setStatePair(getStatePairFromNames(stateName,reasonName))
        
    #
    # Same if same type, and same name
    # i.e project context X is not equals to module context X
    def __eq__(self,other):
        return self.__class__ == other.__class__ and self.name == other.name
        
    def __cmp__(self,other):
        """
        Compare by name
        """
        return cmp(self.name,other.name)
        
    def __hash__(self):
        return hash(self.name)
        
    def __repr__(self):
        return str(self.__class__)+':'+self.name
        
    def __str__(self):
        return str(self.__class__)+':'+self.name

    def getName(self):
        return self.name
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        output.write(getIndent(indent)+'Name: ' + self.name + '\n')
        Annotatable.dump(self,indent,output)
    
    def hasDom(self):
        if self.dom: return True
        return False
        
    def getDom(self):
        return self.dom
        
    # Serialization:
    def writeXml(self,stream,indent='    ',newl='\n') :
        if not self.hasDom():
            self.createDom()            
        self.dom.writexml(stream,indent=indent,newl=newl) 
        
    def getXml(self,indent='    ',newl='\n'):        
        if not self.hasDom():
            self.createDom()    
        return self.dom.toprettyxml(indent=indent,newl=newl)
    
    def hasXmlData(self):
        if hasattr(self,'xmldata') and self.xmldata: return True
        return False
    
    def getXmlData(self):
        if not self.hasXmlData():
            self.xmldata=self.getXml()    
        return self.xmldata
        
    def writeXmlToFile(self, outputFile):
        """ Serialize to a file """
        try:            
            f=open(outputFile, 'w')
            self.writeXml(f)
        finally:
            # Since we may exit via an exception, close explicitly.
            if f: f.close()           
        
    def getTimezoneOffset(self):
        if not hasattr(self,'timezoneOffset') : 
            return self.getOwner().getTimezoneOffset()    
        return self.timezoneOffset
        
    def getTimezone(self):
        if not hasattr(self,'timezone') : 
            return self.getOwner().getTimezone()    
        return self.timezone
        
    def getStartDateTime(self):
        if not hasattr(self,'startDateTime') : 
            return self.getOwner().getStartDateTime()
        return self.startDateTime
        
    def getStartDateTimeUtc(self):
        if not hasattr(self,'startDateTimeUtc') : 
            return self.getOwner().getStartDateTimeUtc()    
        return self.startDateTimeUtc
        
    def getEndDateTime(self):
        if not hasattr(self,'endDateTime') : 
            return self.getOwner().getEndDateTime()    
        return self.endDateTime
        
    def getEndDateTimeUtc(self):
        if not hasattr(self,'endDateTimeUtc') : 
            return self.getOwner().getEndDateTimeUtc()       
        return self.endDateTimeUtc
         
class ResultsSet(dict):
    def __init__(self):
        dict.__init__(self)
        
        self.calculated=0
        self.differences=0
        
    def hasDifferences(self):
        if self.calculated: return self.differences
        
        lastPair=None
        for result in list(self.values()):
            statePair=result.getStatePair()            
            if lastPair:
                if lastPair != statePair:
                    self.differences=1
            lastPair=statePair
            
        self.calculated=1
        return self.differences
        
    def containsFailure(self):
        return self.containsState(STATE_FAILED)
        
    def containsState(self,state):
        for result in list(self.values()):
            if state == result.getState():
                return 1
        return 0
     

# represents a <workspaceResult/> element
class WorkspaceResult(ResultModelObject):
    def __init__(self,name,dom=None,owner=None):
        ResultModelObject.__init__(self,name,dom,owner)    
        
        #
        # Results per module
        #
        self.moduleResults     =    {}
        self.projectResults     =    {}
        
        self.startDateTimeUtc=''
        self.startDateTime=''
        self.endDateTimeUtc=''
        self.endDateTime=''
        self.timezone=''
        self.timezoneOffset=''

    #
    # Lists...
    #
    def hasModuleResults(self):
        if list(self.moduleResults.values()): return True
        return False
        
    def getModuleResults(self):
        return list(self.moduleResults.values())
        
    def hasProjectResults(self):
        if list(self.projectResults.values()): return True
        return False
        
    def getProjectResults(self):
        return list(self.projectResults.values())  
        
    #
    # Named...
    #
    
    def hasModuleResult(self,name):
        if name in self.moduleResults: return True
        return False
                
    def getModuleResult(self,name):
        return self.moduleResults[name]
    
    def hasProjectResult(self,name):
        if name in self.projectResults: return True
        return False
        
    def getProjectResult(self,name):
        return self.projectResults[name]
    
        
    def setModuleResult(self,moduleResult):
        self.moduleResults[moduleResult.getName()] = moduleResult
                
        # Snarf these also, into an ubber map..
        for projectResult in moduleResult.getProjectResults():
            self.setProjectResult(projectResult)
        
    def setProjectResult(self,projectResult):
        self.projectResults[projectResult.getName()] = projectResult
        
    def createDom(self):
        if self.hasDom(): return
        
        self.dom = getDOMImplementation().createDocument(None, 'workspaceResult', None)
        topElement = self.dom.documentElement
        
        topElement.setAttribute('name',self.getName())
        topElement.setAttribute('state',self.getStateName())
        topElement.setAttribute('reason',self.getReasonName())
        
        topElement.setAttribute('startUtc',self.getStartDateTimeUtc())
        topElement.setAttribute('start',self.getStartDateTime())
        topElement.setAttribute('endUtc',self.getEndDateTimeUtc())
        topElement.setAttribute('end',self.getEndDateTime())
        topElement.setAttribute('tzone',self.getTimezone())
        topElement.setAttribute('tzoneOffset',self.getTimezoneOffset())
            
        for moduleResult in list(self.moduleResults.values()):
            moduleResult.createDom(self.dom,topElement)        
                    
    def complete(self): 
        if self.isComplete() or not self.hasDom(): return
                
        # Workspace dom is document, but stuff on first
        # element
        self.completeState(self.dom.documentElement)
                
        # Timing
        self.startDateTime=self.dom.documentElement.getAttribute('start')
        self.startDateTimeUtc=self.dom.documentElement.getAttribute('startUtc')
        
        self.endDateTime=self.dom.documentElement.getAttribute('end')
        self.endDateTimeUtc=self.dom.documentElement.getAttribute('endUtc')
        
        self.timezone=self.dom.documentElement.getAttribute('tzone')
        self.timezoneOffset=self.dom.documentElement.getAttribute('tzoneOffset')
        
        #
        # Import all modules
        #  
        for dommoduleresult in self.dom.getElementsByTagName('moduleResult'): 
            moduleResult=ModuleResult(dommoduleresult.getAttribute('name'),dommoduleresult,self)
            moduleResult.complete()                    
            self.setModuleResult(moduleResult)     
        
        self.setComplete(1)
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        ResultModelObject.dump(self,indent,output)
        
        for moduleResult in list(self.moduleResults.values()):
            moduleResult.dump(indent+1, output)
        
# represents a <moduleResult/> element
class ModuleResult(ResultModelObject):
    def __init__(self,name,dom=None,owner=None):
        ResultModelObject.__init__(self,name,dom,owner)    
        
        # 
        # Results per project
        #
        self.projectResults     =    {}    
        
    def setProjectResult(self,projectResult):
        self.projectResults[projectResult.getName()] = projectResult
        # Attach oneself as owner...
        projectResult.setOwner(self)
                
    def hasProjectResults(self):
        if list(self.projectResults.values()): return 1
        return 0    
        
    def getProjectResults(self):
        return list(self.projectResults.values())
        
    def createDom(self, document, element):
        if self.hasDom(): return
        
        self.dom = document.createElement('moduleResult')
        
        self.dom.setAttribute('name',self.getName())
        self.dom.setAttribute('state',self.getStateName())
        self.dom.setAttribute('reason',self.getReasonName())
        
        element.appendChild(self.dom)
            
        for projectResult in self.getProjectResults():
            projectResult.createDom(document,self.dom)        
            
    def complete(self): 
        if self.isComplete() or not self.hasDom(): return
                        
        self.completeState()
        
        for domprojectresult in self.dom.getElementsByTagName('projectResult'):            
            projectResult=ProjectResult(domprojectresult.getAttribute('name'),domprojectresult,self)
            projectResult.complete()
            self.setProjectResult(projectResult)     
                
        self.setComplete(1)
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        ResultModelObject.dump(self,indent,output)
        
        for projectResult in list(self.projectResults.values()):
            projectResult.dump(indent+1, output)
            
# represents a <projectResult/> element
class ProjectResult(ResultModelObject):
    def __init__(self,name,dom=None,owner=None):
        ResultModelObject.__init__(self,name,dom,owner)    

    def createDom(self, document, element):
        if self.hasDom(): return
        
        self.dom = document.createElement('projectResult')
        
        self.dom.setAttribute('name',self.getName())
        self.dom.setAttribute('state',self.getStateName())
        self.dom.setAttribute('reason',self.getReasonName())
            
        element.appendChild(self.dom)
        
    def complete(self): 
        if self.isComplete(): return
        self.completeState()
        self.setComplete(1)
        
