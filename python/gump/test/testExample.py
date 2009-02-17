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
    This is an example of a testcase. Simply copy and rename this file
    (the filename has to start with "test"), then rename the class below,
    update the reference to the classname in the test_suite() method,
    and write your test methods.
    
    See the documentation for the unittest package for more help with
    tests. You can run all tests from the commandline using "./gump test".
"""

import unittest
from unittest import TestCase

class ExampleTestCase(TestCase):
    def setUp(self):
        # initialize tests here
        pass
    
    def tearDown(self):
        # clean up after tests here
        pass
        
    def testSomething(self):
        # you can do anything inside a test
        # use the assertXXX methods on TestCase
        # to check conditions
        self.assert_( True )
        self.assertEquals( type({}), type({}) )

# this is used by testrunner.py to determine what tests to run
def test_suite():
    # be sure to change the referenceto the TestCase class you create above!
    return unittest.makeSuite(ExampleTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()
