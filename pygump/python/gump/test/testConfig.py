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

"""Tests for gump.config"""

import unittest
from pmock import *

from gump.config import *
import gump
from gump.plugins import AbstractPlugin

import logging
import logging.config

class ConfigTestCase(MockTestCase):
    def setUp(self):
        # replace various methods with mockup versions
        def newfileconfig(filename):
            self.failUnless(isinstance(filename, basestring))
            self.failUnless(filename.startswith('gump.log.config'))
        self.old_fileConfig = logging.config.fileConfig
        logging.config.fileConfig = newfileconfig

        def new_get_logger(config, name):
            return self.get_mock_logger(config, name)
        self.old_get_logger = gump.config.get_logger
        gump.config.get_logger = new_get_logger
    
    def tearDown(self):
        logging.config.fileConfig = self.old_fileConfig
        gump.config.get_logger = self.old_get_logger
    
    def get_mock_logger(self, config, name):
        self.failUnless(unittest.TestCase, isinstance(config, Config))
        self.failUnless(unittest.TestCase, isinstance(name, basestring))
    
        mock = self.mock()
        mock.stubs().method("debug")
        mock.stubs().method("info")
        mock.stubs().method("warn")
        mock.stubs().method("warning")
        mock.stubs().method("error")
        mock.stubs().method("critical")
        mock.stubs().method("log")
        mock.stubs().method("exception")
        mock.stubs().method("close")
        return mock

    def test_run_config_hooks(self):
        class MockConfig:
            debug = False
            quiet = False
        
        mock = MockConfig()
        run_config_hooks(mock)
        
        mock.quiet = True
        run_config_hooks(mock)
        
        mock.debug = True
        run_config_hooks(mock)

    def test_get_config(self):
        testcase = self
        class Settings:
            def __hasattr__(self, name):
                return True
            
            def __getattr__(self, name):
                return name

            def __setattr__(self, name, value):
                testcase.fail("Config tried to set option on settings!")
        
        s = Settings()
        c = get_config(s)
        for arg in ["paths_home", "paths_work", "color", "irc", "blah"]:
            value = getattr(c, arg)
            self.assertEqual(arg, value)
        self.assertEqual(c.log_level, logging.WARN)
        self.assertFalse(c.debug)

    def test_get_plugins(self):
        class Config:
            irc = "user@freenode.net/gump"
            
            def __hasattr__(self, name):
                return True
            
            def __getattr__(self, name):
                return name
        
        conf = Config()
        (a,b,c) = get_plugins(conf)
        
        def test_results(a,b,c):
            self.failUnless(isinstance(a,list))
            self.failUnless(isinstance(b,list))
            self.failUnless(isinstance(c,list))
            l = []
            l.extend(a)
            l.extend(b)
            l.extend(c)
            for p in l:
                self.failUnless(isinstance(p,AbstractPlugin))
        test_results(a,b,c)
        
        conf.do_build = False
        conf.do_update = False
        conf.do_fill_database = False
        conf.debug = False
        (a,b,c) = get_plugins(conf)
        test_results(a,b,c)
