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

__revision__  = "$Rev: 36667 $"
__date__      = "$Date: 2004-08-20 08:55:45 -0600 (Fri, 20 Aug 2004) $"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"


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

from gump.actor.document.resolver import *

class TextResolver(Resolver):
    
    def __init__(self,rootDir,rootUrl):        
        Resolver.__init__(self,rootDir,rootUrl)   
        
    def getDirectory(self,object):
        return self.getRootDir()
        
    def getFile(self,object,documentName=None,extn=None,rawContent=False):  
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getFile.')
        
    def getDirectoryUrl(self,object): 
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getDirectoryUrl.')
           
    def getUrl(self,object,documentName=None,extn=None): 
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getUrl.')
        
    def getDirectoryUrl(self,object): 
        return self.rootUrl
   
    def getStateIconInformation(self,statePair): 
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getStateIconInformation.')
        
    def getImageUrl(self,name,depth=0): 
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getIconUrl.')   
             
    def getIconUrl(self,name,depth=0): 
        raise RuntimeError('Not Implemented on ' + self.__class__.__name__ + ': getImageUrl.')
