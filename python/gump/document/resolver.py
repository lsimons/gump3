#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/document/resolver.py,v 1.7 2003/12/06 18:01:48 ajack Exp $
# $Revision: 1.7 $
# $Date: 2003/12/06 18:01:48 $
#
# ====================================================================
#
# The Apache Software License, Version 1.1
#
# Copyright (c) 2003 The Apache Software Foundation.  All rights
# reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. The end-user documentation included with the redistribution, if
#    any, must include the following acknowlegement:
#       "This product includes software developed by the
#        Apache Software Foundation (http://www.apache.org/)."
#    Alternately, this acknowlegement may appear in the software itself,
#    if and wherever such third-party acknowlegements normally appear.
#
# 4. The names "The Jakarta Project", "Alexandria", and "Apache Software
#    Foundation" must not be used to endorse or promote products derived
#    from this software without prior written permission. For written
#    permission, please contact apache@apache.org.
#
# 5. Products derived from this software may not be called "Apache"
#    nor may "Apache" appear in their names without prior written
#    permission of the Apache Group.
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
# ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# ====================================================================
#
# This software consists of voluntary contributions made by many
# individuals on behalf of the Apache Software Foundation.  For more
# information on the Apache Software Foundation, please see
# <http://www.apache.org/>.

"""
    xdoc generation, for forrest
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
from gump.model.repository import Repository
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
   
def getPathForObject(object,visited=None):
    if not visited:visited=[] 
    visited.append(object)
           
    # Determine Path
    if isinstance(object, Workspace):
        path=Path()
    elif isinstance(object, Repository):
        path=Path(['gump_repo'])
    elif isinstance(object, StatisticsGuru):
        path=Path(['gump_stats'])
    elif isinstance(object, XRefGuru):
        path=Path(['gump_xref'])
    elif isinstance(object, Module):
        path=getPathForObject(object.getWorkspace()).getPostfixed(object.getName())
    elif isinstance(object, Project):
        path=getPathForObject(object.getModule())
    elif isinstance(object, WorkItem):
        path=getPathForObject(object.getOwner()).getPostfixed('work')        
    elif isinstance(object, Ownable):
        if not object.getOwner() in visited:
            path=getPathForObject(object.getOwner())
        else:
            dump(visited)
            raise RuntimeError, "Circular visits acquiring path for :" + `object`
    else:
        raise RuntimeError, "Can't acquire path for :" + `object`
    
    return path
        
def getDepthForObject(object):
    return len(getPathForObject(object))

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

def getRelativeLocation(toObject,fromObject,extn='.xml'):
        
    #
    # Get the target location, get the from path
    # and get relative...
    #
    toLocation=getLocationForObject(toObject,extn)
    toPath=toLocation.getPath()
    fromPath=getPathForObject(fromObject)
        
    relativePath=getRelativePath( toPath, fromPath )
        
    return Location( 	relativePath,
                        toLocation.getDocument(),
                        toLocation.getIndex() )
        
        
def getLocationForObject(object,extn='.xml'):
    return Location(getPathForObject(object),
                    getDocumentForObject(object,extn),
                    getIndexForObject(object))
                    
def getDocumentForObject(object, extn='.xml', visited=None):
    if not visited:visited=[] 
    visited.append(object)
            
    if isinstance(object, Workspace) or isinstance(object, Module) \
        or isinstance(object,StatisticsGuru) 	\
        or isinstance(object,XRefGuru) :    
        document="index"+extn
    elif isinstance(object, Project) 	\
        or isinstance(object, Repository)	\
        or isinstance(object, WorkItem):    
        document=gumpSafeName(object.getName()) + extn
    elif isinstance(object, Ownable) :
        document=getDocumentForObject(object.getOwner(),extn,visited)
    else:
        raise RuntimeError, "Unable to determine document for:" + `object`
            
    return document

def getLinkBetween(toObject,fromObject):
    return getRelativeLocation(toObject,fromObject).serialize()
                        
def getIndexForObject(object):
    
    if 	isinstance(object, Workspace)	or	\
        isinstance(object, Repository)	or	\
        isinstance(object, StatisticsGuru)	or	\
        isinstance(object, XRefGuru)	or	\
        isinstance(object, Module)		or	\
        isinstance(object, Project)		or	\
        isinstance(object, Work):  
        index=None
    elif isinstance(object, Ant):
        index='Build'
    else:
        index=None            
        
    return index  

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
        
        # Content
        contentSubPath=Path(['forrest','src','documentation','content'])
        self.makePath(contentSubPath,rootDir)                
        self.contentDir=concatenate(rootDir,contentSubPath.serialize())
        
        # XDocs
        xdocsSubPath=Path(['forrest','src','documentation','content','xdocs'])
        self.makePath(xdocsSubPath,rootDir)                
        self.xdocsDir=concatenate(rootDir,xdocsSubPath.serialize())
        
        # The root URL
        self.rootUrl=rootUrl    
        
    def makePath(self,path,root=None):
        if not root: root=self.rootDir
        if not os.path.exists(root):
            log.debug('Make directory : [' + root + ']')
            os.mkdir(root)
        for p in path:
            root=os.path.join(root,p)
            if not os.path.exists(root):
                log.debug('Make directory : [' + root + ']')    
                os.mkdir(root)
    
   # :TODO: Do we need to also have this for content not xdocs?
    def getAbsoluteDirectory(self,object):
        path=getPathForObject(object)
        self.makePath(path)
        return concatenate(self.xdocsDir,path.serialize())
        
    def getAbsoluteFile(self,object,documentName=None,extn='.xml'):
        location=getLocationForObject(object)
        if documentName: 
            if not documentName.endswith(extn):
                documentName += extn
            location.setDocument(documentName)
            
        # XDocs in one place, content in another
        # This is a tad lame, not a great way to detect
        # xdocs, but ok for now.
        if not extn == '.xml':
            self.makePath(location.getPath(),self.contentDir)
            file=concatenate(self.contentDir,location.serialize())
        else:
            self.makePath(location.getPath(),self.xdocsDir)
            file=concatenate(self.xdocsDir,location.serialize())
            
        return file
                    
            
    def getAbsoluteDirectoryUrl(self,object):
        return concatenate(self.rootUrl,getPathForObject(object).serialize())
           
    def getAbsoluteUrl(self,object,documentName=None,extn='.html'):
        location=getLocationForObject(object,extn)
        if documentName: location.setDocument(documentName)
        return concatenate(self.rootUrl,location.serialize())

    #
    # Object stuff...
    #
    def getDirectory(self,object):
        return self.getAbsoluteDirectory(object)
        
    def getDirectoryUrl(self,object):
        return self.getAbsoluteDirectory(object)
        
    def getFile(self,object,documentName=None,extn='.xml'):
        return self.getAbsoluteFile(object,documentName,extn)
        
    def getUrl(self,object,documentName=None,extn='.html'):
        return self.getAbsoluteUrl(object,documentName,extn)
        
        
    def getRootUrl(self):
        return self.rootUrl
        
    def getAbsoluteUrlForRelative(self,relativeToRoot):
        return concatenate(self.rootUrl,relativeToRoot)
        
    def getStateIconInformation(self,statePair):
        
        # :TODO: Move this to some resolver, and share with RSS
        sname=statePair.getStateDescription()  
        rdesc=statePair.getReasonDescription()
            
        description=sname    
        if rdesc: 
            description+=' with reason '+rdesc
        
        # Build the URL to the icon
        iconName=gumpSafeName(lower(replace(sname,' ','_')))
        url = self.getAbsoluteUrlForRelative("gump_icons/"+iconName+".png")
        
        return (url, description)