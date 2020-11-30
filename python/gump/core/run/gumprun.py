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

 A gump.core.run (not 'run gump')
 
 This is the root container for information for a run.
 
 It contains the gumpset (the list of projects/modules to work upon)
 It contains the workspace (metadata)
 It contains the tree of context (run information upon metadata items)
 
"""

import os.path
import os
import sys
import fnmatch

from gump.core.config import dir, default, basicConfig
from gump.core.run.gumpenv import GumpEnvironment

import gump.core.run.gumpset
import gump.core.run.options

import gump.util
import gump.util.work
import gump.util.note

from gump.core.model.workspace import Workspace
from gump.core.model.module import Module
from gump.core.model.project import Project
from gump.core.model.depend import  ProjectDependency
from gump.core.model.state import *
    
class GumpRun(gump.util.timing.Timeable,gump.util.work.Workable,gump.util.note.Annotatable,Stateful):
    """
    The container for all information for this run.
    
    A GumpRun is "passive", it doesn't really do much of itself. (TODO: refactor
    so that it does absolutely *nothing*). That is what the gump.core.runner
    package is for.
    
    The GumpRun is pretty central to all the stuff going on during a gump run,
    obviously. It serves as the main communication point between the runner, its
    helpers, and all the different actors.
    
    TODO: evaluate making this class less central and splitting its various
          responsibilities into multiple smaller classes. Making this class so
          central to everything is what promotes most of the "monolithic" feel
          of the gump architecture right now.
    """
    def __init__(self,workspace,expr=None,options=None,env=None,log=None):
        gump.util.work.Workable.__init__(self)
        gump.util.note.Annotatable.__init__(self)
        Stateful.__init__(self)
        gump.util.timing.Timeable.__init__(self, workspace.getName())
        
        if not log: from gump import log
        self.log = log
        
        # The workspace being worked upon
        self.workspace=workspace
        
        # The set of modules/projects/repos in use
        self.gumpSet=gump.core.run.gumpset.GumpSet(self.workspace,expr)
        
        # The run options
        if options:
            self.options=options
        else:
            self.options=gump.core.run.options.GumpRunOptions()
        
        # The environment
        if env:
            self.env=env
        else:
            self.env=GumpEnvironment()
        
        # A repository interface...
        from gump.actor.repository.artifact import ArtifactRepository
        self.outputsRepository=ArtifactRepository(workspace.repodir)
                  
        # Generate a GUID (or close)
        import hashlib
        import socket        
        m=hashlib.md5()
        self.guid = socket.getfqdn()  + ':' + workspace.getName() + ':' + default.datetime_s
        m.update(self.guid.encode('utf-8'))
        self.hexguid=m.hexdigest().upper()     
        self.log.info('Run GUID [' + repr(self.guid) + '] using [' + repr(self.hexguid) + ']')    
        
        # Actor Queue
        self.actors=list()
        
        # Main players
        self.builder=None
        self.updater=None
        
        # Language Helpers
        self.languages={}
        
    def setBuilder(self,builder):
        self.builder=builder
        
    def getBuilder(self):
        return self.builder
        
    def setUpdater(self,updater):
        self.updater=updater
        
    def getUpdater(self):
        return self.updater

    def addLanguageHelper(self,language,helper):
        self.languages[language]=helper
        
    def getLanguageHelper(self,language):
        return self.languages[language]
        
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
        
        i=gump.util.getIndent(indent)
        #output.write(i+'Expression: ' + self.gumpSet. + '\n')
        output.write(i+'Gump Set:\n')
        self.gumpSet.dump(indent+1,output)
       
    def registerActor(self,actor):
        self.log.debug('Register Actor : ' + repr(actor))
        self.actors.append(actor)
        
    def logActors(self):
        self.log.debug('There are %s registered actors : ' % len(self.actors))       
        for actor in self.actors:
            self.log.debug('Registered Actor : ' + repr(actor))    
            
        
    def _dispatchEvent(self,event):        
        """
            Perform the dispatch
        """
        self.log.debug('Dispatch Event : ' + repr(event))        
        for actor in self.actors:
            #self.log.debug('Dispatch Event : ' + `event` + ' to ' + `actor`)     
            actor._processEvent(event)
        gump.util.inspectGarbageCollection(repr(event))
            
    def _dispatchRequest(self,request):
        """
            Perform the dispatch
        """
        self.log.debug('Dispatch Request : ' + repr(request))    
        for actor in self.actors:
            #self.log.debug('Dispatch Request : ' + `request` + ' to ' + `actor`)       
            actor._processRequest(request)
        gump.util.inspectGarbageCollection(repr(request))
            
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
        
        TODO: this is used both as a "marker interface" and as a
        general way to get at the global "context" represented by
        the GumpRun instance. If we can remove it from as many
        classes as possible that'll promote a *lot* of seperation
        of concerns and establishment of control barriers.
    """
    def __init__(self, run):
        self.run = run
        
    def getRun(self):
        return self.run

class RunEvent(RunSpecific):
    """
        An event to actors (e.g. a project built, a module updated).
        
        Note that not all events currently passed around are really
        "events", for example, we pass around actual Workspace and
        Project model elements as if they were "events", by encapsulating
        them into an EntityRunEvent. It is up to the actors to make sense
        of why the entity is an event.
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
        An event to actors (e.g. a project built, a module updated) that is
        associated with a particular piece of the gump model.
    """
            
    def __init__(self, run, entity, realtime=0):
        RunEvent.__init__(self,run)
        
        self.entity=entity
        self.realtime=realtime
            
    def __repr__(self):
        return self.__class__.__name__ + ':' + repr(self.entity)
        
    def getEntity(self):
        return self.entity 
        
    def isRealtime(self): #TODO: what is "realtime"?
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
        return self.__class__.__name__ + ':' + repr(self.entity)
        
    def getEntity(self):
        return self.entity 
                 
