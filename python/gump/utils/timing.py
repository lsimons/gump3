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

import sys

import os
import os.path
import time

from gump.utils import getIndent
from gump.core.config import default, setting

def secsToElapsedTimeTriple(secs):   
    # Extract Hours
    if secs > 3600:
        hours    =    int(secs / 3600)
        secs    %=    3600
    else:
        hours    =    0
          
    # Extract Minutes  
    if secs > 60:
        mins    =    int(secs / 60)
        secs    %=    60
    else:
        mins     =     0
            
    # Seconds
    secs     =    int(round(secs,0))
        
    return (hours, mins, secs)
    
def secsToElapsedTimeString(secs):
    return elapsedTimeTripleToString(secsToElapsedTimeTriple(secs))           
    
def elapsedTimeTripleToString(elapsed,noTimeText=None):
    elapsedString=''
    
    (hours,mins,secs) = elapsed
    
    if hours:
        if elapsedString: elapsedString += ' '
        elapsedString += str(hours)+' hour'
        if hours > 1: elapsedString += 's'
        
    if mins:
        if elapsedString: elapsedString += ' '    
        elapsedString += str(mins)+' min'
        if mins > 1: elapsedString += 's'
        
    if secs:
        if elapsedString: elapsedString += ' '    
        elapsedString += str(secs)+' sec'
        if secs > 1: elapsedString += 's'
        
    if not elapsedString and noTimeText:
        elapsedString=noTimeText
    
    return elapsedString    
    
def secsToDateTime(secs):
    if not secs: return '-'
    return time.strftime(setting.datetimeformat, time.localtime(secs))    
    
# See note on secsToDate               
def secsToTime(secs):
    if not secs: return '-'
    return time.strftime(setting.timeformat, time.localtime(secs))                    
                
def getGeneralSinceDescription(secs, since=None):
    if not since: since = default.time
    return getGeneralDifferenceDescription( since, secs )
            
def getGeneralDifferenceDescription(newerSecs,olderSecs):
    if not 0 >= olderSecs and not olderSecs >= newerSecs:
        diffString='~ '
        diffSecs=newerSecs - olderSecs
        
        diffSecs    =    int(diffSecs)
        diffMins    =    int(diffSecs / 60)
        diffHours    =    int(diffSecs / 3600)
        diffDays    =    int(diffHours / 24)
        diffWeeks    =    int(diffDays / 7)
        diffMonths    =    int(diffDays / 31)
        diffYears    =    int(diffDays / 365)
        
        if diffYears:
            diffString += str(diffYears) + ' year'
            if diffYears > 1: diffString += 's'
        elif diffMonths:
            diffString += str(diffMonths) + ' month'
            if diffMonths > 1: diffString += 's'
        elif diffWeeks:
            diffString += str(diffWeeks) + ' week'
            if diffWeeks > 1: diffString += 's'
        elif diffDays:
            diffString += str(diffDays) + ' day'
            if diffDays > 1: diffString += 's'
        elif diffHours:
            diffString += str(diffHours) + ' hour'
            if diffHours > 1: diffString += 's'
        elif diffMins:
            diffString += str(diffMins) + ' min'
            if diffMins > 1: diffString += 's'
        elif diffSecs:
            diffString += str(diffSecs) + ' sec'
            if diffSecs > 1: diffString += 's'
        else:
            diffString = 'This run: ' + secsToTime(newerSecs)
    elif olderSecs == newerSecs:
        diffString = 'This run: ' + secsToTime(newerSecs)
    else:
        diffString = 'N/A'
    
    return diffString
    

class TimeStamp:       
    def __init__(self,name,stamp=None):
        self.name=name       
        
        if not stamp:
            stamp=time.time()
        self.stampTime=stamp       
        
    # Representations:
    def getUtc():
        if hasattr(self,'utc'): return self.utc 
        self.utc=time.strftime(setting.utcdatetimeformat, time.gmtime(self.stampTime))
        return self.utc
        
    # Representations:
    def getLocal():
        if hasattr(self,'local'): return self.local 
        self.local=time.strftime(setting.datetimeformat, time.localtime(self.stampTime))
        return self.local
     
    def __nonzero__(self):
        return self.stampTime > 0
        
    def __str__(self):
        return 'TimeStamp: '+self.name+' : '+ \
                secsToDateTime(self.stampTime) 
                
    def __cmp__(self,other):
        return int(self.stampTime - other.stampTime) 
        
    def getTime(self):
        return self.stampTime
        
class TimeStampRange:       
    def __init__(self,name,start=None,end=None,external=False):
        
        self.name=name
        
        if not start:
            start=TimeStamp(name)
        self.startTimeStamp=start
          
        if not end: end=start
        self.endTimeStamp=end
        
        self.external=external
    
    def __nonzero__(self):
        return self.getElapsedSecs() > 0
        
    def __str__(self):
        return 'TimeStamp: '+self.name+' : '+ \
                secsToElapsedTimeString(self.getElapsedSecs()) 
                
    def setEndTime(self,end=None):             
        if not end:
            end=TimeStamp('End of ' + self.name)    
        self.endTimeStamp=end
        
    def getStartTimeStamp(self):
        return self.startTimeStamp
         
    def getEndTimeStamp(self):
        return self.endTimeStamp
        
    def hasTimes(self):
        if self.startTimeStamp and self.endTimeStamp: return True
        return False
        
    def getElapsedSecs(self):
        return self.endTimeStamp.getTime() - self.startTimeStamp.getTime()
        
    def getElapsedTimeString(self):
        return secsToElapsedTimeString(self.getElapsedSecs()) 
        
    def setExternal(self,external):
        self.external=external
        
    def isExternal(self):
        return self.external

class TimeStampSet(list):
    """
    
        A named collection of timestamps    
            
    """
    def __init__(self,name,start=None):
        list.__init__(self)
        
        self.name=name        
        if not start:
            start=TimeStamp('Start of ' + name)
        self.startTimeStamp=start        
        self.endTimeStamp=start
        
    def registerStamp(self,stamp):  
        # :TODO: don't assume stored in time order
        self.endTimeStamp=stamp  
        return self.store(stamp)
        
    def registerRange(self,range):  
        # :TODO: don't assume stored in time order
        self.endTimeStamp=range.getEndTimeStamp()         
        return self.store(range)
            
    def stamp(self,sname):
        """
        	Calculate and provide a stamp
        """
        # Stamp (end calculated)...       
        stamp=TimeStamp(sname)  
        return self.store(stamp)
        
    def store(self,stamp):
        # Store for posterity
        self.append(stamp) 
        return stamp
        
    def getElapsedSecs(self):
        return self.endTimeStamp.getTime() - self.startTimeStamp.getTime()
        
    def getTotalTimes(self):
        
        elapsed=0
        accounted=0
        external=0
        
        # Count external/ranges
        for entry in self:
            if isinstance(entry,TimeStampRange):
                e=entry.getElapsedSecs()
                if entry.isExternal():
                    external += e
                accounted+=e
                
        elapsed=self.getElapsedSecs()
        
        return (elapsed, accounted, external)
        
    def importTimes(self,otherSet):
        for entry in otherSet:
            if isinstance(entry,TimeStampRange):    
                self.registerRange(entry)
            elif isinstance(entry,TimeStamp):    
                self.registerStamp(entry)
            else:
                raise RuntimeError, 'Unknown timestamp: ' + `entry` 
                
    def dump(self, indent=0, output=sys.stdout):
        spacing=getIndent(indent)
        output.write('TimeStampSet : ['+self.name+']\n')
        for entry in self:
            output.write(spacing)
            output.write(str(entry))
            output.write('\n')
            
            
class TimeStampSetSet(list):   
    def __init__(self):
        list.__init__(self)
        
    def getTotalTimes(self):
        
        elapsed=0
        accounted=0
        external=0
        
        # Count external/ranges
        for entry in self:
            (e,a,ex)=entry.getTotalTimes()
            
            elapsed += e
            accounted += a
            external += ex
            
        return (elapsed, accounted, external)
        
    