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
    General documentation
"""

import socket
import time
import os
import sys
import logging

from gump import log

class Documenter:
    def __init__(self):  pass
    
    #
    # Call a method called 'prepareRun(run)', if needed
    #
    def prepare(self,run):
        if not hasattr(self,'prepareRun'): return        
        if not callable(self.prepareRun):  return        
        log.info('Prepare to document run using [' + `self` + ']')        
        self.prepareRun(run)
    
    #
    # Call a method called 'documentRun(run)'
    #
    def document(self,run):
        if not hasattr(self,'documentRun'):
            raise RuntimeError, 'Complete [' + `self.__class__` + '] with documentRun(self,run)'
        
        if not callable(self.documentRun):
            raise RuntimeError, 'Complete [' + `self.__class__` + '] with a callable documentRun(self,run)'
        
        log.info('Document run using [' + `self` + ']')
        
        self.documentRun(run)
        
    def getResolver(self,run):
        if not hasattr(self,'getResolverForRun'):
            raise RuntimeError, 'Complete [' + `self.__class__` + '] with getResolverForRun(self,run)'
        
        if not callable(self.getResolverForRun):
            raise RuntimeError, 'Complete [' + `self.__class__` + '] with a callable getResolverForRun(self,run)'
            
        return self.getResolverForRun(run)