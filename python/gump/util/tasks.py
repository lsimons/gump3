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
    This module contains file (dir/plain) references
"""

import os.path
import sys

from gump.util.timing import TimeStampRange
from gump.util.owner import Ownable
from gump.util import dump, display, getIndent

class Task(Ownable):       
    def __init__(self,name,id=None,parentTask=None):
        
        Ownable.__init__(self)
        
        self.name=name
        self.id=id
        
        # Timing...
        self.timeRange=None
        
        # Tasks can spawn tasks...
        self.parentTask=parentTask
        
    def __del__(self):
        Ownable.__del__(self)       
        self.parentTask=None
        self.result=None
        self.failed=None
    
    def __str__(self):
        s=''
        
        if self.id:
            s+=repr(self.id)
            
        if s:
            s+=':'
        s+=self.__class__.__name__+':"'+self.name+'"'
        
        if self.hasParentTask():
            parent=self.getParentTask()
            if parent.hasId():
                s+=':'
                s+=repr(parent.getId())
         
        if self.timeRange:
            s+=':'
            s+=self.timeRange.getElapsedTimeString()
        
        if self.isFailed():
         s+=': *** '
         s+=str(self.getFailed())
         
        if self.hasResult():
         s+=':'
         s+=str(self.getResult())
         
        return s
        
    def getName(self):
        return self.name
        
    def setId(self,id):
        self.id=id
        
    def getId(self):
        return self.id
        
    def hasId(self):
        return hasattr(self,'id') and self.id
        
    def workInitiated(self):
        self.timeRange=TimeStampRange(self.name)
        
    def workCompleted(self):
        self.timeRange.setEnd()

    def setFailed(self,failed):
        self.failed=failed
        
    def isFailed(self):
        return hasattr(self,'failed') and self.failed
        
    def getFailed(self):
        return self.failed
        
    def setResult(self,result):
        self.result=result
        
    def hasResult(self):
        return hasattr(self,'result') and self.result
        
    def getResult(self):
        return self.result      
        
    def setParentTask(self,parentTask):
        self.parentTask=parentTask
        
    def hasParentTask(self):
        return hasattr(self,'parentTask') and self.parentTask
        
    def getParentTask(self):
        return self.parentTask

class TaskList(Ownable):
    
    """
    
        A named set of tasks
                        
    """
    
    def __init__(self,name,owner=None,idgen=None):
        Ownable.__init__(self,owner)
        
        self.name=name  
        
        if not idgen:
            idgen=SequentialIdGenerator()
        self.idgen=idgen
        
        self.todo=list()
        self.working=list()
        self.performed=list()   
        
    def __del__(self):
        Ownable.__del__(self)            
    
    def addTask(self,task):
        if self.idgen:
            task.setId(self.idgen.generateId())
        
        # Assume ownership, disallows multiple owners
        task.setOwner(self)
        
        # Store in TODOs
        self.todo.append(task)
    
    def hasTasksTodo(self):
        return len(self.todo)>0
        
    def getTask(self):
        task=self.todo.pop()   
        self.working.append(task)     
        task.workInitiated()        
        return task
        
    def performedTask(self,task):
        task.workCompleted()
        self.working.remove(task)
        self.performed.append(task)
        
    def __str__(self):
        return self.name+'['+repr(len(self.todo))+':'+repr(len(self.working))+':'+repr(len(self.performed))+']'
        
    def perform(self,worker):        
        while self.hasTasksTodo():
            task=self.getTask()        
            worker.perform(task)
            self.performedTask(task)
            
    def getPerformed(self):
        return self.performed
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        i=getIndent(indent)
        
        self.dumpTaskList(self.todo,'To-Do :',indent+1,output)
        self.dumpTaskList(self.working,'Working :',indent+1,output)
        self.dumpTaskList(self.performed,'Performed :',indent+1,output)
            
    def dumpTaskList(self,list,title,indent=0,output=sys.stdout):
        """ Display a single list """  
        i=getIndent(indent)              
        output.write('\n')
        output.write(i + title + '[' + str(len(list)) + '] : \n') 
        idx=0  
        for task in list:
            idx+=1
            output.write(i+str(idx)+': '+str(task)+ '\n')
    
class IdGenerator:
        
    def __init__(self):
        pass
        
    def generateId(self):
        return None
        
class SequentialIdGenerator(IdGenerator):
        
    def __init__(self):
        self.idNo=0
        
    def generateId(self):
        self.idNo+=1
        return self.idNo
        
class UuidIdGenerator(IdGenerator):
        
    def __init__(self):
        self.idNo=0
        
    def generateId(self):
        # :TODO:
        pass
        
