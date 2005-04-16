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

from gump.model import Mkdir
from gump.model import Rmdir
from gump.model import Error
from gump.model.util import get_project_directory
from gump.plugins import AbstractPlugin

import os
import shutil

class MkdirBuilderPlugin(AbstractPlugin):
    """Execute all "mkdir" commands for all projects."""
    def __init__(self, workdir):
        self.workdir = workdir
        
    def _do_mkdir(self, project, directory):
        projectpath = get_project_directory(self.workdir,project)
        dirpath = os.path.abspath(os.path.join(projectpath,directory))
        if not dirpath.startswith(projectpath):
            raise Error, "Directory '%s' to be created not within project path '%s'!" % (directory, projectpath)
        
        if not os.path.isdir(dirpath):
            if os.path.exists(dirpath):
                raise Error, "Directory path '%s' to be created exists as a file!" % dirpath
            
            os.makedirs(dirpath)

    def visit_project(self, project):
        for command in [command for command in project.commands if isinstance(command,Mkdir)]:
            self._do_mkdir(project, command.directory)

class RmdirBuilderPlugin(AbstractPlugin):
    """Execute all "rmdir" commands for all projects."""
    def __init__(self, workdir):
        self.workdir = workdir
        
    def _do_rmdir(self, project, directory):
        projectpath = get_project_directory(self.workdir,project)
        dirpath = os.path.abspath(os.path.join(projectpath,directory))
        if not dirpath.startswith(projectpath):
            raise Error, "Directory '%s' to be deleted not within project path '%s'!" % (directory, projectpath)
        
        if os.path.exists(dirpath):
            if not os.path.isdir(dirpath):
                raise Error, "Directory path '%s' to be removed exists as a file!" % dirpath
            
            shutil.rmtree(dirpath)

    def visit_project(self, project):
        for command in [command for command in project.commands if isinstance(command,Rmdir)]:
            self._do_rmdir(project, command.directory)
