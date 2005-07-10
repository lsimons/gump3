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

from gump.model import Error
from gump.model import ModelObject
from gump.model import ExceptionInfo
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
from gump.model import DependencyInfo
from gump.model import DEPENDENCY_INHERIT_ALL
from gump.model import Command
from gump.model import Output
from gump.model import Mkdir
from gump.model import Rmdir
from gump.model import Script
from gump.model import Ant
from gump.model import Jar
from gump.model import Classdir

class ModelTestCase(TestCase):
    def tearDown(self):
        if os.path.exists("bla"):
            import shutil
            shutil.rmtree("bla")

    def test_error(self):
        e = Error()
        try:
            raise e
        except:
            pass
    
    def test_model_object(self):
        m = ModelObject()
        
        string = m.__str__()
        self.failUnless(string.find("ModelObject"))
        
        m.name = "blah"
        string = m.__str__()
        self.failUnless(string.find("blah") > 0)
        
    def test_exception_info(self):
        type = "sometype"
        value = "somevalue"
        traceback = "tr"
        
        e = ExceptionInfo(type, value, traceback)
        self.assertEqual(type, e.type)
        self.assertEqual(value, e.value)
        self.assertEqual(traceback, e.traceback)
        
        string = e.__str__()
        self.failUnless(string.index(type) >= 0)
        self.failUnless(string.index(value) >= 0)
    
    def test_workspace(self):
        name = "blah"
        w = Workspace(name, "bla")
        self.assertEqual(name, w.name)
        self.assertEqual({}, w.repositories)
        self.assertEqual({}, w.modules)
        self.assertEqual({}, w.projects)
        self.assertEqual([], w.dependencies)
        
        self.assertRaises(AssertionError, Workspace, None, "blah")
        Workspace(unicode("blah"), "bla") # unicode is okay too...
        
        r = Repository(w, "booh")
        w.add_repository(r)
        self.assertEqual(r, w.repositories["booh"])
        self.assertEqual(1, len(w.repositories))
        
        self.assertRaises(AssertionError, w.add_repository, r)
        self.assertRaises(AssertionError, w.add_repository, None)
        self.assertRaises(AssertionError, w.add_repository, "blah")
        self.assertEqual(1, len(w.repositories))
        
        w2 = Workspace("blah2", "bla")
        r2 = Repository(w2, "booh2")
        self.assertRaises(AssertionError,w.add_repository,r2)
    
    def test_repository(self):
        wname = "blah"
        w = Workspace(wname, "bla")
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
        w = Workspace(wname, "bla")
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
        w = Workspace(wname, "bla")
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

        url2 = url + "/"
        r = SvnRepository(w,name,url2,title,home_page,cvsweb,redistributable,user,password)
        self.assertEqual(r.url, url)

    def test_module(self):
        wname = "blah"
        w = Workspace(wname, "bla")
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
        w = Workspace(wname, "bla")
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
        w = Workspace(wname, "bla")
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
        w = Workspace(wname, "bla")
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
        w = Workspace(wname, "bla")
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
        w = Workspace(wname, "bla")
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
        w = Workspace(wname, "bla")
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
        self.assertRaises(AssertionError, c.add_dependency, c)
        self.assertEqual(2,len(c.dependencies))
        self.assertEqual(0,len(c.dependees))
        
        self.assertRaises(AssertionError,Dependency,None,c)
        self.assertRaises(AssertionError,Dependency,c,None)
        self.assertRaises(AssertionError,Dependency,"B",c)
        self.assertRaises(AssertionError,Dependency,c,"B")
        
        # reset these vars
        a = Project(m,"A")
        b = Project(m,"B")
        c = Project(m,"C")
        
        d1 = c.get_dependency_on_project(b) # c -> b
        self.assertEqual(c, d1.dependee)
        self.assertEqual(b, d1.dependency)
        self.assertEqual(1, len(c.dependencies))
        self.assertEqual(0, len(c.dependees))
        self.assertEqual(0, len(b.dependencies))
        self.assertEqual(1, len(b.dependees))
        
        d2 = c.get_dependency_on_project(a) # c -> a
        d3 = b.get_dependency_on_project(a) # b -> a
        
        d4 = c.get_dependency_on_project(b)
        self.assertEqual(c, d4.dependee)
        self.assertEqual(b, d4.dependency)
        self.assertEqual(2, len(c.dependencies))
        self.assertEqual(0, len(c.dependees))
        self.assertEqual(1, len(b.dependencies))
        self.assertEqual(1, len(b.dependees))
        self.assertEqual(d1, d4)
        
        c.add_dependency(d1) # c -> b
        
        x = Project(m,"someprojectname")
        y = Project(m,"someotherprojectname")
        d = Dependency(x,y)
        string = d.__str__()
        self.failUnless(string.find(x.name) >= 0)
        self.failUnless(string.find(y.name) >= 0)
        self.failUnless(string.find(y.name) < string.find(x.name))
    
    def test_dependency_info(self):
        wname = "blah"
        w = Workspace(wname, "bla")
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

        optional = True
        runtime = True
        inherit = DEPENDENCY_INHERIT_ALL
        specific_output_id1 = "some-sub-project-jar"
        specific_output_id2 = "some-sub-project-jar2"

        di1 = DependencyInfo(d1,optional,runtime,inherit,specific_output_id1)
        
        self.assertEqual(optional,di1.optional)
        self.assertEqual(inherit,di1.inherit)
        self.assertEqual(specific_output_id1,di1.specific_output_ids)

        self.assertEqual(0,len(d1.dependencyInfo))
        d1.add_dependency_info(di1)
        self.assertEqual(1,len(d1.dependencyInfo))
        self.assertEqual(di1,d1.dependencyInfo[0])
        
        di2 = DependencyInfo(d1,optional,runtime,inherit,specific_output_id2)
        d1.add_dependency_info(di2)
        self.assertEqual(2,len(d1.dependencyInfo))
        self.assertEqual(di1,d1.dependencyInfo[0])
        self.assertEqual(di2,d1.dependencyInfo[1])
        
        di3 = DependencyInfo(d2,optional)
        d2.add_dependency_info(di3)
        self.assertEqual(1,len(d2.dependencyInfo))
        self.assertEqual(di3,d2.dependencyInfo[0])
        self.assertEqual(2,len(d1.dependencyInfo))
        self.assertEqual(di1,d1.dependencyInfo[0])
        self.assertEqual(di2,d1.dependencyInfo[1])
        
        self.assertRaises(AssertionError, d2.add_dependency_info, di2)  

        x = Project(m,"someproject")
        y = Project(m,"someotherproject")
        d = Dependency(x,y)
        optional = True
        runtime = True
        inherit = DEPENDENCY_INHERIT_ALL
        specific_output_id1 = "some-sub-project-jar"
        di = DependencyInfo(d,optional,runtime,inherit,specific_output_id1)
        
        string = di.__str__()
        xstring = x.__str__()
        ystring = y.__str__()
        
        self.failUnless(string.find(xstring) >= 0)
        self.failUnless(string.find(ystring) >= 0)
        self.failUnless(string.find("True") >= 0)
        self.failUnless(string.find("True") >= 0)
        self.failUnless(string.find(DEPENDENCY_INHERIT_ALL) >= 0)
        self.failUnless(string.find(specific_output_id1) >= 0)
        
    def test_command(self):
        wname = "blah"
        w = Workspace(wname, "bla")
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
        
        string = c.__str__()
        self.failUnless(string.find(pname) >= 0)

    def test_mkdir(self):
        wname = "blah"
        w = Workspace(wname, "bla")
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
        
        string = c.__str__()
        self.failUnless(string.find(dir) >= 0)

    def test_rmdir(self):
        wname = "blah"
        w = Workspace(wname, "bla")
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

        string = c.__str__()
        self.failUnless(string.find(dir) >= 0)

    def test_script(self):
        wname = "blah"
        w = Workspace(wname, "bla")
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
        c = Script(p,name,None)
        
        self.assertRaises(AssertionError,Script,None,c)
        self.assertRaises(AssertionError,Script,"someproject",c)
        self.assertRaises(AssertionError,Script,p,None)
        self.assertRaises(AssertionError,Script,p,name,"blah")
        self.assertRaises(AssertionError,Script,p,name,[p])

        c = Script(p,name, args)
        self.assertEqual(args,c.args)

        string = c.__str__()
        self.failUnless(string.find(name) >= 0)
        self.failUnless(string.find(args[0]) >= 0)
        self.failUnless(string.find(args[1]) >= 0)

    def test_ant(self):
        wname = "blah"
        w = Workspace(wname, "bla")
        rname = "booh"
        r = Repository(w,rname)
        mname = "bweh"
        m = Module(r,mname)
        pname = "bwop"
        p = Project(m,pname)
        
        target = "build"
        buildfile = "build-gump.xml"
        a = Ant(p, target, buildfile)
        self.assertEqual(target, a.target)
        self.assertEqual(buildfile, a.buildfile)
        self.assertEqual(p, a.project)
        
        self.assertRaises(AssertionError,Ant,None,target)
        self.assertRaises(AssertionError,Ant,"someproject",a)
        self.assertRaises(AssertionError,Ant,p,None)
        self.assertRaises(AssertionError,Ant,p,target,None)

        a = Ant(p, target, buildfile)
        string = a.__str__()
        self.failUnless(string.find(target) >= 0)
        self.failUnless(string.find(buildfile) >= 0)

    def test_output(self):
        wname = "blah"
        w = Workspace(wname, "bla")
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
        
        o = Output(p,"blah")
        string = o.__str__()
        self.failUnless(string.find("blah") >= 0)

    def test_jar(self):
        wname = "blah"
        w = Workspace(wname, "bla")
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

        o = Jar(p, jar, id=id)
        string = o.__str__()
        self.failUnless(string.find(jar) >= 0)
        self.failUnless(string.find(id) >= 0)

    def test_classdir(self):
        wname = "blah"
        w = Workspace(wname, "bla")
        rname = "booh"
        r = Repository(w,rname)
        mname = "bweh"
        m = Module(r,mname)
        pname = "bwop"
        p = Project(m,pname)
        
        path = "my/path"
        o = Classdir(p,path)
        self.assertEqual(p,o.project)
        self.assertEqual(path,o.path)
        self.assertRaises(AssertionError,Classdir,None,path)
        self.assertRaises(AssertionError,Classdir,"someproject",path)
        self.assertRaises(AssertionError,Classdir,p,None)
        self.assertRaises(AssertionError,Classdir,p,p)
        
        string = o.__str__()
        self.failUnless(string.find(path) >= 0)
