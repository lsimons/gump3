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
    SVG Generation
"""

import sys
import logging

from gump import log

# Write a document Header
def writeHeader(stream):
    stream.write("""<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd ">""")


# Write a document Footer
def writeFooter(stream):
    pass
        
# Write an SVG Header
def writeSvg(width='8cm',height='12cm',x=80,y=120):
    stream.write("""<svg width="%s" 
    height="%s"
    viewBox="%s %s %s %s"
    xmlns="http://www.w3.org/2000/svg">
    """
        % width,height,0,0,x,y)
    
# Write a description
def writeDescription(stream,desc=None):
    if desc:
        writeElement(stream,'desc',desc)
           
# Write a generic element 
def writeElement(stream,tag,value):
    stream.write("""\t<%s>%s</%s>\n""" % tag,value,tag)
 
#            
def startDefinitions(self):
    writeStart('defs')
    
def endDefinitions(self):
    writeEnd('defs')
    
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
        
class SimpleSvg:
    def __init__(self,width='8cm',height='12cm',x=80,y=120):
        self.width=width
        self.height=height
        self.x=x
        self.y=y
        
        self.definitions=[]
        self.actions=[]
        
    def addAction(self,type,x,y,context=None):
        pass
        
    def serialize(self,stream=None):
        
        if not stream:
            stream=sys.stdout
            doNotClose=1
        
        try:
            try:
                writeHeader(stream)
                writeSvg(stream,self.width,self.height,self.x,self.y)
                if self.description:
                    writeDesc(stream,self.description)
                if self.definitions:
                    startDefinitions(stream)
                    
                    for definition in self.definitions:
                        #:TODO: write...
                        pass
                        
                    endDefinitions(stream)
                writeFooter(stream)
            except:
                pass
        finally:        
            if not doNotClose: stream.close()