#!/usr/bin/env python
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

    Actor to update stats
    
"""

import os

from gump.core.config import *
from gump import log
from gump.core.run.gumprun import *
from gump.core.run.actor import *

class Statistician(AbstractRunActor):
    def __init__(self,run,db=None):
        
        AbstractRunActor.__init__(self,run)        
        
        self.db=db        
        if not self.db:
        
            # MySQL is optional...
            if self.run.getWorkspace().hasDatabaseInformation():
                try:
                    import gump.actor.stats.mysql.statsdb   
                    # Figure out what DB this workspace uses 
                    dbInfo=self.run.getWorkspace().getDatabaseInformation()
                    self.db=gump.actor.stats.mysql.statsdb.StatisticsDB(dbInfo)   
                except Exception as details:
                    log.error('Failed to load MySQL database driver : %s' % (details), exc_info=1)
            
            if not self.db:
                # DBM is the fallback...
                import gump.actor.stats.dbm.statsdb            
                self.db=gump.actor.stats.dbm.statsdb.StatisticsDB()   
            
    def getDatabase(self):
        return self.db
        
    def processOtherEvent(self,event):                
        """
        Process the 'other' (generic) event, e.g. Init and Finalize
        In other words, load stats at the start, and update them
        at the end
        """
        if isinstance(event,InitializeRunEvent):
            self.loadStatistics()                
        elif isinstance(event,FinalizeRunEvent):          
            if self.run.getOptions().isStatistics():          
                self.updateStatistics()        
            
            
    def loadStatistics(self):
        """
        
        Load statistics from the DB onto the objects, so they can
        reference the latest information (e.g. to set -debug)
        
        """
        log.debug('--- Loading Statistics')
                  
        # Load the W/S statistics
        ws=self.db.getWorkspaceStats(self.workspace.getName())
        self.workspace.setStats(ws)            
                
        for repo in self.workspace.getRepositories():
                        
            # Load the statistics
            rs=self.db.getRepositoryStats(repo.getName())
                
            # Stash for later...
            repo.setStats(rs)    
                      
        for module in self.workspace.getModules():
            # Load the statistics...
            ms=self.db.getModuleStats(module.getName())        
                
            # Stash for later...
            module.setStats(ms)     
            
            for project in module.getProjects():
                # Load the statistics...
                ps=self.db.getProjectStats(project.getName())        
                
                # Stash for later...
                project.setStats(ps)            
            
    def updateStatistics(self):
        """
        
        Go through the tree updating statistics as you go...
        
        """
        log.debug('--- Updating Statistics')
        
        # Load the W/S statistics
        ws=self.db.getWorkspaceStats(self.workspace.getName())
        # Update for this workspace based off this run
        ws.update(self.workspace)
        self.workspace.setStats(ws)      
            
        # Write out the updates
        self.db.putWorkspaceStats(ws)        
                
        for repo in self.workspace.getRepositories():
                        
            # Load the statistics
            rs=self.db.getRepositoryStats(repo.getName())
            
            # Update for this repo based off this run
            rs.update(repo)
                
            # Stash for later...
            repo.setStats(rs)    
            
            # Write out the updates
            self.db.putRepositoryStats(rs)     
              
        for module in self.workspace.getModules():
                        
            # Load the statistics
            ms=self.db.getModuleStats(module.getName())
            
            # Update for this project based off this run
            ms.update(module)
                
            # Stash for later...
            module.setStats(ms)            
                
            # Write out the updates
            self.db.putModuleStats(ms)     
            
            for project in module.getProjects():
                
                # Load the statistics
                ps=self.db.getProjectStats(project.getName())
            
                # Update for this project based off this run
                ps.update(project)
                
                # Stash for later...
                project.setStats(ps)            
                
                # Write out the updates
                self.db.putProjectStats(ps) 
                
        self.db.sync()
            
    def dumpProjects(self):
        """
        Show all that is there
        """
        for key in self.db.getProjects():
            print("Project " + pname + " Key " + key)
            s=self.getProjectStats(pname)
            dump(s)
                
