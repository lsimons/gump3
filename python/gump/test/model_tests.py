#!/usr/bin/env python
# $Header:  1.7 2003/05/10 18:20:36 nicolaken Exp $
# $Revision: 1.7 $
# $Date: 2003/05/10 18:20:36 $
#
# ====================================================================
#
# The Apache Software License, Version 1.1
#
# Copyright (c) 2003 The Apache Software Foundation.  All rights
# reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. The end-user documentation included with the redistribution, if
#    any, must include the following acknowlegement:
#       "This product includes software developed by the
#        Apache Software Foundation (http://www.apache.org/)."
#    Alternately, this acknowlegement may appear in the software itself,
#    if and wherever such third-party acknowlegements normally appear.
#
# 4. The names "The Jakarta Project", "Alexandria", and "Apache Software
#    Foundation" must not be used to endorse or promote products derived
#    from this software without prior written permission. For written
#    permission, please contact apache@apache.org.
#
# 5. Products derived from this software may not be called "Apache"
#    nor may "Apache" appear in their names without prior written
#    permission of the Apache Group.
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
# ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# ====================================================================
#
# This software consists of voluntary contributions made by many
# individuals on behalf of the Apache Software Foundation.  For more
# information on the Apache Software Foundation, please see
# <http://www.apache.org/>.

"""
    Model Testing
"""

import os
import logging
import types, StringIO

from gump import log
import gump.config
from gump.model.state import *
from gump.model.loader import WorkspaceLoader
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
                    
        self.project1=self.workspace.getProject('project1')
        self.project2=self.workspace.getProject('project2')             
        self.project3=self.workspace.getProject('project3')
        self.project4=self.workspace.getProject('project4')
        
        self.module1=self.workspace.getModule('module1')
        self.module2=self.workspace.getModule('module2')
        self.module3=self.workspace.getModule('module3')
        self.module4=self.workspace.getModule('module4')
    
        
    def testWorkspace(self):
        self.assertNonZero('Has Log Directory',	\
                    self.workspace.getLogDirectory() )
        
    def testRepository(self):
        repo1 = self.repo1
        
        self.assertNonZero('Repository CVSWEB',repo1.getCvsWeb())
        self.assertNonZeroString('Repository CVSWEB',repo1.getCvsWeb())        
        self.assertTrue('Repository has Modules', repo1.hasModules())

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
    
    def testCVS(self):
        module1=self.module1
        
        self.assertTrue('Module is CVS', module1.isCVS())
        self.assertNonZeroString('CVSROOT',module1.cvs.getCVSRoot())
    
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
        