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

from gump import log
from gump.core.config import *
from gump.model.project import Project, ProjectStatistics
from gump.model.module import Module, ModuleStatistics
from gump.model.repository import Repository, RepositoryStatistics
from gump.model.workspace import Workspace, WorkspaceStatistics
from gump.model.state import *

from gump.shared.comparator import *

                
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
        self.modulesByElapsed=createOrderedList(workspace.getModules(),compareModulesByElapsed)
        self.modulesByProjectCount=createOrderedList(workspace.getModules(),compareModulesByProjectCount)
        self.modulesByTotalDependencies=createOrderedList(workspace.getModules(),compareModulesByDependencyCount)
        self.modulesByTotalDependees=createOrderedList(workspace.getModules(),compareModulesByDependeeCount)
        self.modulesByFOGFactor=createOrderedList(workspace.getModules(),compareModulesByFOGFactor)
        self.modulesByLastModified=createOrderedList(workspace.getModules(),compareModulesByLastModified)
        
        
        # All Projects                
        self.projectsByElapsed=createOrderedList(workspace.getProjects(),compareProjectsByElapsed)
        self.projectsByTotalDependencies=createOrderedList(workspace.getProjects(),compareProjectsByDependencyCount)
        self.projectsByTotalDependees=createOrderedList(workspace.getProjects(),compareProjectsByDependeeCount)
        self.projectsByFOGFactor=createOrderedList(workspace.getProjects(),compareProjectsByFOGFactor)
        self.projectsByLastModified=createOrderedList(workspace.getProjects(),compareProjectsByLastModified)
        self.projectsBySequenceInState=createOrderedList(workspace.getProjects(),compareProjectsBySequenceInState)
        self.projectsByDependencyDepth=createOrderedList(workspace.getProjects(),compareProjectsByDependencyDepth)
        self.projectsByTotalDependencyDepth=createOrderedList(workspace.getProjects(),compareProjectsByTotalDependencyDepth)
        
