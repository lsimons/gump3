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
from os import mkdir
from os import makedirs
from os.path import abspath
from os.path import isdir
from os.path import join

from shutil import rmtree

from gump.plugins.dirbuilder import MkdirBuilderPlugin
from gump.plugins.dirbuilder import RmdirBuilderPlugin

from gump.model import Error, Workspace, Repository, Module, Project, Mkdir, Rmdir

class DirBuilderTestCase(TestCase):
    def test_do_rmdir(self):
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

            cmd = Rmdir(p,"somedir")

            plugin = RmdirBuilderPlugin(basedir)
            
            makedirs(join(mpath, cmd.directory, "nested", "stuff", "here"))
            plugin._do_rmdir(cmd.project, cmd.directory)
            self.assertFalse(isdir(join(mpath,cmd.directory)))
            self.assert_(isdir(join(mpath)))
        finally:
            rmtree(basedir)
        
    def test_do_mkdir(self):
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

            cmd = Mkdir(p,"somedir")
        
            plugin = MkdirBuilderPlugin(basedir)
            
            plugin._do_mkdir(cmd.project, cmd.directory)
            self.assert_(isdir(join(mpath,cmd.directory)))
            rmtree(join(mpath,cmd.directory))
            
            plugin._do_mkdir(cmd.project, "some/nested/directory")
            self.assert_(isdir(join(mpath,"some/nested/directory")))
            rmtree(join(mpath,"some/nested/directory"))

            p.add_command(cmd)
            cmd2 = Mkdir(p,"somedir2")
            p.add_command(cmd2)
            cmd3 = Rmdir(p,"elsewhere")
            p.add_command(cmd3)
            plugin.visit_project(p)
            
            self.assert_(isdir(join(mpath,cmd.directory)))
            self.assert_(isdir(join(mpath,cmd2.directory)))
            self.assertFalse(isdir(join(mpath,cmd3.directory)))
            rmtree(join(mpath,cmd.directory))
            
            # failure on bad path
            cmd = Mkdir(p,join("..", "..", "..", "somedir"))
            self.assertRaises(Error, plugin._do_mkdir, cmd.project, cmd.directory)

            # failure on bad file
            cmd = Mkdir(p,"somedir")
            file = open(join(mpath,cmd.directory),"w")
            file.write("blah")
            file.close()
            self.assertRaises(Error, plugin._do_mkdir, cmd.project, cmd.directory)
        finally:
            rmtree(basedir)

# this is used by testrunner.py to determine what tests to run
def test_suite():
    return unittest.makeSuite(DirBuilderTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()
