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
    Syndicate
"""

import socket
import time
import os
import sys
import logging

from string import lower, capitalize

from gump import log
from gump.core.gumprun import *
from gump.core.actor import AbstractRunActor

class Syndicator(AbstractRunActor):
    
    def __init__(self,run):              
        AbstractRunActor.__init__(self,run)              
        
    def processOtherEvent(self,event):            
        if isinstance(event,FinalizeRunEvent):
          
            #
            # Update stats (and stash onto projects)
            #
            self.syndicate()
            
    def syndicate(self):

        #
        # Produce an RSS Feed
        #
        try:    
            from gump.syndication.rss import RSSSyndicator
            simple=RSSSyndicator(self.run)
            simple.syndicate()    
        except:
            log.error('Failed to generate RSS Feeds', exc_info=1)    
        
        #
        # Produce an Atom Feed
        #
        try:
            from gump.syndication.atom import AtomSyndicator
            atom=AtomSyndicator(self.run)
            atom.syndicate()
        except:
            log.error('Failed to generate Atom Feeds', exc_info=1)  
            
def syndicate(self,run):
    s=Syndicator(run)
    s.syndicate()