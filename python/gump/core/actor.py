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

 A gump run (not 'run gump')
 
"""

import os.path
import os
import sys
from fnmatch import fnmatch

from gump import log
from gump.core.config import dir, default, basicConfig
from gump.core.gumpenv import GumpEnvironment
from gump.core.gumprun import *


from gump.utils.work import *
from gump.utils import dump, display, getIndent
from gump.utils.note import Annotatable

from gump.model.workspace import Workspace
from gump.model.module import Module
from gump.model.project import Project
from gump.model.depend import  ProjectDependency
from gump.model.state import *


    
###############################################################################
# Functions
###############################################################################

###############################################################################
# Classes
###############################################################################


        
class  RunActor(RunSpecific):     
    """
    
        An actor acts upon the run result events.
        
    """
    
    def __init__(self, run):
        RunSpecific.__init__(self,run)
        
        # Oft used references..
        self.workspace=run.getWorkspace()
        self.options=run.getOptions()
        self.gumpSet=run.getGumpSet()
        
    def __repr__(self):
        return self.__class__.__name__
        
    #
    # Call a method called 'processEvent(event)', if it
    # is available on the sub-class (i.e. if needed)
    #
    def _processEvent(self,event):
        if not hasattr(self,'processEvent'): return        
        if not callable(self.processEvent):  return        
        #log.debug('Process event [' + `event` + '] using [' + `self` + ']')        
        self.processEvent(event)

class AbstractRunActor(RunActor):    
    
    def __init__(self, run):
        RunActor.__init__(self,run)
        
        
    def processEvent(self,event):
        
        if isinstance(event,EntityRunEvent):
            entity=event.getEntity()
        
            if isinstance(entity,GumpRun):
                # We are within run context...
                self._processRun()
            if isinstance(entity,Workspace):
                self._processWorkspace(entity)
            elif isinstance(entity,Module):
                self._processModule(entity)
            elif  isinstance(entity,Project):
                self._processProject(entity)
        else:
            self._processOtherEvent(event)
            
            
    #
    # Call a method called 'processRun(Run)', if it
    # is available on the sub-class (i.e. if needed)
    #
    def _processRun(self):
        if not hasattr(self,'processRun'): return        
        if not callable(self.processRun):  return        
        log.debug('Process Run using [' + `self` + ']')        
        self.processRun()
        
            
    #
    # Call a method called 'processWorkspace(workspace)', if it
    # is available on the sub-class (i.e. if needed)
    #
    def _processWorkspace(self,workspace):
        if not hasattr(self,'processWorkspace'): return        
        if not callable(self.processWorkspace):  return        
        log.debug('Process Workspace [' + `workspace` + '] using [' + `self` + ']')        
        self.processWorkspace()
        
    #
    # Call a method called 'processModule(module)', if it
    # is available on the sub-class (i.e. if needed)
    #
    def _processModule(self,module):
        if not hasattr(self,'processModule'): return        
        if not callable(self.processModule):  return        
        log.debug('Process Module [' + `module` + '] using [' + `self` + ']')        
        self.processModule(module)
        
            
    #
    # Call a method called 'processProject(Project)', if it
    # is available on the sub-class (i.e. if needed)
    #
    def _processProject(self,project):
        if not hasattr(self,'processProject'): return        
        if not callable(self.processProject):  return        
        log.debug('Process Project [' + `project` + '] using [' + `self` + ']')        
        self.processProject(project)
        
            
    #
    # Call a method called 'processOtherEvent(event)', if it
    # is available on the sub-class (i.e. if needed)
    #
    def _processOtherEvent(self,event):
        if not hasattr(self,'processOtherEvent'): return        
        if not callable(self.processOtherEvent):  return        
        log.debug('Process (Other) Event [' + `event` + '] using [' + `self` + ']')        
        self.processOtherEvent(event)
        
            