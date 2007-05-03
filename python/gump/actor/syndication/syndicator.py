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
    Syndicate
"""

import socket
import time
import os
import sys
import logging

from string import lower, capitalize

from gump import log
from gump.core.run.gumprun import *
from gump.core.run.actor import AbstractRunActor
from gump.actor.syndication.rss import RSSSyndicator
from gump.actor.syndication.atom import AtomSyndicator

class Syndicator(AbstractRunActor):
    
    def __init__(self,run):              
        AbstractRunActor.__init__(self,run)    
        
        self.rss=RSSSyndicator(self.run)      
        self.atom=AtomSyndicator(self.run)
        
    def processOtherEvent(self,event):            
        if isinstance(event,InitializeRunEvent):     
            self.rss.prepare()
            self.atom.prepare()
        elif isinstance(event,FinalizeRunEvent):    
            self.rss.complete()
            self.atom.complete()
                      
    def processWorkspace(self):
        """
        Syndicate information about the workspace (if it needs it)
        """
        pass
    
    def processModule(self,module):    
        """
        Syndicate information about the module (if it needs it)
        """
        self.rss.syndicateModule(module)
        self.atom.syndicateModule(module)
    
    def processProject(self,project):    
        """
        Syndicate information about the project (if it needs it)
        """                
        self.rss.syndicateProject(project)
        self.atom.syndicateProject(project)
           
