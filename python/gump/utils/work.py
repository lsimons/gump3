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

from gump.model.state import *
from gump.utils.owner import *
from gump.utils.timing import *
from gump.utils import *

import gump.process.command
import gump.process.launcher
               
WORK_TYPE_CHECK=1
WORK_TYPE_CONFIG=2
WORK_TYPE_UPDATE=3
WORK_TYPE_PREBUILD=4
WORK_TYPE_BUILD=5
WORK_TYPE_POSTBUILD=6
WORK_TYPE_DOCUMENT=7

workTypeDescriptions = { 	WORK_TYPE_CHECK : "CheckEnvironment",
                WORK_TYPE_CONFIG : "Config",
                WORK_TYPE_UPDATE : "Update",
                WORK_TYPE_PREBUILD : "PreBuild",
                WORK_TYPE_BUILD : "Build",
                WORK_TYPE_POSTBUILD : "PostBuild",
                WORK_TYPE_DOCUMENT : "Document" }    
    
def workTypeName(type):
    return workTypeDescriptions.get(type,'Unknown Work Type:' + str(type))
                   
class WorkItem(Ownable):
    """ Unit of Work"""
    def __init__(self,name,type,state,message=''):
        Ownable.__init__(self)
        
        self.name=name
        self.type=type
        self.state=state
        self.message=message            
    	
    def __del__(self):
        Ownable.__del__(self)
        
    def overview(self):
        overview='Work Name: ' + self.name +' (Type: ' + workTypeName(self.type)+')\n'
        overview+='State: ' + stateDescription(self.state)+'\n'
        if self.message:
            overview+=message+'\n'
        return overview
        
    def getType(self):
        return self.type

    def getTypeName(self):
        return workTypeName(self.type)
        
    def getName(self):
        return self.name
        
    def setName(self,name):
        self.name=name
        
    def clone(self):
        return WorkItem(self.name,self.type,self.state,self.message)
        

class TimedWorkItem(WorkItem):
    """ Unit of Work w/ times """
    def __init__(self,name,type,state,startSecs,endSecs,message=''):
        WorkItem.__init__(self,name,type,state,message)
        self.timerange=TimeStampRange(name,
                                TimeStamp(name,startSecs),
                                TimeStamp(name,endSecs),
                                True)
    
    def getStartSecs(self):   
        return self.timerange.getStartTimeStamp().getTime()
        
    def getEndSecs(self):   
        return self.timerange.getEndTimeStamp().getTime()
        
    def getElapsedSecs(self):   
        if self.timerange.hasTimes():
            return self.timerange.getElapsedSecs()
        return 0
        
    def getRange(self):
        return self.timerange
         
    def overview(self):
        overview=WorkItem.overview(self)
        
        overview+='Elapsed: ' 
        overview+=self.timerange.getElapsedTimeString()
        overview+='\n'
        
        return overview
        
    def clone(self):
        return TimedWorkItem(self.name,self.type,self.state,
                                self.timerange.getStartTime(),
                                self.timerange.getEndTime(),
                                self.message)
       
       
CW_STATE_MAP = {   gump.process.command.CMD_STATE_NOT_YET_RUN : STATE_UNSET,
                   gump.process.command.CMD_STATE_SUCCESS : STATE_SUCCESS,
                   gump.process.command.CMD_STATE_FAILED : STATE_FAILED,
                   gump.process.command.CMD_STATE_TIMED_OUT : STATE_FAILED }
               
def commandStateToWorkState(state):
    return CW_STATE_MAP[state]
     
class CommandWorkItem(TimedWorkItem):
    """ Unit of Work"""
    def __init__(self,type,command,result=None,message=''):
        if not result: result=gump.process.command.CmdResult(command)
        TimedWorkItem.__init__(self,command.name,type,\
                commandStateToWorkState(result.state),	\
                result.getStartSecs(),	\
                result.getEndSecs(),message)
        self.command=command
        self.result=result
                
    def __del__(self):
        TimedWorkItem.__del__(self)
        self.command=None
        self.result=None
        
    def overview(self,lines=50,wrapLen=0,eol=None,marker=None):
        overview=TimedWorkItem.overview(self)
        overview += self.command.overview()        
        if self.result:
            overview += "---------------------------------------------\n"                
            overview+=self.result.tail(lines,wrapLen,eol,marker)            
            overview += "---------------------------------------------\n"
        return overview
        
    def hasOutput(self):
        return self.result.hasOutput()
        
    def tail(self,lines=50,wrapLen=0,eol=None,marker=None):
        return self.result.tail(lines,wrapLen,eol,marker)
        
    def clone(self):
        return CommandWorkItem(self.type,self.command,self.result,self.message)
            
class WorkList(list,Ownable):
    
    """List of work (in order)"""
    def __init__(self,owner=None):
        list.__init__(self)     
        Ownable.__init__(self,owner)            
        
        # Organize by name
        self.nameIndex={}
        
        # Timings
        self.timing=TimeStampSet('Named Work')  
            	
    def __del__(self):
        Ownable.__del__(self)
        self.nameIndex=None
        self.timing=None
        
    def shutdown(self):
        self.nameIndex=None
        del self[:]
        
    def add(self,item):
        
        if item.hasOwner():
            raise RuntimeError, 'WorkItem already owned, can\'t add to list.'
        
        # Keep unique within the scope of this list
        name=item.getName()
        uniquifier=1
        while self.nameIndex.has_key(name):
            name=item.getName()+str(uniquifier)
            uniquifier+=1
        item.setName(name)
        
        # Store by name
        self.nameIndex[name]=item
        
        # Store in the list
        self.append(item)
        
        # Register this time...
        if isinstance(item,TimedWorkItem):
            self.timing.registerRange(item.getRange())
        
        # Let this item know its owner
        item.setOwner(self.getOwner())
    
    def getStartSecs(self):
        startSecs=0
        for item in self:
            if isinstance(item,TimedWorkItem): 
                if not startSecs or item.getStartSecs() < startSecs:
                    startSecs=item.getStartSecs()
        if startSecs: return startSecs
    
    def getEndSecs(self):
        endSecs=0
        for item in self:
            if isinstance(item,TimedWorkItem): 
                if not endSecs or item.getEndSecs() < endSecs:
                    endSecs=item.getEndSecs()
        if endSecs: return endSecs
    
    def getElapsedSecs(self):
        elapsedSecs=0
        for item in self:
            if isinstance(item,TimedWorkItem): 
                elapsedSecs += item.getElapsedSecs()
        return elapsedSecs
                
    def clone(self):
        cloned=WorkList()
        for item in self:
            cloned.add(item.clone())
        return cloned
        
    def getTiming(self):
        return timing
        
class Workable(Stateful):       
    def __init__(self):
        Stateful.__init__(self)
        self.worklist=WorkList(self)
                
    def __del__(self):
        # None @ present ... Stateful.__del__(self)
        self.worklist=None
        
    def getWorkList(self):
        return self.worklist
        
    def performedWork(self,item):
    	self.worklist.add(item)   
        	
    def okToPerformWork(self):
        return self.isUnset() or self.isSuccess()        
               
    def getStartSecs(self):
        return self.worklist.getStartSecs()   
          
    def getEndSecs(self):
        return self.worklist.getEndSecs()       
               
    def getElapsedSecs(self):
        return self.worklist.getElapsedSecs()
        
    def shutdownWork(self):
        self.worklist.shutdown()
    
