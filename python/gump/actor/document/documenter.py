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
    General documentation
"""

import socket
import time
import os
import sys
import logging

from gump import log

from gump.core.run.gumprun import *
import gump.core.run.actor

class Documenter(gump.core.run.actor.AbstractRunActor):

    def __init__(self, run):        
        #
        gump.core.run.actor.AbstractRunActor.__init__(self, run)    
        
    def processOtherEvent(self,event):
            
        workspace=self.run.getWorkspace()        
        
        if isinstance(event,InitializeRunEvent):
            self.prepare()
        elif isinstance(event,FinalizeRunEvent):
            if self.run.getOptions().isDocument():
                self.document()
            
    #
    # Call a method called 'prepareRun(run)', if it
    # is available on the sub-class (i.e. if needed)
    #
    def prepare(self):
        if not hasattr(self,'prepareRun'): return        
        if not callable(self.prepareRun):  return        
        log.debug('Prepare to document run using [' + repr(self) + ']')        
        self.prepareRun()       

    #
    # Call a method called 'documentRun(run)'
    #
    def document(self):
        if not hasattr(self,'documentRun'):
            raise RuntimeError('Class [' + repr(self.__class__) + '] needs a documentRun(self,run)')
        
        if not callable(self.documentRun):
            raise RuntimeError('Class [' + repr(self.__class__) + '] needs a callable documentRun(self,run)')
        
        log.info('Document run using [' + repr(self) + ']')
        
        self.documentRun()
        
    def setResolver(self,resolver):
        self.resolver=resolver        

    def getResolver(self):
        return self.resolver
