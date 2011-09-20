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

from gump.core.update.scmupdater import match_workspace_template, ScmUpdater, \
    should_be_quiet, log_repository_and_url
from gump.util.process.command import Cmd
from gump.util.tools import tailFileToString

def maybe_make_quiet(module, cmd):
    if should_be_quiet(module):    
        cmd.addParameter('--quiet')

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
        log_repository_and_url(module, 'git')
        cmd = Cmd('git', 'update_' + module.getName(), 
                  module.getWorkspace().getSourceControlStagingDirectory())
        cmd.addParameter('clone')
        maybe_make_quiet(module, cmd)
        cmd.addParameter(module.getScm().getRootUrl())
        cmd.addParameter(module.getName())
        return cmd

    def getUpdateCommand(self, module):
        """
            Build the appropriate GIT command for pull
        """
        log_repository_and_url(module, 'git')
        cmd = Cmd('git', 'update_' + module.getName(), 
                  module.getSourceControlStagingDirectory())
        cmd.addParameter('pull')
        maybe_make_quiet(module, cmd)
        cmd.addParameter(module.getScm().getRootUrl())
        return cmd

    def workspaceMatchesModule(self, module):
        """
            Run git config remote.origin.url to see whether the URL matches
        """
        return match_workspace_template(module, 'git config remote.origin.url',
                                        lambda result:
                                            tailFileToString(result.getOutput(),
                                                             1).rstrip())
