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

"""This module provides a single plugin, the Dynagumper, which
   is responsible for pushing data to the Dynagump database."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import platform
import os
import time
from urllib import quote

from gump.model import Dependency
from gump.model.util import check_failure, check_skip
from gump.model.util import get_failure_causes
from gump.plugins import AbstractPlugin
from gump.plugins.instrumentation import DEFAULT_TIME_FORMAT
from gump.util.sysinfo import amount_of_memory
from gump.util.sysinfo import amount_of_cpu_mhz
from gump.util.sysinfo import number_of_cpus

BASE_DESCRIPTOR_URI = ""

def get_host():
    (system, host, release, version, machine, processor) = platform.uname()
    return host

_build_id = 0
def set_build_id(project,timeformat):
    global _build_id
    (run_start, run_end, run_name) = get_run_data(project.module.repository.workspace,timeformat)
    run_uri = get_run_uri(project.module.repository.workspace, run_name)
    project.build_id = "%s:%s" % (run_uri, _build_id)
    _build_id = _build_id + 1

def get_build_id(project):
    return project.build_id

# TODO: maybe cache these calculations on the model?? This is going to be
# *a lot* of string operations

def get_workspace_uri(workspace):
    url = "%s%s/%s" % (BASE_DESCRIPTOR_URI, get_host(), workspace.name)
    return url

def get_run_data(workspace, timeformat):
    (year,mon,day,hour,min,sec,wday,yday,isdst) = time.strptime(workspace.run_start, timeformat)
    run_start = time.mktime((year,mon,day,hour,min,sec,wday,yday,isdst))
    run_name = "%04d%02d%02d%02d%02d" % (year,mon,day,hour,min)
    (year,mon,day,hour,min,sec,wday,yday,isdst) = time.strptime(workspace.run_end, timeformat)
    run_end = time.mktime((year,mon,day,hour,min,sec,wday,yday,isdst))
    return (run_start, run_end, run_name)

def get_run_uri(workspace, name):
    url = "%s@%s" % (get_workspace_uri(workspace), name)
    return url

def get_module_uri(module):
    url = "%s/%s" % (get_workspace_uri(module.repository.workspace), module.name)
    return url

def get_project_uri(project):
    url = "%s/%s" % (get_module_uri(project.module), project.name)
    return url

def get_project_version_uri(project,timeformat):
    (run_start, run_end, run_name) = get_run_data(project.module.repository.workspace,timeformat)
    url = "%s/%s" % (get_run_uri(project.module.repository.workspace, run_name), project.name)
    return url

class Dynagumper(AbstractPlugin):
    """
    Plugin to populate the DynaGump run metadata database. It should run
    in the post-processing stage only, after the object model has been fully
    decorated.
    
    In order to understand what this plugin does (or should do), it is important
    to look at both the complete gump object model as implemented in python code
    and at the SQL-based database model defined for Dynagump. The Dynagumper is
    "nothing more" than a mapping between those two.
    
    Further dependencies:
      - TimerPlugin that sets run_start on the workspace
      - TimerPlugin that sets work_start and work_end on the projects
        (can recover)
    """    
    def __init__(self, db, log, timeformat=DEFAULT_TIME_FORMAT):
        AbstractPlugin.__init__(self,log)
        """Set up the Dynagumper.

        Arguments:
            - db is the instance of gump.util.Database that we will be
              using for all our database calls.
            - log is an instance of logging.Logger that we barely use
              (as the db can be responsible for logging all executed
              statements).
        """
        self.db = db
        self.log = log
        self.timeformat = timeformat
        
        (system, host, release, version, machine, processor) = platform.uname()
        self.host = host
        
    def initialize(self):
        self.add_host_to_db()
    
    def add_host_to_db(self):
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

    def _add_workspace_to_db(self, workspace):
        tablename = "workspaces"
        id = get_workspace_uri(workspace)
        
        cmd = "SELECT * FROM %s WHERE id = '%s';" % (tablename, id)
        (rows, result) = self.db.execute(cmd)
        
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
    
    def _add_run_to_db(self, workspace):
        tablename = "runs"
        (run_start, run_end, run_name) = get_run_data(workspace,self.timeformat)
        workspace_id = get_workspace_uri(workspace)
        run_id = get_run_uri(workspace, run_name)

        cmd = """INSERT INTO %s (id, start_time, end_time, workspace_id, name)
                     VALUES ('%s', FROM_UNIXTIME(%s), FROM_UNIXTIME(%s), '%s', '%s')""" \
                % (tablename, run_id, run_start, run_end, workspace_id, run_name)
        self.db.execute(cmd)
    
    def _add_module_to_db(self, module):
        tablename = "modules"
        
        id = get_module_uri(module)

        cmd = "SELECT * FROM %s WHERE id = '%s';" % (tablename, id)
        (rows, result) = self.db.execute(cmd)
                
        # Store into database...
        if rows == 0:
            # Insert
            cmd = """INSERT INTO %s (name, description, id)
                     VALUES ('%s', '%s', '%s')""" \
                % (tablename, module.name, module.description, id)
        else:
            # Update
            cmd = """UPDATE %s SET description='%s',name='%s'
                     WHERE id = '%s';""" \
                % (tablename, module.description, module.name, id)
        self.db.execute(cmd)        
    
    def _add_project_to_db(self, project):
        tablename = "projects"
        
        id = get_project_uri(project)
        module_id = get_module_uri(project.module)

        cmd = "SELECT * FROM %s WHERE id = '%s';" % (tablename, id)
        (rows, result) = self.db.execute(cmd)
                
        # Store into database...
        if rows == 0:
            # Insert
            cmd = """INSERT INTO %s (name, module_id, id)
                     VALUES ('%s', '%s', '%s')""" \
                % (tablename, project.name, module_id, id)
        else:
            # Update
            cmd = """UPDATE %s SET module_id='%s',name='%s'
                     WHERE id = '%s';""" \
                % (tablename, module_id, project.name, id)
        self.db.execute(cmd)
    
        # Gather optional data
        if hasattr(project,'description'):
            description = project.description
            cmd = """UPDATE %s SET description='%s' WHERE id = '%s';"""
            self.db.execute(cmd)
        
    def _add_project_version_to_db(self, project):
        tablename = "project_versions"
        
        id = get_project_version_uri(project,self.timeformat)
        project_id = get_project_uri(project)

        cmd = """INSERT INTO %s (id, project_id)
                VALUES ('%s', '%s')""" \
            % (tablename, id, project_id)
        self.db.execute(cmd)

    def _add_project_dependencies_to_db(self, project):
        tablename = "project_dependencies"
        cmd = """INSERT INTO """ + tablename + """ (dependee, dependant)
                VALUES ('%s', '%s')"""
        for relationship in project.dependencies:
            dependee = get_project_version_uri(project,self.timeformat)
            dependency = get_project_version_uri(relationship.dependency,self.timeformat)
            self.db.execute( cmd % (dependee, dependency))

    def _add_cause_to_db(self, project, problematic_dependency):
        tablename = "causes"
        build_id = get_build_id(project)
        cause_id = get_project_version_uri(problematic_dependency.dependency, self.timeformat)
        
        cmd = """INSERT INTO %s (build_id, cause_id)
                VALUES ('%s', '%s')""" \
            % (tablename, build_id, cause_id)
        self.db.execute(cmd)
        
    def _add_result_to_db(self, project):
        tablename = "builds"
        state = 0
        if check_skip(project):
            state = 2

        if check_failure(project):
            state = 1
            first_problem = get_failure_causes(project)[0]
            if isinstance(first_problem, Dependency):
                state = 2
                self._add_cause_to_db(project, first_problem)
        
        id = get_project_version_uri(project,self.timeformat)
        (run_start, run_end, run_name) = get_run_data(project.module.repository.workspace,self.timeformat)
        run_id = get_run_uri(project.module.repository.workspace,run_name)
        build_id = get_build_id(project)

        work_start = getattr(project, "work_start", project.module.repository.workspace.run_start)
        work_start = time.strptime(work_start, self.timeformat)
        work_start = time.mktime(work_start)
        
        work_end = getattr(project, "work_end", project.module.repository.workspace.run_end)
        work_end = time.strptime(work_end, self.timeformat)
        work_end = time.mktime(work_end)

        cmd = """INSERT INTO %s (id, run_id, project_version_id, start_time, end_time, result, log)
                     VALUES ('%s', '%s', '%s', FROM_UNIXTIME(%s), FROM_UNIXTIME(%s), '%s', '%s')""" \
                % (tablename, build_id, run_id, id, work_start, work_end, state, "Log saving still a TODO!") # TODO
        self.db.execute(cmd)

    def visit_workspace(self, workspace):
        self._add_workspace_to_db(workspace)
        self._add_run_to_db(workspace)
    
    def visit_module(self, module):    
        self._add_module_to_db(module)
    
    def visit_project(self, project):
        set_build_id(project,self.timeformat)
        self._add_project_to_db(project)
        self._add_project_version_to_db(project)
        self._add_project_dependencies_to_db(project)
        self._add_result_to_db(project)
