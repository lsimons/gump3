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

__copyright__ = "Copyright (c) 2004 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import MySQLdb
import MySQLdb.cursors

import platform

from gump import log
from gump.core.run.gumprun import *
import gump.core.run.actor

class Dynagumper(gump.core.run.actor.AbstractRunActor):
    """
    Populate the DynaGump run metadata database.
    """
    
    def __init__(self,run,conn):
        gump.core.run.actor.AbstractRunActor.__init__(self,run)    
        self.conn = conn

    def _execute(self, cmd):
        cursor = self.conn.cursor()
        cursor.execute(cmd)
        #try:
        #    cursor = None    
        #    try:
        #        cursor = self.conn.cursor()
        #        try:
        #            cursor.execute(cmd)
        #        except Exception, details:
        #            log.error('SQL Error on [%s] : %s' % (cmd, details), exc_info=1)
        #    finally:
        #        if cursor: cursor.close()
        #except Exception, details:
        #    log.error('SQL Connection Error: %s' % (details), exc_info=1)
    
    def ensureThisHostIsInDatabase(self):
        (system, host, release, version, machine, processor) = platform.uname()
        tablename = "hosts"
        description = "%s (%s,%s,%s,%s,%s)" % (host, system, release, version, machine, processor)
        cmd = "INSERT INTO %s (address, name, cpu_arch, description) VALUES ('%s', '%s', '%s', '%s')" \
                % (tablename, host, host, processor, description)
        
        self._execute(cmd)
        
    def processOtherEvent(self,event):   
        # do the actual work right here...
        log.warning('dynagumper.py processOtherEvent(): need to implement event processing')
                      
    def processWorkspace(self):
        """
        Add information about the workspace to the database.
        """
        # do the actual work right here...
        self.ensureThisHostIsInDatabase()
        log.warning('dynagumper.py processWorkspace: need to implement workspace event processing')
    
    def processModule(self,module):    
        """
        Add information about the module to the database.
        """
        # do the actual work
        log.warning('dynagumper.py processModule: need to implement module event processing')
    
    def processProject(self,project):    
        """
        Add information about the project to the database.
        """
        # do the actual work right here...
        log.warning('dynagumper.py processProject: need to implement project event processing')
