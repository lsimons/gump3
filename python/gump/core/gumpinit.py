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

__revision__  = "$Rev: 36667 $"
__date__      = "$Date: 2004-08-20 08:55:45 -0600 (Fri, 20 Aug 2004) $"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"


#
# $Header: /home/stefano/cvs/gump/python/gump/core/gumpinit.py,v 1.5 2004/07/13 18:44:35 ajack Exp $
# 

"""

  Gump Entry Points.
  
"""

import os.path
import sys
import time
import datetime

# tell Python what modules make up the gump package
# __all__ = ["config"]

from gump import log
from gump.core.config import dir, default, setting, switch, basicConfig
from gump.util import initializeGarbageCollection

###############################################################################
# Initialize
###############################################################################
def gumpinit(level=None):
        
    #set verbosity to show all messages of severity >= default.logLevel
    log.setLevel(level or default.logLevel)

    # Ensure dirs exists,
    basicConfig()

    # Initialize GC (sometimes w/ debug)
    initializeGarbageCollection()
    
    # If a .timestamp exists, use it.
    timestamp=os.path.join(dir.base,'.timestamp')
    if os.path.exists(timestamp):
        default.timestamp = os.path.getmtime(timestamp)
    else:
        default.timestamp = time.time()
    # Import this timestamp
    default.datetime   = datetime.datetime.fromtimestamp(default.timestamp)
    default.datetime_s = default.datetime.strftime(setting.DATETIME_FORMAT)
    default.date_s     = default.datetime.strftime(setting.DATE_FORMAT)
    default.datetime_sp= default.datetime.strftime(setting.DATETIME_PRESENTATION_FORMAT)
    default.date_sp    = default.datetime.strftime(setting.DATE_PRESENTATION_FORMAT)
    
    
if __name__ == '__main__':
    gumpinit()
