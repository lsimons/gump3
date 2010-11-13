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
    SVG Generation
"""

import sys
import logging

from gump import log

# Write a document Header
def writeHeader(stream):
    stream.write("""<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd ">
""")


# Write a document Footer
def writeFooter(stream):
    stream.write("""<!-- Produced by Apache Gump(TM) -->
""")
        
# Write an SVG Header
def writeSvgHeader(stream,width='8',height='12',x=80,y=120):
    stream.write("""<svg width="%scm" 
    height="%scm"
    viewBox="0 0 %s %s"
    xmlns="http://www.w3.org/2000/svg">
"""
        % (width,height,x,y))
        
def writeSvgFooter(stream):
    stream.write("""</svg>
""")
    
# Write a description
def writeDescription(stream,desc=None):
    if desc:
        writeElement(stream,'desc',desc)
           
# Write a generic element 
def writeElement(stream,tag,value):
    stream.write("""\t<%s>%s</%s>\n""" % tag,value,tag)
 
#            
def startDefinitions(stream):
    writeStart(stream,'defs')
    
def endDefinitions(stream):
    writeEnd(stream,'defs')
    
def writeStart(stream,tag,attrs=None):
    stream.write('\t<')
    stream.write(tag)
    if attrs: stream.write(attrs)
    stream.write('>\n')
    
def writeEnd(stream,tag):
    stream.write('\t</')
    stream.write(tag)
    stream.write('>\n')

class Location:
    def __init__(self,x=0,y=0):
        self.x=x
        self.y=y
        
class SvgDefaults:
    def __init__(): pass
                
class Entity:
    def __init__(self,locn,attrs=None):
        self.location=locn
        self.attrs={}
        if attrs:
            self.attrs=attrs
            
    def getLocation(self):
        return location
        
    def getAttributes(self):
        return attributes
        
def getSvgSizes(w,h):
    """ Don't allow SVGs wider than 25 centimeters, and scale """
    
    # Assume the pixels are at least an order of
    # magnitude larger than we'd like this in
    # centimeters. :TODO: Unhack these values,
    # which basically work for DepDiag only...
    svgW=int(w/30)
    svgH=int(h/30)
    
    if svgW > 20:
        ratio = float(svgW)/20
        svgH=svgH/ratio # Assume browser, so can scroll down
        svgW=svgW/ratio # (ought give 20)
        
    return (int(svgW), int(svgH))
        
class SimpleSvg:
    def __init__(self,viewWidth=80,viewHeight=120,width=-1,height=-1):
        self.width=width
        self.height=height
        self.viewWidth=float(viewWidth)
        self.viewHeight=float(viewHeight)
        
        # Try to size for the user...
        if -1 == width or -1 == height:
            (self.width, self.height) = getSvgSizes(viewWidth,viewHeight)
        
        self.description=None
        
        self.definitions=[]
        self.actions=[]
        
    def formatElement(self,type,attrs,content=None):
        
        element=''
        if 'comment' in attrs:
            element += '<!-- ' + str(attrs['comment']) + ' -->\n        '
        
        # Construct <type a="" b="" /> w/ a,b,... from list
        element+='<'
        element+=type
        element+=''
        
        attrList=[]
        if 'path' == type:
            attrList=['d','fill','stroke','stroke-width']
        elif 'rect' == type:
            attrList=['x','y','width','height','fill','stroke','stroke-width']
        elif 'text' == type:
            attrList=['x','y','fill','stroke','stroke-width']
            
        for attr in attrList:
            if attr in attrs:
                element+=' '
                element+=attr				# Attribute Name
                element+='=\"'
                element+=str(attrs[attr])	# Value
                element+='\"'
        
        if content:
            element+='>'
            element+=content 
            element+='</'
            element+=type    
            element+='>'
        else:                
            element+='/>'            
        
        return element
        
    def addAction(self,type,attrs,content=None):
   
        # Store it ...
        self.actions.append(self.formatElement(type,attrs,content))
        
    def addBorder(self):
    
        # Make stroke width proportional, but not greater than 1
        w=min(self.viewWidth*0.01,self.viewHeight*0.01)
        if w > 1: w = 1
        self.addRect(w,w,self.viewWidth-w,self.viewHeight-w,	\
                        {'stroke':'black','stroke-width':w,'fill':'none',	\
                            'comment':'Border Rectangle'})


        #print '(ROWS,COLS) : ' + `(rows, cols)`
        #for r in range(0,rows):
        #    for c in range(0,cols):
        #        print 'DOTTY (ROW,COL): ' + `(r,c)`
        #        (x,y)=context.realPoint(r,c)
        #        svg.addSpot(x,y)
        #        svg.addText(x,y, `(r,c)`, {'stroke':'black'})
                
    def addSpot(self,x,y):
        self.addRect(x-2,y-2,4,4,	\
                        {'stroke':'black','stroke-width':1,'fill':'black',	\
                            'comment':'Spot Rectangle'})
        
    def addRect(self,x,y,w,h,attrs):
        
        # Side effect...
        attrs['x']=x        
        attrs['y']=y
        attrs['width']=w
        attrs['height']=h
        
        self.addAction('rect',attrs)
        
    def addLine(self,x1,y1,x2,y2,attrs):
        
        # Side effect...
        attrs['d']='M %s %s L %s %s' % (x1,y1,x2,y2)
        
        self.addAction('path',attrs)
        
    def addText(self,x,y,text,attrs):
        
        # Side effect...
        attrs['x']=x        
        attrs['y']=y
        
        self.addAction('text',attrs,text)
        
    def serialize(self,stream=None):
        
        if not stream:
            stream=sys.stdout
            doNotClose=1
        
        try:
            writeHeader(stream)
            writeSvgHeader(stream,self.width,self.height,self.viewWidth,self.viewHeight)
            if self.description:
                writeDesc(stream,self.description)
                    
            if self.definitions:
                startDefinitions(stream)
                    
                for definition in self.definitions:                     
                    stream.write('        ')
                    stream.write(action)
                    stream.write('\n')
                        
                endDefinitions(stream)
                    
            if self.actions:
                for action in self.actions:                        
                    stream.write('        ')
                    stream.write(action)
                    stream.write('\n')
                    
            writeSvgFooter(stream)
            writeFooter(stream)
        except Exception, details:
            log.error("Failed to serialize SVG: " + str(details), exc_info=1)
            raise
            
    def serializeToFile(self,fileName):
        stream=open(fileName,'w')
        try:
            self.serialize(stream)
        finally:
            stream.close()
