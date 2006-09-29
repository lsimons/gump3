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
    Drawing Testing
"""

from gump import log
from gump.tool.svg.drawing import *
from gump.test.pyunit import UnitTestSuite

class DrawingTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def testDrawingContext(self):
        context=StandardDrawingContext('Test', rect=Rect(0,0,100,100))
                
    def testScaledDrawingContext(self):
        context=ScaledDrawingContext('TestScale',None,Rect(0,0,100,100),200,200)
        (x,y)=context.realPoint(50,50)
        self.assertEqual('Half the size', 50/2, x)
        self.assertEqual('Half the size', 50/2, y)
                
    def testShiftedDrawingContext(self):
        context=ShiftedDrawingContext('TestShift',None,200,200)
        (x,y)=context.realPoint(50,50)
        self.assertEqual('Shifted up by 200', 250, x)
        self.assertEqual('Shifted up by 200', 250, y)
        
    def testShiftedScaledDrawingContext(self):
        context=ShiftedDrawingContext('TestShift',	\
                    ScaledDrawingContext('TestScale',None,	\
                        Rect(0,0,100,100),200,200),200,200)
        (x,y)=context.realPoint(50,50)
        self.assertEqual('Shifted & Scaled', 125, x)
        self.assertEqual('Shifted & Scaled', 125, y)
        
    def testGridDrawingContext(self):
        baseContext=StandardDrawingContext('Test',rect=Rect(0,0,100,200))
        context=GridDrawingContext('TestGrid',baseContext,10,10)
        for row in [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ]:
            for col in [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ]:    
                # Caculate generically
                (x,y)=context.realPoint(row,col)
                
                # Calculate expected
                expectedX=(row*10)+5
                expectedY=(col*20)+10
                
                #print `(row,col)`
                #print `(x,y)`
                
                # Check...
                self.assertEqual('Grid', expectedX, x)
                self.assertEqual('Grid', expectedY, y)
