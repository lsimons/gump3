#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/test/model.py,v 1.23 2004/07/14 20:47:02 ajack Exp $
# $Revision: 1.23 $
#!/usr/bin/env python
# Copyright 2003-2004 The Apache Software Foundation
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
"""
    Model Testing
"""

import os
import logging
import types, StringIO

from gump import log
import gump.core.config
from gump.model.state import *
from gump.utils import *
from gump.test import getWorkedTestWorkspace
from gump.test.pyunit import UnitTestSuite

class ModelTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        #
        # Load a decent Workspace
        #
        self.workspace=getWorkedTestWorkspace() 
         
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
        
    def setTearDown(self):
        self.workspace=None
        self.repo1=None

    def testWorkspace(self):
        self.assertNonZero('Has Log Directory',	\
                    self.workspace.getLogDirectory() )
                    
    def testPackages(self):
        
        self.package1.dump()
        
        self.assertTrue('Is a package marked', self.package1.isPackageMarked())
        self.assertTrue('Is a package', self.package1.isPackaged())
        self.assertTrue('Has Jars', self.package1.hasJars())
        self.assertTrue('Is a package', self.packagedModule1.isPackaged())
        
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

    def testComparisons(self):
        project1 = self.project1
        project2 = self.project2
        
        if project1 == project2:
            log.error("Different projects match!!!")
        
        if not project1 == project1:
            log.error("Same project not matching!!!")
        
        projects=[]
        projects.append(project1)
   
        
        self.assertIn('Project in list',project1,projects)
        self.assertNotIn('Project NOT in list',project2,projects)
        
        ordered=createOrderedList([ project2, project1, project2, project1])
        
        self.assertAt('Project First', project1, ordered, 0)
        self.assertAt('Project Second', project1, ordered, 1)
        self.assertAt('Project Third', project2, ordered, 2)
        self.assertAt('Project Fourth', project2, ordered, 3)        
    
    def testCvs(self):
        module1=self.module1
        module2=self.module2
        
        self.assertTrue('Module has CVS', module1.hasCvs())
        self.assertFalse('Module has NOT SVN', module1.hasSvn())
        self.assertNonZeroString('CVSROOT',module1.cvs.getCvsRoot())
        self.assertNonZeroString('Has Tag',module1.cvs.getTag())
        self.assertNonZeroString('Has Tag',module2.getTag())
    
    def testSvn(self):
        svnmodule1= self.workspace.getModule('svn_module1')
        
        self.assertTrue('Module has SVN', svnmodule1.hasSvn())
        self.assertFalse('Module has NOT CVS', svnmodule1.hasCvs())
        self.assertNonZeroString('SVN URL',svnmodule1.svn.getRootUrl())
        self.assertTrue('SVN Dir',svnmodule1.svn.hasDir())
    
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
        
        # Make one 'packaged'
        module1.changeState(STATE_COMPLETE,REASON_PACKAGE)
        
        # Make one 'failed'
        module3.changeState(STATE_FAILED)
        
        self.assertNotEqual('Complete State ought NOT propagate down', project1.getState(), STATE_COMPLETE)
        
        self.assertEqual('State ought propagate to here', project4.getState(), STATE_PREREQ_FAILED)
        self.assertNotEqual('State ought NOT propagate like this', project4.getState(), STATE_FAILED)
    
    def testMetadataLocations(self):
        module1=self.module1
        project1=self.project1
        
        self.assertNotEmpty('Ought have a location', module1.getMetadataLocation() )
        self.assertNotEmpty('Ought have a location', project1.getMetadataLocation() )
        
    def testClasspaths(self):
        
        (classpath,bootclasspath)=self.project1.getClasspaths()
        (classpath,bootclasspath)=self.project4.getClasspaths()
        (classpath,bootclasspath)=self.alias1.getClasspaths()
        (classpath,bootclasspath)=self.project5.getClasspaths(1)        
        #print "Classpath:" + classpath     
        #print "Bootclasspath:" + bootclasspath
        
    def testMaven(self):                
        self.assertTrue('Maven project has a Maven object', self.maven1.hasMaven())
                 
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
                
        (classpath,bootclasspath)=self.project3.getClasspathObjects()
        
        for pathPart in classpath.getSimpleClasspathList():
            #print "pathPart:" + `pathPart`
            self.assertNotSubstring('Ought not get output2.jar from project2',	\
                    'output2.jar',	\
                    pathPart)
        
    def testClasspathOnDepend(self):
        for depend in self.project3.getDirectDependencies():
            print "Depend:" + `depend`        
        else:
            print 'No p3 deps:'
            
        self.assertTrue('<ant <depend gives full dependency (classpath)', \
                self.project3.hasFullDependencyOnNamedProject('project1'))
                
        (classpath,bootclasspath)=self.project3.getClasspathObjects()
        
        found=0
        for pathPart in classpath.getSimpleClasspathList():
            if not -1 == pathPart.find('output1.jar'):
                found=1
            
        self.assertTrue('Ought find output1.jar', found)
        
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
        self.assertNotEmpty('Some servers ought be found', self.workspace.getServers())
        
    def testTrackers(self):
        self.assertNotEmpty('Some trackers ought be found', self.workspace.getTrackers())
                        
    def testNotification(self):
        self.assertTrue('Ought allow notify', self.workspace.isNotify())
        
        