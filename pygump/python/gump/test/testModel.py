#!/usr/bin/env python

# Copyright 2004-2005 The Apache Software Foundation
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

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import unittest

from gump.test.mockobjects import *
from gump.model import Error, Workspace, ModelObject, Repository

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    def testError(self):
        error = Error()
        try:
            raise error
        except:
            pass
    
    def testModelObject(self):
        obj = ModelObject()
    
    def testWorkspace(self):
        w = Workspace("blah")
        self.assertEquals("blah", w.name)
        self.assertEquals({}, w.repositories)
        self.assertEquals({}, w.modules)
        self.assertEquals({}, w.projects)
        self.assertEquals([], w.dependencies)
        
        r = Repository(w, "blahblah")
        self.assertEquals({}, w.repositories)
        w.add_repository(r)
        self.assertEquals(w.repositories["blahblah"], r)
        self.assertEquals(1, len(w.repositories))


# this is used by testrunner.py to determine what tests to run
def test_suite():
    return unittest.makeSuite(ModelTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()
