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
from gump.runner.runner import *
from gump.core.config import dir, default, basicConfig

from gump.utils import dump, display, getIndent, logResourceUtilization, \
                            invokeGarbageCollection, printTopRefs
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

class OnDemandRunner(GumpRunner):

    def __init__(self,run):
        GumpRunner.__init__(self,run)

    ###########################################

    def performRun(self):
        
        self.initialize(1)
        
        printTopRefs(100,'Before Loop')
        
        gumpSet=self.run.getGumpSet()
        
        # In order...
        for project in gumpSet.getProjectSequence():

            # Process the module, upon demand
            module=project.getModule()
            if not module.isUpdated():
                self.updater.updateModule(module)        
                module.setUpdated(1) #:TODO: Move this...
                self.run.generateEvent(module)
                gumpSet.setCompletedModule(module)

            # Process
            self.builder.buildProject(project)   
            self.run.generateEvent(project)
            gumpSet.setCompletedProject(project)
            
            # Seems a nice place to peek/clean-up...    
            #printTopRefs(100,'Before Loop GC')
            #invokeGarbageCollection(self.__class__.__name__)
            #invokeGarbageCollection(self.__class__.__name__)
            #invokeGarbageCollection(self.__class__.__name__)
            #printTopRefs(100,'After GC')
        
        self.finalize()    
        
        printTopRefs(100,'Done')
                
        # Return an exit code based off success
        # :TODO: Move onto run
        if self.run.getWorkspace().isSuccess():
            result = EXIT_CODE_SUCCESS 
        else: 
            result = EXIT_CODE_FAILED
        return result  
