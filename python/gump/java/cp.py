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

    Classpaths
    
"""

import os
from string import split
from gump.utils.note import transferAnnotations, Annotatable

#
# An annotated path has a path entry, plus the context
# of the contributor (i.e. project of Gump.)
#
class AnnotatedPath:
    """Contains a Path plus optional 'contributor' """
    def __init__(self,id,path,contributor=None,instigator=None,note=None):
        self.id=id
        self.path=path
        self.contributor=contributor
        self.instigator=instigator
        self.note=note
        
    def __repr__(self):
        return self.path
        
    def __str__(self):
        return self.path
        
    # Equal if same string
    def __eq__(self,other):
        if not isinstance(other,AnnotatedPath):
            otherPath = other
        else:
            otherPath = other.path             
        return self.path == otherPath
                
    # Equal if same string
    def __cmp__(self,other):
        if not isinstance(other,AnnotatedPath):
            otherPath = other
        else:
            otherPath = other.path                         
        c = cmp(self.path,otherPath)
        return c
        
    def hasContributor(self):
        """ Do we know which entity contributed this path component? """
        if self.contributor: return True
        return False
        
    def getContributor(self):
        """ The cotributing entity """
        return self.contributor
        
    def hasId(self):
        if self.id: return True
        return False
        
    def getId(self):
        return self.id
        
    def hasInstigator(self):
        """ Do we know which entity instagated this path component? """    
        if self.instigator: return True
        return False
        
    def getInstigator(self):
        """ The instagating entity """    
        return self.instigator
        
    def getPath(self):
        return self.path
        
class Classpath(Annotatable):
    def __init__(self,name):
        Annotatable.__init__(self)
        self.name=name
        self.parts=[]
        
    def __del__(self):
        Annotatable.__del__(self)       
        self.parts=None     
    
    def getName(self):
        return self.name
        
    def addPathPart(self,part):
        if part in self.parts:
            self.addDebug('Duplicate Path Part [' + `part` + ']')
        else:
            self.parts.append(part)
        
    def importFlattenedParts(self,parts):
        for part in split(parts,os.pathsep):
            self.addPathPart(part)
            
    def importClasspath(self,cp):
        for part in cp.getPathParts():
            self.addPathPart(part)
    
    def getPathParts(self):
        return self.parts
                        
    #
    # Convert path and AnnotatedPath to simple paths.
    # 
    def getSimpleClasspathList(self):
        """ Return simple string list """
        simple=[]
        for p in self.parts:
            if isinstance(p,AnnotatedPath):
                simple.append(p.path)
            else:
                simple.append(p)
        return simple
        
    def getFlattened(self):
        return os.pathsep.join(self.getSimpleClasspathList())
            