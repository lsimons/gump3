#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/output/Attic/xref.py,v 1.8 2004/01/28 22:54:50 ajack Exp $
# $Revision: 1.8 $
# $Date: 2004/01/28 22:54:50 $
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

from gump import log
from gump.config import *
from gump.model.project import Project
from gump.model.state import *
            
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
                if project.isPackaged(): continue
                for package in project.xml.package:
                    if package:
                        packageName=str(package)
            
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
            if module.isPackaged(): continue
            
            moduleDescription=module.getDescription()
            if moduleDescription:
                if not self.descriptionToModule.has_key(moduleDescription):
                    self.descriptionToModule[moduleDescription]=[]
            
                if not module in self.descriptionToModule[moduleDescription]:
                    self.descriptionToModule[moduleDescription].append(module)
                    
            for project in module.getProjects():
                if project.isPackaged(): continue
                
                projectDescription=project.getDescription()
                if projectDescription:
                    if not self.descriptionToProject.has_key(projectDescription):
                        self.descriptionToProject[projectDescription]=[]
                    
                    if not project in self.descriptionToProject[projectDescription]:
                        self.descriptionToProject[projectDescription].append(project)
    
    
    def mapOutputs(self):
        for module in self.workspace.getModules():            
            for project in module.getProjects():                
                if project.hasJars():
                    for jar in project.getJars():  
                        jarName=os.path.basename(jar.getName())            
                        if not self.outputToProject.has_key(jarName):
                            self.outputToProject[jarName]=[]
                    
                        if not project in self.outputToProject[jarName]:
                            self.outputToProject[jarName].append(project)
    
    def mapDescriptorLocations(self):
        for module in self.workspace.getModules():            
            for project in module.getProjects():                
                metadataLocation=str(project.xml.href)
                
                print project.getName() + ' : ' + metadataLocation + "\n";
                
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
        
    def getDescriptorLocationToProjectMap(self):
        return self.descriptorLocationToProject
        
        