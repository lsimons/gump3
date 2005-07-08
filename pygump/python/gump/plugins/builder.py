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

"""Provides an abstract plugin for Command processing with subclasses."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import os
import sys
from os.path import abspath, join, isfile

from gump.model import Script, Error, Project, Ant, Dependency
from gump.model.util import get_project_directory
from gump.plugins import AbstractPlugin
from gump.util.executor import Popen, PIPE, STDOUT

class BuilderPlugin(AbstractPlugin):
    """Abstract class for creating plugins that handle the execution of Commands.

    To create a subclass, override __init__, then call it from the subclass with
    the method to call."""
    def __init__(self, workdir, log, cmd_clazz, method):
        """Create a new builder. Arguments:
        
          -- workdir = the directory in which to perform the command
          -- log = the Logger instance for debugging
          -- cmd_clazz = the Command subclass the plugin handles
          -- method = the python method (which must be a class method on
             the subclass) to call. It will be provided with a Project
             instance and with the relevant Command instance to process"""
        self.workdir = workdir
        self.log = log
        self.cmd_clazz = cmd_clazz
        self.method = method             

    def visit_project(self, project):
        """Dispatch for each matching command (matching by class type) """        
        assert isinstance(project, Project)
        self.log.debug("Visit %s looking for %s" % (project,self.cmd_clazz))
        for command in [command for command in project.commands if isinstance(command,self.cmd_clazz)]:
            self.log.debug("Perform %s on %s" % (command, project))
            self.method(project, command)
            
class ScriptBuilderPlugin(BuilderPlugin):
    """Execute all "script" commands for all projects."""
    def __init__(self, workdir, log):
        BuilderPlugin.__init__(self, workdir, log, Script, self._do_script)  
        
    def _do_script(self, project, script):
        # NOTE: no support for basedir="", an undocumented feature in gump2        
        assert isinstance(project, Project)
        projectpath = get_project_directory(self.workdir,project)
        
        scriptfile = abspath(join(projectpath, script.name))
        
        # No extension is ok, otherwise guess at one, platform appropriately
        if not isfile(scriptfile):
            if sys.platform == "win32":
                scriptfile += ".bat"
            else:
                scriptfile += ".sh"
            
            if not isfile(scriptfile):
                raise Error, "No script '%s' found!" % scriptfile
        
        self.log.debug("Scriptfile seems to be %s" % scriptfile)
        args = []
        args.append(scriptfile)
        args.extend(script.args)
        cmd = Popen(args,shell=True,cwd=projectpath,stdout=PIPE,stderr=STDOUT,env=project.env)
        
        script.build_log = cmd.communicate()[0]
        script.build_exit_status = cmd.wait()

