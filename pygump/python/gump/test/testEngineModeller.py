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

import unittest
from unittest import TestCase

from xml.dom import minidom
import StringIO

from gump.engine.modeller import _find_element_text
from gump.engine.modeller import _do_drop
from gump.engine.modeller import _find_ancestor_by_tag
from gump.engine.modeller import _find_document_containing_node
from gump.engine.modeller import _find_repository_containing_node
from gump.engine.modeller import _find_module_containing_node
from gump.engine.modeller import _find_project_containing_node
from gump.engine.modeller import _import_node
from gump.engine import EngineError
from gump.engine.loader import Loader

class ModellerTestCase(TestCase):
    def setUp(self):
        self.samplexml = """<?xml version="1.0"?>

<root>
  blah
  <elem>contents</elem>
  <stuff>ignore</stuff>
  <elem>ignore</elem>
  <blah></blah>
  <some>
    <nested>
      <tags>
        <with>
          <some>
            <duplicate>
              <tags>
                <in>
                  <there/>
                </in>
              </tags>
            </duplicate>
          </some>
        </with>
      </tags>
      <repository>
        <module>
          <project>
            <nested>
              <uniquetaghere>
                <foo/>
              </uniquetaghere>
            </nested>
          </project>
        </module>
      </repository>
    </nested>
  </some>
</root>
"""
        self.sampledom = minidom.parseString(self.samplexml)

        self.samplexml2 = """<?xml version="1.0"?>

<otherroot info="true">
  <newelem attr="yo">contents</newelem>
  <newstuff>ignore</newstuff>
  <newelem>ignore</newelem>
</otherroot>
"""
        self.sampledom2 = minidom.parseString(self.samplexml2)

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
    
    def test_find_element_text(self):
        root = self.sampledom.documentElement
        text = _find_element_text(root, "elem")
        self.assertEqual("contents", text)
        text = _find_element_text(root, "blah")
        self.assertEqual(None, text)
        try:
            _find_element_text(root, "notthere")
        except:
            pass
        try:
            _find_element_text(None, "stuff")
        except:
            pass
        try:
            _find_element_text(root, None)
        except:
            pass
    
    def test_do_drop(self):
        # todo test all possibilities
        to_remove = self.sampledom.documentElement.getElementsByTagName("stuff").item(0)
        dropped = []
        _do_drop(to_remove, dropped)
        self.assertEqual(0, len(self.sampledom.documentElement.getElementsByTagName("stuff")))
        self.assertEqual(1, len(dropped))
        self.assertEqual(to_remove, dropped[0])
    
    def test_find_ancestor_by_tag(self):
        # todo test all possibilities
        in_elem = self.sampledom.documentElement.getElementsByTagName("in").item(0)
        first_some_elem = in_elem.parentNode.parentNode.parentNode
        found_some = _find_ancestor_by_tag(in_elem, "some")
        self.assertEqual(first_some_elem, found_some)
    
    def test_find_document_containing_node(self):
        # todo test all possibilities
        in_elem = self.sampledom.documentElement.getElementsByTagName("in").item(0)
        found_doc = _find_document_containing_node(in_elem)
        self.assertEqual(self.sampledom,found_doc)
    
    def test_find_repository_containing_node(self):
        # todo test all possibilities
        child_elem = self.sampledom.documentElement.getElementsByTagName("uniquetaghere").item(0)
        required_repo = child_elem.parentNode.parentNode.parentNode.parentNode
        found_repo = _find_repository_containing_node(child_elem)
        self.assertEqual(required_repo, found_repo)
        
    def test_find_module_containing_node(self):
        # todo test all possibilities
        child_elem = self.sampledom.documentElement.getElementsByTagName("uniquetaghere").item(0)
        required_module = child_elem.parentNode.parentNode.parentNode
        found_repo = _find_module_containing_node(child_elem)
        self.assertEqual(required_module, found_repo)
        
    def test_find_project_containing_node(self):
        # todo test all possibilities
        child_elem = self.sampledom.documentElement.getElementsByTagName("uniquetaghere").item(0)
        required_project = child_elem.parentNode.parentNode
        found_repo = _find_project_containing_node(child_elem)
        self.assertEqual(required_project, found_repo)
    
    def test_import_node(self):
        # todo test all possibilities
        oldroot = self.sampledom.documentElement
        newroot = self.sampledom2.documentElement
        _import_node(oldroot, newroot)
        self.assertEqual("root", oldroot.tagName)
        self.assertEqual(1, oldroot.attributes.length)
        self.assertEqual("info", oldroot.attributes.item(0).nodeName.__str__())
        self.assertEqual("true", oldroot.attributes.item(0).nodeValue.__str__())
        self.assertEqual(2, oldroot.getElementsByTagName("elem").length)
        self.assertEqual(1, oldroot.getElementsByTagName("uniquetaghere").length)
        self.assertEqual(2, oldroot.getElementsByTagName("newelem").length)
        self.assertEqual(1, oldroot.getElementsByTagName("newstuff").length)
    
    def test_engine_error(self):
        error = EngineError()
        self.assert_(isinstance(error, Exception))

