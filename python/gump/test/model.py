#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/test/model.py,v 1.25 2004/07/28 01:26:08 ajack Exp $
# $Revision: 1.25 $
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
from gump.core.model.repository import SCM_TYPE_CVS, SCM_TYPE_SVN
from gump.core.model.state import *
from gump.util import *
from gump.test import getWorkedTestRun
from gump.test.pyunit import UnitTestSuite

import gump.core.model.project

class ModelTestSuite(UnitTestSuite):
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
        self.nant1=self.workspace.getProject('nant1')
        
        self.packagedModule1=self.workspace.getModule('package1')        
        self.module1=self.workspace.getModule('module1')
        self.module2=self.workspace.getModule('module2')
        self.module3=self.workspace.getModule('module3')
        self.module4=self.workspace.getModule('module4')
        self.module5=self.workspace.getModule('module5')

        for p in [self.project1, self.project2, self.project3, self.project4,
                  self.module1, self.module2, self.module3, self.module4]:
            p.resetState()
        
    def suiteTearDown(self):
        self.workspace=None
        self.repo1=None

    def testWorkspace(self):
        self.assertNonZero('Has Log Directory',	\
                    self.workspace.getLogDirectory() )
                    
    def testPackages(self):
        
        #self.package1.dump()
        #self.packagedModule1.dump()
        
        self.assertTrue('Project is package marked', self.package1.isPackageMarked())
        self.assertTrue('Projct is a package', self.package1.isPackaged())
        self.assertTrue('Project Has Outputs', self.package1.hasOutputs())
        
        # Since we now determine if a project is packaged in the complete()
        # method, and module check for this (in it's complete) which runs
        # before the projects ..... oopps.
        #self.assertTrue('Module is a package', self.packagedModule1.isPackaged())
        
    def testNotifys(self):
        
        self.assertTrue('Project1 has notifications', self.project1.hasNotifys())
        self.assertTrue('Module1 has notifications', self.module1.hasNotifys())
        self.assertTrue('Project2 has notifications', self.project2.hasNotifys())
        self.assertFalse('Module2 has NO notifications', self.module2.hasNotifys())
        
        
    def testProject(self):
        
        self.assertEqual('Project1 is type JAVA', 
                            self.project1.getLanguageType(),
                            gump.core.model.project.Project.JAVA_LANGUAGE)
        
        self.assertEqual('NAnt1 is type CSHARP', 
                            self.nant1.getLanguageType(),
                            gump.core.model.project.Project.CSHARP_LANGUAGE)
        
    def testProperties(self):
        properties=project2.getProperties()
        self.assertNotNone('Project2 has properties', project2.hasProperties())
        self.assertNotNone('Project2 has properties', properties)
        self.assertNotEmptyDictionary('Project2 has some properties', properties)
        self.assertEqual('Explicit blank is ok', properties.getProperty('blank-ok'), "")
        self.assertNotNone('Explicit blank is NOT ok', properties.getProperty('blank-bogus'))
        
    def testRepository(self):
        repo1 = self.repo1
        
        #self.web=xml.root.transfer('web')
        #self.assertTrue('Repository WEB',getattr(repo1.xml,'cvsweb').hasString())
        #self.assertNonZeroString('Repository WEB str attr',str(getattr(repo1.xml,'cvsweb')))
        
        self.assertTrue('Repository has WEB',repo1.hasWeb())
        self.assertTrue('Repository is redistributable',repo1.isRedistributable())
        
        self.assertNonZero('Repository WEB',repo1.getWeb())
        self.assertNonZeroString('Repository WEB',repo1.getWeb())        
        
        self.assertTrue('Repository has Modules', repo1.hasModules())
        
        repo2 = self.workspace.getRepository('svn_repository1')  
        self.assertNonZeroString('Repository SVN URL',repo2.getUrl())
        self.assertNonZeroString('Repository Web URL',repo2.getWeb())
        self.assertFalse('Repository has Username',repo2.hasUser())
        self.assertNone('Repository Username',repo2.getUser())
        self.assertFalse('Repository has Password',repo2.hasPassword())
        self.assertNone('Repository Password',repo2.getPassword())

    def testConfigure(self):
        self.assertNotNone('Got project1', self.project1)
        self.assertTrue('Got project1 configure', self.project1.hasConfigure())
        configure = self.project1.getConfigure() 
        self.assertTrue('Has properties', configure.hasProperties())
        properties = configure.getProperties()
        self.assertNotNone('Has properties', properties)
        for prop in properties:
            self.assertNotNone('Has property name', prop.name)
            self.assertNotEmptySequence('Has property name', prop.name)      
            self.assertNotNone('Has property value', prop.value)
            self.assertNotEmptySequence('Has property value', prop.value)      

    def testComparisons(self):
        project1 = self.project1
        project2 = self.project2
        
        if project1 == project2:
            log.error("Different projects match!!!")
        
        if not project1 == project1:
            log.error("Same project not matching!!!")
        
        projects=[]
        projects.append(project1)
   
        
        self.assertInSequence('Project in list',project1,projects)
        self.assertNotInSequence('Project should NOT be in list',project2,projects)
        
        ordered=createOrderedList([ project2, project1, project2, project1])
        
        self.assertAt('Project First', project1, ordered, 0)
        self.assertAt('Project Second', project1, ordered, 1)
        self.assertAt('Project Third', project2, ordered, 2)
        self.assertAt('Project Fourth', project2, ordered, 3)        
    
    def testCvs(self):
        module1=self.module1
        module2=self.module2
        
        self.assertTrue('Module has CVS',
                        module1.getScm().getScmType() == SCM_TYPE_CVS)
        self.assertNonZeroString('CVSROOT',module1.getScm().getCvsRoot())
        self.assertNonZeroString('Has Tag',module1.getScm().getTag())
        self.assertNonZeroString('Has Tag',module2.getTag())
    
    def testSvn(self):
        svnmodule1= self.workspace.getModule('svn_module1')
        
        self.assertTrue('Module has SVN',
                        svnmodule1.getScm().getScmType() == SCM_TYPE_SVN)
        self.assertNonZeroString('SVN URL',svnmodule1.getScm().getRootUrl())
        self.assertTrue('SVN Dir',svnmodule1.getScm().hasDir())
    
    def testDependencyMapping(self):
        
        project1=self.project1
        project2=self.project2
        
        self.assertTrue('Project2 depends upon Project1', project2.hasDirectDependencyOn(project1))
        self.assertTrue('Project1 has Project2 as a Dependee', project1.hasDirectDependee(project2))
        self.assertFalse('Project1 ought NOT have Project1 as a Dependee', project1.hasDirectDependee(project1))
        
    def testStatePropogation(self):
        module1=self.module1
        module2=self.module2
        module3=self.module3
        module4=self.module4
        
        project1=self.project1
        project2=self.project2
        project3=self.project3
        project4=self.project4
        
        self.assertEqual('Initial state should be UNSET',
                         project1.getState(), STATE_UNSET)
        self.assertEqual('Initial state should be UNSET',
                         project2.getState(), STATE_UNSET)
        self.assertEqual('Initial state should be UNSET',
                         project3.getState(), STATE_UNSET)
        self.assertEqual('Initial state should be UNSET',
                         project4.getState(), STATE_UNSET)

        # Make one 'packaged'
        module1.changeState(STATE_COMPLETE, REASON_PACKAGE)
        
        # Make one 'failed'
        module3.changeState(STATE_FAILED)
        
        self.assertNotEqual('Complete State ought NOT propagate down',
                            project1.getState(), STATE_COMPLETE)

        self.assertEqual('State ought propagate to here',
                         project3.getState(), STATE_FAILED)
        self.assertEqual('project4 is a direct dependee of project3',
                         project3.hasDirectDependee(project4), True)
        self.assertNotEqual('State ought NOT propagate like this',
                            project4.getState(), STATE_FAILED)
        self.assertEqual('State ought propagate to here',
                         project4.getState(), STATE_PREREQ_FAILED)
    
    def testMetadataLocations(self):
        module1=self.module1
        project1=self.project1
        
        self.assertNotNone('Ought have a location', module1.getMetadataLocation() )
        self.assertNotNone('Ought have a location', project1.getMetadataLocation() )
    
    def testMaven(self):                
        self.assertTrue('Maven project has a Maven object', self.maven1.hasMaven())
     
    def testNAnt(self):                
        self.assertTrue('NAnt project has a NAnt object', self.nant1.hasNAnt())
 
        
    def testJunitReport(self):
                
        self.assertTrue('This has a <junitreport', self.project3.hasReports())
        self.assertLengthAbove('This has a <junitreport', self.project3.getReports(), 0)
        
        for report in self.project3.getReports():
            self.assertNonZero('Need a directory', report.getResolvedPath())
            
    def testProperties(self):
        self.assertTrue('Has <ant <property', self.project2.getAnt().hasProperties())
        self.assertTrue('Has <workspace <property', self.workspace.hasProperties())
        self.assertTrue('Has <workspace <sysproperty', self.workspace.hasSysProperties())
                
        #print 'Normal Properties:'
        #for property in self.project2.getAnt().getProperties():
        #    print `property`
            
        #print 'Workspace Normal Properties:'
        #for property in self.workspace.getProperties():
        #    print `property`
        
        #print 'Workspace System Properties:'
        #for sysproperty in self.workspace.getSysProperties():
        #    print `sysproperty`
        
        #commandLine=self.builder.getBuildCommand(project2).formatCommandLine()        
        #self.assertInString('Need ant.home', 'ant.home', commandLine)
        #self.assertInString('Need project1.jar', 'project1.jar', commandLine)      
        
        #print 'Command Line:'
        #print commandLine  
        
    def testServers(self):
        self.assertNotEmptySequence('Some servers ought be found', self.workspace.getServers())
        
    def testTrackers(self):
        self.assertNotEmptySequence('Some trackers ought be found', self.workspace.getTrackers())
                        
    def testNotification(self):
        self.assertTrue('Ought allow notify', self.workspace.isNotify())
        
        
