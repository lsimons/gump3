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

from gump.core.model.state import *
from gump.util.owner import *
from gump.util.timing import *
from gump.util import *

import gump.util.process.command
import gump.util.process.launcher
               
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
        overview+='Work ended in a state of : ' + stateDescription(self.state)+'\n'
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
    def __init__(self,name,type,state,start,end,message=''):
        WorkItem.__init__(self,name,type,state,message)
        self.timerange=TimeStampRange(name,
                                start,
                                end,
                                True)
                                
        # Proxy some methods...
        setattr(self,'hasStart',self.timerange.hasStart)
        setattr(self,'getStart',self.timerange.getStart)
        setattr(self,'hasEnd',self.timerange.hasEnd)
        setattr(self,'getEnd',self.timerange.getEnd)
        
        setattr(self,'getElapsedSecs',self.timerange.getElapsedSecs)
      
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
                                self.timerange.getStart().getTimestamp(),
                                self.timerange.getEnd().getTimestamp(),
                                self.message)
       
       
CW_STATE_MAP = {   gump.util.process.command.CMD_STATE_NOT_YET_RUN : STATE_UNSET,
                   gump.util.process.command.CMD_STATE_SUCCESS : STATE_SUCCESS,
                   gump.util.process.command.CMD_STATE_FAILED : STATE_FAILED,
                   gump.util.process.command.CMD_STATE_TIMED_OUT : STATE_FAILED }
               
def commandStateToWorkState(state):
    return CW_STATE_MAP[state]
     
class CommandWorkItem(TimedWorkItem):
    """ Unit of Work"""
    def __init__(self,type,command,result=None,message=''):
        if not result: result=gump.util.process.command.CmdResult(command)
        TimedWorkItem.__init__(self,command.name,type,
                commandStateToWorkState(result.state),
                result.getStart(),
                result.getEnd(),
                message)
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
        self.times=TimeStampSet('Named Work')  
            	
    def __del__(self):
        Ownable.__del__(self)
        self.nameIndex=None
        self.times=None
        
    def shutdown(self):
        self.nameIndex=None
        del self[:]
        
    def add(self,item):
        
        if item.hasOwner():
            raise RuntimeError('WorkItem already owned, can\'t add to list.')
        
        # Keep unique within the scope of this list
        name=item.getName()
        uniquifier=1
        while name in self.nameIndex:
            name=item.getName()+str(uniquifier)
            uniquifier+=1
        item.setName(name)
        
        # Store by name
        self.nameIndex[name]=item
        
        # Store in the list
        self.append(item)
        
        # Register this time...
        if isinstance(item,TimedWorkItem):
            self.times.registerRange(item.getRange())
        
        # Let this item know its owner
        item.setOwner(self.getOwner())
        
    def hasStart(self):
        if self.getStart(): return True
        return False
    
    def getStart(self):
        start=None
        for item in self:
            if isinstance(item,TimedWorkItem): 
                if not start or item.getStart() < start:
                    start=item.getStart()
        return start
    
    def hasEnd(self):
        if self.getEnd(): return True
        return False
            
    def getEnd(self):
        end=None
        for item in self:
            if isinstance(item,TimedWorkItem): 
                if not end or item.getEnd() > end:
                    end=item.getEnd()
        return end
    
    def hasTimes(self):
        if self.getStart() and self.getEnd(): return True
        return False
        
    def getElapsedSecs(self):
        elapsedSecs=0
        for item in self:
            if isinstance(item,TimedWorkItem): 
                elapsedSecs += item.getElapsedSecs()
        return elapsedSecs
        
    def getElapsedTimeString(self):
        return secsToElapsedTimeString(self.getElapsedSecs())
                
    def clone(self):
        cloned=WorkList()
        for item in self:
            cloned.add(item.clone())
        return cloned
        
    def getTimes(self):
        return times
        
class Workable(Stateful):       
    def __init__(self):
        Stateful.__init__(self)
        self.worklist=WorkList(self)
        
        setattr(self, 'hasStart', self.worklist.hasStart)
        setattr(self, 'getStart', self.worklist.getStart)
        setattr(self, 'hasEnd', self.worklist.hasEnd)
        setattr(self, 'getEnd', self.worklist.getEnd)
        setattr(self, 'hasTimes', self.worklist.hasTimes)
        setattr(self, 'getTimes', self.worklist.getTimes)
        setattr(self, 'getElapsedSecs', self.worklist.getElapsedSecs)
        setattr(self, 'getElapsedTimeString', self.worklist.getElapsedTimeString)
                
    def __del__(self):
        # None @ present ... Stateful.__del__(self)
        self.worklist=None
        
    def getWorkList(self):
        return self.worklist
        
    def performedWork(self,item):
    	self.worklist.add(item)           	
    
        
    def shutdownWork(self):
        self.worklist.shutdown()
    
