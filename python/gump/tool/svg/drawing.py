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

    Drawing Shapes
    
"""

import sys
import logging

from gump import log
from gump.util import *

class Point:
    """ A point """
    def __init__(self,x,y):
        self.x=x
        self.y=y
        
    def getX(self): return self.x
    def getY(self): return self.y    
    def getXY(self): return (self.x, self.y)
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        output.write(getIndent(indent)+'Point : ' \
                    + repr(self.x) + ',' 	\
                    + repr(self.y) + '\n')
                	             	                
    def __str__(self):
        return '(' 	+ repr(self.x) + ',' + repr(self.y) + ')'
    
class Rect:
    """ A rectangle """
    def __init__(self,x,y,w,h):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        
    def getX(self): return self.x
    def getY(self): return self.y
    def getWidth(self): return self.w
    def getHeight(self): return self.h
    
    def inRect(self,x,y):
        if not x < self.w: return 0
        if not y < self.h: return 0
        if not x >= self.x: return 0
        if not y >= self.y: return 0
        return 1
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        output.write(getIndent(indent)+'Rect : ' \
                    + repr(self.x) + ',' 	\
                    + repr(self.y) + ' '	\
	                + repr(self.w) + ','	\
	                + repr(self.h) + '\n')
                	             	                
    def __str__(self):
        return '(' 	+ repr(self.x) + ',' + repr(self.y) + ' '	\
	                + repr(self.w) + ',' + repr(self.h) + ')'
	               
# Scale a rectangle
def getScaledRect(scalarW,scalarH,rect):    
    return Rect(rect.getX(),rect.getY(),	\
            float(rect.getWidth())/scalarW,float(rect.getHeight())/scalarH)
    
# Shift a rectangle
def getShiftedRect(shiftX,shiftY,rect):    
    return Rect(rect.getX()+shiftX,rect.getY()+shiftY,rect.getWidth(),rect.getHeight())
        
class DrawingContext:
    """ The interface to a chainable context """
    def __init__(self,name,next=None) : 
        self.name=name
        self.next=next
    
    def realRect(self):
        """ Return the extent of this area. """
        
        # Return rectangle
        if hasattr(self,'getRealRect') and callable(self.getRealRect): 
            rect=self.getRealRect()
            if rect: return rect
        
        # We don't have one, so assume next does...
        self.enforceHasNextContext('DrawingContext.realRect')                    
        return self.getNextContext().realRect()
            
    def realPoint(self,x,y):        
    
        # Calculate (or pass though)
        if hasattr(self,'getRealPoint')and callable(self.getRealPoint): 
            (x1,y1)=self.getRealPoint(x,y)
            #log.debug(`self.name` + ' : ' + `(x,y)` + ' -> ' + `(x1,y1)`)
        else:
            (x1,y1)=(x,y)
        
        # Chain (or pass through)...
        if self.hasNextContext():
            (x2,y2)=self.getNextContext().realPoint(x1,y1)
        else:
            (x2,y2)=(x1,y1)
        
        return (x2,y2)

    def setNextContext(self,next):
        self.next=next
        
    def hasNextContext(self):
        return self.next # __next__
        
    def getNextContext(self):
        return self.next # __next__
        
    def getRootContext(self):
        if self.next: return self.next.getRootContext() # was __next__
        return self
        
    def enforceHasNextContext(self,operation):
        if not self.hasNextContext():
            raise RuntimeError("Missing 'next' context in " + str(operation))

    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        output.write(getIndent(indent)+'Class   : ' + self.__class__.__name__ + '\n')
        output.write(getIndent(indent)+'Name    : ' + self.name + '\n')
                 
class StandardDrawingContext(DrawingContext):
    """ A drawing context, is an area width*height """
    def __init__(self,name,context=None,rect=None):
        DrawingContext.__init__(self,name,context)
        if rect: self.rect=rect
        
    def getPoint(x,y):
        if not self.rect.inRect(x,y): 
            raise RuntimeError("Point not in context rectangle.")
        return (x,y)
    
    def hasRect(self):    return hasattr(self,'rect') and self.rect
    def getRealRect(self): 
        if self.hasRect(): return self.rect
    
    def getWidth(self): return self.realRect().getWidth()
    def getHeight(self): return self.realRect().getHeight()
                
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        DrawingContext.dump(self)
        if self.hasRect(): self.rect.dump(indent,output)
        output.write(getIndent(indent)+'Width   : ' + repr(self.getWidth()) + '\n')
        output.write(getIndent(indent)+'Height  : ' + repr(self.getHeight()) + '\n')
                 
class ScaledDrawingContext(StandardDrawingContext):
    def __init__(self,name,context=None,rect=None,scaledWidth=1,scaledHeight=1):
        StandardDrawingContext.__init__(self,name,context,rect)
        
        if not scaledWidth: raise RuntimeError('Can\'t scale with 0 width.')
        if not scaledHeight: raise RuntimeError('Can\'t scale with 0 height.')
            
        self.scaledWidth=scaledWidth
        self.scaledHeight=scaledHeight
        
        self.wRatio=float(self.getWidth())/self.scaledWidth
        self.hRatio=float(self.getHeight())/self.scaledHeight
    
    def getRealPoint(self,x,y):
        return (x * self.wRatio, y * self.hRatio)
        
    #:TODO: Not working
    def getWidthUnit(self): return self.wRatio
    def getHeightUnit(self): return self.hRatio
                
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        StandardDrawingContext.dump(self)
        output.write(getIndent(indent)+'wScaled : ' + repr(self.scaledWidth) + '\n')
        output.write(getIndent(indent)+'hScaled : ' + repr(self.scaledHeight) + '\n')
        output.write(getIndent(indent)+'wRatio  : ' + repr(self.wRatio) + '\n')
        output.write(getIndent(indent)+'hRatio  : ' + repr(self.hRatio) + '\n')                        
        
class ShiftedDrawingContext(StandardDrawingContext):
    def __init__(self,name,context=None,shiftedX=0,shiftedY=0):
        StandardDrawingContext.__init__(self,name,context)    
        
        if not (shiftedX or shiftedY):
            raise RuntimeError('A ShiftedDrawingContext with no shift')
            
        self.shiftedX=shiftedX
        self.shiftedY=shiftedY
    
    def getRealPoint(self,x,y):
        return (x + self.shiftedX, y + self.shiftedY)
                
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        StandardDrawingContext.dump(self)
        output.write(getIndent(indent)+'xShift  : ' + repr(self.shiftedX) + '\n')
        output.write(getIndent(indent)+'yShift  : ' + repr(self.shiftedY) + '\n')
        
class GridDrawingContext(DrawingContext):
    """ 
        
        An x/y (10/10) grid over a context (e.g. a standard 100/100)
        is a standard scaling (e.g. 1 -> 10), but followed by a 1/2
        unit shift. This is so that point fit halfway through the
        middle of their blocks. E.g. 0,0 -> 5,5 (with units of 10 points)
        
    """
    def __init__(self,name,context=None,rows=10,cols=10):
        
        # Initiaze w/o sub-context
        DrawingContext.__init__(self,name)    
        
        self.rows=rows
        self.cols=cols
        
        # Create the scale
        self.scale=ScaledDrawingContext('GridScale:'+name,context,None,rows,cols)        
        
        # Create the shift
        self.shift=ShiftedDrawingContext('GridShift:'+name,	self.scale,	0.5, 0.5)
        
        # Install this context...
        self.setNextContext(self.shift)
                        
    def getRealPoint(self,x,y):
        #if not x == int(x):
        #    raise RuntimeError, 'X isn\'t an integer [' + `x` + ']'
        #    
        #if not y == int(y):
        #    raise RuntimeError, 'Y isn\'t an integer [' + `y` + ']'
        
        return (x,y)
        
        xrange=list(range(0,self.rows))
        if not x in xrange:
            raise RuntimeError('X isn\'t in range [' + repr(x) + '] [' + repr(xrange) + ']')
            
        yrange=list(range(0,self.cols))
        if not y in yrange:
            raise RuntimeError('Y isn\'t in range [' + repr(y) + '] [' + repr(yrange) + ']')
            
        return (x,y)
                        
#    def generateRowContexts(self,context):
#        rowContexts={}
#    
#        rect=context.realRect()
#        
#        # Get the maximum rows/cols
#        (cols, rows) = self.matrix.getExtent()
#        
#        # 
#        rowHeight=rect.getHeight()/rows        
#        
#        print 'MAIN RECT: ' + str(rect)
#            
#        for row in self.matrix.getRows():
#            
#            colsOnRow=self.matrix.getRowWidth(row)
#            
#            rowRect=getShiftedRect(0,rowHeight*row,getScaledRect(1,rows,rect))
#            rowGrid=GridDrawingContext('RowGriw ' + `row`, \
#                        StandardDrawingContext('Row ' + `row`, context, rowRect),	\
#                        1, colsOnRow)
#            rowContexts[row]=rowGrid
#            row+=1
#        
#        return rowContexts
        
class XInvertDrawingContext(DrawingContext):
    """         
        Invert X        
    """
    def __init__(self,name,context,maxX):
        
        # Initiaze w/o sub-context
        DrawingContext.__init__(self,name)            
        self.maxX=maxX
                        
    def getRealPoint(self,x,y):
        return (self.maxX - x,y)        
        
class YInvertDrawingContext(DrawingContext):
    """         
        Invert Y        
    """
    def __init__(self,name,context,maxY):
        
        # Initiaze w/o sub-context
        DrawingContext.__init__(self,name,context)            
        self.maxY=maxY
                        
    def getRealPoint(self,x,y):
        return (x,self.maxY-y)
                        
class SwitchAxisDrawingContext(DrawingContext):
    """         
        Invert Y        
    """
    def __init__(self,name,context):
        
        # Initiaze w/o sub-context
        DrawingContext.__init__(self,name,context)   
                        
    def getRealPoint(self,x,y):
        return (y,x)
                        
class VirtualPoint:
    def __init__(self,x,y,context):
        self.x=x
        self.y=y
        self.context=context
        
    #:TODO: Check in root context = drawing root context? [in right tree]
    #:TODO: Check in root context? [in scope]
