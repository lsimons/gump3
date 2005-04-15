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
import sys

from gump.util.executor import Popen
from subprocess import PIPE
from gump.util.executor import clean_up_processes

class ZZZExecutorUtilTestCase(TestCase):
    def test_zzz_run_simple_command_then_clean_up_processes(self):
        if sys.platform == "win32":
            return
        
        result = Popen(["pwd"], stdout=PIPE).communicate()[0]
        self.assertNotEqual("", result)

        # This test can only be run once, since after the call to
        # "clean_up_processes" all future invocations of subprocesses
        # will fail. Therefore this class and its methods are awkwardly
        # named (the ZZZ prefix) so we "ensure" they run last. It's
        # ugly, I know.
        processes = []
        for i in range(0,10):
            processes.append(Popen(["cat"], stdin=PIPE, stdout=PIPE))
            
        clean_up_processes(5)
        for p in processes:
            try:
                pid, sts = os.waitpid(p.pid, os.WNOHANG)
                self.assert_(os.WIFSIGNALED(exitcode), "Process should've been signalled...")
            except:
                pass
        
# this is used by testrunner.py to determine what tests to run
def test_suite():
    return unittest.makeSuite(ZZZExecutorUtilTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()