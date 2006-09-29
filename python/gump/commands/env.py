#!/usr/bin/python

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
usage: env

  Checks the Gump environment for the presence of the programs
  required for Gump to perform its operations.

Valid options:
  [none]
"""

__description__ = "Checks the Gump environment"

__revision__  = "$Rev: 54600 $"
__date__      = "$Date: 2004-10-11 12:50:02 -0400 (Mon, 11 Oct 2004) $"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

from gump.core.run.gumpenv import GumpEnvironment

def process(options,arguments):
    env = GumpEnvironment()
    env.checkEnvironment()
    env.getJavaProperties()
