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

"""Tests for gump.engine.objectifier"""

import unittest
from pmock import *

import os

from gump.engine.objectifier import *

class EngineObjectifierTestCase(MockTestCase):
    def setUp(self):
        self.log = self.mock()
        self.log.stubs().method("debug")
        self.log.stubs().method("info")
        self.log.stubs().method("warning")
        self.log.stubs().method("warn")
        self.log.stubs().method("error")
        self.log.stubs().method("critical")
        self.log.stubs().method("log")
        self.log.stubs().method("exception")
        self.log.stubs().method("close")
        
        self.workdir = os.path.join(os.environ["GUMP_HOME"], "pygump", "unittest", "work")
        if not os.path.isdir(self.workdir):
            os.makedirs(self.workdir)
        
        self.o = Objectifier(self.log,self.workdir)
    
        self.samplexml = """<?xml version="1.0"?>
<workspace>
  blah
  <elem>contents</elem>
  <stuff>ignore</stuff>
  <elem>ignore</elem>
  <blah></blah>
      <repositories>
      </repositories>
      <modules>
      </modules>
      <projects>
          <project>
            <nested>
              <uniquetaghere>
                <foo/>
              </uniquetaghere>
            </nested>
          </project>
       </projects>
</workspace>
"""
        self.sampledom = minidom.parseString(self.samplexml)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.workdir)
    
    def test_MissingDependencyError(self):
        p = "someprojectname"
        d = "somedependencyname"
        e = MissingDependencyError(p,d)
        self.assertEqual(e.project,p)
        self.assertEqual(e.dependency_name,d)
        self.assertTrue(e.__str__().index(p) > 0)
        self.assertTrue(e.__str__().index(d) > 0)

    def test_Objectifier__init__(self):
        o = Objectifier(self.log,self.workdir)
        self.assertEqual(self.log,o.log)
        self.assertEqual(self.workdir,o.workdir)
        
        self.assertRaises(AssertionError, Objectifier, self.log, "")
        self.assertRaises(AssertionError, Objectifier, "", self.workdir)
        
    def test_Objectifier_get_workspace(self):
        w = self.o.get_workspace(self.sampledom)