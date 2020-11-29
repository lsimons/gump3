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
    XDOCS|XHTML Testing
"""

import os
import logging
import types, io

from gump.core.gumpinit import gumpinit
from gump.actor.document.xdocs.xdoc import *
from gump.actor.document.xdocs.config import *

from gump.test.pyunit import UnitTestSuite

class XDocsTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def testXhtml(self):
        data=self.createXDoc('XHTML',True)
        #print data
        
    def testXDocs(self):
        data=self.createXDoc('XDOCS',False)
        #print data
        
    def createXDoc(self,title,xhtml):        
        stream=io.StringIO() 
      
        doc1=XDocDocument('Test 1', stream, XDocConfig(xhtml))
        
        section1=doc1.createSection('Test Section 1')
        para1=section1.createParagraph('Test Text 1')
    
        table1=section1.createTable()
        comment1=table1.createComment('Test Comment 1')
        table1.createEntry('Title1:','Data1')
    
        list1=section1.createList()
        list1.createEntry('Title1:','Item1')    
        list1.createItem('Item2').createLink('http://somewhere','Link')
        list1.createItem('Item3').createLink('http://somewhere').createIcon('http://somewhere','Alt')
        list1.createItem('Item4').createIcon('http://somewhere','Alt')
        list1.createEntry('Title1:','Item1').createBreak()
        list1.createEntry('Item5').createLink('http://somewhere','Link')
    
        table1=section1.createTable(['H1','H2'])
    
        doc1.serialize()
    
        stream.seek(0)
        return stream.read()
