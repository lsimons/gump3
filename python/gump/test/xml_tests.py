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
    Model Testing
"""

import os
import logging
import types, StringIO

from gump import log
import gump.config
from gump.utils.xmlutils import *

from gump.test import getTestWorkspace

if __name__=='__main__':

    # init logging
    logging.basicConfig()

    #set verbosity to show all messages of severity >= default.logLevel
    log.setLevel(gump.default.logLevel)

    workspace=getTestWorkspace() 
        
    stream=StringIO.StringIO()       
    xmlize(workspace.xml.getTagName(),workspace.xml,stream)    
    stream.seek(0)
    print stream.read()
    
    module1=workspace.getModule('module1')
    stream=StringIO.StringIO()       
    xmlize(module1.xml.getTagName(),module1.xml,stream)    
    stream.seek(0)
    print stream.read()
    
    project1=workspace.getProject('project1')
    stream=StringIO.StringIO()       
    xmlize(project1.xml.getTagName(),project1.xml,stream)    
    stream.seek(0)
    print stream.read()
    
    