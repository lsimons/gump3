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
    This module contains file (dir/plain) references
"""

import os
import os.path
import time

from gump.utils import secsToElapsedTimeString

class TimeStamp:       
    def __init__(self,name,start=None,end=None):
        self.name=name       
        
        if not start:
            start=time.time()
        self.startTime=start                
        
        if not end:
            end=time.time()
        self.endTime=end
    
    def __nonzero__(self):
        return self.getElapsedTime() > 0
        
    def __str__(self):
        return 'TimeStamp: '+self.name+' '+ \
                secsToElapsedTimeString(self.getElapsedTime()) 
        
    def getStartTime():
        return self.startTime
        
    def setEndTime(self,end=None):             
        if not end:
            end=time.time()    
        self.endTime=end
        
    def getEndTime():
        return self.endTime
        
    def getElapsedTime(self):
        return self.endTime-self.startTime
        
    def getElapsedTimeString(self):
        return secsToElapsedTimeString(self.getElapsedTime()) 

class TimeStampSet(list):
    """
        A named collection of timestamps        
    """
    def __init__(self,name,start=None):
        list.__init__(self)
        
        self.name=name        
        if not start:
            start=time.time()
        self.startTime=start        
        self.lastEndTime=None
        
    def stamp(self,name):
        
        # Calculate stamp start
        start=self.lastEndTime
        if not start:
            start=self.startTime
        
        # Stamp (end calculated)...       
        stamp=TimeStamp(name,start)
        
        # Store for posterity
        self.append(stamp)
        
        #
        self.lastEndTime=stamp.getEndTime()
        
        return stamp
        
    def getElapsedTime(self):
        return self.lastEndTime-self.startTime
    