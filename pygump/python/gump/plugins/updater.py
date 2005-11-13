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
from gump.util.sync import smart_sync

from gump.model.util import UPDATE_TYPE_CHECKOUT, UPDATE_TYPE_UPDATE

SYNC_EXCLUDES=[".gump-persist"]

class ModuleUpdater(AbstractPlugin):
    def __init__(self, log=None, cleanup=False):
        self.log = log
        self.cleanup = cleanup

    def visit_repository(self, repository):
        checkoutrepopath = get_repository_directory(repository, location="checkouts")
        buildrepopath = get_repository_directory(repository)
        
        if self.cleanup:
            if self.log:
                self.log.debug(
"Removing %s so that new checkouts will be fresh" % checkoutrepopath)
            shutil.rmtree(checkoutrepopath)
        
        if not os.path.exists(checkoutrepopath):
            os.makedirs(checkoutrepopath)
        if not os.path.exists(buildrepopath):
            os.makedirs(buildrepopath)

    def visit_module(self, module):
        checkoutmodulepath = get_module_directory(module, location="checkouts")
        buildmodulepath = get_module_directory(module)
        if not os.path.exists(checkoutmodulepath):
            os.makedirs(checkoutmodulepath)
        #DONT -- breaks "smart" sync... if not os.path.exists(buildmodulepath):
        #    os.makedirs(buildmodulepath)
        
        def onerror(*args, **kwargs):
            if self.log:
                self.log.error(
"Problem while syncing %s -> %s" % (checkoutmodulepath, buildmodulepath))
        
        smart_sync(checkoutmodulepath, buildmodulepath,
                   excludes=SYNC_EXCLUDES, cleanup=self.cleanup, onerror=onerror)
        

class CvsUpdater(ModuleUpdater):
    def __init__(self, log=None, cleanup=False):
        ModuleUpdater.__init__(self, log=log, cleanup=cleanup)
    
    def visit_repository(self, repository):
        if isinstance(repository, CvsRepository):
            ModuleUpdater.visit_repository(self, repository)
    
    def visit_module(self, module):
        if not isinstance(module.repository, CvsRepository): return

        repopath = get_repository_directory(module.repository, location="checkouts")
        modulepath = os.path.join(repopath, module.name)
        if not os.path.exists(modulepath):
            os.makedirs(modulepath)

        cvsdir = os.path.join(modulepath, 'CVS')
        if not os.path.exists(cvsdir):
            if self.log: self.log.debug("New CVS checkout in %s" % modulepath)
            self.checkout(module, repopath)
        else:
            if self.log: self.log.debug("CVS update in %s" % modulepath)
            self.update(module, modulepath)

        ModuleUpdater.visit_module(self, module)

    
    def checkout(self, module, cwd):
        # no 'CVS', but there is a module dir. That could cause cvs to fail.
        # get rid of the contents...
        targetdir=os.path.join(cwd, module.name)
        if os.path.exists(targetdir):
            shutil.rmtree(targetdir)

        repository = module.repository.to_url()
        cvs = Popen(['cvs', '-q', '-d', repository, 'checkout', module.name], \
                    cwd=cwd, stdout=PIPE, stderr=STDOUT)
        module.update_log = cvs.communicate()[0]
        module.update_exit_status = cvs.wait()
        module.update_type = UPDATE_TYPE_CHECKOUT
    
    def update(self, module, cwd):
        cvs = Popen(['cvs', '-q', 'up', '-Pd'], cwd=cwd, stdout=PIPE, stderr=STDOUT)
        module.update_log = cvs.communicate()[0]
        module.update_exit_status = cvs.wait()
        module.update_type = UPDATE_TYPE_UPDATE

class SvnUpdater(ModuleUpdater):
    def __init__(self, log=None, cleanup=False):
        ModuleUpdater.__init__(self, log=log, cleanup=cleanup)
    
    def visit_repository(self, repository):
        if isinstance(repository, SvnRepository):
            ModuleUpdater.visit_repository(self, repository)
    
    def visit_module(self, module):
        if not isinstance(module.repository, SvnRepository): return

        modulepath = get_module_directory(module, location="checkouts")
        if not os.path.exists(modulepath):
            os.makedirs(modulepath)
        svndir = os.path.join(modulepath, '.svn')
        if not os.path.exists(svndir):
            self.checkout(module, modulepath)
        else:
            svninfo = Popen(['svn', 'info', modulepath], stdout=PIPE,\
                            stderr=STDOUT).communicate()[0]
            currurl = None
            for line in svninfo.split('\n'):
                if line.startswith("URL: "):
                    currurl = line[5:].strip()
                    break
            if not currurl == module.repository.url + '/' + module.path:
                shutil.rmtree(modulepath)
                self.checkout(module, modulepath)
            else:
                self.update(module, modulepath)
    
        ModuleUpdater.visit_module(self, module)

    def checkout(self, module, cwd):
        if not os.path.exists(cwd):
            os.makedirs(cwd)
        
        repository = module.repository.url + '/' + module.path
        svn = Popen(['svn', 'checkout', repository, '.'], cwd=cwd, \
                    stdout=PIPE, stderr=STDOUT)
        module.update_log = svn.communicate()[0]
        module.update_exit_status = svn.wait()
        module.update_type = UPDATE_TYPE_CHECKOUT
    
    def update(self, module, cwd):
        svn = Popen(['svn', 'up'], cwd=cwd, stdout=PIPE, stderr=STDOUT)
        module.update_log = svn.communicate()[0]
        module.update_exit_status = svn.wait()
        module.update_type = UPDATE_TYPE_UPDATE
