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

    Scale Diagram
    
"""

from gump.tool.svg.drawing import *
from gump.tool.svg.svg import *

class ScaleDiagram:
    """ The interface to a chainable context """
    def __init__(self, vals, width=3, height=0.5) : 
        self.vals=vals
        self.width=width
        self.height=height
    
        self.total=sum(self.vals)
        
    def generateDiagram(self):
        
        context=ScaledDrawingContext('Scale', None,	\
                        Rect(0,0,self.width,self.height),	\
                        (self.total), 1)
                        
        # Let the context define the rect.
        rect=context.realRect()
        
        # Build an SVG to fit the real world size, and the
        # context rectangle.
        svg=SimpleSvg(rect.getWidth(),rect.getHeight(),self.width,self.height)
        
        runningTotal=0
        colorId=0
        color=None
        for v in self.vals:  
            colorId = colorId % 3
            if 0 == colorId: color='green'
            elif 1 == colorId: color='blue'
            else: color='red'
            
            if v > 0:
                # Box...           
                (x1,y1)=context.realPoint(runningTotal,0)
                (x2,y2)=context.realPoint(runningTotal+v,1)        
                svg.addRect(x1,y1,x2,y2, { 'fill':color })
                runningTotal+=v
                
            colorId+=1
        
        
        # Last, since likely overlaps
        
        svg.addBorder()
        
        return svg
