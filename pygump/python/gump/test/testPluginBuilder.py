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
from unittest import TestCase

from tempfile import mkdtemp
import stat
import os
import sys
from os import mkdir
from os import makedirs
from os.path import abspath
from os.path import isdir
from os.path import join
from shutil import rmtree
from pmock import *

from gump.plugins.builder import ScriptBuilderPlugin

from gump.model import Workspace, Repository, Module, Project, Script, Error

class BuilderTestCase(MockTestCase):
    def test_do_script(self):
        basedir = abspath(mkdtemp())
        try:
            w = Workspace("w")
            mkdir(join(basedir,w.name))
            r = Repository(w,"r")
            mkdir(join(basedir,w.name,r.name))
            m = Module(r,"m")
            mpath = join(basedir,w.name,r.name,m.name)
            mkdir(mpath)
            p = Project(m,"p")
            if sys.platform == "win32":
                scriptpath = join(mpath,"dobuild.bat")
                scriptfile = open(scriptpath, mode='w')
                scriptfile.write("""echo off
echo RESULT
""")
                scriptfile.close()
            else:
                scriptpath = join(mpath,"dobuild")
                scriptfile = open(scriptpath, mode='w')
                scriptfile.write("""#!/bin/sh
    
echo RESULT
""")
                scriptfile.close()
                os.chmod(scriptpath, 0755)

            plugin = ScriptBuilderPlugin(basedir, self.mock())

            cmd = Script(p, "dobuild")
            plugin._do_script(cmd.project, cmd)
            self.assertEqual("RESULT\n", cmd.build_log)
            self.assertEqual(0, cmd.build_exit_status)
            
            cmd = Script(p, "nosuchscript")
            self.assertRaises(Error, plugin._do_script, cmd.project, cmd)
        finally:
            rmtree(basedir)        
