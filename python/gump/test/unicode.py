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
    Model Testing
"""

import os
import logging
import types, io
from xml.sax.saxutils import escape

from gump import log
from gump.test.pyunit import UnitTestSuite
import xml.dom.minidom

class UnicodeTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def setUp(self):
        self.map=[]
        i=0
        while i<32:
            self.map.append(chr(95))
            i+=1
        while i<128:
            self.map.append(chr(i))
            i+=1
        while i<=255:
            self.map.append(chr(95))
            i+=1
        self.maps=''.join(self.map)
        
    def testUnicodeSerialization(self):
        data=''
        i=0
        while i < 128:
            data+=chr(i)
            i+=1
        edata=data.translate(self.maps)
        xmld='<xml>'+escape(edata)+'</xml>'     
        #print xmld   
        dom=xml.dom.minidom.parseString(xmld)
    
        
