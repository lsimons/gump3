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
    Utils Testing
"""

from gump.util.tools import *
from gump.util.work import *
from gump.util.file import *
from gump.test.pyunit import UnitTestSuite

class TestFileHolder(FileHolder):
    def __init__(self):    
        # Holds work (with state)
    	FileHolder.__init__(self)    
    	
class TestWorkable(Workable):
    def __init__(self):    
        # Holds work (with state)
    	Workable.__init__(self)    
    
class ToolsTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        self.testworkable=TestWorkable()
        self.testfileholder=TestFileHolder()
        
    def testListAsWork(self):
        listDirectoryAsWork(self.testworkable,'.','test')
    
    def testCatFileAsWork(self):
        catFileAsWork(self.testworkable,'./text.xml','test')
        
    def testCatDirAsWork(self):
        catDirectoryContentsAsWork(self.testworkable,'.','test')
        
    # :TODO: Move to work unit tests module (once written)
    def testWorkClone(self):
        self.testworkable.getWorkList().clone()
        
    def testListToFileHolder(self):
        listDirectoryToFileHolder(self.testfileholder,'.','test')
    
    def testCatFileToFileHolder(self):
        catFileToFileHolder(self.testfileholder,'./text.xml','test')
        
    def testCatDirToFileHolder(self):
        catDirectoryContentsToFileHolder(self.testfileholder,'.')
        
    def testFileClone(self):
        self.testfileholder.getFileList().clone()
        
