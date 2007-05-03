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

from gump.core.update.updater import *
from gump.core.build.builder import *

import gump.core.language.java
import gump.core.language.csharp

from gump.actor.document.text.documenter import TextDocumenter
from gump.actor.document.xdocs.documenter import XDocDocumenter
from gump.actor.document.xdocs.synchronizer import Synchronizer

from gump.actor.timing.keeper import TimeKeeper
from gump.actor.stats.statistician import Statistician
from gump.actor.repository.publisher import RepositoryPublisher
from gump.actor.notify.notifier import Notifier
from gump.actor.results.resulter import Resulter
from gump.actor.syndication.syndicator import Syndicator

class GumpRunner(RunSpecific):
    """
    Base class for other runners that initializes several helper objects.
    
    the lifecycle for this class is as follows:
    
        runner.initialize() # set up environment
        runner.perform()    # delegates to subclass to perform actual work
        runner.finalize()   # do some cleanup work
    """

    def __init__(self, run, log=None):
        RunSpecific.__init__(self, run)
        
        if not log: from gump import log
        self.log = log
        
        # Main players (soon we ought make them into actors, like the others).         
        self.updater = GumpUpdater(run)
        self.builder = GumpBuilder(run)
        
        # A helper per language/type
        self.java = gump.core.language.java.JavaHelper(run)
        self.csharp = gump.core.language.csharp.CSharpHelper(run)
        
        # Stash them for reference...
        run.setUpdater(self.updater)
        run.setBuilder(self.builder)
            
        run.addLanguageHelper(Project.JAVA_LANGUAGE,self.java)  
        run.addLanguageHelper(Project.CSHARP_LANGUAGE,self.csharp)
        
    def initialize(self,exitOnError=True):
        """
        Set up all of the neccessary resources for the subclass implementation to use.
        Besides modifying the properties of this class, we also modify bits of the
        workspace and bits of the GumpRun instance.
        
        TODO: currently this method must be called from the performRun() method of the
        subclass. Call it from perform() instead.
        
        TODO: clean this up and have a clear responsibility split between the various
        parts we're modifying here...
        """
        
        logResourceUtilization('Before initialize')
        
        # Perform start-up logic 
        workspace = self.run.getWorkspace()
                
        # Check out environment
        if not self.run.getOptions().isQuick():
            logResourceUtilization('Before check environment')            
            self.run.getEnvironment().checkEnvironment(exitOnError)
            logResourceUtilization('After check environment')
        
        # Now, force cetain things (like blanking CLASSPATH)
        self.run.getEnvironment().setEnvironment()
        
        # Modify the log location on the fly, if --dated
        if self.run.getOptions().isDated():
            workspace.setDatedDirectories()     
                    
        # Check the workspace
        if not workspace.getVersion() >= setting.WS_VERSION:
            message='Workspace version ['+str(workspace.getVersion())+'] below preferred [' + setting.WS_VERSION + ']'
            workspace.addWarning(message)
            self.log.warn(message)   

        if not workspace.getVersion() >= setting.WS_MINIMUM_VERSION:
            message='Workspace version ['+str(workspace.getVersion())+'] below minimum [' + setting.WS_MINIMUM_VERSION + ']'
            workspace.addError(message)
            self.log.error(message)   
            
        # Write workspace to a 'merge' file        
        if not self.run.getOptions().isQuick():
            workspace.writeXmlToFile(default.merge)
            workspace.setMergeFile(default.merge)
                 
        # :TODO: Put this somewhere else, and/or make it depend upon something...
        workspace.changeState(STATE_SUCCESS)
 
        # Initialize Actors
        self.initializeActors()             
 
        # Let's get going...
        self.run._dispatchEvent(InitializeRunEvent(self.run))
    
    def initializeActors(self):
        """
        Populate the GumpRun instance with the various actors.
        
        The actors handle all the "optional" behaviour like writing HTML or sending e-mail. One
        way to think of this method is where we configure the "glue" between all the different
        bits and pieces of the application.
        
        TODO:
        """
        
        # Stamp times
        self.run.registerActor(TimeKeeper(self.run))
        
        # Update statistics
        self.run.registerActor(Statistician(self.run))
        
        # Load/Generate results (if we are in a multi-server)
        # environment, where result sharing is important
        if self.run.getOptions().isResults() and \
            self.run.getWorkspace().hasMultiplePythonServers():
            self.run.registerActor(Resulter(self.run))            

        # Add Database storer
        if self.run.getOptions().isOfficial() and \
            self.run.getWorkspace().hasDatabaseInformation() and \
            not self.run.getOptions().isHistorical():    
            try:
                import gump.actor.mysql.databaser
                self.run.registerActor(gump.actor.mysql.databaser.Databaser(self.run))
            except Exception, details:
                self.log.warning('Unable to register Database Actor :  %s ' % details,
                            exc_info=1)
        
        # Add Historical Database storer -- ??? no such thing...
        if self.run.getOptions().isOfficial() and \
            self.run.getWorkspace().hasDatabaseInformation() and \
            self.run.getOptions().isHistorical():       
            try:
                import gump.actor.history.historical
                self.run.registerActor(gump.actor.history.historical.Historical(self.run))
            except Exception, details:
                self.log.warning('Unable to register Historical Database Actor :  %s ' % details,
                            exc_info=1)

        # Add Dynagump database populator
        if self.run.getWorkspace().hasDatabaseInformation():
            # create the database helper
            dbInfo = self.run.getWorkspace().getDatabaseInformation()
            from gump.util.mysql import Database
            database = Database(dbInfo)

            # now create the Dynagumper using that database
            import gump.actor.mysql.dynagumper
            self.run.registerActor(gump.actor.mysql.dynagumper.Dynagumper(self.run,database))
        
        # Document..
        # Use XDOCS if not overridden...
        xdocs=False
        documenter=None
        if self.run.getOptions().isText() :
            documenter=TextDocumenter(self.run)
        else:
            xdocs=True
            documenter=XDocDocumenter(	self.run,	\
                                        self.run.getWorkspace().getBaseDirectory(), \
                                        self.run.getWorkspace().getLogUrl())  
        self.run.getOptions().setResolver(documenter.getResolver())                                                  
        self.run.registerActor(documenter)    
        
        # Syndicate once documented
        if self.run.getOptions().isSyndicate():
            self.run.registerActor(Syndicator(self.run))   
            
        # Describe [once documented]
        if self.run.getOptions().isDescribe():
            try:
                import gump.actor.rdf.describer
                self.run.registerActor(gump.actor.rdf.describer.RDFDescriber(self.run))   
            except Exception, details:
                self.log.warning('Unable to register RDF Describer :  %s ' % details,
                            exc_info=1)
            
        # Publish artifacts
        if self.run.getOptions().isPublish():
            self.run.registerActor(RepositoryPublisher(self.run))   

        # Synchonize
        if xdocs:
            self.run.registerActor(Synchronizer(self.run,documenter))
        
        # Notify last
        if self.run.getOptions().isNotify() and self.run.getWorkspace().isNotify():
            self.run.registerActor(Notifier(self.run))    
        else:
            self.log.info('Not doing notifications [%s,%s]' \
                % (self.run.getOptions().isNotify(), \
                    self.run.getWorkspace().isNotify() ) )
                    
                    
        # See what we have...            
        self.run.logActors()
        
    def finalize(self):            
        # About to shutdown...
        self.run._dispatchEvent(FinalizeRunEvent(self.run))
        
    def getUpdater(self):
        return self.updater
        
    def getBuilder(self):
        return self.builder
   
    def perform(self):
        """
        Does the actual gump work by delegating to the performRun(run) method of a subclass.
        """
        if not hasattr(self,'performRun'):
            raise RuntimeError, \
                    'Class [' + `self.__class__` + '] needs a performRun(self,run)'
        
        if not callable(self.performRun):
            raise RuntimeError, \
                    'Class [' + `self.__class__` + '] needs a callable performRun(self,run)'
        
        self.log.debug('Perform run using [' + `self` + ']')
        
        return self.performRun()

def getRunner(run):
    """
    Factory method that provides the default GumpRunner subclass to use.
    """
    from gump.core.runner.demand import OnDemandRunner
    return OnDemandRunner(run)
