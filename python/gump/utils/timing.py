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
import datetime

from gump.utils import getIndent
from gump.core.config import default, setting

ZERO_DELTA=datetime.timedelta(seconds=0)

def deltaToSecs(delta):
    """
    	Convert a delta into it's total seconds
    """
    if delta < ZERO_DELTA:
        raise RuntimeError, "Can not cope with backwards deltas"
        
    # Convert days to seconds, and add extra seconds.
    return int(round(((delta.days * 24 * 3600) + delta.seconds),0))
    
def deltaToElapsedTimeTriple(delta):  
        
    secs = deltaToSecs(delta)
    
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
    return deltaToElapsedTimeString(datetime.timedelta(seconds=secs))
     
def deltaToElapsedTimeString(delta):
    return elapsedTimeTripleToString(deltaToElapsedTimeTriple(delta))           
    
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
    
def toDateTime(datetime):
    if not datetime: return '-'
    return datetime.strftime(setting.DATETIME_PRESENTATION_FORMAT)    
    
# See note on toDate               
def toTime(datetime):
    if not datetime: return '-'
    return datetime.strftime(setting.TIME_PRESENTATION_FORMAT)                    
                
def getGeneralSinceDescription(secs, since=None):
    if not since: since = default.datetime
    return getGeneralDifferenceDescription( since, secs )
            
def getGeneralDifferenceDescription(newer,older):
    if not newer: return '-'
    if not older: return '-'
    
    """
    Get a presentation format for a time difference,
    	e.g 1 day or 1 hour, etc.
    """
    if older < newer:
        
        diffSecs = deltaToSecs(newer - older)
        
        diffString='~ '
        diff=newer - older
        
        diffSecs     =    int(diffSecs)
        diffMins     =    int(diffSecs / 60)
        diffHours    =    int(diffSecs / 3600)
        diffDays     =    int(diffHours / 24)
        diffWeeks    =    int(diffDays / 7)
        diffMonths   =    int(diffDays / 31)
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
            diffString = 'This run: ' + toTime(newer)
    elif older == newer:
        diffString = 'This run: ' + toTime(newer)
    else:
        diffString = 'N/A'
    
    return diffString
    
class TimeStamp:       
    def __init__(self,name,stamp=None):
        self.name=name               
        if not stamp:
            stamp=datetime.datetime.now()
        self.timestamp=stamp       
        
    # Representations:
    def getUtc(self):
        if hasattr(self,'utc'): return self.utc 
        self.utc=self.timestamp.strftime(setting.UTC_DATETIME_PRESENTATION_FORMAT)
        return self.utc
        
    # Representations:
    def getLocal(self):
        if hasattr(self,'local'): return self.local 
        self.local=self.timestamp.strftime(setting.UTC_DATETIME_PRESENTATION_FORMAT)
        return self.local
    
    def getTimestamp(self):
        return self.timestamp
     
    def __nonzero__(self):
        if self.timestamp: return True
        return False
        
    def __str__(self):
        return 'TimeStamp: '+self.name+' : '+ \
                toDateTime(self.timestamp) 
                
    def __cmp__(self,other):
        return int(self.timestamp - other.timestamp) 
        
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
                
    def setEnd(self,end=None):             
        if not end:
            end=TimeStamp('End of ' + self.name)    
        self.endTimeStamp=end
        
    def hasStart(self):
        if self.startTimeStamp: return True
        return False
        
    def getStart(self):
        return self.startTimeStamp
         
    def getEnd(self):
        return self.endTimeStamp
        
    def hasEnd(self):
        if self.endTimeStamp: return True
        return False
        
    def hasTimes(self):
        return self.hasStart() and self.hasEnd()
        
    def getElapsedSecs(self):
        return deltaToSecs(self.endTimeStamp.getTimestamp() - self.startTimeStamp.getTimestamp())
        
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
        self.endTimeStamp=range.getEnd()         
        return self._store(range)
            
    def stamp(self,sname):
        """
        	Calculate and provide a stamp
        """
        # Stamp (end calculated)...       
        stamp=TimeStamp(sname)  
        return self._store(stamp)
        
    def _store(self,stamp):
        # Store for posterity
        self.append(stamp) 
        return stamp
        
    def getElapsedSecs(self):
        return self.endTimeStamp.getTimestamp() - self.startTimeStamp.getTimestamp()
        
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
       
    # :TODO: Move these to run, like much dynamic stuff on W/S

    def setStart(self,comment='Start'):                                
        self.stamp(comment)
        
    def setEnd(self,comment='End'):                             
        self.stamp(comment)                                   
        
    def getStart(self):
        return self.startTimeStamp
        
    def getEnd(self):
        return self.endTimeStamp
        
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
        
class Timeable:
    def __init__(self,name):        
        if not name:
            name = self.__class__.__name__
        self.times=TimeStampSet(name)
        
    def getTimes(self):
        return self.times
        
    def hasStart(self):
        return self.times.hasStart()
        
    def setStart(self,comment=None):
        self.times.setStart(comment)
        
    def getStart(self):
        return self.times.getStart()
    
    def hasEnd(self):
        return self.times.hasEnd()
        
    def setEnd(self,comment=None):
        self.times.setEnd(comment)
        
    def getEnd(self):
        return self.times.getEnd()
    