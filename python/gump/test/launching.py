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

    Utility Testing
    
"""

from gump.util import *
import gump.util.process.command
import gump.util.process.launcher
from gump.test.pyunit import UnitTestSuite

class LaunchingTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def testSpacesInCommandLines(self):
        params=gump.util.process.command.Parameters()
        params.addParameter('NoSpaces', 'aaaaa','=')
        params.addParameter('WithValueSpaces', 'aa aa a','=')
        params.addParameter('With Name Spaces', 'aaaaa','=')
        params.addParameter('WithQuotesAndSpaces', 'aa \' \" aa a','=')
        params.addParameter('WithEscapes', 'aa\\a','=')
        
        #print params.formatCommandLine()
        
        params=gump.util.process.command.Parameters()
        params.addPrefixedParameter('-D','X', 'aaaaa','=')
        params.addPrefixedParameter('-D','Y', 'aa aa a','=')
        params.addPrefixedParameter('-D','Z', 'aa \' aa a','=')
        params.addPrefixedParameter('-D','Z', 'aa \" aa a','=')
        
        #print params.formatCommandLine()
 
# Annoyingly, to fix threading issues (when changing directories, setting
# environment, etc.) we fork python/gump.util.process/launcher.py, but when we
# (currently) run unit tests we are in python, so 
 
        
#    def testGoodLaunch(self):
#        env=gump.util.process.command.Cmd('env')
#        result=gump.util.process.launcher.execute(env)
#        self.assertEqual( 'Ought succeed', 
#                          result.state, 
#                          gump.util.process.command.CMD_STATE_SUCCESS)
#        self.assertTrue( 'Ought succeed', 
#                         result.isOk())
#
#    def testBadLaunch(self):
#        env=gump.util.process.command.Cmd('eXnXv')
#        result=gump.util.process.launcher.execute(env)
#        self.assertEqual('Ought fail', result.state, gump.util.process.command.CMD_STATE_FAILED)
#  
#    def testFailedLaunch(self):      
#        env=gump.util.process.command.Cmd('exit 2')
#        result=gump.util.process.launcher.execute(env)
#        self.assertEqual('Ought fail', result.state, gump.util.process.command.CMD_STATE_FAILED)
#        self.assertEqual('Expected an exit of', result.exit_code, 2)
#        
#    def testFailedLaunch2(self):      
#        env=gump.util.process.command.Cmd('exit 70')
#        result=gump.util.process.launcher.execute(env)
#        self.assertEqual('Ought fail', result.state, gump.util.process.command.CMD_STATE_FAILED)
#        self.assertEqual('Expected an exit of', result.exit_code, 70)
  
