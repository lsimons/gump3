#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/output/Attic/statsdb.py,v 1.11 2004/01/09 23:46:53 ajack Exp $
# $Revision: 1.11 $
# $Date: 2004/01/09 23:46:53 $
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
from gump.model.project import Project, ProjectStatistics
from gump.model.module import Module, ModuleStatistics
from gump.model.repository import Repository, RepositoryStatistics
from gump.model.workspace import Workspace, WorkspaceStatistics
from gump.model.state import *
  
class StatisticsDB:
    """Statistics Interface"""

    def __init__(self,dbdir=None,name=None):
        if not name: name='stats.db'
        if not dbdir: dbdir=dir.work
        self.dbpath    = os.path.abspath('%s/%s' % (dbdir,name))
        
        if not os.path.exists(self.dbpath):
            log.info('*New* Statistic Database:' + self.dbpath)
            
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
                
    # Workspace
    def getWorkspaceStats(self):
        stats=WorkspaceStatistics()
        self.getBaseStats(stats)
        return stats
        
    # Project
    
    def getProjectStats(self,projectName):
        stats=ProjectStatistics(projectName)        
        self.getBaseStats(stats)
        return stats
                
    def putProjectStats(self,stats):
        self.putBaseStats(stats)

    def delProjectStats(self,stats):
        self.delBaseStats(stats)          

    # Repository
    
    def getRepositoryStats(self,projectName):
        stats=RepositoryStatistics(projectName)        
        self.getBaseStats(stats)
        return stats
                
    def putRepositoryStats(self,stats):
        self.putBaseStats(stats)

    def delRepositoryStats(self,stats):
        self.delBaseStats(stats)          

    # Module
    
    def getModuleStats(self,moduleName):
        stats=ModuleStatistics(moduleName)        
        self.getBaseStats(stats)
        stats.lastUpdated=self.getDate(stats.lastUpdatedKey())
        return stats
                
    def putModuleStats(self,stats):
        self.putBaseStats(stats)
        self.putDate(stats.lastUpdatedKey(), stats.lastUpdated)

    def delModuleStats(self,stats):
        self.delBaseStats(stats)
        try:
            del self.db[stats.lastUpdatedKey()]
        except:
            """ Hopefully means it wasn't there... """                

    def getBaseStats(self,stats):
        stats.successes=self.getInt(stats.successesKey())
        stats.failures=self.getInt(stats.failuresKey())
        stats.prereqs=self.getInt(stats.prereqsKey())
        stats.first=self.getDate(stats.firstKey())
        stats.last=self.getDate(stats.lastKey())
        stats.currentState=stateForName(self.get(stats.currentStateKey()))
        stats.previousState=stateForName(self.get(stats.previousStateKey()))
        stats.startOfState=self.getDate(stats.startOfStateKey())
        stats.sequenceInState=self.getInt(stats.sequenceInStateKey())
        
    def putBaseStats(self,stats):        
        self.put(stats.nameKey(), stats.name)
        self.putInt(stats.successesKey(), stats.successes)
        self.putInt(stats.failuresKey(), stats.failures)
        self.putInt(stats.prereqsKey(), stats.prereqs)
        self.putDate(stats.firstKey(), stats.first)
        self.putDate(stats.lastKey(), stats.last)
        self.put(stats.currentStateKey(), stateName(stats.currentState))
        self.put(stats.previousStateKey(), stateName(stats.previousState))
        self.putDate(stats.startOfStateKey(), stats.startOfState)
        self.putInt(stats.sequenceInStateKey(), stats.sequenceInState)

    def delBaseStats(self,stats):
        try:
            del self.db[stats.nameKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[stats.successesKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[stats.failuresKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[stats.prereqsKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[stats.firstKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[stats.lastKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[stats.currentStateKey()]
        except:
            """ Hopefully means it wasn't there... """        
        try:
            del self.db[stats.previousStateKey()]
        except:
            """ Hopefully means it wasn't there... """        
        try:
            del self.db[stats.startOfStateKey()]
        except:
            """ Hopefully means it wasn't there... """        
        try:
            del self.db[stats.sequenceInStateKey()]
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
        log.debug('--- Loading Statistics')
                  
        for repo in workspace.getRepositories():
                        
            # Load the statistics
            rs=self.getRepositoryStats(repo.getName())
                
            #
            # Stash for later...
            #
            repo.setStats(rs)    
                      
        for module in workspace.getModules():
            #
            # Load the statistics...
            #
            ms=self.getModuleStats(module.getName())        
                
            #
            # Stash for later...
            #
            module.setStats(ms)     
            
            for project in module.getProjects():
                #
                # Load the statistics...
                #
                ps=self.getProjectStats(project.getName())        
                
                #
                # Stash for later...
                #
                project.setStats(ps)            
            
                       
    def updateStatistics(self,workspace):
        log.debug('--- Updating Statistics')
                  
        for repo in workspace.getRepositories():
                        
            # Load the statistics
            rs=self.getRepositoryStats(repo.getName())
            
            #
            # Update for this repo based off this run
            #
            rs.update(repo)
                
            #
            # Stash for later...
            #
            repo.setStats(rs)    
              
        for module in workspace.getModules():
                        
            # Load the statistics
            ms=self.getModuleStats(module.getName())
            
            #
            # Update for this project based off this run
            #
            ms.update(module)
                
            #
            # Stash for later...
            #
            module.setStats(ms)            
                
            #
            # Write out the updates
            #
            self.putModuleStats(ms)     
            
            for project in module.getProjects():
                
                # Load the statistics
                ps=self.getProjectStats(project.getName())
            
                #
                # Update for this project based off this run
                #
                ps.update(project)
                
                #
                # Stash for later...
                #
                project.setStats(ps)            
                
                #
                # Write out the updates
                #
                self.putProjectStats(ps) 
                
    def sync(self):
        if not os.name == 'dos' and not os.name == 'nt':    
            self.db.sync()
                
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
            
#
# Module Comparisons
#            
        
def compareModulesByElapsed(module1,module2):
    elapsed1=module1.getElapsedSecs()
    elapsed2=module2.getElapsedSecs()
    c = 0
    if elapsed1 > elapsed2: c = -1
    if elapsed1 < elapsed2: c = 1       
    if not c: c=cmp(module1,module2)
    return c

def compareModulesByProjectCount(module1,module2):
    count1=len(module1.getProjects())
    count2=len(module2.getProjects())
    c = count2 - count1                  
    if not c: c=cmp(module1,module2)
    return c

def compareModulesByDependencyCount(module1,module2):
    count1=module1.getFullDependencyCount()
    count2=module2.getFullDependencyCount()
    c= count2 - count1                 
    if not c: c=cmp(module1,module2)
    return c        
        
def compareModulesByDependeeCount(module1,module2):
    count1=module1.getFullDependeeCount()
    count2=module2.getFullDependeeCount()
    c= count2 - count1                  
    if not c: c=cmp(module1,module2)
    return c       
    
def compareModulesByFOGFactor(module1,module2):
    fog1=module1.getFOGFactor()
    fog2=module2.getFOGFactor()
    c= int(round(fog2 - fog1,0))                  
    if not c: c=cmp(module1,module2)
    return c             
            
def compareModulesByFOGFactor(module1,module2):
    fog1=module1.getFOGFactor()
    fog2=module2.getFOGFactor()
    c= int(round(fog2 - fog1,0))                  
    if not c: c=cmp(module1,module2)
    return c             
            
def compareModulesByLastUpdated(module1,module2):
    fog1=module1.getLastUpdated()
    fog2=module2.getLastUpdated()
    c= int(round(fog2 - fog1,0))                  
    if not c: c=cmp(module1,module2)
    return c             
            
#
# Project Comparisons
#            
        

def compareProjectsByElapsed(project1,project2):
    elapsed1=project1.getElapsedSecs()
    elapsed2=project2.getElapsedSecs()
    c = 0
    if elapsed1 > elapsed2: c = -1
    if elapsed1 < elapsed2: c = 1       
    if not c: c=cmp(project1,project2)
    return c

def compareProjectsByDependencyCount(project1,project2):
    count1=project1.getDependencyCount()
    count2=project2.getDependencyCount()
    c= count2 - count1                 
    if not c: c=cmp(project1,project2)
    return c        
        
def compareProjectsByDependeeCount(project1,project2):
    count1=project1.getDependeeCount()
    count2=project2.getDependeeCount()
    c= count2 - count1                  
    if not c: c=cmp(project1,project2)
    return c       
    
def compareProjectsByFOGFactor(project1,project2):
    fog1=project1.getFOGFactor()
    fog2=project2.getFOGFactor()
    c= int(round(fog2 - fog1,0))                  
    if not c: c=cmp(project1,project2)
    return c             
            
def compareProjectsByFOGFactor(project1,project2):
    fog1=project1.getFOGFactor()
    fog2=project2.getFOGFactor()
    c= int(round(fog2 - fog1,0))                  
    if not c: c=cmp(project1,project2)
    return c             
            
def compareProjectsByLastUpdated(project1,project2):
    fog1=project1.getLastUpdated()
    fog2=project2.getLastUpdated()
    c= int(round(fog2 - fog1,0))                  
    if not c: c=cmp(project1,project2)
    return c                         
            
class StatisticsGuru:
    """ Know it all ... """
    
    def __init__(self,workspace):
        self.workspace=workspace
        
        # One for the whole workspace
        self.wguru=WorkspaceStatisticsGuru(workspace)      
        
        # All Modules          
        self.modulesByElapsed=createOrderedList(workspace.getModules(),compareModulesByElapsed)
        self.modulesByProjectCount=createOrderedList(workspace.getModules(),compareModulesByProjectCount)
        self.modulesByTotalDependencies=createOrderedList(workspace.getModules(),compareModulesByDependencyCount)
        self.modulesByTotalDependees=createOrderedList(workspace.getModules(),compareModulesByDependeeCount)
        self.modulesByFOGFactor=createOrderedList(workspace.getModules(),compareModulesByFOGFactor)
        self.modulesByLastUpdated=createOrderedList(workspace.getModules(),compareModulesByLastUpdated)
        
        
        
        # All Projects                
        self.projectsByElapsed=createOrderedList(workspace.getProjects(),compareProjectsByElapsed)
        self.projectsByTotalDependencies=createOrderedList(workspace.getProjects(),compareProjectsByDependencyCount)
        self.projectsByTotalDependees=createOrderedList(workspace.getProjects(),compareProjectsByDependeeCount)
        self.projectsByFOGFactor=createOrderedList(workspace.getProjects(),compareProjectsByFOGFactor)
        self.projectsByLastUpdated=createOrderedList(workspace.getProjects(),compareProjectsByLastUpdated)
        