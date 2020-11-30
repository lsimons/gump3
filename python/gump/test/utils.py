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
    Utility Testing
"""

from gump.util import *
from gump.test.pyunit import UnitTestSuite

class TestBean:
    def getX(self): return 1
    def isY(self): return 0
    def getYadaYada(self): return 'Yowzer'
    
class UtilsTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        self.now=default.datetime
    
    def testWrap(self):
        
        eol='\n'
        wrapper='[WRAPPED]'
        
        totalWrapperLen=len(eol)+len(wrapper)
        
        line='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        wrapped=wrapLine(line,100,eol,wrapper)
        #print wrapped
        self.assertNotSubstring('Ought NOT be wrapped', wrapper, wrapped)
        self.assertEqual('Ought be wrapped once', len(line), len(wrapped))
        
        
        line='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        wrapped=wrapLine(line,100,eol,wrapper)
        #print wrapped
        self.assertInString('Ought be wrapped', wrapper, wrapped)
        self.assertEqual('Ought be wrapped once', len(line)+totalWrapperLen, len(wrapped))
        
        
        line='1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
        wrapped=wrapLine(line,100,eol,wrapper)
        #print wrapped
        self.assertInString('Ought be wrapped', wrapper, wrapped)
        self.assertEqual('Ought be wrapped twice', len(line)+(2*totalWrapperLen), len(wrapped))
        
    def testBeanAttributes(self):
        attrs=getBeanAttributes(TestBean())
        self.assertNotEmptyDictionary('Ought be some', attrs)
        self.assertNotNone('Ought be one called X', attrs['X'])
        
    def testRandomStuff(self):
        getIndent(5)
        logResourceUtilization()
  
    def testInspectGarbageCollection(self):
        invokeGarbageCollection('testInspect')
        
    def testGarbageCollection1(self):
        invokeGarbageCollection('testCollect')
        
    def testGarbageCollection2(self):
        invokeGarbageCollection('before add circular')
        a=TestBean()
        b=TestBean()
        a.other=b
        b.other=a
        invokeGarbageCollection('after circular')     
                
    def testRefCounts(self):
        getRefCounts()     
        printTopRefs(100)       
