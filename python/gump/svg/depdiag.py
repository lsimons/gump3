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

    Dependency Diagram
    
"""

import logging
import sys

from gump import log
from gump.shared.comparator import compareProjectsByFOGFactor
from gump.utils import getIndent,createOrderedList

class DependencyNode:
    def __init__(self,project):
        self.project=project
        self.point=None

class DependencyMatrix:
    """
        This matrix
    """
    def __init__(self,project):
        
        self.project=project
        
        # Create a sparse matrix
        self.depths={}
        self.maxNumAtDepth=0
        
        # Create a lookup
        self.nodes={}
    
    def compute(self):
        """
            Build the matrix
        """
        
        # Start with the focus
        self.insertProject(self.project)
        
        # Go onto all dependencies
        for project in self.project.getFullDependencyProjectList():
            self.insertProject(project)
            
        # Now re-order the rows, sorting by FOG
        for rowNo in self.depths.keys():
            row=self.depths[rowNo] 
            newRow=createOrderedList(row,compareProjectsByFOGFactor)
            self.depths[rowNo]=newRow
        
    # Insert into lists 
    def insertProject(self,project):
        depth=project.getDependencyDepth()
        if not self.depths.has_key(depth):
            self.depths[depth]=[]    
        
        # Context
        node=DependencyNode(project)
        
        # Insert into sparce matrix
        depthList=self.depths[depth]          
        depthList.append(node)
        
        # Keep track of 
        numAtDepth=len(depthList)        
        if (numAtDepth > self.maxNumAtDepth):
            self.maxNumAtDepth=numAtDepth        
            
        # Lookups
        self.nodes[project]=node
        
    def getExtent(self):        
        # Max by max
        return (self.maxNumAtDepth, len(self.depths.keys()))
        
    def getNodeForProject(self,project):
        return self.nodes[project]
        
        self.projectsByFOGFactor=createOrderedList(workspace.getProjects(),compareProjectsByFOGFactor)
        
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        
        output.write(getIndent(indent)+'Extent : ' + `self.getExtent()` +  '\n')
        
        # Now re-order the rows, sorting by FOG
        for rowNo in self.depths.keys():
            row=self.depths[rowNo]             
            output.write(getIndent(indent)+'Row [Depth]: ' + `rowNo` +  '\n')
            for value in row:
                output.write(getIndent(indent+1)+'Row : ' + `value` +  '\n')

class DependencyDiagram:
    """ The interface to a chainable context """
    def __init__(self, project) : 
        self.project=project
        self.matrix=None
        
    def compute(self):
        self.matrix=DependencyMatrix(self.project)
        self.matrix.compute()
        
        
    def generateDiagram(self):
        self.matrix.dump()
        
        
    
        