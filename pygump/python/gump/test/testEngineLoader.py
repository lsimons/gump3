#!/usr/bin/env python

# Copyright 2005 The Apache Software Foundation
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

__copyright__ = "Copyright (c) 2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

"""Tests for gump.engine.loader"""

import unittest
from pmock import *

from xml.dom import minidom
import StringIO

from gump.engine.loader import Loader
from gump.engine import EngineError

class EngineLoaderTestCase(MockTestCase):
    def setUp(self):
        self.sampleworkspacestring = """<?xml version="1.0"?>

<workspace>
  <newelem attr="yo">contents</newelem>
  <module name="foo">
    <project name="bar">
      <blah/>
    </project>
  </module>
  <newelem>ignore</newelem>
</workspace>
"""
        self.sampleworkspace = minidom.parseString(self.sampleworkspacestring)
   
    def test_loader_init(self):
        log = MockLog()
        vfs = MockVFS()
        
        loader = Loader(log,vfs)
        loader = Loader(log,None)
        
        self.assertRaises(AssertionError, Loader, self, vfs)
        self.assertRaises(AssertionError, Loader, log, self)
        self.assertRaises(AssertionError, Loader, None, vfs)
    
    def test_loader_get_workspace_tree_simple(self):
        log = MockLog()
        vfs = MockVFS()
        loader = Loader(log,vfs)
        
        (wsdom, dropped_nodes) = loader.get_workspace_tree(StringIO.StringIO(self.sampleworkspacestring))
        # TODO check wsdom content validity
        self.assertEqual(0, len(dropped_nodes))
        self.assertEqual(type(self.sampleworkspace), type(wsdom))
        self.assertEqual(None, log.msg)
        self.assertEqual(None, vfs.href)
    
    # TODO test loader href resolution
    # TODO test loader looping href resolution
    # TODO test loader href resolution failure
    # TODO test loader vfs exception
        
class MockLog:
    msg = None
    def warning(self,msg):
        self.msg = msg

class MockVFS:
    href = None
    def get_as_stream(href):
        self.href = href
        return StringIO.StringIO()
