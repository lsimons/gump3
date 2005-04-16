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
from gump.model import SvnRepository
from gump.model import Project
from gump.model import CvsModule
from gump.model import SvnModule
from gump.model import Dependency
from gump.model import DEPENDENCY_INHERIT_ALL
from gump.model import Command
from gump.model import Output
from gump.model import Mkdir
from gump.model import Rmdir
from gump.model import Script
from gump.model import Homedir
from gump.model import OUTPUT_ID_HOME
from gump.model import Jar

class ModelTestCase(TestCase):
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
        Workspace(unicode("blah")) # unicode is okay too...
        
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
        Repository(w,unicode("blah")) # unicode is okay too...

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

    def test_svn_repository(self):
        wname = "blah"
        w = Workspace(wname)
        name = "booh"
        url = "http://svn.somewhere.org/some/svn/repo"
        title = "t"
        home_page = "h"
        cvsweb = "c"
        redistributable = True
        user = "anonymous"
        password = "blah"
        
        r = SvnRepository(w,name,url,title,home_page,cvsweb,redistributable,user,password)
        self.assertEqual(w, r.workspace)
        self.assertEqual(name, r.name)
        self.assertEqual(url, r.url)
        self.assertEqual(title, r.title)
        self.assertEqual(home_page, r.home_page)
        self.assertEqual(cvsweb, r.cvsweb)
        self.assertEqual(redistributable, r.redistributable)
        self.assertEqual(user, r.user)
        self.assertEqual(password, r.password)
        self.assertEqual({}, r.modules)
        
        r = SvnRepository(w,name,url,user=user)
        self.assertEqual(user, r.user)
        r = SvnRepository(w,name,url,password=password)
        self.assertEqual(password, r.password)
        
        self.assertRaises(AssertionError, SvnRepository, w, name, w)
    
    def test_module(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        
        url = "http://www.somewhere.org/bweh/"
        description = "Bweh is foo bar blah."
        
        name = "bweh"
        m = Module(r,name,url,description)
        self.assertEqual(r, m.repository)
        self.assertEqual(name,m.name)
        self.assertEqual(url,m.url)
        self.assertEqual(description,m.description)
        self.assertEqual({}, m.projects)
        
        self.assertRaises(AssertionError, Module, None, name)
        self.assertRaises(AssertionError, Module, name, None)
        self.assertRaises(AssertionError, Module, "wrong", name)
        self.assertRaises(AssertionError, Module, r, r)
        Module(r,unicode("blah")) # unicode is okay too...
        
        m = Module(r,name,url=url)
        self.assertEqual(url,m.url)
        m = Module(r,name,description=description)
        self.assertEqual(description, description)
        
        m = Module(r, name)
        pname = "blaat"
        p = Project(m,pname)
        m.add_project(p)
        self.assertEqual(p,m.projects[pname])
        self.assertEqual(1,len(m.projects))
        
        self.assertRaises(AssertionError, m.add_project, None)
        self.assertRaises(AssertionError, m.add_project, "blaaaa")
        self.assertRaises(AssertionError, m.add_project, p)
        self.assertEqual(1,len(m.projects))
    
    def test_module_is_added_to_workspace_by_repository(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        r2name = "booh2"
        r2 = Repository(w,r2name)
        
        url = "http://www.somewhere.org/bweh/"
        description = "Bweh is foo bar blah."
        name = "bweh"
        m = Module(r,name,url,description)

        url2 = "http://www.somewhere.org/bweh2/"
        description2 = "Bweh2 is foo bar blah."
        name = "bweh"
        m2 = Module(r,name,url,description)
        
        r.add_module(m)
        self.assert_(w.modules.has_key(name))
        self.assert_(m, w.modules.get(name))
        
        self.assertRaises(AssertionError,r.add_module,m2)
        
    def test_cvs_module(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        
        url = "http://www.somewhere.org/bweh/"
        description = "Bweh is foo bar blah."
        tag = "VERSION_1_0"
        
        name = "bweh"
        m = CvsModule(r,name,tag,url,description)
        self.assertEqual(r, m.repository)
        self.assertEqual(name,m.name)
        self.assertEqual(tag,m.tag)
        self.assertEqual(url,m.url)
        self.assertEqual(description,m.description)
        self.assertEqual({}, m.projects)
        
        m = CvsModule(r,name,tag=tag)
        self.assertEqual(tag,m.tag)

    def test_svn_module(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        
        url = "http://www.somewhere.org/bweh/"
        description = "Bweh is foo bar blah."
        path = "some/where"
        
        name = "bweh"
        m = SvnModule(r,name,path,url,description)
        self.assertEqual(r, m.repository)
        self.assertEqual(name,m.name)
        self.assertEqual(path,m.path)
        self.assertEqual(url,m.url)
        self.assertEqual(description,m.description)
        self.assertEqual({}, m.projects)
        
    def test_project(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        mname = "bweh"
        m = Module(r,mname)
        
        name = "bwop"
        p = Project(m,name)
        self.assertEqual(m, p.module)
        self.assertEqual(name,p.name)
        self.assertEqual([],p.dependees)
        self.assertEqual([],p.dependencies)
        self.assertEqual([],p.commands)
        self.assertEqual([],p.outputs)
        
        self.assertRaises(AssertionError, Project, None, name)
        self.assertRaises(AssertionError, Project, name, None)
        self.assertRaises(AssertionError, Project, "wrong", name)
        self.assertRaises(AssertionError, Project, m, m)
        Project(m,unicode("blah")) # unicode is okay too...
        
        # note that dependencies are tested in test_dependencies...
        
        c = Command(p)
        p.add_command(c)
        self.assertEqual(c,p.commands[0])
        self.assertEqual(1,len(p.commands))
        p.add_command(c)
        self.assertEqual(c,p.commands[1])
        self.assertEqual(2,len(p.commands))
        
        self.assertRaises(AssertionError,p.add_command,None)
        self.assertRaises(AssertionError,p.add_command,"stop!")
        
        o = Output(p)
        p.add_output(o)
        self.assertEqual(o,p.outputs[0])
        self.assertEqual(1,len(p.outputs))
        p.add_output(o)
        self.assertEqual(o,p.outputs[1])
        self.assertEqual(2,len(p.outputs))
    
        self.assertRaises(AssertionError,p.add_output,None)
        self.assertRaises(AssertionError,p.add_output,"jarfile!")
        
    def test_project_is_added_to_workspace_by_module(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        url = "http://www.somewhere.org/bweh/"
        description = "Bweh is foo bar blah."
        mname = "bweh"
        m = Module(r,mname,url,description)
        m2name = "bweh2"
        m2 = Module(r,m2name,url,description)

        name = "ugh"
        p = Project(m,name)
        p2 = Project(m2,name)
        
        m.add_project(p)
        self.assert_(w.projects.has_key(name))
        self.assert_(p, w.projects.get(name))
        
        self.assertRaises(AssertionError,m2.add_project,p2)
        
    def test_dependencies(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        mname = "bweh"
        m = Module(r,mname)
        #      A
        #      ^
        #      |
        #     / \
        #    B<--C
        a = Project(m,"A")
        b = Project(m,"B")
        c = Project(m,"C")
        
        d1 = Dependency(b,c) # c -> b
        d2 = Dependency(a,c) # c -> a
        d3 = Dependency(a,b) # b -> a
        
        c.add_dependency(d1) # c -> b
        self.assertEqual(d1,c.dependencies[0])
        self.assertEqual(1,len(c.dependencies))
        self.assertEqual(0,len(c.dependees))
        self.assertEqual(d1,b.dependees[0])
        self.assertEqual(0,len(b.dependencies))
        self.assertEqual(1,len(b.dependees))
        
        c.add_dependency(d2) # c -> a
        self.assertEqual(d2,c.dependencies[1])
        self.assertEqual(2,len(c.dependencies))
        self.assertEqual(0,len(c.dependees))
        self.assertEqual(d2,a.dependees[0])
        self.assertEqual(0,len(a.dependencies))
        self.assertEqual(1,len(a.dependees))

        b.add_dependency(d3) # b -> a
        self.assertEqual(d3,b.dependencies[0])
        self.assertEqual(1,len(b.dependencies))
        self.assertEqual(1,len(b.dependees))
        self.assertEqual(d3,a.dependees[1])
        self.assertEqual(0,len(a.dependencies))
        self.assertEqual(2,len(a.dependees))
        
        self.assertRaises(AssertionError, c.add_dependency, None)
        self.assertRaises(AssertionError, c.add_dependency, "blaaaa")
        self.assertRaises(AssertionError, c.add_dependency, b)
        self.assertEqual(2,len(c.dependencies))
        self.assertEqual(0,len(c.dependees))
        
        # TODO: test DependencyInfo
        #optional = True
        #runtime = True
        #inherit = DEPENDENCY_INHERIT_ALL
        #specific_output_id = "some-sub-project-jar"
        #d = Dependency(c,b,optional,runtime,inherit,specific_output_id)
        #self.assertEqual(c,d.dependency)
        #self.assertEqual(b,d.dependee)
        #self.assertEqual(optional,d.optional)
        #self.assertEqual(inherit,d.inherit)
        #self.assertEqual(specific_output_id,d.specific_output_id)
        
        #d = Dependency(dependency=c,dependee=b,optional=False)
        #self.assertEqual(c,d.dependency)
        #self.assertEqual(b,d.dependee)
        #self.assertEqual(False,d.optional)
        
        #d = Dependency(dependency=c,dependee=b,inherit=False)
        #self.assertEqual(c,d.dependency)
        #self.assertEqual(b,d.dependee)
        #self.assertEqual(False,d.inherit)
        
        #d = Dependency(dependency=c,dependee=b,specific_output_id="blah")
        #self.assertEqual(c,d.dependency)
        #self.assertEqual(b,d.dependee)
        #self.assertEqual("blah",d.specific_output_id)
        
        self.assertRaises(AssertionError,Dependency,None,c)
        self.assertRaises(AssertionError,Dependency,c,None)
        self.assertRaises(AssertionError,Dependency,"B",c)
        self.assertRaises(AssertionError,Dependency,c,"B")
    
    def test_command(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        mname = "bweh"
        m = Module(r,mname)
        pname = "bwop"
        p = Project(m,pname)
        
        c = Command(p)
        self.assertEqual(p,c.project)
        self.assertRaises(AssertionError,Command,None)
        self.assertRaises(AssertionError,Command,"someproject")
        
    def test_mkdir(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        mname = "bweh"
        m = Module(r,mname)
        pname = "bwop"
        p = Project(m,pname)
        
        dir = "some/dir"
        c = Mkdir(p,dir)
        self.assertEqual(dir,c.directory)
        
        self.assertRaises(AssertionError,Mkdir,None,c)
        self.assertRaises(AssertionError,Mkdir,"someproject",c)
        self.assertRaises(AssertionError,Mkdir,p,None)
        self.assertRaises(AssertionError,Mkdir,p,p)

    def test_rmdir(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        mname = "bweh"
        m = Module(r,mname)
        pname = "bwop"
        p = Project(m,pname)
        
        dir = "some/dir"
        c = Rmdir(p,dir)
        self.assertEqual(dir,c.directory)
        
        self.assertRaises(AssertionError,Rmdir,None,c)
        self.assertRaises(AssertionError,Rmdir,"someproject",c)
        self.assertRaises(AssertionError,Rmdir,p,None)
        self.assertRaises(AssertionError,Rmdir,p,p)

    def test_script(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        mname = "bweh"
        m = Module(r,mname)
        pname = "bwop"
        p = Project(m,pname)
        
        name = "build"
        args = ["-d", "some/dir"]
        c = Script(p,name, args)
        self.assertEqual(name,c.name)
        self.assertEqual(args,c.args)
        c = Script(p,name)
        self.assertEqual(name,c.name)
        self.assertEqual([],c.args)
        
        self.assertRaises(AssertionError,Script,None,c)
        self.assertRaises(AssertionError,Script,"someproject",c)
        self.assertRaises(AssertionError,Script,p,None)
        self.assertRaises(AssertionError,Script,p,name,None)
        self.assertRaises(AssertionError,Script,p,name,"blah")
        self.assertRaises(AssertionError,Script,p,name,[p])

    def test_output(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        mname = "bweh"
        m = Module(r,mname)
        pname = "bwop"
        p = Project(m,pname)
        
        o = Output(p)
        self.assertEqual(p,o.project)
        self.assertRaises(AssertionError,Output,None)
        self.assertRaises(AssertionError,Output,"someproject")
        
    def test_homedir(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        mname = "bweh"
        m = Module(r,mname)
        pname = "bwop"
        p = Project(m,pname)
        
        dir = "some/dir"
        o = Homedir(p,dir)
        self.assertEqual(p,o.project)
        self.assertEqual(dir,o.directory)
        self.assertEqual(OUTPUT_ID_HOME,o.id)
        self.assertRaises(AssertionError,Homedir,None,dir)
        self.assertRaises(AssertionError,Homedir,"someproject",dir)
        self.assertRaises(AssertionError,Homedir,p,None)
        self.assertRaises(AssertionError,Homedir,p,p)
        
    def test_jar(self):
        wname = "blah"
        w = Workspace(wname)
        rname = "booh"
        r = Repository(w,rname)
        mname = "bweh"
        m = Module(r,mname)
        pname = "bwop"
        p = Project(m,pname)
        
        jar = "my.jar"
        o = Jar(p,jar)
        self.assertEqual(p,o.project)
        self.assertEqual(jar,o.name)
        self.assertRaises(AssertionError,Jar,None,jar)
        self.assertRaises(AssertionError,Jar,"someproject",jar)
        self.assertRaises(AssertionError,Jar,p,None)
        self.assertRaises(AssertionError,Jar,p,p)
        
        id = "blah"
        bootclass = True
        o = Jar(p, jar, id, bootclass)
        self.assertEqual(p,o.project)
        self.assertEqual(jar,o.name)
        self.assertEqual(id,o.id)
        self.assertEqual(bootclass,o.add_to_bootclass_path)

        o = Jar(p, jar, id=id)
        self.assertEqual(id,o.id)
        o = Jar(p, jar, add_to_bootclass_path=bootclass)
        self.assertEqual(bootclass,o.add_to_bootclass_path)
        

# this is used by testrunner.py to determine what tests to run
def test_suite():
    return unittest.makeSuite(ModelTestCase,'test')

# this allows us to run this test by itself from the commandline
if __name__ == '__main__':
    unittest.main()