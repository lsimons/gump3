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
    Timing Utilities Testing
"""

from gump.utils import *
from gump.utils.timing import *
from gump.test.pyunit import UnitTestSuite

class TimingTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        self.now=default.time
        
    def testDateTimeUtils(self):
        oneHourBefore=self.now - (60*60)
        twoHoursBefore=self.now - (60*60*2)
        oneDayBefore=self.now - (60*60*24)
        twoDaysBefore=self.now - (60*60*24*2)
        oneWeekBefore=self.now - (60*60*24*7)
        twoWeeksBefore=self.now - (60*60*24*7*2)
        oneMonthBefore=self.now - (60*60*24*31)
        twoMonthsBefore=self.now - (60*60*24*31*2)
        oneYearBefore=self.now - (60*60*24*365)
        twoYearsBefore=self.now - (60*60*24*365*2)
        
        rough=getGeneralDifferenceDescription(self.now, oneHourBefore)
        self.assertInString('Date Diff String', '1 hour', rough)
        
        rough=getGeneralDifferenceDescription(self.now, twoHoursBefore)
        self.assertInString('Date Diff String', '2 hours', rough)
      
        rough=getGeneralDifferenceDescription(self.now, oneDayBefore)
        self.assertInString('Date Diff String', '1 day', rough)
        
        rough=getGeneralDifferenceDescription(self.now, twoDaysBefore)
        self.assertInString('Date Diff String', '2 days', rough)
      
        rough=getGeneralDifferenceDescription(self.now, oneWeekBefore)
        self.assertInString('Date Diff String', '1 week', rough)
        
        rough=getGeneralDifferenceDescription(self.now, twoWeeksBefore)
        self.assertInString('Date Diff String', '2 weeks', rough)
      
        rough=getGeneralDifferenceDescription(self.now, oneMonthBefore)
        self.assertInString('Date Diff String', '1 month', rough)
        
        rough=getGeneralDifferenceDescription(self.now, twoMonthsBefore)
        self.assertInString('Date Diff String', '2 months', rough)        
        
        rough=getGeneralDifferenceDescription(self.now, oneYearBefore)
        self.assertInString('Date Diff String', '1 year', rough)
        
        rough=getGeneralDifferenceDescription(self.now, twoYearsBefore)
        self.assertInString('Date Diff String', '2 years', rough)
        
    def testRandomStuff(self):
        # :TODO: Clean this up, just moved it here so as not to loose it.
        secsToElapsedTimeTriple(1340)
        secsToElapsedTimeString(1340)
        secsToTime(1340)
        elapsedTimeTripleToString(secsToElapsedTimeTriple(1340))
  
    def testTimeStampSet(self):
        set=TimeStampSet('Test1')
        set.stamp('Stamp1')
        
        time.sleep(5)
        set.stamp('Stamp2')
        
        time.sleep(10)
        set.stamp('Stamp3')
        
        range1=TimeStampRange('Range1')
        time.sleep(5)
        range1.setEndTime()
        range1.setExternal(True)
        set.registerRange(range1)
        
        range2=TimeStampRange('Range2')
        time.sleep(5)
        range2.setEndTime()
        range2.setExternal(False)
        set.registerRange(range2)
        
        #set.dump()
        set.getTotalTimes()