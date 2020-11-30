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
    Resolving URLs/Files.
"""

import socket
import time
import os
import sys
import logging
from xml.sax.saxutils import escape

from gump import log
from gump.core.config import *
from gump.util import *

from gump.util.work import *
from gump.util.file import *

from gump.core.run.gumpenv import GumpEnvironment

from gump.core.model.repository import Repository
from gump.core.model.server import Server
from gump.core.model.tracker import Tracker
from gump.core.model.workspace import Workspace
from gump.core.model.module import Module
from gump.core.model.project import Project
from gump.core.model.object import *
from gump.core.model.state import *

def concatenateUrl(root,part):
    conc=''
    if not '.'==root:
        conc=root
        if not conc.endswith('/'):
            conc+='/'
    conc+=part
    return conc

class Path(list):
    """
    
    	Path manipulable as a list of parts (from a root)
    	
    """
    def __init__(self,path=None):
    
        # Import other...
        if path:
            for p in path:
                self.append(p)
    
    def __str__(self):
        return self.serialize()
        
    def postfix(self,sub):
        """
            Add a path to the end of this one
        """
        if sub:
            if isinstance(sub,list):
                for s in sub: self.postfix(s)
            else:
                self.append(gumpSafeName(sub))   
        return self     

    def prefix(self,sub):
        """
        	Add a path to the front of this one
        """
        if sub:
            if isinstance(sub,list):
                rev=list(sub) # Clone
                rev.reverse() # Reverse
                for r in rev: # Prefix each one...
                    self.prefix(r)
            else:
                self.insert(0,gumpSafeName(sub))   
        return self     

    def getPostfixed(self,sub):
        """
        	Add two paths,
        """
        subPath=Path(self)
        subPath.postfix(sub)        
        return subPath
        
    def getPrefixed(self,sub):
        """
        	
        """
        subPath=Path(self)
        subPath.prefix(sub)        
        return subPath
    
    def getPathUp(self):
        """
        	Get a path 'up' to the root, from here (e.g. ../..)
        """
        return getPathUp(self.getPathLength())
        
    def getPathLength(self):
        return len(self)
        
    def serialize(self,sep=os.sep):
        """
        	Represent as a string, using the appropriate
        	separator
        """
        s=sep.join(self)
        if not s: return '.'
        return s
   
def getShortenedPath(path,index):
    """
    	Create a trimmed path (from index to end)
    """
    return Path(path[index:len(path)])
        
def getPathUp(depth):
    """
    	Get a path 'up' a given depth
    """
    up=Path()
    i = 0
    while i < int(depth):
        up.postfix('..')
        i += 1
    return up
    
def getRelativePath(toPath,fromPath):
    """
    
    	Get a path from one path to another path.
    	
    """
 
    # print "Get Relative TO:[" + `toPath` + "] FROM:[" + `fromPath` + "]"
    
    # If paths aren't identicle
    # (and both empty would be identicle)
    if fromPath:                    
        if toPath:
            # See if both in same sub-dir
            fromPart=fromPath[0]    
            toPart=toPath[0]            
            if fromPart==toPart:
                # Both in same sub-directory...                    
                return getRelativePath(
                            getShortenedPath(toPath,1),
                            getShortenedPath(fromPath,1))  
            
            # Come up and go down...
            else:
                return fromPath.getPathUp().postfix(toPath)           
        else:
            return fromPath.getPathUp()            
        
    return Path(toPath)


class FileSpecification:
    """ 
        A root (or None for relative), a relative path, and a document    
    """
    def __init__(self,root,path,document):
        self.root=root
        self.path=path
        self.document=document
    
    def __repr__(self):
        return self.__str__()
        
    def __str__(self):
        return repr(self.root)+':'+repr(self.path)+':'+repr(self.document)
        
    def setRoot(self,root):
        self.root=root
        
    def getRoot(self):
        return self.root
        
    def getPath(self):
        return self.path
        
    def setDocument(self,document):
        self.document=document
        
    def getDocument(self):
        return self.document
  
    def serialize(self):
        s=''
        if self.path:
            s+=self.path.serialize()
            s+='/'
        s+=self.document
        return s
        
    def getFile(self):
        if not self.root:
            return  os.path.join(self.path.serialize(), self.document)
          
        return os.path.abspath(
                    os.path.join(
                        os.path.join(
                            self.root, 
                            self.path.serialize()),
                        self.document))
        
    def getRootPath(self):
        return self.path.getPathUp().serialize()
    
class Location(FileSpecification):
    """ 
    	A path, a document, and an index (into that document)	
    """
    def __init__(self,root,path,document,index=None):
        FileSpecification.__init__(self,root,path,document)
        self.index=index
    
    def __repr__(self):
        return self.__str__()
        
    def __str__(self):
        return FileSpecification.__str__(self)+':'+repr(self.index)
        
    def setIndex(self,index):
        self.index=index
                
    def getIndex(self):
        return self.index
        
    def serialize(self):
        s=FileSpecification.serialize(self)
        if self.index:
            s+='#'
            s+=self.index
        return s
    
class Resolver:
    """
    
    	Resolve objects to paths/files/dirs/urls
    	
    """
    
    def __init__(self,rootDir,rootUrl):
        
        # The root directory
        self.rootDir=rootDir
        
        # The root URL
        self.rootUrl=rootUrl    
        
    def makePath(self,path,root=None):
        if not root: root=self.rootDir
        if not os.path.exists(root):
            #log.debug('Make directory : [' + root + ']')
            os.makedirs(root)
        for p in path:
            root=os.path.join(root,p)
            if not os.path.exists(root):
                #log.debug('Make directory : [' + root + ']')    
                os.mkdir(root)
                
    def getRootUrl(self): 
        return self.rootUrl           
        
    def getRootDir(self):
        return self.rootDir
        
    # Skeleton
    
    def getDirectoryRelativePath(self,object):
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getDirectoryRelativePath.')
        
    def getDirectoryPath(self,object):
        path=self.getDirectoryRelativePath(object)
        self.makePath(path)   
        return path
        
    def getDirectory(self,object):
        path=self.getDirectoryPath(object)    
        return os.path.join(self.xdocsDir,path.serialize())
        
    def getFileSpec(self,object,documentName=None,extn=None,rawContent=False):  
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getFileSpec.')
        
    def getFile(self,object,documentName=None,extn=None,rawContent=False):  
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getFile.')
        
    def getDirectoryUrl(self,object): 
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getDirectoryUrl.')
           
    def getUrl(self,object,documentName=None,extn=None): 
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getUrl.')
        
    def getAbsoluteUrlForRelative(self,relativeToRoot):
        """
            Get an absolute URL, relative to a root
        """
        return concatenateUrl(self.rootUrl,relativeToRoot)    
        
    def getStateIconInformation(self,statePair): 
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getStateIconInformation.')
         
    def getAbsoluteImageUrl(self,name):
        return self.getAbsoluteFromRelative(self.getImageUrl(name))
        
    def getImageUrl(self,name,depth=0): 
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getImageUrl.')    
           
    def getAbsoluteIconUrl(self,name):
        return self.getAbsoluteFromRelative(self.getIconUrl(name))
        
    def getIconUrl(self,name,depth=0): 
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getIconUrl.')
