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
    Manage Depot Interactions
"""
import os

from gump import log
from gump.core.config import *

def getDepotHome(visual=True):
    if os.environ.has_key('DEPOT_UPDATE_HOME'):        
        return os.environ['DEPOT_UPDATE_HOME']
    if os.environ.has_key('DEPOT_HOME'):        
        return os.environ['DEPOT_HOME']
    if visual:
        return '${DEPOT_HOME}'
    
def getDepotUpdatePath():
    return os.path.join(
            os.path.join(getDepotHome(),'bin'),
            'update.py')
    
    
def getDepotUpdateCmd():
    return 'python '+getDepotUpdatePath()
    
    



 
