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
from gump.core.config import *
from gump.utils import *

from gump.utils.work import *
from gump.utils.file import *

from gump.core.gumpenv import GumpEnvironment

from gump.model.repository import Repository
from gump.model.server import Server
from gump.model.tracker import Tracker
from gump.model.workspace import Workspace
from gump.model.module import Module
from gump.model.project import Project
from gump.model.object import *
from gump.model.state import *

from gump.document.resolver import *

class TextResolver(Resolver):
    
    def __init__(self,rootDir,rootUrl):        
        Resolver.__init__(self,rootDir,rootUrl)