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
    xdoc generation, for forrest
"""

import socket
import time
import os
import sys
import logging

from gump import log

class Event:
    def __init__(self):		pass

class Listener:
    def __init__(self):  	pass
    
    #
    # Call a method called 'notify(event)', if needed
    #
    def handleEvent(self,event):
        if not hasattr(self,'notify'): return        
        if not callable(self.notify):  return        
        #log.debug('Prepare to notify using [' + `self` + ']')        
        self.notify(event)
