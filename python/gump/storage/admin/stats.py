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


"""

    A tool for statistics manipulation [e.g. reseting, etc.]
    
"""

import time
import os
import sys
import logging
import anydbm

from gump import log
from gump.core.config import *
from gump.output.stats import Project, ProjectStatistics
from gump.core.model.module import Module, ModuleStatistics
from gump.core.model.repository import Repository, RepositoryStatistics
from gump.output.stats import StatisticsDB
from gump.core.model.state import *
  
class StatisticsTools:
    """Statistics Interface"""

    def __init__(self,db=None):
        if not db: db=StatisticsDB()
        
    # :TODO: Complete...
                  
if __name__=='__main__':
    
    gumpinit()
        
    tool=StatisticsTool()
    
    tool.dump()        
