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

class CustomConfig:
    irc = "user@freenode.net/gump"
    
    def __hasattr__(self, name):
        return True
    
    def __getattr__(self, name):
        if name == "paths_work":
            return ConfigTestCase.wd
        
        if name == "project_name":
            return []
        return name

class ConfigTestCase(MockTestCase):
    wd = os.path.join(os.environ["GUMP_HOME"], "pygump", "unittest")

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
        self.mock_log = self.get_mock_logger(CustomConfig(),"bla")
        
        def new_shutdown_logging():
            pass
        
        self.old_shutdown = logging.shutdown
        logging.shutdown = new_shutdown_logging

        # set up working directory
        if not os.path.isdir(self.wd):
            os.makedirs(self.wd)

    def tearDown(self):
        logging.config.fileConfig = self.old_fileConfig
        logging.shutdown = self.old_shutdown
        gump.config.get_logger = self.old_get_logger
        
        import shutil
        shutil.rmtree(self.wd)
    
    def get_mock_logger(self, config, name):
        self.failUnless(unittest.TestCase,
                isinstance(config, Config) or isinstance(config, CustomConfig))
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
    
    def test_get_logger(self):
        logger = self.old_get_logger(CustomConfig(), "bla")
        self.failUnless(isinstance(logger, logging.Logger))

    def test_run_config_hooks(self):
        class MockConfig:
            debug = False
            quiet = False
            local_repository_name = False
            local_module_name = False
        
        mock = MockConfig()
        run_config_hooks(mock)
        
        mock.quiet = True
        run_config_hooks(mock)
        
        mock.debug = True
        run_config_hooks(mock)
        
        mock.local_repository_name = "test"
        run_config_hooks(mock)
        
        mock.local_module_name = "test"
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
        
        class Settings2:
            debug = False
            quiet = False
            def __hasattr__(self, name):
                if name == "paths_pygump" or name == "paths_metadata" or name == "do_mail":
                    return False
                return True
            
            def __getattr__(self, name):
                if name == "paths_pygump" or name == "paths_metadata" or name == "do_mail":
                    raise Exception
                return name

        s = Settings2()
        c = get_config(s)
        self.assertEqual(c.log_level, logging.INFO)

        self.failUnless(c.paths_pygump.find("pygump") > 0)
        self.failUnless(c.paths_metadata.find("metadata") > 0)
        self.failUnless(c.do_mail)
        
        c = Config([])
        self.assertRaises(AttributeError, getattr, c, "bla")
        

    def test_get_plugins(self):
        conf = CustomConfig()
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
        
        conf.irc = False
        conf.do_build = False
        conf.do_update = False
        conf.do_fill_database = False
        conf.debug = False
        (a,b,c) = get_plugins(conf)
        test_results(a,b,c)

    def test_get_plugin(self):
        (a,b,c) = get_plugin(CustomConfig())

    def test_shutdown_logging(self):
        shutdown_logging()

    def test_get_error_handler(self):
        conf = CustomConfig()
        get_error_handler(conf)
        
    def test_get_db(self):
        db = get_db(self.mock_log,CustomConfig())
        self.failUnless(isinstance(db,gump.util.mysql.Database))
    
    def test_get_dom_implementation(self):
        i = get_dom_implementation()
        self.failIfEqual(i, None)
    
    def test_get_error_handler(self):
        e = get_error_handler(CustomConfig())
        self.failUnless(callable(e.handle))
        
    def test_get_engine_loader(self):
        vfs = self.mock()
        vfs.stubs().method("get_as_stream")
        
        l = get_engine_loader(self.mock_log, vfs)
        self.failUnless(callable(l.get_workspace_tree))
        l = get_engine_loader(self.mock_log)
        self.failUnless(callable(l.get_workspace_tree))
    
    def test_get_engine_normalizer(self):
        n = get_engine_normalizer(self.mock_log)
        
    def test_get_engine_objectifier(self):
        o = get_engine_objectifier(CustomConfig(),self.mock_log)
        
    def test_get_engine_verifier(self):
        v = get_engine_verifier(CustomConfig(), get_engine_walker(CustomConfig()))
    
    def test_get_engine_walker(self):
        w = get_engine_walker(CustomConfig())

    def test_get_vfs(self):
        c = CustomConfig()
        c.paths_work = os.path.join(os.environ["GUMP_HOME"], "work", "pygump", "unittests")
        v = get_vfs(c)
        self.failUnless(callable(v.get_as_stream))
        import shutil
        shutil.rmtree(c.paths_work)