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

	The OnDemand runner performs a run, but does work on
	modules as the needs of projects demands it.


"""

import os.path
import sys

from gump import log
from gump.run.gumprun import *
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

from gump.threads.tools import *


###############################################################################
# Classes
###############################################################################
  
class UpdateWork:
    def __init__(self,runner,module):
        self.runner=runner
        self.module=module
        
    def __str__(self):
        return 'UpdateWork:'+`self.module`
        
class UpdateWorker(WorkerThread):
    def performWork(self,work):
        # Do the work...
        work.runner.performUpdate(work.module)
        
class OnDemandRunner(GumpRunner):

    def __init__(self,run):
        GumpRunner.__init__(self,run)

    ###########################################
    def spawnUpdateThreads(self, updaters=1):
        """
        Fork off a bunch of threads.
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
        self.group.waitForAll()
        
    def performUpdate(self,module):
        """
        
        	Perform a module update (locking whilst doing it)	
        	
        """
        
        # Lock the module, while we work on it...
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
            
    def performBuild(self,project):
        """
            Perform a project build
        """
            
        # Perform the build action
        self.builder.buildProject(project)   
        
        # Generate the build event
        self.run.generateEvent(project)
        
        # Mark completed
        self.run.getGumpSet().setCompletedProject(project)
        
    ###########################################

    def performRun(self):
        """
        
        	Perform a run, building projects (and updating modules)
        	as needed.
        	
        	Basically walk the the project list (or full sequence)
        	and for all modules that need updating, update them,
        	then proceed to build the project.
        	
        	Fire events (1) before everything (2) for each entity
        	[module or project] and (3) after everything.
        	
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

            # Process the module, upon demand
            module=project.getModule()
            
            # If we want to be updating...
            if gumpOptions.isUpdate():
                # W/ multiple project in one module, it may be done
                if not module.isUpdated():
                    log.debug('Update module *inlined* ' + `module` + '.')     
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
