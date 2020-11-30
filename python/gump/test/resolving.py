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
from gump.test import *
from gump.actor.document.text.resolver import *
from gump.actor.document.xdocs.resolver import *

from gump.test.pyunit import UnitTestSuite


class ResolvingTestSuite(UnitTestSuite):
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
        
        self.module1=self.workspace.getModule('module1')
        self.module2=self.workspace.getModule('module2')    
        self.project1=self.workspace.getProject('project1')    
        self.project2=self.workspace.getProject('project2')    
        self.ant2=self.project2.getAnt()
        
    def checkRelativePath(self,path1,path2):      
        rpath=gump.actor.document.resolver.getRelativePath(path1,path2)
    
        self.assertNotNone('Relative Path: ', rpath)

        #print 'From ' + `path2` + ' to ' + `path1` + \
        #    ' -> ' + `rpath` + ', length ' + `len(rpath)`
    
    def checkLocation(self,object1):
        location=getLocationForObject(object1,'.test')
        #printSeparator()
        self.assertNotNone('Location: ', location)
        self.assertNotNone('Location: ', location.serialize())
    
    def checkRelativeLocation(self,object1,object2):  
        self.assertNotNone('To               : ', object1)
        self.assertNotNone('From             : ', object2)  
        location1=getLocationForObject(object1,'.test')    
        location2=getLocationForObject(object2,'.test')
        location=getRelativeLocation(object1,object2,'.test')
        #printSeparator()
        self.assertNotNone('To       Location: ', location1)
        self.assertNotNone('From     Location: ', location2)
        self.assertNotNone('Relative Location: ', location)
        self.assertNotNone('Relative Location: ', location.serialize())

    def checkResolve(self,object):
        
        #printSeparator()
        self.assertNotNone("Resolved Object: ", object)
        self.assertNotNone("Resolved Object: ", resolver.getDirectory(object))
        self.assertNotNone("Resolved Object: ", resolver.getFile(object))
        self.assertNotNone("Resolved Object: ", resolver.getDirectoryUrl(object))
        self.assertNotNone("Resolved Object: ", resolver.getUrl(object))
        
    def testPaths(self):

        path=Path()
        
        print(path.getPathUp())
        self.assertNotNone('Ought be period.', path.getPathUp())
        
        path1=path.getPostfixed('ABC')
        path2=path1.getPostfixed('DEF')
        path3=path2.getPostfixed(['GHI','JKL'])
        path4=path3.getPrefixed('789')
        path5=path4.getPrefixed(['123','456'])
        self.assertNotNone("Sub-Path 1: ", path1.serialize())
        self.assertNotNone("Sub-Path 2: ", path2.serialize())
        self.assertNotNone("Sub-Path 3: ", path3.serialize())
        self.assertNotNone("Sub-Path 4: ", path4.serialize())
        self.assertNotNone("Sub-Path 5: ", path5.serialize())
    
        # Relative Tests
    
        self.checkRelativePath(['A'],['A'])
        self.checkRelativePath(['A'],['A','B'])
        self.checkRelativePath(['A','B'],['A','B'])
        self.checkRelativePath(['A'],['A','B'])
        self.checkRelativePath(['A','B','C','D','E1'],['A','B','C','D','E2'])
        self.checkRelativePath(['A','B1','C','D','E1'],['A','B2','C','D','E2'])
        
    def testLocations(self):
    
        self.checkLocation(self.workspace)
        self.checkLocation(self.module1)
        self.checkLocation(self.module2)    
        self.checkLocation(self.project1)    
    
        self.checkRelativeLocation(self.project1,self.project1)
        self.checkRelativeLocation(self.project1,self.module1)
        self.checkRelativeLocation(self.module1,self.module2)
        self.checkRelativeLocation(self.module1,self.ant2)
        self.checkRelativeLocation(self.ant2,self.module1)
    
    def testResolving(self):
        
        # :TODO: Restore TextResolver
        # TextResolver('./test/bogus','http://somewhere/something'),	\
        for resolver in [	  XDocResolver('./test/bogus','http://somewhere/something') ] :

            #print `resolver`            
            #printSeparator()
            
            message = "Resolver [" + resolver.__class__.__name__ + "] "
            
            self.assertNotNone(message + "::getDirectory", resolver.getDirectory(self.module1))
            self.assertNotNone(message + "::getFile", resolver.getFile(self.module1))
            self.assertNotNone(message + "::getDirectoryUrl", resolver.getDirectoryUrl(self.module1))
            self.assertNotNone(message + "::getUrl", resolver.getUrl(self.module1))
    
            self.assertNotEmptySequence('Need work on workspace', self.workspace.getWorkList())        
            for work in self.workspace.getWorkList():
                #printSeparator()    
                self.assertNotNone(message + "::work", work)
                self.assertNotNone(message + "::getDirectory", resolver.getDirectory(work))
                self.assertNotNone(message + "::getFile", resolver.getFile(work))
                self.assertNotNone(message + "::getDirectoryUrl", resolver.getDirectoryUrl(work))
                self.assertNotNone(message + "::getUrl", resolver.getUrl(work))
