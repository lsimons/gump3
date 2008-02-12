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

import os.path
import sys

from gump.core.run.gumprun import *
from gump.core.runner.runner import *
from gump.core.config import dir, default, basicConfig

from gump.util import dump, display, getIndent, logResourceUtilization, \
                            invokeGarbageCollection, printTopRefs
from gump.util.note import Annotatable
from gump.util.work import *

from gump.util.tools import *

from gump.core.model.workspace import *
from gump.core.model.module import Module
from gump.core.model.project import Project
from gump.core.model.depend import  ProjectDependency
from gump.core.model.stats import *

from gump.util.threads.tools import *
from gump.util.locks import *

class OnDemandRunner(GumpRunner):
    """
	The OnDemand runner updates modules just-in-time before a project is built.
	
	However, if gump is configured for multithreading, it also spawns several updater
	threads in the background which do module updates. This is an effort to maximize
	network and disk I/O.
    """

    def __init__(self, run, log=None):
        GumpRunner.__init__(self,run,log)

    def spawnUpdateThreads(self, updaters=1):
        """
        Fork off a bunch of threads for running module updates.
        """
        
        self.workList=ThreadWorkList('Updates')
        
        # Add work for each module (in order)
        for module in self.run.gumpSet.getModuleSequence():
            self.workList.addWork(UpdateWork(self,module))    
            
        # Create a group of workers...
        self.group=WorkerThreadGroup('Update',updaters,self.workList,UpdateWorker)
        self.group.start()
        
    def waitForThreads(self):
        """
        Wait for all workers to complete.
        """
        if self.group:
            if hasattr(self.group, "waitForAll"):
                self.group.waitForAll()
        
    def performUpdate(self,module):
        """
        	Perform the (cvs,svn) update of a single module.
        	
        	The module is locked during the update. Most of the actual work
        	is delegated to the updater that's provided by the parent GumpRunner
        	class.
        """
        flock=None
        try:
            # Only on POSIX can we block on a file lock,
            # so only here do we support shared update
            # staging areas.
            if 'posix'==os.name:
                flock = acquireLock(module.getUpdateLockFile())
              
            # Normal thread locking...
            lock=module.getLock()
            try:
                lock.acquire()
        
                if not module.isUpdated():
                
                    # Perform Update
                    self.updater.updateModule(module)         
        
                    # Fire event
                    self.run.generateEvent(module)
        
                    # Mark as done in set
                    self.run.gumpSet.setCompletedModule(module)
                
                    # Mark Updated
                    module.setUpdated(True)
            finally:
                lock.release()
        finally:
            if flock:
                releaseLock(flock,module.getUpdateLockFile())
            
            
    def performBuild(self,project):
        """
            Perform the actual (ant,maven,make) build of a single project.
            
            Most of the actual work is delegated to the builder that's
            provided by the parent GumpRunner class.
        """
            
        # Perform the build action
        self.builder.buildProject(project)   
        
        # Generate the build event
        self.run.generateEvent(project)
        
        # Mark completed
        self.run.getGumpSet().setCompletedProject(project)
        
    def performRun(self):
        """
        	Perform a run, building projects (and updating modules)
        	as needed.
        	
        	Basically walk the the project list (or full sequence)
        	and for all modules that need updating, update them,
        	then proceed to build the project.
        	
        	Fire events (1) before everything (2) for each entity
        	[module or project] and (3) after everything.
        	
        	You may think of this method as performing "all the real beef" for
        	a gump run, delegating to lots of different helpers and actors in
        	the process.
        """
        # Initialize to run
        self.initialize(True)
        
        # printTopRefs(100,'Before Loop')
        
        # The key information
        gumpSet=self.run.getGumpSet()
        gumpOptions=self.run.getOptions() 
        workspace = self.run.getWorkspace()
        
        # If we want to do updates
        if gumpOptions.isUpdate():
            # If we want multithreaded (and workspace allows)
            if workspace.isMultithreading() and workspace.hasUpdaters():
                # Experimental: Spawn some...
                self.spawnUpdateThreads(workspace.getUpdaters())
        
        # The project TODO list...
        if gumpOptions.isQuick():
            # Just the projects
            sequence=gumpSet.getProjects()
        else:
            # The full build sequence
            sequence=gumpSet.getProjectSequence()
        
        # Number of modules not updated by a
        # background thread.
        inlined=0
        
        # In project order...
        for project in sequence:

            # If we want to be updating...
            if gumpOptions.isUpdate():
                
                if project.inModule():
                    # Process the module, upon demand
                    module=project.getModule()
            
                    # W/ multiple project in one module, it may be done
                    if not module.isUpdated():
                        self.log.debug('Update module *inlined* (not in background thread) ' + `module` + '.')     
                        inlined+=1
                        self.performUpdate(module)

            # If we want to be building...
            if gumpOptions.isBuild():
                # Process the project
                self.performBuild(project)
            
            # Seems a nice place to peek/clean-up...    
            #printTopRefs(100,'Before Loop GC')
            #invokeGarbageCollection(self.__class__.__name__)
            #invokeGarbageCollection(self.__class__.__name__)
            #invokeGarbageCollection(self.__class__.__name__)
            #printTopRefs(100,'After GC')
        
        # Kinda pointless given the above logic,
        # but a belt/braces to ensure all done.
        if workspace.isMultithreading() and workspace.hasUpdaters():    
            self.waitForThreads()
        
        # Done...
        self.finalize()    
        
        # printTopRefs(100,'Done')
                
        # Return an exit code based off success
        # :TODO: Move onto run
        if self.run.getWorkspace().isSuccess():
            result = EXIT_CODE_SUCCESS 
        else: 
            result = EXIT_CODE_FAILED
            
        return result  

class UpdateWork:
    """
    Simple internal helper class which defines a unit of module updating work that can be
    handled by one of the update workers.
    """
    def __init__(self,runner,module):
        self.runner=runner
        self.module=module
        
    def __str__(self):
        return 'UpdateWork:'+`self.module`
        
class UpdateWorker(WorkerThread):
    """
    Simple internal worker thread which performs one unit of module updating work (one
    UpdateWork) each time it is fired up.
    """
    def performWork(self,work):
        # Do the work...
        work.runner.performUpdate(work.module)
