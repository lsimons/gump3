#!/usr/bin/python


# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from gump import log
from gump.core.model.workspace import Cmd
from gump.core.update.scmupdater import ScmUpdater

def log_repository_and_url(module):
    repository = module.repository
    url = module.getScm().getRootUrl()
    log.debug("GIT URL: [" + url + "] on Repository: " + \
                  repository.getName())

                  
###############################################################################
# Classes
###############################################################################

class GitUpdater(ScmUpdater):
    """
    Updater for GIT
    """
    
    def __init__(self, run):
        ScmUpdater.__init__(self, run)


    def getCheckoutCommand(self, module):
        """
            Build the appropriate GIT command for clone
        """
        log_repository_and_url(module)
        cmd = Cmd('git-clone', 'update_' + module.getName(), 
                  module.getWorkspace().getSourceControlStagingDirectory())
        self.maybeMakeQuiet(module, cmd)
        cmd.addParameter(module.getScm().getRootUrl())
        cmd.addParameter(module.getName())
        return cmd

    def getUpdateCommand(self, module):
        """
            Build the appropriate GIT command for pull
        """
        log_repository_and_url(module)
        cmd = Cmd('git-pull', 'update_' + module.getName(), 
                  module.getSourceControlStagingDirectory())
        self.maybeMakeQuiet(module, cmd)
        return cmd

    def maybeMakeQuiet(self, module, cmd):
        if self.shouldBeQuiet(module):    
            cmd.addParameter('--quiet')
