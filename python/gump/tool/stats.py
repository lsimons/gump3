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
    Statistics manipulation [e.g. reseting, etc.]
"""

import time
import os
import sys
import logging
import anydbm

from gump import log
from gump.config import *
from gump.output.stats import Project, ProjectStatistics
from gump.model.module import Module, ModuleStatistics
from gump.model.repository import Repository, RepositoryStatistics
from gump.output.stats import StatisticsDB
from gump.model.state import *
  
class StatisticsTools:
    """Statistics Interface"""

    def __init__(self,db=None):
        if not db: db=StatisticsDB()
        
    # :TODO: Complete...
                  
if __name__=='__main__':
    
    # init logging
    logging.basicConfig()

    #set verbosity to show all messages of severity >= default.logLevel
    log.setLevel(gump.default.logLevel)
        
    tool=StatisticsTool()
    
    tool.dump()
            
        