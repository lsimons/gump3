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

import os
import sys
from os.path import abspath, join, isfile

from gump.model import Script, Error
from gump.model.util import get_project_directory
from gump.plugins import AbstractPlugin
from gump.util.executor import Popen, PIPE, STDOUT

class ScriptBuilderPlugin(AbstractPlugin):
    """Execute all "script" commands for all projects."""
    def __init__(self, workdir):
        self.workdir = workdir
        
    def _do_script(self, project, script):
        # NOTE: no support for basedir="", an undocumented feature in gump2
        projectpath = get_project_directory(self.workdir,project)
        
        scriptfile = abspath(join(projectpath, script.name))
        if not isfile(scriptfile):
            if sys.platform == "win32":
                scriptfile += ".bat"
            else:
                scriptfile += ".sh"
            
            if not isfile(scriptfile):
                raise Error, "No script '%s' found!" % scriptfile
        
        args = [scriptfile] + script.args
        cmd = Popen(args,shell=True,cwd=projectpath,stdout=PIPE,stderr=STDOUT)
        
        script.build_log = cmd.communicate()[0]
        script.build_exit_status = cmd.wait()

    def visit_project(self, project):
        for command in [command for command in project.commands if isinstance(command,Script)]:
            self._do_script(project, command)
