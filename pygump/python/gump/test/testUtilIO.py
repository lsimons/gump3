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

import os
import StringIO

from gump.util.io import open_file_or_stream
from gump.util.io import VFS

class IOUtilTestCase(TestCase):
    def test_open_file_or_stream(self):
        contents = "blahblah"
        filename = os.path.join(os.getcwd(), "gump-ioutiltestcase-tmp.txt")
        
        try:
            file = open_file_or_stream(filename, 'w')
            file.write(contents)
            file.close()
            file = open_file_or_stream(filename, mode='r')
            result = file.read()
            file.close()
            self.assertEqual(contents, result)
        finally:
            try:
                os.remove(filename)
            except:
                pass
        
        stream = StringIO.StringIO(contents)
        file = open_file_or_stream(stream)
        result = file.read()
        file.close()
        self.assertEqual(contents, result)
        
        file = open_file_or_stream(contents)
        result = file.read()
        file.close()
        self.assertEqual(contents, result)

        result = open_file_or_stream(None)
        self.assertEqual(None, result)
        
    
    def test_error(self):
        from gump.util.io import Error
        try:
            raise Error
        except:
            pass
    
    def test_vfs(self):
        base = os.path.join(os.getcwd(), "gump-ioutiltestcase-base-tmp")
        cache = os.path.join(os.getcwd(), "..", "gump-ioutiltestcase-cache-tmp")
        try:
            os.rmdir(base)
        except:
            pass
        try:
            os.mkdir(base)
        except:
            pass

        try:
            os.rmdir(cache)
        except:
            pass
        try:
            os.mkdir(cache)
        except:
            pass
        
        vfs = VFS(False, False)
        self.assertEqual(None, vfs.filesystem_root)
        self.assertEqual(None, vfs.cachedir)

        vfs = VFS(base, cache)
        self.assertEqual(os.path.normpath(os.path.abspath(base)), vfs.filesystem_root)
        self.assertEqual(os.path.normpath(os.path.abspath(cache)), vfs.cachedir)
        vfs = VFS(base, None)
        
        contents = "blahblah"
        filename = os.path.join(base, "gump-ioutiltestcase-tmp.txt")
        
        try:
            file = open_file_or_stream(filename, 'w')
            file.write(contents)
            file.close()
            file = vfs.get_as_stream("gump-ioutiltestcase-tmp.txt")
            result = file.read()
            file.close()
            self.assertEqual(contents, result)
        finally:
            try:
                os.remove(filename)
            except:
                pass
        
        try:
            file = vfs.get_as_stream("http://gump.apache.org/")
            result = file.read()
            file.close()
            self.assert_( result.index("<html>") > -1 )
        except:
            print """
The testcase for the VFS utility needs a live internet connection. It seems
that is currently not available. This is likely a non-critical problem.
"""
            raise
        
        try:
            os.rmdir(base)
        except:
            pass
        try:
            os.rmdir(cache)
        except:
            pass

# this is used by testrunner.py to determine what tests to run
def test_suite():
    # be sure to change the referenceto the TestCase class you create above!
    return unittest.makeSuite(IOUtilTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()