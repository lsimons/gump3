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

from gump import log
from gump.core.run.gumprun import *
import gump.core.run.actor

class Dynagumper(gump.core.run.actor.AbstractRunActor):
    """
    Populate the DynaGump run metadata database.
    """
    
    def __init__(self,run):              
        gump.core.run.actor.AbstractRunActor.__init__(self,run)    
        self.dbInfo=self.workspace.getDatabaseInformation()
        
    def processOtherEvent(self,event):   
        conn=None
        helper=None
        try:
            conn=self.getConnected()
            # do the actual work right here...
            log.warning('dynagumper.py line 42: need to implement event processing')
        finally:
            if conn: conn.close()
                      
    def processWorkspace(self):
        """
        Add information about the workspace to the database.
        """
        conn=None
        helper=None
        try:
            conn=self.getConnected()
            # do the actual work right here...
            log.warning('dynagumper.py line 56: need to implement workspace event processing')
        finally:
            if conn: conn.close()
    
    def processModule(self,module):    
        """
        Add information about the module to the database.
        """
        conn=None
        helper=None
        try:
            conn=self.getConnected()
            # do the actual work
            log.warning('dynagumper.py line 68: need to implement module event processing')
        finally:
            if conn: conn.close()
    
    def processProject(self,project):    
        """
        Add information about the project to the database.
        """
        conn=None
        helper=None
        try:
            conn=self.getConnected()
            # do the actual work right here...
            log.warning('dynagumper.py line 82: need to implement project event processing')
        finally:
            if conn: conn.close()
        
        
    def getConnected(self):
        """
        Get a database connection.
        """
                
        return MySQLdb.Connect(
                    host=self.dbInfo.getHost(), 
                    user=self.dbInfo.getUser(),
                    passwd=self.dbInfo.getPasswd(), 
                    db=self.dbInfo.getDatabase(),
                    compress=1,
                    cursorclass=MySQLdb.cursors.DictCursor)
