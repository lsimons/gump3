#!/usr/bin/env python
# $Header: /home/stefano/cvs/gump/python/gump/test/stats.py,v 1.8 2004/02/17 21:54:21 ajack Exp $
# $Revision: 1.8 $
# $Date: 2004/02/17 21:54:21 $
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
from gump.output.statsdb import *
from gump.test import getWorkedTestWorkspace
from gump.test.pyunit import UnitTestSuite

class StatsTestSuite(UnitTestSuite):
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
        self.module1=self.workspace.getModule('module1')
    
        self.statsDB=StatisticsDB(dir.test,'test.db')
        
    def testGetStats(self):
        self.statsDB.getProjectStats(self.project1.getName())
        self.statsDB.getModuleStats(self.module1.getName())
        self.statsDB.getRepositoryStats(self.repo1.getName())
        
        
    def testPutStats(self):
        ps1=self.statsDB.getProjectStats(self.project1.getName())
        ms1=self.statsDB.getModuleStats(self.module1.getName())
        rs1=self.statsDB.getRepositoryStats(self.repo1.getName())
                
        self.statsDB.putProjectStats(ps1)
        self.statsDB.putModuleStats(ms1)
        self.statsDB.putRepositoryStats(rs1)
              
    def testGetChangePutGetCheckStats(self):
        # Get 1
        ps1=self.statsDB.getProjectStats(self.project1.getName())
        ms1=self.statsDB.getModuleStats(self.module1.getName())
        rs1=self.statsDB.getRepositoryStats(self.repo1.getName())
                
        # Change
        ps1s = ps1.successes
        ps1.successes += 1
        
        ps1f = ps1.failures
        ps1.failures += 1
        
        ps1p = ps1.prereqs
        ps1.prereqs += 1
        
        ps1seq = ps1.sequenceInState
        ps1.sequenceInState += 1
        
        # Put        
        self.statsDB.putProjectStats(ps1)
        self.statsDB.putModuleStats(ms1)
        self.statsDB.putRepositoryStats(rs1)
        
        # Get 2
        ps2=self.statsDB.getProjectStats(self.project1.getName())
        ms2=self.statsDB.getModuleStats(self.module1.getName())
        rs2=self.statsDB.getRepositoryStats(self.repo1.getName())
            
        if not os.name == 'dos' and not os.name == 'nt':  
            self.assertGreater('Incremented Successes', ps2.successes, ps1s )
            self.assertGreater('Incremented Failures', ps2.failures, ps1f )
            self.assertGreater('Incremented Prereqs', ps2.prereqs, ps1p )
            self.assertGreater('Incremented SequenceInState', ps2.sequenceInState, ps1seq )
        
        #print str(ps1s) + ' : ' + str(ps1f) + ' : ' + str(ps1p) + ' : ' + str(ps1seq)
        
        self.statsDB.sync()
        
    def testLoadAndUpdateStats(self):
        self.statsDB.loadStatistics(self.workspace)
        
        # Mark Updated (so we get an updated reading)
        self.module1.setUpdated(1)
        
        self.statsDB.updateStatistics(self.workspace)   
        
        lastUpdated=self.module1.getLastUpdated()
        
        # Give some padding.
        lastUpdated -= (60*60*7)
        
        rough=getGeneralDifferenceDescription(default.time, lastUpdated)
        self.assertNonZeroString('Date Diff String', rough)
        self.assertNotSubstring('Date Diff String', 'year', rough)        
     
        