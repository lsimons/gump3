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
import shutil

from gump.plugins import AbstractPlugin
from gump.model import CvsRepository, SvnRepository
from gump.model.util import get_repository_directory
from gump.model.util import get_module_directory

from gump.util.executor import Popen
from gump.util.executor import PIPE
from gump.util.executor import STDOUT

UPDATE_TYPE_CHECKOUT="checkout"
UPDATE_TYPE_UPDATE="update"

class ModuleUpdater(AbstractPlugin):
    def __init__(self, workdir):
        self.workdir = workdir

    def visit_repository(self, repository):
        repopath = get_repository_directory(self.workdir, repository)
        if not os.path.exists(repopath):
            os.makedirs(repopath)

    def visit_module(self, module):
        modulepath = get_module_directory(self.workdir, module)
        if not os.path.exists(modulepath):
            os.makedirs(modulepath)

class CvsUpdater(ModuleUpdater):
    def __init__(self, workdir):
        ModuleUpdater.__init__(self, workdir)
    
    def visit_repository(self, repository):
        if isinstance(repository, CvsRepository):
            ModuleUpdater.visit_repository(self, repository)
    
    def visit_module(self, module):
        if not isinstance(module.repository, CvsRepository): return

        ModuleUpdater.visit_module(self, module)

        repopath = get_repository_directory(self.workdir, module.repository)
        current = os.path.curdir
        modulepath = os.path.join(repopath, module.name)
        cvsdir = os.path.join(modulepath, 'CVS')
        if not os.path.exists(cvsdir):
            self.checkout(module, repopath)
        else:
            self.update(module, modulepath)
    
    def checkout(self, module, cwd):
        # no 'CVS', but there is a module dir. That could cause cvs to fail.
        # get rid of the contents...
        targetdir=os.path.join(cwd, module.name)
        if os.path.exists(targetdir):
            shutil.rmtree(targetdir)

        repository = module.repository.to_url()
        cvs = Popen(['cvs', '-q', '-d', repository, 'checkout', module.name], cwd=cwd, stdout=PIPE, stderr=STDOUT)
        module.update_log = cvs.communicate()[0]
        module.update_exit_status = cvs.wait()
        module.update_type = UPDATE_TYPE_CHECKOUT
    
    def update(self, module, cwd):
        cvs = Popen(['cvs', '-q', 'up', '-Pd'], cwd=cwd, stdout=PIPE, stderr=STDOUT)
        module.update_log = cvs.communicate()[0]
        module.update_exit_status = cvs.wait()
        module.update_type = UPDATE_TYPE_UPDATE

class SvnUpdater(ModuleUpdater):
    def __init__(self, workdir):
        ModuleUpdater.__init__(self, workdir)
    
    def visit_repository(self, repository):
        if isinstance(repository, SvnRepository):
            ModuleUpdater.visit_repository(self, repository)
    
    def visit_module(self, module):
        if not isinstance(module.repository, SvnRepository): return

        ModuleUpdater.visit_module(self, module)

        modulepath = get_module_directory(module)
        current = os.path.curdir
        os.chdir(modulepath)
        svndir = os.path.join(modulepath, '.svn')
        if not os.path.exists(svndir):
            self.checkout(module, modulepath)
        else:
            self.update(module, moduelpath)
        os.chdir(current)
    
    def checkout(self, module, cwd):
        repository = module.repository.url + '/' + module.path
        if not os.path.exists(cwd):
            os.makedirs(cwd)
        
        svn = Popen(['svn', 'checkout', repository, '.'], cwd=cwd, stdout=PIPE, stderr=STDOUT)
        module.update_log = svn.communicate()[0]
        module.update_exit_status = svn.wait()
        module.update_type = UPDATE_TYPE_CHECKOUT
    
    def update(self, module, cwd):
        svn = Popen(['svn', 'up'], cwd=cwd, stdout=PIPE, stderr=STDOUT)
        module.update_log = svn.communicate()[0]
        module.update_exit_status = svn.wait()
        module.update_type = UPDATE_TYPE_CHECKOUT
