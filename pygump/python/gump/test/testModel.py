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

from gump.model import Error
from gump.model import ModelObject
from gump.model import Workspace
from gump.model import Repository
from gump.model import Module
from gump.model import CvsRepository
from gump.model import CVS_METHOD_PSERVER

class ModelTestCase(TestCase):
    def setUp(self):
        # initialize tests here
        pass
    
    def tearDown(self):
        # clean up after tests here
        pass
    
    def test_error(self):
        e = Error()
        try:
            raise e
        except:
            pass
    
    def test_model_object(self):
        m = ModelObject()
    
    def test_workspace(self):
        name = "blah"
        w = Workspace(name)
        self.assertEqual(name, w.name)
        self.assertEqual({}, w.repositories)
        self.assertEqual({}, w.modules)
        self.assertEqual({}, w.projects)
        self.assertEqual([], w.dependencies)
        
        self.assertRaises(AssertionError, Workspace, None)
        
        r = Repository(w, "booh")
        w.add_repository(r)
        self.assertEqual(r, w.repositories["booh"])
        self.assertEqual(1, len(w.repositories))
        
        self.assertRaises(AssertionError, w.add_repository, r)
        self.assertRaises(AssertionError, w.add_repository, None)
        self.assertRaises(AssertionError, w.add_repository, "blah")
        self.assertEqual(1, len(w.repositories))
        
        w2 = Workspace("blah2")
        r2 = Repository(w2, "booh2")
        self.assertRaises(AssertionError,w.add_repository,r2)
    
    def test_repository(self):
        wname = "blah"
        w = Workspace(wname)
        name = "booh"
        title = "t"
        home_page = "h"
        cvsweb = "c"
        redistributable = True
        
        r = Repository(w,name,title,home_page,cvsweb,redistributable)
        self.assertEqual(w, r.workspace)
        self.assertEqual(name, r.name)
        self.assertEqual(title, r.title)
        self.assertEqual(home_page, r.home_page)
        self.assertEqual(cvsweb, r.cvsweb)
        self.assertEqual(redistributable, r.redistributable)
        self.assertEqual({}, r.modules)
        
        r = Repository(w,name,title=title)
        self.assertEqual(title, r.title)
        r = Repository(w,name,home_page=home_page)
        self.assertEqual(home_page, r.home_page)
        r = Repository(w,name,cvsweb=cvsweb)
        self.assertEqual(cvsweb, r.cvsweb)
        r = Repository(w,name,redistributable=redistributable)
        self.assertEqual(redistributable, r.redistributable)
        
        self.assertRaises(AssertionError, Repository, "test", name)
        self.assertRaises(AssertionError, Repository, "test", w)
        
        r = Repository(w,name)
        mname="bweh"
        m = Module(r,mname)
        r.add_module(m)
        self.assertEqual(m,r.modules["bweh"])
        self.assertEqual(1,len(r.modules))
        self.assertRaises(AssertionError, r.add_module, None)
        self.assertRaises(AssertionError, r.add_module, "bweh")
        self.assertRaises(AssertionError, r.add_module, m)
        self.assertEqual(1,len(r.modules))
        
        r2 = Repository(w,"booh2")
        m2 = Module(r2,"bweh2")
        self.assertRaises(AssertionError, r.add_module, m2)
    
    def test_cvs_repository(self):
        wname = "blah"
        w = Workspace(wname)
        name = "booh"
        hostname = "cvs.somewhere.org"
        path = "/some/cvs/location"
        title = "t"
        home_page = "h"
        cvsweb = "c"
        redistributable = True
        method = CVS_METHOD_PSERVER
        user = "anonymous"
        password = "blah"
        
        r = CvsRepository(w,name,hostname,path,title,home_page,cvsweb,redistributable,method,user,password)
        self.assertEqual(w, r.workspace)
        self.assertEqual(name, r.name)
        self.assertEqual(hostname,r.hostname)
        self.assertEqual(path,r.path)
        self.assertEqual(title, r.title)
        self.assertEqual(home_page, r.home_page)
        self.assertEqual(cvsweb, r.cvsweb)
        self.assertEqual(redistributable, r.redistributable)
        self.assertEqual(method, r.method)
        self.assertEqual(user, r.user)
        self.assertEqual(password, r.password)
        self.assertEqual({}, r.modules)
        
        r = CvsRepository(w,name,hostname,path,method=method)
        self.assertEqual(method, r.method)
        r = CvsRepository(w,name,hostname,path,user=user)
        self.assertEqual(user, r.user)
        r = CvsRepository(w,name,hostname,path,password=password)
        self.assertEqual(password, r.password)
        
        self.assertRaises(AssertionError, CvsRepository, w, name, w, path)
        self.assertRaises(AssertionError, CvsRepository, w, name, hostname, w)

        r = CvsRepository(w,name,hostname,path,title,home_page,cvsweb,redistributable,"blah",user,password)
        self.assertEqual(":blah:anonymous@cvs.somewhere.org:/some/cvs/location", r.to_url())
        r = CvsRepository(w,name,hostname,path)
        self.assertEqual(":pserver:cvs.somewhere.org:/some/cvs/location", r.to_url())


# this is used by testrunner.py to determine what tests to run
def test_suite():
    return unittest.makeSuite(ModelTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()