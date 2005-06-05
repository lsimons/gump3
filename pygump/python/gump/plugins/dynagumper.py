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
        
        (system, host, release, version, machine, processor) = platform.uname()
        self.host = host
        
    def initialize(self):
        self.storeHost()
    
    def storeHost(self):
        """Adds information about this server to the hosts table."""
        (system, host, release, version, machine, processor) = platform.uname()
        tablename = "hosts"
        
        cmd = "SELECT * FROM %s WHERE address = '%s' AND name = '%s';" % (tablename, host, host)
        (rows, result) = self.db.execute(cmd)
        
        # Gather information
        memory = amount_of_memory()
        mhz = amount_of_cpu_mhz()
        cpus = number_of_cpus()
        description = "%s (%s,%s,%s,%s,%s)" % (host, system, release, version, machine, processor)

        # Store into database...
        if rows == 0:
            # Insert
            cmd = """INSERT INTO %s (address, name, cpu_arch, cpu_number, cpu_speed_Mhz, memory_Mb, description)
                     VALUES ('%s', '%s', '%s', %s, %s, %s, '%s')""" \
                % (tablename, host, host, processor, cpus, mhz, memory, description)
        else:
            # Update
            cmd = """UPDATE %s SET cpu_arch='%s',cpu_number=%s,cpu_speed_Mhz=%s,memory_Mb=%s,description='%s'
                     WHERE address = '%s' AND name = '%s';""" \
                % (tablename, processor, cpus, mhz, memory, description, host, host)
        self.db.execute(cmd)
    
    def visit_workspace(self, workspace):
        """Add information about the workspace to the database."""
        tablename = "workspaces"
        
        cmd = "SELECT * FROM %s WHERE name = '%s' AND host = '%s';" % (tablename, workspace.name, self.host)
        (rows, result) = self.db.execute(cmd)
        
        #TODO For want of any other ID...
        id = 'gump://%s@%s' % (workspace.name, self.host)
        
        description = None
        if hasattr(workspace,'description'): description = workspace.description
        
        # Store into database...
        if rows == 0:
            # Insert
            cmd = """INSERT INTO %s (id, name, host, description)
                     VALUES ('%s', '%s', '%s', '%s')""" \
                % (tablename, id, workspace.name, self.host, description)
        else:
            # Update
            cmd = """UPDATE %s SET id='%s',description='%s'
                     WHERE name = '%s' AND host = '%s';""" \
                % (tablename, id, description, workspace.name, self.host)
        self.db.execute(cmd)
    
    def visit_module(self, module):    
        """Add information about a module to the database."""
        tablename = "modules"
        
        cmd = "SELECT * FROM %s WHERE name = '%s';" % (tablename, module.name)
        (rows, result) = self.db.execute(cmd)
                
        # Store into database...
        if rows == 0:
            # Insert
            cmd = """INSERT INTO %s (name, description, descriptor)
                     VALUES ('%s', '%s', '%s')""" \
                % (tablename, module.name, module.description, module.url)
        else:
            # Update
            cmd = """UPDATE %s SET description='%s',descriptor='%s'
                     WHERE name = '%s';""" \
                % (tablename, module.description, module.url, module.name)
        self.db.execute(cmd)
    
    def visit_project(self, project):    
        """Add information about a project to the database."""
        tablename = "projects"
        startdate = project.run_start
        enddate = project.run_end
        name = project.name
        
        cmd = "SELECT * FROM %s WHERE name = '%s';" % (tablename, project.name)
        (rows, result) = self.db.execute(cmd)
                
        # Gather data
        description = None
        if hasattr(project,'description'): description = project.description
        descriptor=None
        if hasattr(project,'url'): descriptor = project.url
        
        # Store into database...
        if rows == 0:
            # Insert
            cmd = """INSERT INTO %s (name, description, module, descriptor)
                     VALUES ('%s', '%s', '%s', '%s')""" \
                % (tablename, project.name, description, project.module.name, descriptor)
        else:
            # Update
            cmd = """UPDATE %s SET description='%s',module='%s',descriptor='%s'
                     WHERE name = '%s';""" \
                % (tablename, description, project.module.name, descriptor, project.name)
        self.db.execute(cmd)
