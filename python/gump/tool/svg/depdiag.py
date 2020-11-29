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

    Dependency Diagram
    
"""

import logging
import sys

from gump import log
from gump.tool.shared.comparator import compareProjectsByFOGFactor
from gump.tool.svg.drawing import *
from gump.tool.svg.svg import *
from gump.util import getIndent,createOrderedList

class DependencyNode:
    def __init__(self,project):
        self.project=project
        self.point=None
        
    def getProject(self):
        return self.project
        
    def setRowCol(self,rowNo,colNo):
        self.rowNo=rowNo
        self.colNo=colNo
        
    def getRowCol(self):
        return (self.rowNo,self.colNo)
        
    def setPoint(self,point):
        self.point=point
        
    def getPoint(self):
        return self.point

def compareNodesByProjectFOGFactor(node1,node2):
    project1=node1.getProject()    
    project2=node2.getProject()
    fog1=project1.getFOGFactor()
    fog2=project2.getFOGFactor()
    # Allow comparison to 2 decimal places, by *100
    c= int(round((fog2 - fog1)*100,0))                  
    if not c: c=cmp(project1,project2)
    return c       
    
class DependencyMatrix:
    """
        This matrix
    """
    def __init__(self,project):
        
        self.project=project
        
        # Create a sparse matrix
        self.depths={}
        self.maxDepth=0
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
        for rowNo in list(self.depths.keys()):
            row=self.depths[rowNo] 
            newRow=createOrderedList(row,compareNodesByProjectFOGFactor)
            self.depths[rowNo]=newRow
            
        # Now fix the (x,y) for all nodes (based of this sort)
        for rowNo in list(self.depths.keys()):
            colNo=0
            for node in self.depths[rowNo]:
                node.setRowCol(rowNo,colNo)
                colNo+=1
        
    # Insert into lists 
    def insertProject(self,project):
        depth=project.getDependencyDepth()
        if depth not in self.depths:
            self.depths[depth]=[]    
        
        # Context
        node=DependencyNode(project)
        
        # Insert into sparce matrix
        depthList=self.depths[depth]          
        depthList.append(node)
        
        # Keep track of ...
        numAtDepth=len(depthList)        
        if (numAtDepth > self.maxNumAtDepth):
            self.maxNumAtDepth=numAtDepth   
            
        # Keep track of ...
        if (depth > self.maxDepth):
            self.maxDepth=depth        
            
        # Lookups
        self.nodes[project]=node
        
    def getExtent(self):        
        # Max by max
        return (self.maxDepth+1,self.maxNumAtDepth)
        
    def getRowWidth(self,row):
        return len(self.depths[row])
        
    def hasRow(self,row):
        return row in self.getRows()
        
    def getRows(self):
        return list(self.depths.keys())
        
    def getNodes(self):
        return list(self.nodes.values())
        
    def getNodeForProject(self,project):
        return self.nodes[project]        
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        
        output.write(getIndent(indent)+'Extent : ' + repr(self.getExtent()) +  '\n')
        
        # Now re-order the rows, sorting by FOG
        for rowNo in list(self.depths.keys()):
            row=self.depths[rowNo]             
            output.write(getIndent(indent)+'Row [Depth]: ' + repr(rowNo) +  '\n')
            for value in row:
                output.write(getIndent(indent+1)+'Row : ' + repr(value) +  '\n')

class DependencyDiagram:
    """ The interface to a chainable context """
    def __init__(self, project) : 
        self.project=project
        self.matrix=None
        
    def compute(self):
        self.matrix=DependencyMatrix(self.project)
        self.matrix.compute()
        
    def generateDiagram(self):
        
        # Get the maximum rows/cols
        (rows, cols) = self.matrix.getExtent()
        
        # The drawing plane
        absoluteRect=Rect(0,0,100*cols,100*rows)
        
        # The standard context for that plane
        mainContext=StandardDrawingContext('Dependencies', None,
                        absoluteRect)
        
        #print 'RECT: ' + str(absoluteRect)
        #print '(ROWS,COLS) : ' + `(rows, cols)`
        
        context=SwitchAxisDrawingContext('Switch',
                    YInvertDrawingContext('Invert', 
                        GridDrawingContext('Grid', mainContext, cols, rows ),
                        rows - 1 ) )
        
        # Build an SVG to fit the real world size, and the
        # context rectangle.
        svg=SimpleSvg(absoluteRect.getWidth(), absoluteRect.getHeight())
        
        #
        # Add a border
        #
        svg.addBorder()

        #
        # Find centers
        #
        for node in self.matrix.getNodes():
            (row, col) = node.getRowCol()
            
            rowColumns=self.matrix.getRowWidth(row)
            
            # Center...
            centeredCol = (float(cols)/float(rowColumns)) * col
            
            
            #print 'NODE (ROW,COL) : ' + `(row, col)`
            (x,y) = context.realPoint(row,centeredCol)
            (x1,y1) = context.realPoint(row,col)
            if y1 != y:	
                print('Cols:',cols,'Row Cols',rowColumns,' COLS:', col,' -> ',centeredCol)            
                print('(X,Y) : ' + repr((x, y)))
                print('(X1,Y1) : ' + repr((x1, y1)))
            node.setPoint(Point(x,y))            
            node.setRowCol(row,centeredCol)
                
        #
        # Draw dependency lines
        #
        for node in self.matrix.getNodes():
            project = node.getProject()
            
            # Draw lines to represent dependencies
            for dependency in project.getDirectDependencies():
                                
                # For each dependent project
                dependProject=dependency.getProject()
                
                depNode=self.matrix.getNodeForProject(dependProject)
                
                (x,y) = node.getPoint().getXY()
                (x1,y1) = depNode.getPoint().getXY()
                
                width=1+(dependProject.getFOGFactor()*3)
                # Shape color
                color='black'
                if dependency.isOptional(): 
                    color='green'
                if project.isPackaged(): 
                    color='blue'
                elif not project.hasBuilder():
                    color='purple'
                elif project.getFOGFactor() < 0.1:
                    color='red'
            
                attributes =	{ 'stroke':color, \
                          'stroke-width':width, \
                          'comment': project.getName() + ' to ' + dependProject.getName() }
                          
                if dependency.isRuntime(): 
                    attributes['stroke-dasharray']='5,2'
                    
                #print 'LINE %s,%s -> %s,%s' % (x,y,x1,y1)
                svg.addLine(x,y,x1,y1, attributes )
                                          
        #
        # The shapes and text
        #                            
        for node in self.matrix.getNodes():
            project = node.getProject()
            
            (row, col) = node.getRowCol()
            (x,y) = context.realPoint(row+0.25,col-0.25)
            (x1,y1) = context.realPoint(row-0.25,col+0.25)
            
            #print 'RECTANGLE %s,%s -> %s,%s' % (x,y,x1,y1)
            
            # Shape color
            color='green'
            if project.isPackaged(): 
                color='blue'
            elif not project.hasBuilder():
                color='purple'
            elif project.getFOGFactor() < 0.1:
                color='red'
                
            svg.addRect(x,y,(x1-x),(y1-y),  \
                    { 	'fill':color, \
                        'comment':project.getName() } )
                        
            (x,y) = context.realPoint(row+0.27,col-0.27)
            #print 'TEXT %s,%s' % (x,y)
            
            svg.addText(x,y,project.getName() + ' (' + repr(project.getFOGFactor()) + ')',  \
                    { 	'fill':'red', \
                        'comment':project.getName() } )
                        
        return svg
        
        
# static void main()
if __name__=='__main__':
        
        
    from gump.core.run.gumprun import GumpRun
    from gump.core.run.gumpset import GumpSet
    from gump.core.run.options import GumpRunOptions
    from gump.core.commandLine import handleArgv
    from gump.core.loader.loader import WorkspaceLoader
    from gump.output.statsdb import *

    # Process command line
    (args,options) = handleArgv(sys.argv)
    ws=args[0]
    ps=args[1]

    # get parsed workspace definition
    workspace=WorkspaceLoader(options.isCache()).load(ws)    
        
    # Ensure we use text, not xdocs...
    options.setText(1)
    
    # The Run Details...
    run=GumpRun(workspace,ps,options)
        
    # Load statistics    
    db=StatisticsDB()  
    db.loadStatistics(workspace)  
    
    for project in run.getGumpSet().getProjects():
        diagram=DependencyDiagram(project)        
        diagram.compute()        
        svg=diagram.generateDiagram()
        svgName=project.getName()+'.svg'
        svg.serializeToFile(svgName)        
        print("Generated : " + svgName)
    
    #
    log.info('Dependency Generation complete.')
        
