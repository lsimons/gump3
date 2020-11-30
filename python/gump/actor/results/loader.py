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
    This module contains information on
"""
import os, os.path

import xml.dom.minidom

from gump import log
from gump.actor.results.model import WorkspaceResult

from gump.util.note import transferAnnotations, Annotatable
from gump.util.http import cacheHTTP
from gump.util import dump
from gump.core.config import gumpPath

class WorkspaceResultLoader:
    def __init__(self):
        self.annotations=[]
        
    def loadFromUrl(self,url):
        """Builds in memory from the xml file. Return the generated objects."""
      
        # Download (relative to base)
        if not url.startswith('http://'):
            newurl=gumpPath(url,'.');
        else:
            newurl=cacheHTTP(url)
            
        return self.load(newurl)
        
    def load(self,file):
      """Builds in memory from the xml file. Return the generated objects."""

      if not os.path.exists(file):
        log.error('WorkspaceResult metadata file ['+file+'] not found')
        raise IOError("""WorkspaceResult %s not found!""" % file) 
    
      log.debug("Launch DOM Parser onto : " + file);
              
      dom=xml.dom.minidom.parse(file)
    
      # Construct object around XML.
      workspaceResult=WorkspaceResult(dom.documentElement.getAttribute('name'),dom)
  
      #
      # Cook the raw model...
      #
      workspaceResult.complete()
      
      dom.unlink()
      
      return workspaceResult      
