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

#
# $Header: /home/stefano/cvs/gump/python/gump/core/gumpinit.py,v 1.2.2.3 2004/05/21 00:09:45 ajack Exp $
# 

"""
  Gump Entry Points.
"""

import os.path
import sys
import time

# tell Python what modules make up the gump package
# __all__ = ["config"]

from gump import log
from gump.core.config import dir, default, setting, switch, basicConfig
from gump.utils import initializeGarbageCollection

###############################################################################
# Initialize
###############################################################################
def gumpinit():
        
    #set verbosity to show all messages of severity >= default.logLevel
    log.setLevel(default.logLevel)

    # Ensure dirs exists,
    basicConfig()

    # Initialize GC (sometimes w/ debug)
    initializeGarbageCollection()
    
    #
    timestamp=os.path.join(dir.base,'.timestamp')
    if os.path.exists(timestamp):
        default.time = os.path.getmtime(timestamp)
    else:
        default.time = time.time()

    default.ltime=time.localtime(default.time)
    default.date = time.strftime('%Y%m%d',default.ltime)
    default.datetime = time.strftime('%Y%m%d %H:%M:%S',default.ltime)
    
