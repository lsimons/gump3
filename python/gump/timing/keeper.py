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
    Times
"""

import gump.run.gumprun
import gump.run.actor

class TimeKeeper(gump.run.actor.AbstractRunActor):
    
    def __init__(self,run):          
        """
        The TimeKeeper extracts elapsed time information.    
        """
        gump.run.actor.AbstractRunActor.__init__(self,run)              
        
    def processOtherEvent(self,event):      
        """
        	Process non-Entity based events, i.e.
        	timstamp the start and end of the
        	run.      
        """
        if isinstance(event,gump.run.gumprun.InitializeRunEvent):
            self.run.setStart()
            print 'KEEPER: START'
        elif isinstance(event,gump.run.gumprun.FinalizeRunEvent):  
            self.run.setEnd()
            print 'KEEPER: STOP'
            
        self.run.times.dump()
            