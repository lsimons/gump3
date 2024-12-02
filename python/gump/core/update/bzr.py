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

def setup_common_parameters(module, cmd):
    if should_be_quiet(module):    
        cmd.addParameter('-q')
    elif module.isDebug():
        cmd.addParameter('-v')

URL_REGEX = re.compile(r'^\s*parent branch:\s+(.*)\s*$', re.MULTILINE | re.UNICODE)

###############################################################################
# Classes
###############################################################################

class BzrUpdater(ScmUpdater):
    """
    Updater for Bazaar
    """
    
    def __init__(self, run):
        ScmUpdater.__init__(self, run)


    def getCheckoutCommand(self, module):
        """
            Build the appropriate bzr command for branch
        """
        log_repository_and_url(module, 'bzr')
        cmd = Cmd('bzr', 'update_' + module.getName(), 
                  module.getWorkspace().getSourceControlStagingDirectory())
        cmd.addParameter('branch')
        setup_common_parameters(module, cmd)
        cmd.addParameter(module.getScm().getRootUrl())
        cmd.addParameter(module.getName())
        return cmd

    def getUpdateCommand(self, module):
        """
            Build the appropriate bzr command for merge
        """
        log_repository_and_url(module, 'bzr')
        cmd = Cmd('bzr', 'update_' + module.getName(), 
                  module.getSourceControlStagingDirectory())
        cmd.addParameter('merge')
        setup_common_parameters(module, cmd)
        return cmd

    def workspaceMatchesModule(self, module):
        """
            Run bzr info to see whether the URL matches
        """
        return match_workspace_template(module, 'bzr info',
                                        lambda result:
                                            extract_URL(result, URL_REGEX,
                                                        'bzr info'),
                                        module.getScm().getRootUrl())
