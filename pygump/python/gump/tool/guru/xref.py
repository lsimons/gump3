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
    Cross-reference gathering/manipulation
"""

import time
import os
import sys
import logging

from gump import log
from gump.core.config import *
from gump.core.model.project import Project
from gump.core.model.state import *
            
class XRefGuru:
    """ Know it all ... """
    
    def __init__(self,workspace):
        self.workspace=workspace
    
        self.repositoryToModule={}
        
        self.packageToModule={}
        self.packageToProject={}
        
        self.descriptionToModule={}
        self.descriptionToProject={}
        
        self.outputToProject={}
        self.outputIdToProject={}
        
        self.descriptorLocationToProject={}
        
        # Build Information Maps
        self.mapRepositories()
        self.mapPackages()
        self.mapDescriptions()
        self.mapOutputs()
        self.mapDescriptorLocations()
        
    def mapRepositories(self):
        for module in self.workspace.getModules():
            repository=module.getRepository()
            if repository:
                if not self.repositoryToModule.has_key(repository):
                    self.repositoryToModule[repository]=[]
                
                # Store
                self.repositoryToModule[repository].append(module)
    
    def mapPackages(self):
        for module in self.workspace.getModules():
            for project in module.getProjects():
                if project.hasPackageNames():
                    for packageName in project.getPackageNames():
                        if not self.packageToModule.has_key(packageName):
                                self.packageToModule[packageName]=[]
            
                        if not self.packageToProject.has_key(packageName):
                                self.packageToProject[packageName]=[]
                
                        # Store
                        if not module in self.packageToModule[packageName]:
                            self.packageToModule[packageName].append(module)
    
                        if not project in self.packageToProject[packageName]:
                            self.packageToProject[packageName].append(project)
    
    def mapDescriptions(self):
        for module in self.workspace.getModules():
            
            moduleDescription=module.getDescription()
            if moduleDescription:
                if not self.descriptionToModule.has_key(moduleDescription):
                    self.descriptionToModule[moduleDescription]=[]
            
                if not module in self.descriptionToModule[moduleDescription]:
                    self.descriptionToModule[moduleDescription].append(module)
                    
            for project in module.getProjects():
                
                projectDescription=project.getDescription()
                if projectDescription:
                    if not self.descriptionToProject.has_key(projectDescription):
                        self.descriptionToProject[projectDescription]=[]
                    
                    if not project in self.descriptionToProject[projectDescription]:
                        self.descriptionToProject[projectDescription].append(project)
    
    
    def mapOutputs(self):
        for module in self.workspace.getModules():            
            for project in module.getProjects():                
                if project.hasOutputs():
                    for output in project.getOutputs():  
                        outputName=os.path.basename(output.getName())  
                        outputId=output.getId() or 'No Identifier'
                        
                        # Create a list to hold multiple (if needed)          
                        if not self.outputToProject.has_key(outputName):
                            self.outputToProject[outputName]=[]
                        
                        # Create a list to hold multiple (if needed)          
                        if not self.outputIdToProject.has_key(outputId):
                            self.outputIdToProject[outputId]=[]
                    
                        # Store the Project
                        if not project in self.outputToProject[outputName]:
                            self.outputToProject[outputName].append(project)
                        if not project in self.outputIdToProject[outputId]:
                            self.outputIdToProject[outputId].append(project)
    
    def mapDescriptorLocations(self):
        for module in self.workspace.getModules():            
            for project in module.getProjects():                
                metadataLocation=project.getMetadataLocation()
                
                # print project.getName() + ' : Metadata Location = ' + metadataLocation + "\n";
                
                if metadataLocation:          
                    if not self.descriptorLocationToProject.has_key(metadataLocation):
                        self.descriptorLocationToProject[metadataLocation]=[]
                    
                    if not project in self.descriptorLocationToProject[metadataLocation]:
                        self.descriptorLocationToProject[metadataLocation].append(project)
    
    def getRepositoryToModuleMap(self):
        return self.repositoryToModule
                
    def getPackageToModuleMap(self):
        return self.packageToModule
        
    def getPackageToProjectMap(self):
        return self.packageToProject
                
    def getDescriptionToModuleMap(self):
        return self.descriptionToModule
        
    def getDescriptionToProjectMap(self):
        return self.descriptionToProject
        
    def getOutputToProjectMap(self):
        return self.outputToProject
        
    def getOutputIdToProjectMap(self):
        return self.outputIdToProject
        
    def getDescriptorLocationToProjectMap(self):
        return self.descriptorLocationToProject
        
        
