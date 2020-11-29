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

__copyright__ = "Copyright (c) 2004 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

class MockLog:
    def __init__(self):
        pass
    
    def debug(self,msg):
        print("DEBUG: %s" % (msg))

    def info(self,msg):
        print("INFO: %s" % (msg))

    def warning(self,msg):
        print("WARNING: %s" % (msg))

    def error(self,msg):
        print("ERROR: %s" % (msg))
        
class MockConnection:
    def __init__(self,cursor):
        self._cursor = cursor
    def cursor(self):
        return self._cursor

class MockCursor:
    def __init__(self):
        self.lastCommand = ''
    
    def execute(self,command):
        self.lastCommand = command

class MockWorkspace:
    def __init__(self):
        pass

class MockOptions:
    def __init__(self):
        pass

class MockGumpSet:
    def __init__(self):
        pass

class MockRun:
    def __init__(self,workspace,options,gumpSet):
        self.workspace = workspace
        self.options = options
        self.gumpSet = gumpSet
        
    def getWorkspace(self):
        return self.workspace
    
    def getOptions(self):
        return self.options
    
    def getGumpSet(self):
        return self.gumpSet

class MockDatabase:
    def __init__(self):
        self.lastCommand = ''
    
    def execute(self,command):
        self.lastCommand = command

class MockObjects:
    def __init__(self):
        self.log = MockLog()
        self.workspace = MockWorkspace()
        self.options = MockOptions()
        self.gumpSet = MockGumpSet()
        self.run = MockRun(self.workspace,self.options,self.gumpSet)
        self.cursor = MockCursor()
        self.conn = MockConnection(self.cursor)
        self.database = MockDatabase()
