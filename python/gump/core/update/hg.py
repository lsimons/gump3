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

import re
from gump.core.update.scmupdater import extract_URL, log_repository_and_url, \
    match_workspace_template, ScmUpdater, should_be_quiet
from gump.util.process.command import Cmd
from gump.util.process.launcher import execute

def setup_common_parameters(module, cmd):
    if should_be_quiet(module):    
        cmd.addParameter('-q')
    elif module.isDebug():
        cmd.addParameter('-v')

URL_REGEX = re.compile('^paths.default=(.*)\s*$', re.MULTILINE | re.UNICODE)

###############################################################################
# Classes
###############################################################################

class HgUpdater(ScmUpdater):
    """
    Updater for Mercurial
    """
    
    def __init__(self, run):
        ScmUpdater.__init__(self, run)


    def getCheckoutCommand(self, module):
        """
            Build the appropriate hg command for clone
        """
        log_repository_and_url(module, 'hg')
        cmd = Cmd('hg', 'update_' + module.getName(), 
                  module.getWorkspace().getSourceControlStagingDirectory())
        cmd.addParameter('clone')
        setup_common_parameters(module, cmd)
        cmd.addParameter(module.getScm().getRootUrl())
        cmd.addParameter(module.getName())
        return cmd

    def getUpdateCommand(self, module):
        """
            Build the appropriate hg command for pull if hg incoming
            indicates any changes
        """
        log_repository_and_url(module, 'hg')

        cmd = Cmd('hg', 'incoming_' + module.getName(), 
                  module.getSourceControlStagingDirectory())
        cmd.addParameter('incoming')
        setup_common_parameters(module, cmd)
        result = execute(cmd)

        if not result.isOk():
            module.addInfo('No updates')
            cmd = Cmd('echo', 'update_' + module.getName(), 
                      module.getSourceControlStagingDirectory())
            cmd.addParameter('hg incoming indicated no changes to pull')
        else:
            cmd = Cmd('hg', 'update_' + module.getName(), 
                  module.getSourceControlStagingDirectory())
        cmd.addParameter('pull')
        # update working copy
        cmd.addParameter('-u')
        setup_common_parameters(module, cmd)
        # pull everything, don't ask
        cmd.addParameter('-y')
        return cmd

    def workspaceMatchesModule(self, module):
        """
            Run hg showconfig to see whether the URL matches
        """
        return match_workspace_template(module, 'hg showconfig',
                                        lambda result:
                                            extract_URL(result, URL_REGEX,
                                                        'hg showconfig'),
                                        module.getScm().getRootUrl())
