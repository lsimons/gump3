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

import os
import StringIO

from main import print_help
from main import _Logger
from main import DEBUG
from main import CRITICAL
from main import _check_version

class MainTestCase(TestCase):
    def test_print_help(self):
        file = StringIO.StringIO("")
        print_help(file)
        result = file.getvalue()
        file.close()
        self.assert_(len(result) > 100) # for want of a better idea...

    def test_logger(self):
        try:
            l = _Logger("gump-maintestcase-logdir-tmp", CRITICAL-1, CRITICAL-1)
            l.debug("blah")
            l.log(DEBUG,"blahblah")
            l.info("blahblahblah")
            l.warning("blahblahblahblah")
            l.error("ehm")
            try:
                raise Exception
            except:
                l.exception("ehmehm")
            l.critical("whoops!")
            l.close()
        finally:
            try:
                os.remove(l.filename)
            except:
                pass
            try:
                os.rmdir(l.logdir)
            except:
                pass
    
    def test_check_version(self):
        try:
            _check_version()
        except:
            pass
    
    # TODO: refactor the main module to make it easier testable!
    
    # don't test _parse_workspace since that should be removed anyway
    
    # don't test _svn_update since that should be removed as well and
    # handled elsewhere
    
    # don't test _send_email because that would entail actually sending
    # e-mail, which is way more trouble than its worth to test
    
    # dont't test send_error_email because that would entail actually
    # sending e-mail, which is way more trouble than its worth to test
    
    # don't test _start_engine because that would basically be running
    # an integration test
    
    # don't test main because that would basically be running
    # an integration test

# this is used by testrunner.py to determine what tests to run
def test_suite():
    # be sure to change the referenceto the TestCase class you create above!
    return unittest.makeSuite(MainTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()