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
    This package tests some aspects of the main module. Note this is
    not an integration test, but a real unit test. Please keep it that
    way :-D
"""

import unittest
from unittest import TestCase

import StringIO

from main import print_help

class MainTestCase(TestCase):
    def test_print_help(self):
        file = StringIO.StringIO("")
        print_help(file)
        result = file.getvalue()
        file.close()
        self.assert_(len(result) > 10) # for want of a better idea...

# this is used by testrunner.py to determine what tests to run
def test_suite():
    # be sure to change the referenceto the TestCase class you create above!
    return unittest.makeSuite(MainTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()