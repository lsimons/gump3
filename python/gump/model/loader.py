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
    This module contains information on
"""
import os.path
import time

from gump import log
from gump.model.rawmodel import XMLWorkspace,XMLProfile,	\
            XMLModule, XMLProject, XMLRepository, \
            XMLServer,	XMLTracker
from gump.model.workspace import Workspace
from gump.model.module import Module
from gump.utils.xmlutils import SAXDispatcher
from gump.utils.note import transferAnnotations, Annotatable
from gump.utils import dump,secsToElapsedTimeString

from gump.core.config import dir, switch, setting

class WorkspaceLoader:
    def __init__(self):
        self.annotations=[]
        
    def load(self,file,cache=0):
        """Builds a GOM in memory from the xml file. Return the generated GOM."""

        start_time=time.time()
        log.info('Loading metadata from ' + file)
        
        if not os.path.exists(file):
            log.error('Workspace metadata file ['+file+'] not found')
            raise IOError, """Workspace %s not found!

      You need to specify a valid workspace for Gump to run
      If you are new to Gump, simply copy minimal-workspace.xml
      to a file with the name of your computer (`hostname`.xml)
      and rerun this program.""" % file 
    
        #
        # Clear out the maps
        #
        XMLWorkspace.map={}
        XMLProfile.map={}
        XMLRepository.map={}
        XMLModule.map={}
        XMLProject.map={}
        XMLServer.map={}
        XMLTracker.map={}
    
        log.debug("Launch SAX Dispatcher onto : " + file)
    
        o=0
        on=0
        try:
            if cache:
                # Hack, temporarily turn on optimization
                o=switch.optimize 
                on=switch.optimizenetwork
                switch.optimize=1 
                switch.optimizenetwork=1
          
            parser=SAXDispatcher(file,'workspace',XMLWorkspace)
    
            # Extract the root XML
            xmlworkspace=parser.docElement
    
            if not xmlworkspace:
                raise IOError, 'Failed to load workspace: ' + file
    
            loaded_time=time.time()
            loadElapsed=(loaded_time-start_time)
            log.info('Loaded metadata [' + secsToElapsedTimeString(loadElapsed) + ']')
        
            # Construct object around XML.
            workspace=Workspace(xmlworkspace)
      
            # Copy over any XML errors/warnings
            transferAnnotations(parser, workspace)
  
            #
            # Cook the raw model...
            #
            workspace.complete(XMLProfile.map,XMLRepository.map,	\
                          XMLModule.map,XMLProject.map,	\
                          XMLServer.map, XMLTracker.map)
                     
            processed_time=time.time()     
            processElapsed=(processed_time-loaded_time)
            log.info('Processed metadata [' + secsToElapsedTimeString(processElapsed) + ']')
            
        finally:
            #
            # Clear out the maps [so don't continue to use them]
            #
            XMLWorkspace.map={}
            XMLModule.map={}
            XMLProject.map={}
            XMLProfile.map={}
            XMLRepository.map={}
            XMLTracker.map={}
            XMLServer.map={}
  
            if cache:
                # Hack, temporarily turn on optimization
                switch.optimize=o
                switch.optimizenetwork=on
                
        return workspace      
      
    def loadModule(self,url,workspace):
        
        log.debug("Launch SAX Dispatcher onto : " + url);
        
        XMLModule.map={}
        XMLProject.map={}
      
        xmlmodule=SAXDispatcher(url,'module',XMLModule).docElement
    
        if not xmlmodule:
            raise IOError, "Failed to load module: " + url

        #
        #for xmlproject in xmlmodule.project:
        #    print "XMLProject: " + str(xmlproject)
                       
        #
        module=Module(xmlmodule,None)        
        module.complete(workspace)

        #
        # Clear out the maps [so don't continue to use them]
        #
        XMLModule.map={}
        XMLProject.map={}
      
        return module