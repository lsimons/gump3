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

    Multi-Threading Stuff
    
"""

from threading import Lock,Semaphore,Condition,Thread
from gump import log


class ThreadWorkList(list):
    def __init__(self,size):
        self.lock=Lock()
        
    def addWork(self,work):
        self.lock.acquire()
        try:
            self.append(work)
        finally:
            self.lock.release()
            
    def getWork(self):
        self.lock.acquire()
        try:
            if len(self) > 0:
                work=self.pop(0)
            else:
                work=None
        finally:
            self.lock.release() 
        return work 

class WorkerThread(Thread):
    def __init__(self,name,done,workList):
        Thread.__init__(self,None,None,name)
        self.done=done
        self.workList=workList
      
    def run(self):
        log.debug('Thread ' + repr(self) + ' started.')    
        
        try:
            work = self.getWork()
            
            while work:
                self.performWork(work)
                
                # Get work todo (if none, exit)
                work = self.getWork()
            else:
                log.debug('No work for thread ' + self.getName())
                
        finally:
            self.done.release()
            
        log.debug('Thread ' + repr(self) + ' completed.')
            
    def getWork(self):
        return self.workList.getWork()

class WorkerThreadGroup:
    def __init__(self,name,count,workList,cls):
        
        self.name=name
        self.count=count 
        self.workList=workList
        self.cls=cls
        
        # Covers the size of pool
        self.done=Condition(Semaphore(self.count))
        
    def start(self):
        for i in range(self.count):
            name = self.name + ':' + repr((1+i))
            
            # Create a new Thread
            thread = self.cls(name,self.done,self.workList)
            
            # Mark it as active
            self.done.acquire()
            thread.start()
            
    def waitForAll(self):
            
        log.debug('Wait for all threads to complete.')    
        # Try to acquire every count
        for i in range(self.count):    
            self.done.acquire() 
            log.debug('Completed. Thread #' + repr(i) + '.')    
            
        log.debug('All threads completed.')    
