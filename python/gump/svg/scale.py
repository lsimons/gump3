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

    Scale Diagram
    
"""

from gump.svg.drawing import *
from gump.svg.svg import *

class ScaleDiagram:
    """ The interface to a chainable context """
    def __init__(self, val1, val2, width=3, height=0.5) : 
        self.width=width
        self.height=height
        self.val1=val1
        self.val2=val2
        
    def generateDiagram(self):
        
        context=ScaledDrawingContext('Scale', None,	\
                        Rect(0,0,self.width,self.height),	\
                        (self.val1 + self.val2), 1)
                        
        # Let the context define the rect.
        rect=context.realRect()
        
        # Build an SVG to fit the real world size, and the
        # context rectangle.
        svg=SimpleSvg(rect.getWidth(),rect.getHeight(),self.width,self.height)
        
        # Border box ...           
        (x1,y1)=context.realPoint(0,0)
        (x2,y2)=context.realPoint(self.val1+self.val2,1)        
        svg.addRect(x1,y1,x2-0.1,y2-0.1, { 'fill':'none','stroke':'black','stroke-width':'0.2' })
        
        # Red box [right side]...           
        (x1,y1)=context.realPoint(self.val1,0)
        (x2,y2)=context.realPoint(self.val1+self.val2,1)        
        svg.addRect(x1,y1,x2,y2, { 'fill':'red' })
        
        # Green box [left side]...                
        (x1,y1)=context.realPoint(0,0)
        (x2,y2)=context.realPoint(self.val1,1)
        svg.addRect(x1,y1,x2,y2, { 'fill':'green' })
        
        return svg