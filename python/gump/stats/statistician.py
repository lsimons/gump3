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

    Actor to update stats
    
"""

import os

from gump.core.config import *
from gump import log
from gump.model import *
from gump.core.gumprun import *
from gump.core.actor import *
from gump.stats.statsdb import StatisticsDB
        

class Statistician(AbstractRunActor):
    def __init__(self,run):
        
        AbstractRunActor.__init__(self,run)        
        self.db=StatisticsDB()   
        
        
    def processOtherEvent(self,event):
            
        workspace=self.run.getWorkspace()        
        
        if isinstance(event,InitializeRunEvent):
            #
            # Load stats (and stash onto projects)
            #    
            self.db.loadStatistics(workspace)            
            self.db.sync()
        elif isinstance(event,FinalizeRunEvent):
          
            #
            # Update stats (and stash onto projects)
            #
            self.db.updateStatistics(workspace)            
            self.db.sync()