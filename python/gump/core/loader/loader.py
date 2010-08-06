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

    This module contains information on loading metadata
    
"""
import os.path
import time

import xml.dom.minidom

from gump import log
from gump.util.tasks import *
from gump.util.note import transferAnnotations, Annotatable
from gump.util.timing import TimeStampSet
        
class XmlLoader:
    def __init__(self,basedir='.',cache=False):
        self.annotations=[]
        self.basedir=basedir
        self.cache=cache
        
    def loadFile(self,file,base='.',tag=None):
        """ Builds a GOM in memory from the xml file. Return the generated GOM. """
        
        if not os.path.exists(file):
            raise IOError, 'Metadata file [%s] not found.' % file 
    
        return self.load(file,tag)
    
    def loadFromUrl(self,url,base='.',tag=None):
        """Builds in memory from the xml file. Return the generated objects."""
    
        basedir=base or self.basedir
            
        # Download (relative to base)
        if not url.startswith('http://'):
            from gump.core.config import gumpPath
            urlFile=gumpPath(url,basedir);
        else:
            from gump.util.http import cacheHTTP
            urlFile=cacheHTTP(url,optimize=self.cache)
        
        dom = self.load(urlFile,tag)

        log.info('Parsed file %s/%s ' % (basedir,url))
        
        return dom
        
    def load(self,file,tag=None):
        """
            Builds in memory from the xml file. 
        """

        if not os.path.exists(file):
            log.error('Metadata file [' + file + '] not found')
            raise IOError, 'Metadata File %s not found.' % file 
            
        dom=xml.dom.minidom.parse(file)
        
        # We normalize the thing, 'cos we don't care about
        # pieces of text (just text as one value)
        dom.normalize()
        
        # :TODO:: Hmm, do we want to remove empty text? Might be
        # nicer for presentation. Seems (somehow) we get extra <CR>
        # with them (when we ask for XML pretty).
        
        # Do tag validation (if requested)        
        xtag=dom.documentElement.tagName
        if tag:
            if not tag == xtag:
                dom.unlink()
                raise IOError, 'Incorrect XML Element, expected %s found %s.' % (tag,xtag)        
                
        return dom
    
class XmlResult:
    def __init__(self,dom):
        self.dom=dom
        
    def getDom(self):
        return self.dom
        
    def __str__(self):
        return '<'+self.dom.documentElement.tagName
        
    def setObject(self,object):
        self.object=object
        
    def getObject(self):
        return self.object

class XmlTask(Task):
    def __init__(self,name,tag,basedir=None):
        Task.__init__(self,name)
        self.tag=tag
        self.basedir=basedir
        
    def getTag(self):
        return self.tag
        
    def getBaseDir(self):
        return self.basedir
        
    def getDescription(self):
        return self.tag
        
class XmlUrlTask(XmlTask):
    def __init__(self,tag,url,basedir=None):
        XmlTask.__init__(self,url,tag,basedir)
        self.url=url
        
    def getLocation(self): return self.getUrl()
    def getUrl(self):
        return self.url
        
    def getDescription(self):
        return '%s @ %s' % (self.tag, self.url)
                
class XmlFileTask(XmlTask):
    def __init__(self,tag,file,basedir=None):
        XmlTask.__init__(self,file,tag,basedir)
        self.file=file
        
    def getLocation(self): return self.getFile()
    def getFile(self):
        return self.file
        
    def getDescription(self):
        return '%s @ %s' % (self.tag, self.file)
        
class XmlWorker:   

    def __init__(self):
        self.loader=XmlLoader()
        
    def perform(self,task):
        
        try:
            if isinstance(task,XmlFileTask):
                dom=self.loader.loadFile(
                            task.getFile(),task.getBaseDir())
            elif isinstance(task,XmlUrlTask):
                dom=self.loader.loadFromUrl(
                            task.getUrl(),task.getBaseDir())
            
            # Process DOM and extract new tasks...    
            self.postProcess(task,dom)        
            
            task.setResult(XmlResult(dom))
        except Exception, details:
            
            log.warning('Failed to parse XML %s : %s' % (task.getDescription(),details))
            
            task.setFailed(str(details))
      
    def postProcess(self,task,dom):        
        #log.debug("Post Process DOM : " + `dom`)   
        
        taskList=task.getOwner()
        
        # Traverse looking for href='... tasks to queue
        for child in dom.documentElement.childNodes:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE:
                if child.hasAttribute('href'):
                    if not 'url' == child.tagName:
                        newTask=XmlUrlTask(	child.tagName,
                                        child.getAttribute('href'),
                                        task.getBaseDir())
                        newTask.setParentTask(task)
                        taskList.addTask(newTask)
            elif child.nodeType == xml.dom.Node.COMMENT_NODE:
                pass # log.debug("Skip Comment: " + `child.nodeType`) 
            elif child.nodeType == xml.dom.Node.ATTRIBUTE_NODE:
                pass # log.debug("Skip Attribute: " + `child.nodeType`) 
            elif child.nodeType == xml.dom.Node.TEXT_NODE:
                pass # log.debug("Skip Text: " + `child.nodeType`)          
            else:
                log.debug("Skip Node: " + `child.nodeType` + ' ' + `child`)                       
    
class ModelLoader:
    """
    Load some XML, and map that to a model.
    """
    def __init__(self,cache=False):
        self.annotations=[]
        self.xmlloader=XmlLoader(cache)
        
        self.tasks=TaskList('Model Loader',self)
        self.times=TimeStampSet("ModelLoader")
        
    def loadFile(self,file,cls,tag=None):
        base=os.path.dirname(file)
        self.tasks.addTask(XmlFileTask(tag,file,base))
        self.performTasks()        
        return self.postProcess(cls)
        
    def loadFromUrl(self,url,cls,tag=None):
        self.tasks.addTask(XmlUrlTask(tag,url))
        self.performTasks()                   
        return self.postProcess(cls)
        
    def postProcess(self,cls):
        """
        Convert the XML (DOM) into a class.
        """
        
        rootObject=None
        
        for task in self.tasks.getPerformed():
            if not task.isFailed():
                dom=task.getResult().getDom()
                
                # What are we working with for this document
                element=dom.documentElement
                name=None
                if element.hasAttribute('name'):            
                    name=element.getAttribute('name')
        
                # See what the parent has to say about this...
                parent=None
                parentObject=None
                if task.hasParentTask():
                    parent=task.getParentTask()
                if parent:
                    parentObject=parent.getResult().getObject()
                
                # Allow context-sensetive instantiation, or we are root
                if parentObject:
                    object=parentObject.getObjectForTag(element.tagName,dom,name)
                    
                    log.debug("Used parent: %s to get %s for <%s %s" %(`parentObject`,`object`,
                                `element.tagName`,`name`))  
                else:
                    # Just construct
                    if name: object=cls(name,dom)
                    else:    object=cls('',dom)
                    rootObject=object
               
                if object:
                    # Store the metadata
                    object.setMetadataLocation(task.getLocation())
                    # Resolve entities...
                    if not object.isResolved():
                        object.resolve()                    
                    task.getResult().setObject(object)
            
        if rootObject:
            if not rootObject.isResolved():
                rootObject.resolve()
            # Cook the raw model...                    
            rootObject.complete()
             
        # Copy over any XML errors/warnings
        #if isinstance(object,Annotatable):
        #    transferAnnotations(parser, object)
        
        if not rootObject:
            raise RuntimeError, 'Failed to extract %s from XML.' % cls.__name__
        
        return rootObject
        
    def performTasks(self):
        worker=XmlWorker()
        self.tasks.perform(worker)
        #self.tasks.dump()
        
class WorkspaceLoader(ModelLoader):
    
    def __init__(self,cache=False):
        ModelLoader.__init__(self,cache)
    
    def load(self,file):
        from gump.core.model.workspace import Workspace
        return self.loadFile(file,Workspace)
        
# static void main()
if __name__=='__main__':

    import logging
    from gump.core.gumpinit import gumpinit
    gumpinit(logging.DEBUG)   
    
    import sys
    from gump.core.model.workspace import Workspace
    loader=ModelLoader()
    loader.loadFile(sys.argv[1] or 'workspace.xml',Workspace).dump()
