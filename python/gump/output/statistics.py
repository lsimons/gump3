#!/usr/bin/env python

# $Header: /home/cvspublic/jakarta-gump/python/gump/conf.py,v 1.7 2003/05/10 18:20:36 nicolaken Exp $
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
    Statistics gathering/manipulation
"""

import time
import os
import sys
import logging
import anydbm

from gump import log
from gump.config import *
from gump.model.project import Project
from gump.model.state import *

class ProjectStatistics:
    """Statistics Holder"""
    def __init__(self,projectname):
        self.projectname=projectname
        self.successes=0
        self.failures=0
        self.prereqs=0
        self.first=''
        self.last=''
        self.currentState=STATE_UNSET
        self.previousState=STATE_UNSET
        self.sequenceInState=0
        
    def getFOGFactor(self):
        return (self.successes - self.failures - self.prereqs)
        
    def nameKey(self):
        return self.projectname + '-pname'
        
    def successesKey(self):
        return self.projectname + '-successes'
        
    def failuresKey(self):
        return self.projectname + '-failures'
        
    def prereqsKey(self):
        return self.projectname + '-prereqs'
        
    def firstKey(self):
        return self.projectname + '-first'
        
    def lastKey(self):
        return self.projectname + '-last'
        
    def currentStateKey(self):
        return self.projectname + '-current-state'
        
    def previousStateKey(self):
        return self.projectname + '-previous-state'
        
    def sequenceInStateKey(self):
        return self.projectname + '-state-seq'
        
    def update(self,project):        
        #
        # Update based off current run
        #
        if project.isSuccess():
            self.successes += 1
            self.last = time.time()
            
            # A big event...
            if not self.first:
                self.first=self.last
            elif project.isFailed():
                s.failures += 1    
            elif project.isPrereqFailure():                        
                s.prereqs  += 1
                
        #
        # Deal with states & changes...
        #
        lastCurrentState=self.currentState
        self.currentState=project.getState()
        
        if lastCurrentState==self.currentState:
            self.sequenceInState += 1
        else:
            self.sequenceInState = 1
            self.previousState=lastCurrentState
         
class StatisticsDB:
    """Statistics Interface"""

    def __init__(self):
        self.dbpath    = os.path.normpath('%s/%s' % (dir.work,'stats.db'))
        log.debug('Open Statistic Database:' + self.dbpath)
        if not os.name == 'dos' and not os.name == 'nt':
            self.db		=	anydbm.open(self.dbpath,'c')
        else:
            self.db={}
 
    def dumpProjects(self):
        for key in self.db.keys():
            if not -1 == key.find('-pname'):
                pname=key[0:len(key)-6]
                print "Project " + pname + " Key " + key
                s=self.getProjectStats(pname)
                dump(s)
            
    def getProjectStats(self,projectname):
        s=ProjectStatistics(projectname)
        s.successes=self.getInt(s.successesKey())
        s.failures=self.getInt(s.failuresKey())
        s.prereqs=self.getInt(s.prereqsKey())
        s.first=self.getDate(s.firstKey())
        s.last=self.getDate(s.lastKey())
        s.currentState=stateForName(self.get(s.currentStateKey()))
        s.previousState=stateForName(self.get(s.previousStateKey()))
        s.sequenceInState=self.getInt(s.sequenceInStateKey())
        return s
    
    def putProjectStats(self,s):
        self.put(s.nameKey(), s.projectname)
        self.putInt(s.successesKey(), s.successes)
        self.putInt(s.failuresKey(), s.failures)
        self.putInt(s.prereqsKey(), s.prereqs)
        self.putDate(s.firstKey(), s.first)
        self.putDate(s.lastKey(), s.last)
        self.put(s.currentStateKey(), stateName(s.currentState))
        self.put(s.previousStateKey(), stateName(s.previousState))
        self.putInt(s.sequenceInStateKey(), s.sequenceInState)
        
    def delProjectStats(self,s):
        try:
            del self.db[s.nameKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[s.successesKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[s.failuresKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[s.prereqsKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[s.firstKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[s.lastKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[s.currentStateKey()]
        except:
            """ Hopefully means it wasn't there... """        
        try:
            del self.db[s.previousStateKey()]
        except:
            """ Hopefully means it wasn't there... """        
        try:
            del self.db[s.sequenceInStateKey()]
        except:
            """ Hopefully means it wasn't there... """
        
    def get(self,key):
        val=''
        if self.db.has_key(key): val=self.db[key]
        return val
        
    def getInt(self,key):
        val=0
        if self.db.has_key(key): val=self.db[key]
        return int(val)
        
    def getFloat(self,key):
        val=0
        if self.db.has_key(key): val=self.db[key]
        return float(val)
        
    def getDate(self,key):
        return self.getFloat(key)
        
    def put(self,key,val=''):
        self.db[key]=val
        
    def putInt(self,key,val=0):
        self.db[key]=str(val)
        
    def putDate(self,key,val=0):
        self.putInt(key,val)
        
  
    def loadStatistics(self,workspace):
        log.debug('--- Loading Project Statistics')
          
        for module in workspace.getModules():
            for project in module.getProjects():
                #
                # Load the statistics...
                #
                s=self.getProjectStats(project.getName())        
                
                #
                # Stash for later...
                #
                project.setStats(s)            
            
                       
    def updateStatistics(self,workspace):
        log.debug('--- Updating Project Statistics')
          
        for module in workspace.getModules():
            for project in module.getProjects():
                # Load the statistics
                s=self.getProjectStats(project.getName())
            
                #
                # Update for this project based off this run
                #
                s.update(project)
                
                #
                # Stash for later...
                #
                project.setStats(s)            
                
                #
                # Write out the updates
                #
                self.putProjectStats(s) 
                
class WorkspaceStatisticsGuru:                        
    """ Know it all for a workspace... """
    def __init__(self, workspace):
        self.workspace=workspace
        
        # Crunch the numbers...
        self.calculate()
        
    def calculate(self):
        self.modulesInWorkspace=len(self.workspace.getModules())
        self.projectsInWorkspace=len(self.workspace.getProjects())
        
        self.maxProjectsForAModule=1
        self.moduleWithMaxProjects=''
        
        for module in self.workspace.getModules():
            
            #
            # Calculate per project
            #
            projectCount=len(module.getProjects())
            if projectCount > self.maxProjectsForAModule:
                self.maxProjectsForAModule=projectCount
                self.moduleWithMaxProjects=module.getName()
                
        #
        # Average Projects Per Module
        #
        self.averageProjectsPerModule=	\
            round(self.projectsInWorkspace/self.modulesInWorkspace,2)
        
def sortByElapsed(module1,module2):
    elapsed1=module1.elapsedSecs()
    elapsed2=module2.elapsedSecs()
    c = 0
    if elapsed1 > elapsed2: c = -1
    if elapsed1 < elapsed2: c = 1       
    if not c: c=cmp(module1,module2)
    return c

def sortByProjectCount(module1,module2):
    count1=len(module1.getProjects())
    count2=len(module2.getProjects())
    c = count2 - count1                  
    if not c: c=cmp(module1,module2)
    return c

def sortByDependencyCount(module1,module2):
    count1=module1.dependencyCount()
    count2=module2.dependencyCount()
    c= count2 - count1                 
    if not c: c=cmp(module1,module2)
    return c        
        
def sortByDependeeCount(module1,module2):
    count1=module1.dependeeCount()
    count2=module2.dependeeCount()
    c= count2 - count1                  
    if not c: c=cmp(module1,module2)
    return c       
    
def sortByFOGFactor(module1,module2):
    fog1=module1.getFOGFactor()
    fog2=module2.getFOGFactor()
    c= int(round(fog2 - fog1,0))                  
    if not c: c=cmp(module1,module2)
    return c             
            
class StatisticsGuru:
    """ Know it all ... """
    
    def __init__(self,workspace):
        self.workspace=workspace
        
        # One for the whole workspace
        self.wguru=WorkspaceStatisticsGuru(workspace)                
        self.modulesByElapsed=createOrderedList(workspace.getModules(),sortByElapsed)
        self.modulesByProjectCount=createOrderedList(workspace.getModules(),sortByProjectCount)
        self.modulesByTotalDependencies=createOrderedList(workspace.getModules(),sortByDependencyCount)
        self.modulesByTotalDependees=createOrderedList(workspace.getModules(),sortByDependeeCount)
        self.modulesByFOGFactor=createOrderedList(workspace.getModules(),sortByFOGFactor)
