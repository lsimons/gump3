#!/usr/bin/env python
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

    MySQL Statistics gathering/manipulation
    
"""

import time
import datetime
import types
import os
import sys

import MySQLdb
import MySQLdb.cursors

from gump import log
from gump.core.config import *
from gump.model.project import Project, ProjectStatistics
from gump.model.module import Module, ModuleStatistics
from gump.model.repository import Repository, RepositoryStatistics
from gump.model.workspace import Workspace, WorkspaceStatistics
from gump.model.state import *

import gump.utils.mysql
  
class StatisticsDB:
    """
    	MySQL Statistics Database Interface
    """
    
    FIRST_COLUMN='first'
    LAST_COLUMN='last'
    START_OF_STATE_COLUMN='start_of_state'
    LAST_MODIFIED_COLUMN='last_modified'
    
    DATES=[ FIRST_COLUMN, 
            LAST_COLUMN,
            START_OF_STATE_COLUMN,
            LAST_MODIFIED_COLUMN ]
    
    ATTR_COLUMN_MAP={
                        'successes':'successes',
                        'failures':'failures',
                        'prereqs':'prereqs',
                        'first':FIRST_COLUMN,
                        'last':LAST_COLUMN,
                        'currentState':'current_state',
                        'previousState':'previous_state',
                        'startOfState':START_OF_STATE_COLUMN,
                        'sequenceInState':'sequence_in_state'
                    }
    
    def __init__(self,dbInfo):
        self.conn=MySQLdb.Connect(
                host=dbInfo.getHost(), 
                user=dbInfo.getUser(),
                passwd=dbInfo.getPasswd(), 
                db=dbInfo.getDatabase(),
                compress=1,
                cursorclass=MySQLdb.cursors.DictCursor)
            
        # print 'ThreadSafe : ' + `MySQLdb.threadsafety`
        
        self.helper=gump.utils.mysql.DbHelper(self.conn,dbInfo.getDatabase())
 
    # Workspace
    def getWorkspaceStats(self,workspaceName):
        stats=WorkspaceStatistics(workspaceName)
        try:
            self._getStats('workspace_stats','workspace_name',workspaceName,stats)
        except IndexError:
            pass
        return stats
        
    def putWorkspaceStats(self,stats):
        self._putStats('workspace_stats','workspace_name',stats)

    def delWorkspaceStats(self,stats):
        self._delStats('workspace_stats','workspace_name',stats)          
        
    # Project    
    def getProjectStats(self,projectName):
        stats=ProjectStatistics(projectName)         
        try:
            self._getStats('project_stats','project_name',projectName,stats)         
        except IndexError:
            pass
        return stats
                
    def putProjectStats(self,stats): 
        self._putStats('project_stats','project_name',stats)
        
    def delProjectStats(self,stats): 
        self._delStats('project_stats','project_name',stats)

    # Repository 
    def getRepositoryStats(self,repositoryName):
        stats=RepositoryStatistics(repositoryName)     
        try:   
            self._getStats('repository_stats','repository_name',repositoryName,stats)
        except IndexError:
            pass    
        return stats
                
    def putRepositoryStats(self,stats):
        self._putStats('repository_stats','repository_name',stats)  

    def delRepositoryStats(self,stats):
        self._delStats('repository_stats','repository_name',stats)          

    # Module    
    def getModuleStats(self,moduleName):
        stats=ModuleStatistics(moduleName)        
        try:
            settings = self._getStats('module_stats','module_name',moduleName,stats)
            
            # Extract that extra
            if settings.has_key('last_modified') and settings['last_modified']:
                stats.lastModified=settings['last_modified']
        except IndexError:
            pass
        return stats
                
    def putModuleStats(self,stats):
        extras=None
        if stats.lastModified:
            extras={'last_modified':stats.lastModified}        
        self._putStats('module_stats','module_name',stats,extras)

    def delModuleStats(self,stats):
        self._delStats('module_stats','module_name',stats)     
        
        
    # Helpers...
    def _getStats(self,table_name,column_name,entity_name,stats):
        
        # Select the row settings from the database
        settings=self.helper.select(table_name,column_name,entity_name,
                                StatisticsDB.ATTR_COLUMN_MAP.values())
        
        # Extract columns
        self._getBaseStats(stats,settings)
            
        return settings
        
    def _putStats(self,table_name,column_name,stats,extras=None): 
    
        settings = self._putBaseStats(stats,column_name)
        if extras: 
            for (key,value) in extras.items(): settings[key] = value
            
        # Perform the update (we've ensured a row exists).
        self.helper.set(table_name,column_name,stats.name,settings)
    
    def _delStats(self,table_name,column_name,stats):       
        """ Perform an SQL DELETE """        
        # Perform the delete
        self.helper.delete(table_name,column_name,stats.name)

    def _getBaseStats(self,stats,settings):
        """
        Extract values by name from the DB row
        """      
        for (attr, column) in StatisticsDB.ATTR_COLUMN_MAP.items():
            if settings.has_key(column) and settings[column]:
                if hasattr(stats,attr):
                    value=settings[column]
                    
                    # Seems some SQL interfaces do not return datetime objects
                    # but strings, for SQL:datetime.
                    
                    
                    if column in StatisticsDB.DATES:   
                        print "GET ATTR : " + `type(getattr(stats,attr))`                      
                        if isinstance(value,datetime.datetime):
                            setattr(stats,attr,value)
                        else:
                            if not value == '0000-00-00 00:00:00':
                                setattr(stats,attr,
                                    datetime.datetime.fromtimestamp(time.mktime(time.strptime(value,
                                                                                '%Y-%m-%d %H:%M:%S'))))
                    else:    
                        setattr(stats,attr,value)
        
    def _putBaseStats(self,stats,column_name): 
        """
        Return a dictionary of the named values
        """
        settings=dict()
        
        settings[column_name] = "'" + stats.name + "'"
        
        for (attr, column) in StatisticsDB.ATTR_COLUMN_MAP.items():
            if hasattr(stats,attr):
                value = getattr(stats,attr)
                if value:
                    if column in StatisticsDB.DATES:   
                        #print "SET ATTR : " + `value` 
                        settings[column] = "'" + value.strftime('%Y-%m-%d %H:%M:%S') + "'"
                    elif isinstance(value,types.StringTypes):
                        settings[column] = "'" + str(value) + "'"
                    else:
                        settings[column] = str(value)
                
        return settings

    def sync(self): pass
    
if __name__ == '__main__':
    import logging
    
    # init logging
    logging.basicConfig()

    #set verbosity to show all messages of severity >= default.logLevel
    log.setLevel(logging.DEBUG)
    
    stats=StatisticsDB()
    
    # Project
    ps=stats.getProjectStats('test')
    ps.successes+=1
    ps.first=datetime.datetime.now()
    stats.putProjectStats(ps)     
    if len(sys.argv) > 1:
        stats.delProjectStats(ps)
    print "Project"
    ps.dump()    
    
    sys.exit()
    
    # Workspace
    ws=stats.getWorkspaceStats('test')
    ws.successes+=1
    stats.putWorkspaceStats(ws)     
    if len(sys.argv) > 1:
        stats.delWorkspaceStats(ws)
    print "Workspace"
    ws.dump()    
    
    # Module
    ms=stats.getModuleStats('test')
    ms.successes+=1
    stats.putModuleStats(ms)     
    if len(sys.argv) > 1:
        stats.delModuleStats(ms)
    print "Module"
    ms.dump()
          
    # Repository
    rs=stats.getRepositoryStats('test')
    rs.successes+=1
    stats.putRepositoryStats(rs)     
    if len(sys.argv) > 1:
        stats.delRepositoryStats(rs)
    print "Repository"
    rs.dump()
          