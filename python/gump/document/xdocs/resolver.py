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

import time
import os
import sys
from xml.sax.saxutils import escape
from string import lower,replace

from gump import log
from gump.core.config import *
from gump.utils import *

from gump.utils.work import *
from gump.utils.file import *

from gump.core.gumpenv import GumpEnvironment
from gump.core.gumprun import GumpRun

from gump.model.repository import Repository
from gump.model.server import Server
from gump.model.tracker import Tracker
from gump.model.workspace import Workspace
from gump.model.module import Module
from gump.model.project import Project
from gump.model.ant import Ant
from gump.model.object import *
from gump.model.state import *

from gump.document.resolver import *

from gump.guru.stats import *
from gump.guru.xref import *


def getPathForObject(object,visited=None):
    if not visited:visited=[] 
    visited.append(object)
           
    # Determine Path
    if isinstance(object, Workspace) or isinstance(object, GumpRun):
        path=Path()
    elif isinstance(object, GumpEnvironment):
        path=Path()
    elif isinstance(object, Repository):
        path=Path(['gump_repo'])
    elif isinstance(object, Server):
        path=Path(['gump_srv'])
    elif isinstance(object, Tracker):
        path=Path(['gump_track'])
    elif isinstance(object, StatisticsGuru):
        path=Path(['gump_stats'])
    elif isinstance(object, XRefGuru):
        path=Path(['gump_xref'])
    elif isinstance(object, Module):
        path=getPathForObject(object.getWorkspace()).getPostfixed(object.getName())
    elif isinstance(object, Project):
        path=getPathForObject(object.getModule()).getPostfixed(object.getName())
    elif isinstance(object, WorkItem):
        path=getPathForObject(object.getOwner()).getPostfixed('gump_work')  
    elif isinstance(object, FileReference):
        path=getPathForObject(object.getOwner()).getPostfixed('gump_file')        
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
            
    if isinstance(object, GumpRun) \
        or isinstance(object, Module) \
        or isinstance(object, Project) 	\
        or isinstance(object,StatisticsGuru) 	\
        or isinstance(object,XRefGuru) :    
        document="index"+extn
    elif isinstance(object, Workspace):
        document="workspace"+extn           
    elif isinstance(object, GumpEnvironment):
        document="environment"+extn            
    elif isinstance(object, Server)	\
        or isinstance(object, Tracker)	\
        or isinstance(object, Repository)	\
        or isinstance(object, FileReference) \
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
        isinstance(object, GumpEnvironment)	or	\
        isinstance(object, Server)	or	\
        isinstance(object, Tracker)	or	\
        isinstance(object, Repository)	or	\
        isinstance(object, StatisticsGuru)	or	\
        isinstance(object, XRefGuru)	or	\
        isinstance(object, Module)		or	\
        isinstance(object, Project)		or	\
        isinstance(object, WorkItem)	or	\
        isinstance(object, FileReference):  
        index=None
    elif isinstance(object, Ant):
        index='Build'
    else:
        index=None            
        
    return index  

class XDocResolver(Resolver):
    
    def __init__(self,rootDir,rootUrl):
        
        Resolver.__init__(self,rootDir,rootUrl)

        # Content
        #contentSubPath=Path(['forrest-work','src','documentation','content'])
        contentSubPath=Path(['forrest-work','content'])
        self.makePath(contentSubPath,rootDir)                
        self.contentDir=concatenate(rootDir,contentSubPath.serialize())
        
        # XDocs
        #xdocsSubPath=Path(['forrest-work','src','documentation','content','xdocs'])
        xdocsSubPath=Path(['forrest-work','content','xdocs'])
        self.makePath(xdocsSubPath,rootDir)                
        self.xdocsDir=concatenate(rootDir,xdocsSubPath.serialize())
    
   # :TODO: Do we need to also have this for content not xdocs?
    def getAbsoluteDirectory(self,object):
        path=getPathForObject(object)
        self.makePath(path)
        return concatenate(self.xdocsDir,path.serialize())
        
    def getAbsoluteFile(self,object,documentName=None,extn='.xml',notXDocs=None):
        location=getLocationForObject(object)
        if documentName: 
            if not documentName.endswith(extn):
                documentName += extn
            location.setDocument(documentName)
            
        # XDocs in one place, content in another...
        if (not extn == '.xml' and not extn == '.svg') or notXDocs:
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
        if documentName:         
            if not documentName.endswith(extn):
                documentName += extn
            location.setDocument(documentName)
        return concatenate(self.rootUrl,location.serialize())
        
    #
    # Object stuff...
    #
    def getDirectory(self,object):
        return self.getAbsoluteDirectory(object)
        
    def getDirectoryUrl(self,object):
        return self.getAbsoluteDirectory(object)
        
    def getFile(self,object,documentName=None,extn='.xml',notXDocs=None):
        return self.getAbsoluteFile(object,documentName,extn,notXDocs)
        
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
        url = self.getAbsoluteUrlForRelative('gump_icons/'+iconName+'.png')
        
        return (url, description)
        
    def getImageUrl(self,name):
        return self.getAbsoluteUrlForRelative('images/'+name)