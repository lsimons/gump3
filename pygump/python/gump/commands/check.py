#!/usr/bin/python

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
usage: check [workspace]

  Perform the integration build.

Valid options:
  workspace
"""

__description__ = "Check the gump metadata for validity and consistency"

__revision__  = "$Rev: 54600 $"
__date__      = "$Date: 2004-10-11 12:50:02 -0400 (Mon, 11 Oct 2004) $"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import socket
import logging
from gump import log
from gump.core.loader.loader import WorkspaceLoader

def process(options,arguments):

    if len(arguments) > 0:
        ws = arguments[0]
    else:
        ws = "./metadata/" + socket.gethostname() + ".xml"

    log.setLevel(logging.DEBUG)
    
    workspace = WorkspaceLoader().load(ws)    
    
    workspace.dump()
