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

"""This module defines contracts closely related to the object model."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

from os.path import abspath
from os.path import join

def get_project_directory(workdir, project):
    """Determine the base directory for a project."""
    return get_module_directory(workdir, project.module)

def get_module_directory(workdir, module):
    """Determine the base directory for a module."""
    return join(get_repository_directory(workdir,module.repository),module.name)

def get_repository_directory(workdir, repository):
    """Determine the base directory for a repository."""
    return join(get_workspace_directory(workdir,repository.workspace),repository.name)

def get_workspace_directory(workdir, workspace):
    """Determine the base directory for a workspace."""
    return abspath(join(workdir,workspace.name))
