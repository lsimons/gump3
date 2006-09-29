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
import os
import sys
import logging

from gump import log
from gump.core.config import *
from gump.core.model.project import Project, ProjectStatistics
from gump.core.model.module import Module, ModuleStatistics
from gump.core.model.repository import Repository, RepositoryStatistics
from gump.core.model.workspace import Workspace, WorkspaceStatistics
from gump.core.model.state import *
from gump.util import createOrderedList

from gump.tool.shared.comparator import *

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
            float(self.projectsInWorkspace)/self.modulesInWorkspace

class StatisticsGuru:
    """ Know it all ... """
    
    def __init__(self,workspace):
        self.workspace=workspace
        
        # One for the whole workspace
        self.wguru=WorkspaceStatisticsGuru(workspace)      
        
        # All Modules            
        log.debug('compareModulesByElapsed')
        self.modulesByElapsed=createOrderedList(workspace.getModules(),compareModulesByElapsed)
        log.debug('compareModulesByProjectCount')
        self.modulesByProjectCount=createOrderedList(workspace.getModules(),compareModulesByProjectCount)
        log.debug('compareModulesByDependencyCount')
        self.modulesByTotalDependencies=createOrderedList(workspace.getModules(),compareModulesByDependencyCount)
        log.debug('compareModulesByDependeeCount')
        self.modulesByTotalDependees=createOrderedList(workspace.getModules(),compareModulesByDependeeCount)
        log.debug('compareModulesByFOGFactor')
        self.modulesByFOGFactor=createOrderedList(workspace.getModules(),compareModulesByFOGFactor)
        log.debug('compareModulesByLastModified')
        self.modulesByLastModified=createOrderedList(workspace.getModules(),compareModulesByLastModified)
        
        
        # All Projects                
        log.debug('compareProjectsByElapsed')
        self.projectsByElapsed=createOrderedList(workspace.getProjects(),compareProjectsByElapsed)
        log.debug('compareProjectsByDependencyCount')
        self.projectsByTotalDependencies=createOrderedList(workspace.getProjects(),compareProjectsByDependencyCount)
        log.debug('compareProjectsByDependeeCount')
        self.projectsByTotalDependees=createOrderedList(workspace.getProjects(),compareProjectsByDependeeCount)
        log.debug('compareProjectsByFOGFactor')
        self.projectsByFOGFactor=createOrderedList(workspace.getProjects(),compareProjectsByFOGFactor)
        log.debug('compareProjectsByLastModified')
        self.projectsByLastModified=createOrderedList(workspace.getProjects(),compareProjectsByLastModified)
        log.debug('compareProjectsBySequenceInState')
        self.projectsBySequenceInState=createOrderedList(workspace.getProjects(),compareProjectsBySequenceInState)
        log.debug('compareProjectsByDependencyDepth')
        self.projectsByDependencyDepth=createOrderedList(workspace.getProjects(),compareProjectsByDependencyDepth)
        log.debug('compareProjectsByTotalDependencyDepth')
        self.projectsByTotalDependencyDepth=createOrderedList(workspace.getProjects(),compareProjectsByTotalDependencyDepth)
        
