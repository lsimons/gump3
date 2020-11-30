#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/test/language.py,v 1.1 2004/07/28 01:26:08 ajack Exp $
# $Revision: 1.1 $
#!/usr/bin/env python
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
    Model Testing
"""

import os
import logging
import types, io

from gump import log

import gump.core.config
import gump.core.build.builder
import gump.core.language.java
import gump.core.language.csharp

from gump.core.model.state import *
from gump.util import *
from gump.test import getWorkedTestRun
from gump.test.pyunit import UnitTestSuite

class LanguageTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        #
        # Load a decent Run/Workspace
        #
        self.run=getWorkedTestRun()  
        self.assertNotNone('Needed a run', self.run)
        self.workspace=self.run.getWorkspace()          
        self.assertNotNone('Needed a workspace', self.workspace)
 
        self.repo1=self.workspace.getRepository('repository1')  
                    
        self.package1=self.workspace.getProject('package1')
        
        self.project1=self.workspace.getProject('project1')
        self.project2=self.workspace.getProject('project2')             
        self.project3=self.workspace.getProject('project3')
        self.project4=self.workspace.getProject('project4')
        self.project5=self.workspace.getProject('project5')
        self.alias1=self.workspace.getProject('alias1')
        self.maven1=self.workspace.getProject('maven1')
        
        self.packagedModule1=self.workspace.getModule('package1')        
        self.module1=self.workspace.getModule('module1')
        self.module2=self.workspace.getModule('module2')
        self.module3=self.workspace.getModule('module3')
        self.module4=self.workspace.getModule('module4')
        self.module5=self.workspace.getModule('module5')
        
        self.builder=gump.core.build.builder.GumpBuilder(self.run)
        self.java=gump.core.language.java.JavaHelper(self.run)
        
    def suiteTearDown(self):
        self.run=None
        self.workspace=None
        self.repo1=None

    def testClasspaths(self):
        
        (classpath,bootclasspath)=self.java.getClasspaths(self.project1)
        (classpath,bootclasspath)=self.java.getClasspaths(self.project4)
        (classpath,bootclasspath)=self.java.getClasspaths(self.alias1)
        (classpath,bootclasspath)=self.java.getClasspaths(self.project5)        
        #print "Classpath:" + classpath     
        #print "Bootclasspath:" + bootclasspath
   
    def testNoClasspath(self):
        
        tested=False
        for depend in self.project5.getDirectDependencies():
            if self.project4 == depend.getProject():
                tested=True
                self.assertTrue('NoClasspath', depend.isNoClasspath())
        self.assertTrue('Did a NoClasspath test', tested)
                
        tested=False          
        for depend in self.project4.getDirectDependencies():
            tested=True           
            self.assertFalse('Not NoClasspath', depend.isNoClasspath())
        self.assertTrue('Did a NOT NoClasspath test', tested)
        
    def testNoClasspathOnProperty(self):  
        self.assertFalse('<ant <property does NOT gives full dependency (noclasspath)',	\
                self.project3.hasFullDependencyOnNamedProject('project2'))
                
        (classpath,bootclasspath)=self.java.getClasspathObjects(self.project3)
        
        for pathPart in classpath.getSimplePathList():
            #print "pathPart:" + `pathPart`
            self.assertNotSubstring('Ought not get output2.jar from project2',	\
                    'output2.jar',	\
                    pathPart)
        
    def testClasspathOnDepend(self):
        for depend in self.project3.getDirectDependencies():
            print("Depend:" + repr(depend))        
        else:
            print('No p3 deps:')
            
        self.assertTrue('<ant <depend gives full dependency (classpath)', \
                self.project3.hasFullDependencyOnNamedProject('project1'))
                
        (classpath,bootclasspath)=self.java.getClasspathObjects(self.project3)
        
        found=0
        for pathPart in classpath.getSimplePathList():
            if not -1 == pathPart.find('output1.jar'):
                found=1
            
        self.assertTrue('Ought find output1.jar', found)
  
