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

"""
    This package tests some aspects of the gump.engine module. Note this is
    not an integration test, but a real unit test. Please keep it that
    way :-D
"""

import unittest
from unittest import TestCase

from pmock import *

import StringIO

from gump.engine import _Engine

class EngineTestCase(MockTestCase):
    def setUp(self):
        self.log = self.mock()
        self.log.stubs().method("debug")
        self.log.stubs().method("info")
        self.log.stubs().method("warning")
        self.log.stubs().method("error")
        self.log.stubs().method("critical")
        self.log.stubs().method("log")
        self.log.stubs().method("exception")
        self.log.stubs().method("close")        
        
        self.workspace_loader = self.mock()
        self.workspace_normalizer = self.mock()
        self.workspace_objectifier = self.mock()
        self.workspace_verifier = self.mock()
        self.walker = self.mock()
        self.dom_implementation = self.mock()
        self.pre_process_visitor = self.mock()
        self.visitor = self.mock()
        self.post_process_visitor = self.mock()
        self.workspace = self.mock()
        self.merge_to = StringIO.StringIO()
        self.drop_to = StringIO.StringIO()
    
    def test_constructor(self):
        e = _Engine(self.log,
                    self.workspace_loader,
                    self.workspace_normalizer,
                    self.workspace_objectifier,
                    self.workspace_verifier,
                    self.walker,
                    self.dom_implementation,
                    self.pre_process_visitor,
                    self.visitor,
                    self.post_process_visitor,
                    self.workspace,
                    self.merge_to,
                    self.drop_to)
        self.assertRaises(AssertionError,_Engine,
                    "blah",
                    self.workspace_loader,
                    self.workspace_normalizer,
                    self.workspace_objectifier,
                    self.workspace_verifier,
                    self.walker,
                    self.dom_implementation,
                    self.pre_process_visitor,
                    self.visitor,
                    self.post_process_visitor,
                    self.workspace,
                    self.merge_to,
                    self.drop_to)
        self.assertRaises(AssertionError,_Engine,
                    self.log,
                    "blah",
                    self.workspace_normalizer,
                    self.workspace_objectifier,
                    self.workspace_verifier,
                    self.walker,
                    self.dom_implementation,
                    self.pre_process_visitor,
                    self.visitor,
                    self.post_process_visitor,
                    self.workspace,
                    self.merge_to,
                    self.drop_to)
        self.assertRaises(AssertionError,_Engine,
                    self.log,
                    self.workspace_loader,
                    "blah",
                    self.workspace_objectifier,
                    self.workspace_verifier,
                    self.walker,
                    self.dom_implementation,
                    self.pre_process_visitor,
                    self.visitor,
                    self.post_process_visitor,
                    self.workspace,
                    self.merge_to,
                    self.drop_to)
        self.assertRaises(AssertionError,_Engine,
                    self.log,
                    self.workspace_loader,
                    self.workspace_normalizer,
                    "blah",
                    self.workspace_verifier,
                    self.walker,
                    self.dom_implementation,
                    self.pre_process_visitor,
                    self.visitor,
                    self.post_process_visitor,
                    self.workspace,
                    self.merge_to,
                    self.drop_to)
        self.assertRaises(AssertionError,_Engine,
                    self.log,
                    self.workspace_loader,
                    self.workspace_normalizer,
                    self.workspace_objectifier,
                    "blah",
                    self.walker,
                    self.dom_implementation,
                    self.pre_process_visitor,
                    self.visitor,
                    self.post_process_visitor,
                    self.workspace,
                    self.merge_to,
                    self.drop_to)
        self.assertRaises(AssertionError,_Engine,
                    self.log,
                    self.workspace_loader,
                    self.workspace_normalizer,
                    self.workspace_objectifier,
                    self.workspace_verifier,
                    "blah",
                    self.dom_implementation,
                    self.pre_process_visitor,
                    self.visitor,
                    self.post_process_visitor,
                    self.workspace,
                    self.merge_to,
                    self.drop_to)
        self.assertRaises(AssertionError,_Engine,
                    self.log,
                    self.workspace_loader,
                    self.workspace_normalizer,
                    self.workspace_objectifier,
                    self.workspace_verifier,
                    self.walker,
                    "blah",
                    self.pre_process_visitor,
                    self.visitor,
                    self.post_process_visitor,
                    self.workspace,
                    self.merge_to,
                    self.drop_to)
        self.assertRaises(AssertionError,_Engine,
                    self.log,
                    self.workspace_loader,
                    self.workspace_normalizer,
                    self.workspace_objectifier,
                    self.workspace_verifier,
                    self.walker,
                    self.dom_implementation,
                    self.pre_process_visitor,
                    self.visitor,
                    self.post_process_visitor,
                    None,
                    self.merge_to,
                    self.drop_to)
        e = _Engine(
                    self.log,
                    self.workspace_loader,
                    self.workspace_normalizer,
                    self.workspace_objectifier,
                    self.workspace_verifier,
                    self.walker,
                    self.dom_implementation,
                    self.pre_process_visitor,
                    self.visitor,
                    self.post_process_visitor,
                    self.workspace,
                    None,
                    self.drop_to)
        e = _Engine(
                    self.log,
                    self.workspace_loader,
                    self.workspace_normalizer,
                    self.workspace_objectifier,
                    self.workspace_verifier,
                    self.walker,
                    self.dom_implementation,
                    self.pre_process_visitor,
                    self.visitor,
                    self.post_process_visitor,
                    self.workspace,
                    self.merge_to,
                    None)
    
    def test_run(self):
        domtree = self.mock()
        domtree.expects(once()).unlink()
        dropped = []
        passaroundobj = (domtree,dropped)
        ws = StringIO.StringIO("won't get read anyway")
        objectws = "Blah"
        self.workspace_loader.expects(once()).get_workspace_tree(same(ws)).will(return_value(passaroundobj))
        self.workspace_normalizer.expects(once()).normalize(same(domtree)).will(return_value(domtree))
        self.workspace_objectifier.expects(once()).get_workspace(same(domtree)).will(return_value(objectws))
        self.workspace_verifier.expects(once()).verify(same(objectws))
        self.walker.expects(once()).walk(same(objectws),same(self.pre_process_visitor))
        self.walker.expects(once()).walk(same(objectws),same(self.visitor))
        self.walker.expects(once()).walk(same(objectws),same(self.post_process_visitor))
        e = _Engine(
                    MockLog(),
                    self.workspace_loader,
                    self.workspace_normalizer,
                    self.workspace_objectifier,
                    MockVerifier(objectws, self),
                    self.walker,
                    self.dom_implementation,
                    self.pre_process_visitor,
                    self.visitor,
                    self.post_process_visitor,
                    ws,
                    None,
                    None)
        e.run()
        
        # TODO test exceptions
        
        # TODO test writing merge xml files


class MockLog:
    def exception(self,msg):
        raise


class MockVerifier:
    def __init__(self,expected, testcase):
        self.expected = expected
        self.testcase = testcase
        
    def verify(self,argument):
        TestCase.failUnlessEqual(self.testcase, self.expected, argument)
        
        
# this is used by testrunner.py to determine what tests to run
def test_suite():
    # be sure to change the referenceto the TestCase class you create above!
    return unittest.makeSuite(EngineTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()