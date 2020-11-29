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
    Statistics gathering/manipulation
"""

import time
import datetime
import os
import sys
import logging
import dbm

from gump import log
from gump.core.config import *
from gump.core.model.project import Project, ProjectStatistics
from gump.core.model.module import Module, ModuleStatistics
from gump.core.model.repository import Repository, RepositoryStatistics
from gump.core.model.workspace import Workspace, WorkspaceStatistics
from gump.core.model.state import *

from gump.tool.shared.comparator import *

class MockDB(dict):
    """
        Mock Database
    """

    def __init(self):
        pass 

class StatisticsDB:
    """
    	Statistics Database Interface
    """

    def __init__(self,dbdir=None,name=None):
        if not name: name='stats.db'
        if not dbdir: dbdir=dir.work
        self.dbpath    = os.path.abspath('%s/%s' % (dbdir,name))
        
        if not os.path.exists(self.dbpath):
            log.info('*New* Statistics Database:' + self.dbpath)
            
        # Unfortuantely Python on M$ does not have an implementation (yet)
        log.debug('Open Statistic Database:' + self.dbpath)
        if not os.name == 'dos' and not os.name == 'nt':
            self.db=dbm.open(self.dbpath,'c')
        else:
            self.db=MockDB()
 
                
    # Workspace
    def getWorkspaceStats(self,workspaceName):
        stats=WorkspaceStatistics(workspaceName)
        self._getBaseStats(stats)
        return stats
        
    def putWorkspaceStats(self,stats):
        self._putBaseStats(stats)

    def delWorkspaceStats(self,stats):
        self._delBaseStats(stats)          
        
        
    # Project
    
    def getProjectStats(self,projectName):
        stats=ProjectStatistics(projectName)        
        self._getBaseStats(stats)
        return stats
                
    def putProjectStats(self,stats):
        self._putBaseStats(stats)

    def delProjectStats(self,stats):
        self._delBaseStats(stats)          

    # Repository
    
    def getRepositoryStats(self,projectName):
        stats=RepositoryStatistics(projectName)        
        self._getBaseStats(stats)
        return stats
                
    def putRepositoryStats(self,stats):
        self._putBaseStats(stats)

    def delRepositoryStats(self,stats):
        self._delBaseStats(stats)          

    # Module
    
    def getModuleStats(self,moduleName):
        stats=ModuleStatistics(moduleName)        
        self._getBaseStats(stats)
        stats.lastModified=self._getDate(stats.lastModifiedKey())
        return stats
                
    def putModuleStats(self,stats):
        self._putBaseStats(stats)
        self._putDate(stats.lastModifiedKey(), stats.lastModified)

    def delModuleStats(self,stats):
        self._delBaseStats(stats)
        try:
            del self.db[stats.lastModifiedKey()]
        except:
            """ Hopefully means it wasn't there... """                

    def _getBaseStats(self,stats):
        stats.successes=self._getInt(stats.successesKey())
        stats.failures=self._getInt(stats.failuresKey())
        stats.prereqs=self._getInt(stats.prereqsKey())
        stats.first=self._getDate(stats.firstKey())
        stats.last=self._getDate(stats.lastKey())
        stats.currentState=stateForName(self._get(stats.currentStateKey()))
        stats.previousState=stateForName(self._get(stats.previousStateKey()))
        stats.startOfState=self._getDate(stats.startOfStateKey())
        stats.sequenceInState=self._getInt(stats.sequenceInStateKey())
        
    def _putBaseStats(self,stats):        
        self._put(stats.nameKey(), stats.name)
        self._putInt(stats.successesKey(), stats.successes)
        self._putInt(stats.failuresKey(), stats.failures)
        self._putInt(stats.prereqsKey(), stats.prereqs)
        self._putDate(stats.firstKey(), stats.first)
        self._putDate(stats.lastKey(), stats.last)
        self._put(stats.currentStateKey(), stateName(stats.currentState))
        self._put(stats.previousStateKey(), stateName(stats.previousState))
        self._putDate(stats.startOfStateKey(), stats.startOfState)
        self._putInt(stats.sequenceInStateKey(), stats.sequenceInState)

    def _delBaseStats(self,stats):
        """
        Store the common stats
        """
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
        
    def _get(self,key):
        key=str(key)
        val=''
        if key in self.db: val=self.db[key].decode(encoding="utf-8")
        return val
        
    def _getInt(self,key):
        key=str(key)
        val=0
        if key in self.db: val=int(self.db[key])
        return val
        
    def _getFloat(self,key):
        """
        Get a float from the DB
        """
        key=str(key)
        val=0.0
        if key in self.db: val=float(self.db[key])
        return val
        
    def _getDate(self,key):
        """
        Get a date from the DB
        """
        dateF=self._get(key)
        
        if dateF:
            #print('dateF ' + dateF)
            if not ' ' in dateF:
                # Historical float perhaps?
                date=datetime.datetime.utcfromtimestamp(int(dateF))
            else:
                date=datetime.datetime.utcfromtimestamp(time.mktime(time.strptime(dateF,'%Y-%m-%d %H:%M:%S')))
        else:
            date=None
            
        return date
        
    def _put(self,key,val=''):
        self.db[str(key)]=val
        
    def _putInt(self,key,val=0):
        """
        Store an int
        """
        self.db[str(key)]=str(val)
        
    def _putDate(self,key,val):
        """
        Store a date (in iso format)
        """
        if val:
            self._put(str(key),val.strftime('%Y-%m-%d %H:%M:%S'))

    def sync(self):
        """
        Try to sync the DB to disk (assuming it has a sync, which
        some implementations do not).
        """
        if hasattr(self.db, 'sync'):
            self.db.sync()
          
