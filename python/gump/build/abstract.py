#!/usr/bin/python


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

	An Abstract Java Builder, with the ability to get JVM arguments

"""

from gump import log
import gump.core.gumprun
import gump.process.command

###############################################################################
# Classes
###############################################################################

class AbstractJavaBuilder(gump.core.gumprun.RunSpecific):
    
    def __init__(self,run):
        gump.core.gumprun.RunSpecific.__init__(self,run)

    def getJVMArgs(self,project):
        """ Get JVM arguments for a project """
        args=gump.process.command.Parameters()
        
        for jvmarg in project.getDomChildIterator('jvmarg'):
            if hasDomAttribute(jvmarg,'value'):                
                args.addParameter(getDomAttributeValue(jvmarg,'value'))
            else:
                log.error('Bogus JVM Argument w/ Value')            
        
        return args
