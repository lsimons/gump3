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
    Resolving URLs/Files.
"""

import socket
import time
import os
import sys
import logging
from xml.sax.saxutils import escape
from string import lower,replace

from gump import log
from gump.config import *
from gump.utils import *

from gump.output.statsdb import StatisticsGuru
from gump.output.xref import XRefGuru
from gump.utils.work import *
from gump.utils.file import *

from gump.gumpenv import GumpEnvironment

from gump.model.repository import Repository
from gump.model.server import Server
from gump.model.tracker import Tracker
from gump.model.workspace import Workspace
from gump.model.module import Module
from gump.model.project import Project
from gump.model.ant import Ant
from gump.model.object import *
from gump.model.state import *

class Path(list):
    
    def __init__(self,path=None):
    
        # Import other...
        if path:
            for p in path:
                self.append(p)
    
    def __str__(self):
        return self.serialize()
        
    def postfix(self,sub):
        if sub:
            if isinstance(sub,list):
                for s in sub:
                    self.postfix(s)
            else:
                self.append(gumpSafeName(sub))   
        return self     

    def prefix(self,sub):
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
        subPath=Path(self)
        subPath.postfix(sub)        
        return subPath
        
    def getPrefixed(self,sub):
        subPath=Path(self)
        subPath.prefix(sub)        
        return subPath
    
    def getPathUp(self):
        return Path(getPathUp(len(self)))
        
    def serialize(self):
        return '/'.join(self)
   

def getShortenedPath(path,index):
    return Path(path[index:len(path)])
        
def getPathUp(depth):
    up=Path()
    i = 0
    while i < int(depth):
        up.postfix('..')
        i += 1
    return up
    
def getRelativePath(toPath,fromPath):
 
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



class Location:
    def __init__(self,path,document,index=None):
        self.path=path
        self.document=document
        self.index=index
    
    def __repr__(self):
        return self.__str__()
        
    def __str__(self):
        return `self.path`+':'+`self.document`+':'+`self.index`
        
    def getPath(self):
        return self.path
        
    def setDocument(self,document):
        self.document=document
        
    def getDocument(self):
        return self.document
        
    def setIndex(self,index):
        self.index=index
                
    def getIndex(self):
        return self.index
        
    def serialize(self):
        s=''
        if self.path:
            s+=self.path.serialize()
            s+='/'
        s+=self.document
        if self.index:
            s+='#'
            s+=self.index
        return s
    
def concatenate(root,part):
    conc=root
    if not conc.endswith('/'):
        conc+='/'
    conc+=part
    return conc
        
class Resolver:
    
    def __init__(self,rootDir,rootUrl):
        
        self.rootDir=rootDir
        # The root URL
        self.rootUrl=rootUrl    
        
    def makePath(self,path,root=None):
        if not root: root=self.rootDir
        if not os.path.exists(root):
            log.debug('Make directory : [' + root + ']')
            os.makedirs(root)
        for p in path:
            root=os.path.join(root,p)
            if not os.path.exists(root):
                log.debug('Make directory : [' + root + ']')    
                os.mkdir(root)
                
    def getRootUrl(self): 
        return self.rootUrl           
        
    def getRootDir(self):
        return self.rootDir
        
    # Bogus settings
    def getAbsoluteDirectory(self,object):
        return self.rootDir        
        
    def getAbsoluteFile(self,object,documentName=None,extn='.xml',notXDocs=None):  
        if not documentName: documentName='bogus'          
        location=Location(Path(),documentName,extn)
        file=concatenate(self.rootDir,location.serialize())
        return file                    
               
    def getAbsoluteDirectoryUrl(self,object): 
        return self.rootUrl                   
    def getAbsoluteUrl(self,object,documentName=None,extn='.html'): 
        return self.rootUrl
    def getDirectory(self,object): 
        return self.rootDir                
    def getDirectoryUrl(self,object): 
        return self.rootUrl                
        
    def getFile(self,object,documentName=None,extn='.xml',notXDocs=None): 
        return self.getAbsoluteFile(object,documentName,extn,notXDocs)                        
        
    def getUrl(self,object,documentName=None,extn='.html'):
        return self.rootUrl
    
    def getAbsoluteUrlForRelative(self,relativeToRoot): 
        return self.rootUrl              
    def getStateIconInformation(self,statePair): 
        return (self.rootUrl, statePair.getStateDescription() )
    def getImageUrl(self,name): 
        return self.rootUrl              