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
# $Header: /home/stefano/cvs/gump/python/gump/__init__.py,v 1.24 2004/05/21 23:14:59 ajack Exp $
# 

"""

  Gump Basic Init.
  
"""

# Either python-2.3 [or http://www.red-dove.com/python_logging.html]
import logging

# init logging
logging.basicConfig()

# base gump logger
log = logging.getLogger(__name__)

#set verbosity to show all messages of severity >= default.logLevel
log.setLevel(logging.INFO) # logging.DEBUG


# tell Python what modules make up the gump package
__all__ = ["build","check","debug","env","integrate","preview","update"]
