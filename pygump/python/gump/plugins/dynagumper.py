#!/usr/bin/env python

# Copyright 2004-2005 The Apache Software Foundation
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

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import platform
import os

from gump.plugins import AbstractPlugin
from gump.util.sysinfo import amount_of_memory
from gump.util.sysinfo import amount_of_cpu_mhz
from gump.util.sysinfo import number_of_cpus

class Dynagumper(AbstractPlugin):
    """
    Populate the DynaGump run metadata database.
    """    
    def __init__(self, db, log):
        AbstractPlugin.__init__(self,log)
        """Set up the Dynagumper.

        Arguments:
            - db is an instance of a gump.util.Database.
            - log is an instance of logging.Logger.
        """
        self.db = db
        self.log = log
        
    def initialize(self):
        self.ensureThisHostIsInDatabase()
    
    def ensureThisHostIsInDatabase(self):
        """Adds information about this server to the hosts table."""
        (system, host, release, version, machine, processor) = platform.uname()
        tablename = "hosts"
        
        cmd = "SELECT * FROM %s WHERE address = '%s' AND name = '%s';"
        (rows, result) = self.db.execute(cmd)
        if rows == 0:
            memory = amount_of_memory()
            mhz = amount_of_cpu_mhz()
            cpus = number_of_cpus()
            
            description = "%s (%s,%s,%s,%s,%s)" % (host, system, release, version, machine, processor)
            cmd = """INSERT INTO %s (address, name, cpu_arch, cpu_number, cpu_speed_Mhz, memory, description)
                     VALUES ('%s', '%s', '%s', %s, %s, %s, '%s')""" \
                % (tablename, host, host, processor, cpus, mhz, memory, description)
            self.db.execute(cmd)
    
    def visit_workspace(self, workspace):
        """Add information about the workspace to the database."""
        pass
        #TODO do the actual work right here...
    
    def visit_module(self, module):    
        """Add information about a module to the database."""
        pass
        #TODO do the actual work
    
    def visit_project(self, project):    
        """Add information about a project to the database."""
        tablename = "projects"
        startdate = project.startdate
        enddate = project.enddate
        name = project.name
        
        cmd = "INSERT INTO %s (project_name, start_date, end_date) VALUES ('%s', '%s', '%s')" \
            % (tablename, name, startdate, enddate)
        #TODO make query fit database model
        # self.db.execute(cmd)
        #TODO do the actual work right here...
