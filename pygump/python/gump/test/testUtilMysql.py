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

import pmock
from pmock import *

from gump.util.mysql import Database

class MysqlUtilTestCase(pmock.MockTestCase):
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
    
    def test_database(self):
        host = "localhost"
        user = "test"
        password = ''
        db = "test"
        d = Database(self.log,host,user,password,db)
        self.assertEqual(host,d.host)
        self.assertEqual(user,d.user)
        self.assertEqual(password,d.password)
        self.assertEqual(db,d.db)
        
        d.commit()
        d.rollback()
        
        try:
            c = d.cursor()
            self.assertNotEqual(None, c)
            c = None
            (rows, result) = d.execute("DROP TABLE IF EXISTS gump_unit_test;")
            self.assertEqual(0, rows)
            
            (rows, result) = d.execute("CREATE TABLE gump_unit_test (id INT);")
            self.assertEqual(0, rows)
            self.assertEqual(None, result)
            
            (rows, result) = d.execute("INSERT INTO gump_unit_test (id) VALUES (10);")
            self.assertEqual(1, rows)
            self.assertEqual(None, result)
            
            (rows, result) = d.execute("SELECT * FROM gump_unit_test;")
            self.assertEqual(1, rows)
            self.assertEqual(10, result[0]["id"])
            
            (rows, result) = d.execute("DROP TABLE gump_unit_test;")
            self.assertEqual(0, rows)
        except Exception:
            print """
The MySQL test depends on a running mysql server to which one can connect
as a test user. That seems to have failed. This is probably not critical.
"""
            raise

        

# this is used by testrunner.py to determine what tests to run
def test_suite():
    # be sure to change the referenceto the TestCase class you create above!
    return unittest.makeSuite(MysqlUtilTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()