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
from gump.core.runner import *
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

from gump.net.cvs import *

from gump.document.text.documenter import TextDocumenter
from gump.document.forrest.documenter import ForrestDocumenter

from gump.output.statsdb import *
from gump.output.repository import JarRepository
from gump.output.notify import notify
from gump.results.resulter import gatherResults,generateResults
from gump.syndication.syndicator import syndicate


###############################################################################
# Classes
###############################################################################

class SequentialTaskRunner(GumpRunner):

    def __init__(self,run):
        GumpRunner.__init__(self,run)

    ###########################################
        
    def performUpdate(self):
        return self.perform(GumpTaskList(['update','document']) )
    
    def performBuild(self):
        return self.perform(GumpTaskList(['build','document']) )
    
    def performDebug(self):
        return self.perform(GumpTaskList(['update','build','document']) )
    
    def performIntegrate(self):
        return self.perform(\
                GumpTaskList(['update','build','syndicate','generateResults','document','notify']) )
        
    def performCheck(self):
        return self.perform(GumpTaskList(['check','document']) )
        
    ###########################################
    
        
    # A few proxies...
    def preprocess(self): self.misc.preprocess()
    def build(self): self.builder.build()
    def update(self): self.updater.update()
    def document(self): self.misc.document()
    def syndicate(self): self.misc.syndicate()
    
    ###########################################
    
    def perform(self,taskList):     
    
        # Bind this list to these methods (on this engine)
        taskList.bind(self)
        
        # Run the method sequence...
        self.performTasks(taskList)      
                
        # Return an exit code based off success
        # :TODO: Move onto run
        if run.getWorkspace().isSuccess():
            result = EXIT_CODE_SUCCESS 
        else: 
            result = EXIT_CODE_FAILED
        
        return result  
    
    def performTasks(self,taskList):
        for task in taskList:
            # Perform tasks sequentially
            log.info('Perform task [' + task.getName() + ']')
            task.invoke()
            
            # Seems a nice place to clean up...    
            invokeGarbageCollection()
   
        
class GumpTask:
    
    def __init__(self, name, dependencyNames):
        self.dependencyNames=dependencyNames
        self.name=name
        self.method=None
        self.performed=0
            
    def __repr__(self):
        return self.__class__.__name__ + ':' + self.getName()
        
    def __str__(self):
        return self.getName()
        
    def getName(self):
        return self.name
        
    def getDependentTaskNames(self):
        return self.dependencyNames
    
    def setPerformed(self,performed):
        self.performed=performed
    
    def isPerformed(self):
        return self.performed
        
        
    def bind(self,engine):
        self.method=getattr(engine,self.name,None)            
        
        # For debugging ...        
        #if not (isinstance(self.method,types.MethodType) and callable(self.method)): 
        #    raise RuntimeError, 'Failed to bind task name [' + self.name + '] to engine [' + `engine` + ']'
        
    def invoke(self):
        if self.method:
            return self.method()
                                
class GumpTaskList(list):
    
    def __init__(self,taskNames=None):
        self.tasks={}
        if taskNames:
            self.populateForTaskNameList(taskNames)
        
    def addTask(self,task):
        if not self.hasTask(task):
            self.append(task)
            self.tasks[task.getName()]=task
    
    def hasTaskByName(self,name):
        return self.tasks.has_key(name)
        
    def hasTask(self,task):
        return self.hasTaskByName(task.getName())
        
    def getTask(self,name):
        if self.tasks.has_key(name):
            return self.tasks[name]     
                   
        #
        # The rules (the bare minimum of what needs
        # to have run, for a task to run w/o crashing).
        #
        
        
        if 'preprocess'==name:
            # Everything needs this ...
            task=GumpTask(name,[])            
        elif 'loadStatistics'==name:
            # The minimum to load stats onto the tree
            task=GumpTask(name,['preprocess'])  
        elif 'updateStatistics'==name:
            # Publish results to the statistics database
            # NB: Not really true to depend upon load, but cleaner..
            task=GumpTask(name,['preprocess','gatherResults','loadStatistics'])           
        elif 'update'==name:
            # Update from CVS|SVN repositories
            task=GumpTask(name,['preprocess','loadStatistics'])                    
        elif 'build'==name:
            # Build using Ant|Maven|...
            task=GumpTask(name,['preprocess','loadStatistics'])                    
        elif 'check'==name:
            # Check metadata
            task=GumpTask(name,['preprocess','loadStatistics'])             
        elif 'prepareDocumentation'==name:
            # Prepare documentation (e.g. create forest templates)
            task=GumpTask(name,['preprocess',])   
        elif 'document'==name:
            # Perform actual documentation
            task=GumpTask(name,	\
                    ['preprocess','loadStatistics','prepareDocumentation','gatherResults','updateStatistics',])    
        elif 'notify'==name:
            # Was once called 'nag'...
            task=GumpTask(name,['preprocess','loadStatistics'])  
        elif 'syndicate'==name:
            # Syndicate to news feeds
            task=GumpTask(name,['preprocess','loadStatistics','prepareDocumentation'])  
        elif 'gatherResults'==name:
            # Gather results.xml from other servers 
            task=GumpTask(name,['preprocess'])   
        elif 'setEndTime'==name:
            # Gather results.xml from other servers 
            task=GumpTask(name,['preprocess'])   
        elif 'generateResults'==name:
            # Generate the results.xml for this server/workspace
            task=GumpTask(name,['preprocess','loadStatistics','setEndTime','prepareDocumentation'])   
        else:
            raise RuntimeError, 'Unknown task name ['+name+']'            
        return task
            
    def getDependentTasks(self,task):
        dependencies=[]
        taskNames=task.getDependentTaskNames()
        for taskName in taskNames:
            dependencies.append(self.getTask(taskName))        
        return dependencies 
        
    def populateForTaskNameList(self,taskNames):        
        for taskName in taskNames:
            self.populateForTaskName(taskName)
        
    def populateForTaskName(self,taskName):
        self.populateForTask(self.getTask(taskName))
        
    def populateForTask(self,task):
        if not task in self:
            for depend in self.getDependentTasks(task):
                self.populateForTask(depend)
            self.addTask(task)                            
            
    def bind(self,engine):
        for task in self: task.bind(engine)
                    