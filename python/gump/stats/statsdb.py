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
    Statistics gathering/manipulation
"""

import time
import os
import sys
import logging
import anydbm

from gump import log
from gump.core.config import *
from gump.model.project import Project, ProjectStatistics
from gump.model.module import Module, ModuleStatistics
from gump.model.repository import Repository, RepositoryStatistics
from gump.model.workspace import Workspace, WorkspaceStatistics
from gump.model.state import *

from gump.shared.comparator import *
  
class StatisticsDB:
    """
    	Statistics Database Abstract Interface
    """

    def __init__(self,dbdir=None,name=None):
        pass
 
                
    # Workspace
    def getWorkspaceStats(self,workspaceName):
        stats=WorkspaceStatistics(workspaceName)
        self.getBaseStats(stats)
        return stats
        
    def putWorkspaceStats(self,stats):
        self.putBaseStats(stats)

    def delWorkspaceStats(self,stats):
        self.delBaseStats(stats)          
        
        
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
        stats.lastModified=self.getDate(stats.lastModifiedKey())
        return stats
                
    def putModuleStats(self,stats):
        self.putBaseStats(stats)
        self.putDate(stats.lastModifiedKey(), stats.lastModified)

    def delModuleStats(self,stats):
        self.delBaseStats(stats)
        try:
            del self.db[stats.lastModifiedKey()]
        except:
            """ Hopefully means it wasn't there... """                
  
    def sync(self):
        """
        Try to sync the DB to disk (assuming it has a sync, which
        some implementations do not).
        """
        if hasattr(self.db, 'sync'):
            self.db.sync()
          