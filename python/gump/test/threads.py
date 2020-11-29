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

    Threading Testing
    
"""
import time
from gump.util.threads.tools import *
from gump.test.pyunit import UnitTestSuite
    
class TestWork:
    def __init__(self,stuff):
        self.stuff=stuff
        
    def __str__(self):
        return 'Work:'+repr(self.stuff)
        
class TestWorker(WorkerThread):
    def performWork(self,work):
        print('Thread ' + self.getName() + ' performs ' + str(work))
        time.sleep(2)
        
        
class ThreadingTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def testThreadWorkList(self):
        workList=ThreadWorkList('Test')
        for i in range(5):
            workList.addWork(TestWork(i))
        
        work=workList.getWork()
        while work:
            print('Get Work : ' + str(work))
            work=workList.getWork()
        
    def testThreadWorkers1(self):
        self.checkGroup()
        
    def testThreadWorkers2(self):
        self.checkGroup(2)
        
    def testThreadWorkers3(self):
        self.checkGroup(5)
        
    def testThreadWorkers4(self):
        self.checkGroup(10)
        
    def checkGroup(self,groupSize=1):
    
        workList=ThreadWorkList('Test')
        for i in range(5):
            workList.addWork(TestWork(i))    
            
        group=WorkerThreadGroup('Test',groupSize,workList,TestWorker)
        group.start()
        group.waitForAll()
        
        
