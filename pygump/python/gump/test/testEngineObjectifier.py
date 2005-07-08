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

"""Tests for gump.engine.objectifier"""

import unittest
from pmock import *

import os
from xml.dom import minidom

from gump.engine.objectifier import _add_dependency
from gump.engine.objectifier import MissingDependencyError
from gump.engine.objectifier import Objectifier
from gump.model import Dependency
from gump.model import DependencyInfo
from gump.model import Module
from gump.model import Project
from gump.model import Repository
from gump.model import Workspace

class EngineObjectifierTestCase(MockTestCase):
    def setUp(self):
        self.log = self.mock()
        self.log.stubs().method("debug")
        self.log.stubs().method("info")
        self.log.stubs().method("warning")
        self.log.stubs().method("warn")
        self.log.stubs().method("error")
        self.log.stubs().method("critical")
        self.log.stubs().method("log")
        self.log.stubs().method("exception")
        self.log.stubs().method("close")
        
        self.workdir = os.path.join(os.environ["GUMP_HOME"], "pygump", "unittest", "work")
        if not os.path.isdir(self.workdir):
            os.makedirs(self.workdir)
        
        self.o = Objectifier(self.log,self.workdir)
    
        self.samplexml = """<?xml version="1.0"?>
<workspace 
        version="0.5" 
        name="gump3-unittestworkspace">

<repositories>
    <repository name="ant" type="cvs">
        <title>Ant</title>
        <home-page>http://ant.apache.org/</home-page>
        <cvsweb>http://cvs.apache.org/viewcvs/</cvsweb>
        <redistributable/>
        
        <hostname>cvs.apache.org</hostname>
        <method>pserver</method>
        <path>/home/cvspublic</path>
        <user>anoncvs</user>
        <password>anoncvs</password>
    </repository>

    <repository name="gump" type="svn">
        <title>Gump</title>
        <home-page>http://gump.apache.org/</home-page>
        <web>http://cvs.apache.org/viewcvs.cgi/gump/?root=Apache-SVN</web>
        <url>http://svn.apache.org/repos/asf/gump/branches/Gump3</url>
        <redistributable/>
    </repository>

    <repository name="xml" type="cvs">
        <title>XML</title>
        <home-page>http://xml.apache.org/</home-page>
        <cvsweb>http://cvs.apache.org/viewcvs/</cvsweb>
        <redistributable/>
        
        <hostname>cvs.apache.org</hostname>
        <method>pserver</method>
        <path>/home/cvspublic</path>
        <user>anoncvs</user>
        <password>anoncvs</password>
    </repository>
</repositories>
    
<modules>
    <module name="ant">
        <repository name="ant"/>
        
        <url>http://ant.apache.org/index.html</url>
        <description>Java based build tool</description>
    </module>
    
    <module name="gump-test" path="test">
        <repository name="gump"/>
        
        <url>http://gump.apache.org/index.html</url>
        <description>Gump Testing</description>
    </module>

    <module name="gump">
        <repository name="gump"/>
        
        <url>http://gump.apache.org/index.html</url>
        <description>Python based integration tool</description>
    </module>

    <module name="xml-commons">
        <repository name="xml"/>
    
        <url>htp://xml.apache.org/commons/</url>
        <description>XML commons -- externally defined standards - DOM,SAX,JAXP; plus xml utilities</description>
    </module>

    <module name="xml-xerces">
        <repository name="xml"/>
    
        <url href="http://xml.apache.org/xerces2-j/index.html"/>
        <description>Java XML Parser - the sequel with no equal</description>
    </module>
</modules>

<projects>
    <project name="gump-unit-tests">
        <module name="gump"/>
        <script name="gump">
            <arg name="" value="test"/>
        </script> 
    </project>
    
    <project name="bootstrap-ant">
        <module name="ant"/>
        
        <!-- commands -->
        <script name="bootstrap"/>
        
        <!-- outputs -->
        <home nested="bootstrap"/>
        <jar name="lib/ant.jar"/>
        <jar name="lib/ant-launcher.jar" id="ant-launcher"/>
    </project>
    
    <project name="ant">
        <module name="ant"/>
        
        <!-- commands -->
        <ant/>
        
        <!-- dependencies -->
        <depend project="bootstrap-ant"/>
    </project>

    <project name="xml-apis">
        <module name="xml-commons"/>

        <!-- commands -->
        <ant basedir="java/external"/>

        <!-- outputs -->
        <home nested="java/external/build"/>
        <jar name="xml-apis.jar" type="boot"/>
        
        <!-- dependencies -->
        <depend project="bootstrap-ant"/>
        <depend project="jaxp"/>
    </project>

    <project name="xml-commons-which">
        <module name="xml-commons"/>
        
        <!-- commands -->
        <ant basedir="java" buildfile="which.xml" target="jar" />

        <!-- outputs -->
        <home nested="java/build"/>
        <jar name="which.jar" id="which"/>
        
        <!-- dependencies -->
        <depend project="xml-xerces" />
        <depend project="bootstrap-ant"/>
    </project>

    <project name="xml-commons-resolver">
        <module name="xml-commons"/>
        <depend project="xml-resolver" inherit="jars" />
    </project>

    <project name="xml-resolver">
        <module name="xml-commons"/>

        <!-- commands -->
        <ant basedir="java" buildfile="resolver.xml" target="gump"/>
        
        <!-- outputs -->
        <home nested="java/build"/>
        <jar name="resolver.jar"/>

        <!-- dependencies -->
        <depend project="jaxp"/>
        <depend project="xml-apis"/>
        <depend project="bootstrap-ant" inherit="runtime"/>
    </project>
    
    <project name="jaxp">
        <module name="xml-commons"/>
        <!-- assumed to be provided by JDK -->
    </project>

    <project name="xml-xerces">
        <module name="xml-xerces"/>
        
        <!-- commands -->
        <ant basedir="java" target="jar"/>
        
        <!-- outputs -->
        <home nested="java/build"/>
        <jar name="xercesImpl.jar" id="xml-parser" type="boot"/>
        
        <!-- dependencies -->
        <depend project="bootstrap-ant"/>
        <depend project="xjavac"/>
        <depend project="xml-commons-resolver"/>
        <option project="jaxp" ids="jaxp-api dom sax"/>
    </project>
    
    <project name="xml-xercesImpl">
        <module name="xml-xerces"/>

        <!-- outputs -->
        <home nested="java/build"/>
        <jar name="xercesImpl.jar" id="xercesImpl"/>
        <license name="java/LICENSE"/>

        <!-- dependencies -->
        <depend project="xml-xerces"/>
    </project>
    
    <project name="dist-xerces">
        <module name="xml-xerces"/>

        <!-- commands -->
        <ant basedir="java" target="pack-bin">
            <sysproperty name="build.clonevm" value="true"/>
        </ant>
        
        <!-- dependencies -->
        <depend project="ant" inherit="runtime"/>
        <depend project="xjavac"/>
        <depend project="xalan"/>
        <depend project="xml-xerces"/>
        <depend project="xml-stylebook2"/>
        <depend project="xml-site"/>
    </project>
        
    <project name="xjavac">
        <module name="xml-xerces"/>
        
        <!-- outputs -->
        <home nested="java/tools"/>
        <jar name="bin/xjavac.jar"/>
    </project>

</projects>
</workspace>
"""
        self.sampledom = minidom.parseString(self.samplexml)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.workdir)
    
    def test_MissingDependencyError(self):
        p = "someprojectname"
        d = "somedependencyname"
        e = MissingDependencyError(p,d)
        self.assertEqual(e.project,p)
        self.assertEqual(e.dependency_name,d)
        self.assertTrue(e.__str__().index(p) > 0)
        self.assertTrue(e.__str__().index(d) > 0)

    def test_Objectifier__init__(self):
        o = Objectifier(self.log,self.workdir)
        self.assertEqual(self.log,o.log)
        self.assertEqual(self.workdir,o.workdir)
        
        self.assertRaises(AssertionError, Objectifier, self.log, "")
        self.assertRaises(AssertionError, Objectifier, "", self.workdir)
        
    def test_Objectifier_get_workspace(self):
        w = self.o.get_workspace(self.sampledom)
        self.failUnless(isinstance(w, Workspace))

    def test__add_dependency(self):
        class XMLDependency:
            def __init__(self, project, runtime, inherit, optional, ids=None):
                self.project = project
                self.runtime = runtime
                self.inherit = inherit
                self.optional = optional
                self.ids = ids

            def getAttribute(self, name):
                return getattr(self, name, None)
        
        w = Workspace("bla")
        r = Repository(w, "blabla")
        m = Module(r, "blablabla")
        bla_project = Project(m, "blablablabla")
        other_project = Project(m, "other")
        project_list = {bla_project.name: bla_project, other_project.name: other_project}
        
        d = XMLDependency("other", "true", "all", "true")
        
        _add_dependency(bla_project, d, project_list)
        
        relationships = bla_project.dependencies
        self.assertEqual(1,len(relationships))
        relationship = relationships[0]
        self.assertEqual(relationship.dependency, other_project)
        self.assertEqual(relationship.dependee, bla_project)
        self.assertEqual(1,len(relationship.dependencyInfo))
        info = relationship.dependencyInfo[0]
        self.failUnless(info.runtime)
        self.failUnless(info.optional)
        self.assertEqual("all", info.inherit)
        self.assertEqual(0,len(info.specific_output_ids))
