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

from gump.engine.modeller import _find_element_text
from gump.engine.modeller import _do_drop
from gump.engine.modeller import _find_ancestor_by_tag

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
    </nested>
  </some>
</root>
"""
        self.sampledom = minidom.parseString(self.samplexml)
        
    def test_find_element_text(self):
        root = self.sampledom.documentElement
        text = _find_element_text(root, "elem")
        self.assertEqual("contents", text)
        text = _find_element_text(root, "blah")
        self.assertEqual("", text)
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
        to_remove = self.sampledom.documentElement.getElementsByTagName("stuff").item(0)
        dropped = []
        _do_drop(to_remove, dropped)
        self.assertEqual(0, len(self.sampledom.documentElement.getElementsByTagName("stuff")))
        self.assertEqual(1, len(dropped))
        self.assertEqual(to_remove, dropped[0])
    
    def test_find_ancestor_by_tag(self):
        in_elem = self.sampledom.documentElement.getElementsByTagName("in").item(0)
        first_some_elem = in_elem.parentNode.parentNode.parentNode
        found_some = _find_ancestor_by_tag(in_elem, "some")
        self.assertEqual(first_some_elem, found_some)

# this is used by testrunner.py to determine what tests to run
def test_suite():
    # be sure to change the referenceto the TestCase class you create above!
    return unittest.makeSuite(ModellerTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()