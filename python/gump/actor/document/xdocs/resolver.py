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

    Resolving URLs/Files for Gump objects.
    
"""

import time
import os
import sys
from xml.sax.saxutils import escape
from string import lower,replace

from gump import log
from gump.core.config import *
from gump.util import *

from gump.util.work import *
from gump.util.file import *

from gump.core.run.gumpenv import GumpEnvironment
from gump.core.run.gumprun import GumpRun

from gump.core.model.repository import Repository
from gump.core.model.server import Server
from gump.core.model.tracker import Tracker
from gump.core.model.workspace import Workspace
from gump.core.model.module import Module
from gump.core.model.project import Project
from gump.core.model.builder import Ant,NAnt,Maven,Maven1,Script,Configure,Make
from gump.core.model.object import *
from gump.core.model.state import *

from gump.actor.document.resolver import *
from gump.actor.document.xdocs.config import *

from gump.tool.guru.stats import *
from gump.tool.guru.xref import *

def getPathForObject(object,visited=None):
    """
    	Get the path to a given object, recursing where
    	neccessary (e.g. to get path of project under
    	path for module). Ensure no infinite recursion
    	using a dynamic list of visited objects.
    """
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
    """
    	How 'deep' is this object (under the root)
    """
    return len(getPathForObject(object))

def getRelativeLocation(toObject,fromObject,extn):
    """
    Give the location relative to another
    """
    toLocation=getLocationForObject(toObject,extn)
    toPath=toLocation.getPath()
    fromPath=getPathForObject(fromObject)
        
    relativePath=getRelativePath( toPath, fromPath )
        
    return Location( 	None,
                        relativePath,
                        toLocation.getDocument(),
                        toLocation.getIndex() )
        
        
def getLocationForObject(object,extn):
    """
    	Get the *relative* location for an object
    	[relative to root]
    """
    return Location(None,
                    getPathForObject(object),
                    getDocumentForObject(object,extn),
                    getIndexForObject(object))
                    
def getDocumentForObject(object, extn, visited=None):
    """
    	What document describes this object?
    """
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
    """
    	Link from one to another
    """
    return getRelativeLocation(toObject,fromObject,'.html').serialize()
                        
def getIndexForObject(object):
    """
    	Get the index (into a document) for an object
    """
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
    elif isinstance(object, Ant) or \
        isinstance(object, NAnt) or \
        isinstance(object, Maven) or \
        isinstance(object, Maven1) or \
        isinstance(object, Configure) or \
        isinstance(object, Make) or \
        isinstance(object, Script) :
        index='Build'
    else:
        index=None            
        
    return index  

class XDocResolver(Resolver):
    
    def __init__(self,rootDir,rootUrl,config=None):
        
        Resolver.__init__(self,rootDir,rootUrl)

        if not config:
            config=XDocConfig()
        self.config=config
        
        # Content
        #contentSubPath=Path(['xdocs-work','src','documentation','content'])
        if not self.config.isXhtml():
            contentSubPath=Path(['xdocs-work','content'])
        else:
            contentSubPath=Path(['xdocs-work'])
        self.makePath(contentSubPath,rootDir)                
        self.contentDir=os.path.join(rootDir,contentSubPath.serialize())
            
        if not self.config.isXhtml():
            
            # XDocs
            #xdocsSubPath=Path(['xdocs-work','src','documentation','content','xdocs'])
            xdocsSubPath=Path(['xdocs-work','content','xdocs'])
            self.makePath(xdocsSubPath,rootDir)                
            self.xdocsDir=os.path.join(rootDir,xdocsSubPath.serialize())
        else:
            # :TODO: Clean-up this. Don't set xdocsDir, just don't use it...
            self.xdocsDir=self.contentDir
    
    def getDirectoryRelativePath(self,object):
        return getPathForObject(object)

    def getFileSpec(self,object,documentName=None,extn=None,rawContent=False):
        # Could be configured for .html (XHTML) or .xml (XDOCS)
        if not extn:
            extn=self.config.getExtension()
            
        # Ascertain the location (path/document/index)
        location=getLocationForObject(object,extn)
        if documentName: 
            if not documentName.endswith(extn):
                documentName += extn
            location.setDocument(documentName)
            
        # XDocs in one place, raw content/XHTML in another...
        if self.config.isXdocs() and (not extn == '.xml' and not extn == '.svg') or rawContent:
            self.makePath(location.getPath(),self.contentDir)
            file=os.path.join(self.contentDir,location.serialize())
            # Stash the root (that this path is relative to)
            location.setRoot(self.contentDir)    
        else:
            self.makePath(location.getPath(),self.xdocsDir)
            file=os.path.join(self.xdocsDir,location.serialize())
            # Stash the root (that this path is relative to)
            location.setRoot(self.xdocsDir)    
            
        return location                    
        
    def getFile(self,object,documentName=None,extn=None,rawContent=False):
        # Could be configured for .html (XHTML) or .xml (XDOCS)
        if not extn:
            extn=self.config.getExtension()
            
        # Ascertain the location (path/document/index)
        location=getLocationForObject(object,extn)
        if documentName: 
            if not documentName.endswith(extn):
                documentName += extn
            location.setDocument(documentName)
            
        location.setRoot(self.xdocsDir)
        
        # XDocs in one place, raw content/XHTML in another...
        if self.config.isXdocs() and (not extn == '.xml' and not extn == '.svg') or rawContent:
            self.makePath(location.getPath(),self.contentDir)
            file=os.path.join(self.contentDir,location.serialize())
        else:
            self.makePath(location.getPath(),self.xdocsDir)
            file=os.path.join(self.xdocsDir,location.serialize())
            
        return file                    
            
    def getDirectoryUrl(self,object):
        return concatenateUrl(self.rootUrl,getPathForObject(object).serialize('/'))
           
    def getUrl(self,object,documentName=None,extn='.html'):
        location=getLocationForObject(object,extn)
        if documentName:         
            if not documentName.endswith(extn):
                documentName += extn
            location.setDocument(documentName)
        return concatenateUrl(self.rootUrl,location.serialize()) 
        
    def getStateIconInformation(self,statePair,depth=0):
        """
        	Get the URL (and ALT description) for a state pair
        """
        
        # :TODO: Move this to some resolver, and share with RSS
        sname=statePair.getStateDescription()  
        rdesc=statePair.getReasonDescription()
            
        description=sname    
        if rdesc: 
            description+=' with reason '+rdesc
        
        # Build the URL to the icon
        iconName=gumpSafeName(lower(replace(sname,' ','_')))
        url = self.getIconUrl(iconName+'.png',depth)
        
        return (url, description)
        
    def getImageUrl(self,name,depth=0):
        """
            Get URL for a given image
        """
        return getPathUp(depth).postfix(Path(['images',name])).serialize('/')
        
    def getIconUrl(self,name,depth=0):
        """
            Get URL for a given icon
        """
        return getPathUp(depth).postfix(Path(['gump_icons',name])).serialize('/')
