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

    Artifact/Repository Testing
    
"""

import os
import logging

from gump import log
import gump.core.config
from gump.test import getWorkedTestRun
from gump.test.pyunit import UnitTestSuite

import gump.actor.repository.artifact
import gump.actor.repository.publisher

class ArtifactsTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
        self.testRepo = 'test/repo/'
        self.license  = 'test/LICENSE'
        self.jar1  = 'test/output1.jar'
        
    def suiteSetUp(self):
        # Create a repository
        self.repo=gump.actor.repository.artifact.ArtifactRepository(self.testRepo)
        
        # Create some test files
        open(self.license,'w').close()
        open(self.jar1,'w').close()
        
        # Load a decent Run/Workspace
        self.run=getWorkedTestRun()  
        self.assertNotNone('Needed a run', self.run)
        self.workspace=self.run.getWorkspace()          
        self.assertNotNone('Needed a workspace', self.workspace)
      
    def testPublishLicense(self):
        self.repo.publish('testGroup',self.license)
    
    def testPublishJar(self):
        self.repo.publish('testGroup',self.jar1,'id1')
        
    def testPublisher(self):
        p=gump.actor.repository.publisher.RepositoryPublisher(self.run)
        p.processProject(self.workspace.getProject('project1'))
            
    def testRepositoryExtract(self):
        # Create a repository & populate it
        self.repo=gump.actor.repository.artifact.ArtifactRepository(self.testRepo)   
        self.testPublishJar()
         
        (dated, latest)=self.repo.extractGroup('testGroup')
        
        self.assertNotNone('Extracted something', dated)
        
    def testRepositoryExtract2(self):
        # Create a repository & populate it
        self.repo=gump.actor.repository.artifact.ArtifactRepository(self.testRepo)   
        
        gdir=self.repo.getGroupDir('test')
        
        open(os.path.join(gdir,'id1-gump-20030221.jar'),'w').close()
        open(os.path.join(gdir,'id1-gump-20040221.jar'),'w').close()
        open(os.path.join(gdir,'id1-gump-20050221.jar'),'w').close()
        open(os.path.join(gdir,'id2-gump-20030221.jar'),'w').close()
        open(os.path.join(gdir,'id2-gump-20040221.jar'),'w').close()
        open(os.path.join(gdir,'id2-gump-20050221.jar'),'w').close()
        open(os.path.join(gdir,'id3-gump-20030221.jar'),'w').close()
        open(os.path.join(gdir,'id3-gump-20040221.jar'),'w').close()
        open(os.path.join(gdir,'id3-gump-20050221.jar'),'w').close()
        open(os.path.join(gdir,'id4-gump-20050221.jar'),'w').close()
        
        (dated, latest)=self.repo.extractGroup('test')
        
        #import pprint
        #pprint.pprint(dated)
        
        self.assertNotNone('Extracted something', dated)
        self.assertEqual('Extracted correct groups', len(list(dated.keys())), 3)
        self.assertEqual('Detected correct latest', latest, '20050221')
        
