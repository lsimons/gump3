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
 
 This is the root container for information for a run.
 
 It contains the gumpset (the list of projects/modules to work upon)
 It contains the workspace (metadata)
 It contains the tree of context (run information upon metadata items)
  
 
"""

import os.path
import os
import sys
import fnmatch

from gump import log
from gump.core.config import dir, default, basicConfig
from gump.run.gumpenv import GumpEnvironment

import gump.run.gumpset
import gump.run.options

import gump.utils
import gump.utils.work
import gump.utils.note

from gump.model.workspace import Workspace
from gump.model.module import Module
from gump.model.project import Project
from gump.model.depend import  ProjectDependency
from gump.model.state import *
    
###############################################################################
# Init
###############################################################################

###############################################################################
# Classes
###############################################################################


class GumpRun(gump.utils.work.Workable,gump.utils.note.Annotatable,Stateful):
    """
    The container for all information for this run
    """
    def __init__(self,workspace,expr=None,options=None,env=None):
        
        gump.utils.work.Workable.__init__(self)
        gump.utils.note.Annotatable.__init__(self)
        Stateful.__init__(self)
        
        # The workspace being worked upon
        self.workspace=workspace
        
        # The set of modules/projects/repos in use
        self.gumpSet=gump.run.gumpset.GumpSet(self.workspace,expr)
        
        # The run options
        if options:
            self.options=options
        else:
            self.options=gump.run.options.GumpRunOptions()
        
        # The environment
        if env:
            self.env=env
        else:
            self.env=GumpEnvironment()
        
        # A repository interface...
        from gump.repository.artifact import ArtifactRepository
        self.outputsRepository=ArtifactRepository(workspace.jardir)
                  
        # Generate a GUID (or close)
        import md5
        import socket        
        m=md5.new()
        self.guid = socket.getfqdn()  + ':' + workspace.getName() + ':' + default.datetime
        m.update(self.guid)
        self.hexguid=m.hexdigest().upper()     
        log.debug('Run GUID [' + `self.guid` + '] using [' + `self.hexguid` + ']')    
        
        # Actor Queue
        self.actors=list()

    def getRunGuid(self):
        return self.guid
        
    def getRunHexGuid(self):
        return self.hexguid
        
    def getWorkspace(self):
        return self.workspace

    def setEnvironment(self,env):
        self.env=env

    def getEnvironment(self):
        return self.env

    def getOptions(self):
        return self.options
        
    def getGumpSet(self):
        return self.gumpSet
        
    def getOutputsRepository(self):
        return self.outputsRepository
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        
        i=gump.utils.getIndent(indent)
        #output.write(i+'Expression: ' + self.gumpSet. + '\n')
        output.write(i+'Gump Set:\n')
        self.gumpSet.dump(indent+1,output)
       
    def registerActor(self,actor):
        log.debug('Register Actor : ' + `actor`)
        self.actors.append(actor)
        
    def _dispatchEvent(self,event):    	
    	"""
    		Perform the dispatch
    	"""
        log.debug('Dispatch Event : ' + `event`)        
        for actor in self.actors:
            log.debug('Dispatch Event : ' + `event` + ' to ' + `actor`)     
            actor._processEvent(event)
        gump.utils.inspectGarbageCollection(`event`)
            
    def _dispatchRequest(self,request):
    	"""
    		Perform the dispatch
    	"""
        log.debug('Dispatch Request : ' + `request`)    
        for actor in self.actors:
            log.debug('Dispatch Request : ' + `request` + ' to ' + `actor`)       
            actor._processRequest(request)
        gump.utils.inspectGarbageCollection(`request`)
            
    def generateEvent(self,entity):
        """
    		Fire off an entity event.
    	"""
        self._dispatchEvent(EntityRunEvent(self, entity))
        
    def generateRequest(self,type):
    	"""
    		Fire off a typed request.
    	"""
        self._dispatchRequest(RunRequest(self, type))
        
class RunSpecific:
    """
        A class that is it specific to an instance of a run.
        
        A run is so central to Gump that it is like a thread,
        the basis for everything, so many things are specific
        to a single run (for conveinience).
        
    """
    def __init__(self, run):
        self.run    =    run
        
    def getRun(self):
        return self.run

class RunEvent(RunSpecific):
    """
        An event to actors (e.g. a project built, a module updated)
    """
            
    def __init__(self, run):
        RunSpecific.__init__(self,run)
        
    def __repr__(self):
        return self.__class__.__name__
        
class InitializeRunEvent(RunEvent): 
    """
        The run is starting...
    """
    pass
    
class FinalizeRunEvent(RunEvent): 
    """
        The run is completed...
    """
    pass
        
class EntityRunEvent(RunEvent):
    """
    
        An event to actors (e.g. a project built, a module updated)
        
    """
            
    def __init__(self, run, entity, realtime=0):
        RunEvent.__init__(self,run)
        
        self.entity=entity
        self.realtime=realtime
            
    def __repr__(self):
        return self.__class__.__name__ + ':' + `self.entity`
        
    def getEntity(self):
        return self.entity 
        
    def isRealtime(self):
        return self.realtime    
        
                
class RunRequest(RunEvent):
    """
    
        A request for some work (not used yet)

    """            
    def __init__(self, run, type):
        RunEvent.__init__(self,run)
        self.type=type
        self.satisfied=False
        
    def getType(self):
        return self.type
        
    def isSatisfied(self):
        return self.satisfied  
        
class EntityRunRequest(RunEvent):
    """
    
        An request regarding a known entity (e.g. Workspace/Module/Project).
        (not used yet)
        
    """
    def __init__(self, run, type, entity):
        RunEvent.__init__(self, run, type)
        
        self.entity=entity
        
    def __repr__(self):
        return self.__class__.__name__ + ':' + `self.entity`
        
    def getEntity(self):
        return self.entity 
                 