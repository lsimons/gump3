#!/usr/bin/env python
#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# $Header: /home/stefano/cvs/gump/python/tool/profileResults.py,v 1.2 2004/07/08 20:33:10 ajack Exp $

"""
  Used to do Python testing prior to commiting a code change.
"""

import profile
import pstats

SEP='--------------------------------------------------------------------'

def title(t):
    print(SEP)
    print(t)

def printStats(sort,percentage,t):    
    title(t)
    stats.sort_stats(sort)
    stats.print_stats(percentage)
    
# static void main()
if __name__=='__main__':

    stats=pstats.Stats('iprof')
    
    printStats('time',.1,'By internal time')
    printStats('cumulative',.5,'By cumulative time')
