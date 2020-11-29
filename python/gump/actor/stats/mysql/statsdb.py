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

    MySQL Statistics gathering/manipulation

"""

import time
import datetime
import types
import sys

import MySQLdb
import MySQLdb.cursors

from gump import log
from gump.core.model.project import ProjectStatistics
from gump.core.model.module import ModuleStatistics
from gump.core.model.repository import RepositoryStatistics
from gump.core.model.workspace import WorkspaceStatistics

import gump.util.mysql
from gump.util.timing import getLocalNow

class StatisticsDB:
    """
        MySQL Statistics Database Interface
    """

    FIRST_COLUMN = 'first'
    LAST_COLUMN = 'last'
    START_OF_STATE_COLUMN = 'start_of_state'
    LAST_MODIFIED_COLUMN = 'last_modified'

    DATES = [ FIRST_COLUMN, 
              LAST_COLUMN,
              START_OF_STATE_COLUMN,
              LAST_MODIFIED_COLUMN ]

    ATTR_COLUMN_MAP = {
        'successes' : 'successes',
        'failures' : 'failures',
        'prereqs' : 'prereqs',
        'first' : FIRST_COLUMN,
        'last' : LAST_COLUMN,
        'currentState' : 'current_state',
        'previousState' : 'previous_state',
        'startOfState' : START_OF_STATE_COLUMN,
        'sequenceInState' : 'sequence_in_state'
        }

    def __init__(self, dbInfo):
        self._dbinfo = dbInfo
        self._helper = None

    def _get_helper(self):
        """
        Returns a cached DBHelper or creates and caches a new one
        """
        if self._helper:
            return self._helper
        conn = MySQLdb.Connect(
            host = self._dbinfo.getHost(), 
            user = self._dbinfo.getUser(),
            passwd = self._dbinfo.getPasswd(), 
            db = self._dbinfo.getDatabase(),
            compress = 1,
            cursorclass = MySQLdb.cursors.DictCursor)

        # print 'ThreadSafe : ' + `MySQLdb.threadsafety`

        self._helper = gump.util.mysql.DbHelper(conn,
                                                self._dbinfo.getDatabase())
        return self._helper
 
    # Workspace
    def getWorkspaceStats(self, workspaceName):
        stats = WorkspaceStatistics(workspaceName)
        try:
            self._getStats('gump_workspace_stats', 'workspace_name',
                           workspaceName,stats)
        except IndexError:
            pass
        return stats

    def putWorkspaceStats(self, stats):
        self._putStats('gump_workspace_stats', 'workspace_name', stats)

    def delWorkspaceStats(self, stats):
        self._delStats('gump_workspace_stats', 'workspace_name', stats)

    # Project
    def getProjectStats(self, projectName):
        stats = ProjectStatistics(projectName)
        try:
            self._getStats('gump_project_stats', 'project_name', projectName,
                           stats)
        except IndexError:
            pass
        return stats

    def putProjectStats(self, stats): 
        self._putStats('gump_project_stats', 'project_name', stats)

    def delProjectStats(self, stats): 
        self._delStats('gump_project_stats', 'project_name', stats)

    # Repository 
    def getRepositoryStats(self, repositoryName):
        stats = RepositoryStatistics(repositoryName)
        try:
            self._getStats('gump_repository_stats', 'repository_name',
                           repositoryName, stats)
        except IndexError:
            pass
        return stats

    def putRepositoryStats(self, stats):
        self._putStats('gump_repository_stats', 'repository_name', stats)

    def delRepositoryStats(self, stats):
        self._delStats('gump_repository_stats', 'repository_name', stats)

    # Module
    def getModuleStats(self, moduleName):
        stats = ModuleStatistics(moduleName)
        try:
            settings = self._getStats('gump_module_stats', 'module_name',
                                      moduleName, stats)

            # Extract that extra
            if settings.has_key('last_modified') and settings['last_modified']:
                value = settings['last_modified']
                if isinstance(value, datetime.datetime):
                    stats.lastModified = value
                else:
                    if not value == '0000-00-00 00:00:00':
                        stats.lastModified = datetime.datetime.fromtimestamp( \
                            time.mktime(time.strptime(value,
                                                      '%Y-%m-%d %H:%M:%S')))
        except IndexError:
            pass
        return stats

    def putModuleStats(self, stats):
        extras = None
        if stats.lastModified:
            extras = {'last_modified' : "'" +\
                          stats.lastModified.strftime('%Y-%m-%d %H:%M:%S') +\
                          "'"}
        self._putStats('gump_module_stats', 'module_name', stats, extras)

    def delModuleStats(self, stats):
        self._delStats('gump_module_stats', 'module_name', stats)


    # Helpers...
    def _getStats(self, table_name, column_name, entity_name, stats):

        # Select the row settings from the database
        settings = self._with_reconnect_on_error(\
            lambda helper:
                helper.select(table_name, column_name, entity_name,
                              StatisticsDB.ATTR_COLUMN_MAP.values()))

        # Extract columns
        self._getBaseStats(stats, settings)

        return settings

    def _putStats(self, table_name, column_name, stats, extras = None): 

        settings = self._putBaseStats(stats, column_name)
        if extras:
            for (key, value) in extras.items():
                settings[key] = value

        def setter(helper):
            helper.set(table_name, column_name, stats.name, settings)
            helper.commit()

        # Perform the update (we've ensured a row exists).
        self._with_reconnect_on_error(setter)

    def _delStats(self, table_name, column_name, stats):
        """ Perform an SQL DELETE """

        def deleter(helper):
            helper.delete(table_name, column_name, stats.name)
            helper.commit()

        # Perform the delete
        self._with_reconnect_on_error(deleter)

    def _getBaseStats(self, stats, settings):
        """
        Extract values by name from the DB row
        """
        for (attr, column) in StatisticsDB.ATTR_COLUMN_MAP.items():
            if settings.has_key(column) and settings[column]:
                if hasattr(stats, attr):
                    value = settings[column]

                    # Seems some SQL interfaces do not return datetime objects
                    # but strings, for SQL:datetime.

                    if column in StatisticsDB.DATES:
                        #print "GET ATTR : " + `type(getattr(stats,attr))`
                        if isinstance(value, datetime.datetime):
                            setattr(stats, attr, value)
                        else:
                            if not value == '0000-00-00 00:00:00':
                                setattr(stats, attr,
                                        datetime.datetime\
                                            .fromtimestamp(\
                                        time.mktime(time.strptime(value,
                                                                  '%Y-%m-%d %H:%M:%S'))))
                    else:
                        setattr(stats, attr, value)

    def _putBaseStats(self, stats, column_name): 
        """
        Return a dictionary of the named values
        """
        settings = dict()

        settings[column_name] = "'" + stats.name + "'"

        for (attr, column) in StatisticsDB.ATTR_COLUMN_MAP.items():
            if hasattr(stats, attr):
                value = getattr(stats, attr)
                if value:
                    if column in StatisticsDB.DATES:
                        #print "SET ATTR : " + `value` 
                        settings[column] = "'" +\
                            value.strftime('%Y-%m-%d %H:%M:%S') + "'"
                    elif isinstance(value, types.StringTypes):
                        settings[column] = "'" + str(value) + "'"
                    else:
                        settings[column] = str(value)

        return settings

    def sync(self):
        pass

    def _with_reconnect_on_error(self, command):
        """
        Executes command (passing in a DbHelper instance) and retries
        it with a new instance if an OperationalError occurs
        """
        try:
            return command(self._get_helper())
        except MySQLdb.OperationalError:
            log.info("Caught an exception from DB, reconnecting")
            self._helper = None
            return command(self._get_helper())

if __name__ == '__main__':
    import logging

    # init logging
    logging.basicConfig()

    #set verbosity to show all messages of severity >= default.logLevel
    log.setLevel(logging.DEBUG)

    stats = StatisticsDB()

    # Project
    ps = stats.getProjectStats('test')
    ps.successes += 1
    ps.first = getLocalNow()
    stats.putProjectStats(ps)
    if len(sys.argv) > 1:
        stats.delProjectStats(ps)
    print ("Project")
    ps.dump()

    sys.exit()

    # Workspace
    ws = stats.getWorkspaceStats('test')
    ws.successes += 1
    stats.putWorkspaceStats(ws)
    if len(sys.argv) > 1:
        stats.delWorkspaceStats(ws)
    print ("Workspace")
    ws.dump()

    # Module
    ms = stats.getModuleStats('test')
    ms.successes += 1
    stats.putModuleStats(ms)
    if len(sys.argv) > 1:
        stats.delModuleStats(ms)
    print ("Module")
    ms.dump()

    # Repository
    rs = stats.getRepositoryStats('test')
    rs.successes += 1
    stats.putRepositoryStats(rs)
    if len(sys.argv) > 1:
        stats.delRepositoryStats(rs)
    print ("Repository")
    rs.dump()

