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
    An actor works upon the context tree. Events (and in the future,
    perhaps Requests) are passed to the Actor, and the Actor performs
    it's work.
    
    Example actors are:
    
        Statistician (keeps track of statistics, in a DB)
        TimeKeeper (keeps track of time spent on various things)
        Documenter (writes HTML for the work)
"""

import os.path
import os
import sys
from fnmatch import fnmatch

from gump.core.config import dir, default, basicConfig
from gump.core.run.gumpenv import GumpEnvironment
from gump.core.run.gumprun import *

from gump.util.work import *
from gump.util import dump, display, getIndent
from gump.util.note import Annotatable

from gump.core.model.workspace import Workspace
from gump.core.model.module import Module
from gump.core.model.project import Project
from gump.core.model.depend import  ProjectDependency
from gump.core.model.state import *

class  RunActor(RunSpecific):     
    """
        Abstract base class for all actors. The gump runner fires off different
        kinds of "events" (really just bits of the context trees that the gump
        runner has just updated then built) to the actor.
        
        This base class sets up some class properties that are often used in
        subclasses, and defines a base _processEvent that fires off processEvent
        on subclasses only if that method exists on the subclass.
    """
    
    def __init__(self, run, log = None):
        RunSpecific.__init__(self,run)
        
        if not log: from gump import log
        self.log = log
        
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
    """
    Abstract base class for nearly all actors. It acts as a basic event filter,
    sending different types of events to different methods in the subclass if
    those are defined. The supported methods are:
    
        processRun() -- for events of the GumpRun type. Use this one for doing
                start-of-run setup work.
        processWorkspace() -- fed the Workspace for this run after it is fully
                set up. Use this one for customizing the actor's behaviour
                based on the workspace and performing any late initialization.
        processModule() -- fed the Module instance for each and every module that
                has been processed by the main runner (ie, has been updated).
        processProject() -- fed the Project instance for each and every project
                that has been built by the main runnner (whether successful or
                not).
        processOtherEvent() -- fed all the other events (ie the ones that
                AbstractRunActor doesn't know about).
    """
    
    def __init__(self, run, log=None):
        RunActor.__init__(self, run, log)
        
    def processEvent(self,event):
        """
        Event handler that redirects to each of the _processXXXEvent methods,
        which in turn delegate to processXXXEvent methods on subclasses.
        """
        
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
            
    def _processRun(self):
        """
        Call a method called 'processRun(Run)', if it
        is available on the sub-class (i.e. if needed)
        """
        if not hasattr(self,'processRun'): return        
        if not callable(self.processRun):  return        
        self.log.debug('Process Run using [' + `self` + ']')        
        self.processRun()
        
            
    def _processWorkspace(self,workspace):
        """
        Call a method called 'processWorkspace(workspace)', if it
        is available on the sub-class (i.e. if needed)
        """
        if not hasattr(self,'processWorkspace'): return        
        if not callable(self.processWorkspace):  return        
        self.log.debug('Process Workspace [' + `workspace` + '] using [' + `self` + ']')        
        self.processWorkspace()
        
    def _processModule(self,module):
        """
        Call a method called 'processModule(module)', if it
        is available on the sub-class (i.e. if needed)
        """
        if not hasattr(self,'processModule'): return        
        if not callable(self.processModule):  return        
        self.log.debug('Process Module [' + `module` + '] using [' + `self` + ']')        
        self.processModule(module)
        
            
    def _processProject(self,project):
        """
        Call a method called 'processProject(Project)', if it
        is available on the sub-class (i.e. if needed)
        """
        if not hasattr(self,'processProject'): return        
        if not callable(self.processProject):  return     
        
        # Hack for bad data.
        if project.inModule():   
            self.log.debug('Process Project [' + `project` + '] using [' + `self` + ']')        
            self.processProject(project)
        else:
            self.log.debug('Skip Project (not in module) [' + `project` + '] for [' + `self` + ']')        
               
    def _processOtherEvent(self,event):
        """
        Call a method called 'processOtherEvent(event)', if it
        is available on the sub-class (i.e. if needed)
        """
        if not hasattr(self,'processOtherEvent'): return        
        if not callable(self.processOtherEvent):  return        
        self.log.debug('Process (Other) Event [' + `event` + '] using [' + `self` + ']')        
        self.processOtherEvent(event)
