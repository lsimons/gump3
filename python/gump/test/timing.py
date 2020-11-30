#!/usr/bin/env python
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
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
import time

from gump.util import *
from gump.util.timing import *
from gump.test.pyunit import UnitTestSuite

class TimingTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        self.nowTimestamp=time.time()
        self.now=datetime.datetime.utcfromtimestamp(self.nowTimestamp)
        
    def testDateTimeUtils(self):
        oneHourBefore=datetime.datetime.utcfromtimestamp(self.nowTimestamp - (60*60))
        twoHoursBefore=datetime.datetime.utcfromtimestamp(self.nowTimestamp - (60*60*2))
        oneDayBefore=datetime.datetime.utcfromtimestamp(self.nowTimestamp - (60*60*24))
        twoDaysBefore=datetime.datetime.utcfromtimestamp(self.nowTimestamp - (60*60*24*2))
        oneWeekBefore=datetime.datetime.utcfromtimestamp(self.nowTimestamp - (60*60*24*7))
        twoWeeksBefore=datetime.datetime.utcfromtimestamp(self.nowTimestamp - (60*60*24*7*2))
        oneMonthBefore=datetime.datetime.utcfromtimestamp(self.nowTimestamp - (60*60*24*31))
        twoMonthsBefore=datetime.datetime.utcfromtimestamp(self.nowTimestamp - (60*60*24*31*2))
        oneYearBefore=datetime.datetime.utcfromtimestamp(self.nowTimestamp - (60*60*24*365))
        twoYearsBefore=datetime.datetime.utcfromtimestamp(self.nowTimestamp - (60*60*24*365*2))
        
        try:
            getGeneralDifferenceDescription(oneHourBefore, self.now)
            self.failed('Expect exception on reverse time')
        except: pass
        
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
        
    def testTimeStampSet(self):
        set=TimeStampSet('Test1')
        set.stamp('Stamp1')
        
        time.sleep(5)
        set.stamp('Stamp2')
        
        time.sleep(10)
        set.stamp('Stamp3')
        
        # Create the first range
        range1=TimeStampRange('Range1')
        time.sleep(5)
        range1.setEnd()
        range1.setExternal(True)
        set.registerRange(range1)
        
        # Create the second range
        range2=TimeStampRange('Range2')
        time.sleep(5)
        range2.setEnd()
        range2.setExternal(False)
        set.registerRange(range2)
        
        #set.dump()
        set.getTotalTimes()
        
        self.assertLesser('Time passes', range1.getStart(), range1.getEnd())        
        self.assertLesser('Time passes', range2.getStart(), range2.getEnd())        
        self.assertLesser('Time passes', range1.getEnd(), range2.getEnd())
        
        self.assertLesser('Time passes', set.getStart(), set.getEnd())
        
    def testUTCTimes(self):
        stamp1=TimeStamp('S1')
        stamp2=TimeStamp('S2')
        
        t1=stamp1.getUtc()
        t2=stamp2.getUtc()
        
        self.assertInSequence('UTC', 'UTC', t1)
        self.assertInSequence('UTC', 'UTC', t2)
