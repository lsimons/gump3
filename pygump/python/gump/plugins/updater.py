#!/usr/bin/env python
#
# Copyright 2005 The Apache Software Foundation
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

"""This preprocessor handles checkouts and updates from cvs and svn."""

__copyright__ = "Copyright (c) 2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import os
import commands

from gump.plugin import AbstractPlugin
from gump.model import CvsRepository, SvnRepository

UPDATE_TYPE_CHECKOUT="checkout"
UPDATE_TYPE_UPDATE="update"

class ModuleUpdater(AbstractPlugin):
    def __init__(self, workdir):
        self.workdir = workdir

    def visit_repository(self, repository):
        repopath = self.get_repo_path()
        if not os.path.exists(repopath):
            os.mkdir(repopath)

    def visit_module(self, module):
        modulepath = self.get_module_path()
        if not os.path.exists(modulepath):
            os.mkdir(modulepath)
            
    def get_repo_path(self, repository):
        return os.path.join(self.workdir, repository.name)

    def get_module_path(self, module):
        return os.path.join(self.get_repo_path(), module.name)

class CvsUpdater(ModuleUpdater):
    def __init__(self, workdir):
        ModuleUpdater.__init__(self, workdir)
    
    def visit_repository(self, repository):
        if isinstance(repository, CvsRepository):
            ModuleUpdater.visit_repository(self, repository)
    
    def visit_module(self, module):
        if not isinstance(repository, CvsRepository): return

        ModuleUpdater.visit_module(self, module)

        modulepath = self.get_module_path()
        current = os.path.curdir
        os.chdir(modulepath)
        cvsdir = os.path.join(modulepath, 'CVS')
        if not os.path.exists(cvsdir):
            self.checkout(module)
        else:
            self.update(module)
        os.chdir(current)
    
    def checkout(self, module, modulepath):
        repository = module.repository.to_url()
        cmd = 'cvs -d %s checkout -P %s .' % (repository, module.name)
        
        (status, output) = commands.getstatusoutput(cmd)
        module.update_log = output
        module.update_exit_status = status
        module.update_type = UPDATE_TYPE_CHECKOUT
    
    def update(self, module, modulepath):
        cmd = 'cvs up -Pd'

        (status, output) = commands.getstatusoutput(cmd)
        module.update_log = output
        module.update_exit_status = status
        module.update_type = UPDATE_TYPE_UPDATE

class SvnUpdater(ModuleUpdater):
    def __init__(self, workdir):
        ModuleUpdater.__init__(self, workdir)
    
    def visit_repository(self, repository):
        if isinstance(repository, SvnRepository):
            ModuleUpdater.visit_repository(self, repository)
    
    def visit_module(self, module):
        if not isinstance(repository, SvnRepository): return

        ModuleUpdater.visit_module(self, module)

        modulepath = self.get_module_path()
        current = os.path.curdir
        os.chdir(modulepath)
        svndir = os.path.join(modulepath, '.svn')
        if not os.path.exists(svndir):
            self.checkout(module)
        else:
            self.update(module)
        os.chdir(current)
    
    def checkout(self, module, modulepath):
        repository = module.repository.url + '/' + module.path
        cmd = 'svn checkout %s .' % repository
        
        (status, output) = commands.getstatusoutput(cmd)
        module.update_log = output
        module.update_exit_status = status
        module.update_type = UPDATE_TYPE_CHECKOUT
    
    def update(self, module, modulepath):
        cmd = 'svn up'

        (status, output) = commands.getstatusoutput(cmd)
        module.update_log = output
        module.update_exit_status = status
        module.update_type = UPDATE_TYPE_UPDATE
