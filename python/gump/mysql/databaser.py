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
    Stash in Database
"""

import time
import os
import sys

import MySQLdb
import MySQLdb.cursors

from gump import log
from gump.run.gumprun import *
import gump.run.actor

class Databaser(gump.run.actor.AbstractRunActor):
    
    def __init__(self,run):              
        gump.run.actor.AbstractRunActor.__init__(self,run)    
        
    def processOtherEvent(self,event):   
        pass
                      
    def processWorkspace(self):
        """
        Add information about the workspace to the database 
        """
        pass
    
    def processModule(self,module):    
        """
        Add information about the module to the database
        """
        conn=None
        helper=None
        try:
            conn=self.getConnected()
            helper=gump.utils.mysql.DbHelper(conn)
            
            # Prepare the data
            settings = {}
            
            settings['run_id'] = "'" + self.run.getRunHexGuid() + "'"  
            settings['module_name']="'" + module.getName() + "'"
            settings['state']=module.getState()
            settings['reason']=module.getReason()
            
            if module.hasCause():
                settings['cause']="'" + module.getCause().getName() + "'"
                
            #settings['start']=
            #settings['end']=
            
            helper.insert('module_run',settings)
            
        finally:
            if conn: conn.close()
    
    def processProject(self,project):    
        """
        Add information about the project to the database 
        """
        conn=None
        helper=None
        try:
            conn=self.getConnected()
            helper=gump.utils.mysql.DbHelper(conn)
            
            # Prepare the data
            settings = {}
            
            settings['run_id'] = "'" + self.run.getRunHexGuid() + "'"
            settings['project_name']="'" + project.getName() + "'"
            settings['state']=project.getState()
            settings['reason']=project.getReason()
            
            if project.hasCause():
                settings['cause']="'" + project.getCause().getName() + "'"
                
            #settings['start']=
            #settings['end']=
            
            helper.insert('project_run',settings)
            
        finally:
            if conn: conn.close()
        
        
    def getConnected(self):
        """
        Get a database connection.
        """
        dbInfo=self.workspace.getDatabaseInformation()
                
        return MySQLdb.Connect(
                    host=dbInfo.getHost(), 
                    user=dbInfo.getUser(),
                    passwd=dbInfo.getPasswd(), 
                    db=dbInfo.getDatabase(),
                    compress=1,
                    cursorclass=MySQLdb.cursors.DictCursor)
        
           