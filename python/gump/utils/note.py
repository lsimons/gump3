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
    This module contains 'annotations'
"""

import sys

from gump.utils import *

LEVEL_UNSET=0
LEVEL_DEBUG=1
LEVEL_INFO=2
LEVEL_WARNING=3
LEVEL_ERROR=4
LEVEL_FATAL=5

levelDescriptions = { 	LEVEL_UNSET : "Not Set",
                    LEVEL_DEBUG : "Debug",
                    LEVEL_INFO : "Info",
                    LEVEL_WARNING : "Warning",
                    LEVEL_ERROR : "Error",
                    LEVEL_FATAL : "Fatal" }               

def levelName(level):
    return levelDescriptions.get(level,'Unknown Level:' + str(level))
    
class Annotation:
    """ An annotation ... a log entry on the object ..."""
    def __init__(self,level,text):
        self.level=level
        self.text=text
        
    def __str__(self):
        return levelName(self.level) + ":" + self.text      
        
    def getLevelName(self):
        return levelName(self.level) 
    
    def getText(self):
        return self.text
    
    def dump(self, indent=0, output=sys.stdout):        
        output.write(getIndent(indent)+str(self)+'\n')
        
class Annotatable:
    
    def __init__(self):
        self.annotations=[]

    def __del__(self):
        self.annotations=None

    def addDebug(self,text):
        self.addAnnotation(LEVEL_DEBUG, text)        

    def addInfo(self,text):
        self.addAnnotation(LEVEL_INFO, text)
        
    def addWarning(self,text):
        self.addAnnotation(LEVEL_WARNING, text)
        
    def addError(self,text):
        self.addAnnotation(LEVEL_ERROR, text)
        
    def addFatal(self,text):
        self.addAnnotation(LEVEL_FATAL, text)
        
    def addAnnotation(self,level,text):
        self.addAnnotationObject(Annotation(level,text))
        
    def addAnnotationObject(self,note):
        self.annotations.append(note)
        
    def getAnnotations(self):
        return self.annotations
        
    def containsNasties(self):
        return self.containsOrAbove(LEVEL_WARNING)
        
    def containsOrAbove(self,level):
        for note in self.annotations:
            if note.level >= level:
                return 1
        return 0
                
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """         
        if self.annotations:
            output.write(getIndent(indent)+'Annotations:\n')
       
            for note in self.annotations:
                note.dump(indent+1,output)    
                    
    def getAnnotationsAsString(self,eol="\n"):
        notes=''
        
        if self.annotations:
            for note in self.annotations:
                notes += str(note) + eol    
    
        return notes
                
def transferAnnotations(source,destination):
    for note in source.annotations:
        destination.addAnnotationObject(note)
    
  
        