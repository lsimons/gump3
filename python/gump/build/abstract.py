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

"""

import os.path
import sys

from gump import log
from gump.core.gumprun import *
from gump.core.config import dir, default, basicConfig

from gump.utils import dump, display, getIndent, logResourceUtilization, \
                            invokeGarbageCollection
from gump.utils.note import Annotatable
from gump.utils.work import *

from gump.utils.tools import *

from gump.model.workspace import *
from gump.model.module import Module
from gump.model.project import Project
from gump.model.depend import  ProjectDependency
from gump.model.stats import *
from gump.model.state import *


###############################################################################
# Classes
###############################################################################

class AbstractJavaBuilder(Runnable):
    
    def __init__(self,run):
        Runnable.__init__(self,run)


    def getJVMArgs(self):
        """Get JVM arguments for a project"""
        args=Parameters()
        
        if self.hasAnt():
            jvmargs=self.getAnt().xml.jvmarg
        elif self.hasMaven():
            jvmargs=self.getMaven().xml.jvmarg
                
        for jvmarg in jvmargs:
            if jvmarg.value:
                args.addParameter(jvmarg.value)
            else:
                log.error('Bogus JVM Argument w/ Value')            
        
        return args
