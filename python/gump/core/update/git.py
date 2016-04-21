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
from gump.core.update.scmupdater import match_workspace_template, ScmUpdater, \
    should_be_quiet, log_repository_and_url, extract_URL
from gump.util.process.command import Cmd, getCmdFromString
from gump.util.process.launcher import execute
from gump.util.tools import tailFileToString

def maybe_make_quiet(module, cmd):
    if should_be_quiet(module):    
        cmd.addParameter('--quiet')

BRANCH_REGEX = re.compile('^\* (.*)$', re.MULTILINE | re.UNICODE)

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

        # Setting core.logAllRefUpdates=false disables reflog support,
        # so that subsequent updates do not waste time updating the
        # reflog file, .git/logs/refs/remotes/origin/master.

        cmd = Cmd('git', 'update_' + module.getName(), 
                  module.getWorkspace().getSourceControlStagingDirectory())
        cmd.addParameter('-c')
        cmd.addParameter('core.logallrefupdates=false')
        cmd.addParameter('clone')
        maybe_make_quiet(module, cmd)
        cmd.addParameter('--recursive')
        cmd.addParameter('--branch')
        cmd.addParameter(module.getScm().getBranch())
        cmd.addParameter(module.getScm().getRootUrl())
        cmd.addParameter(module.getName())
        return cmd

    def getUpdateCommand(self, module):
        """
            Build the appropriate GIT fetch command that pulls changes
            from remote repository.
            This command updates origin/branchName. The local branch is
            updated by 'git reset --hard' that is executed later.
        """
        log_repository_and_url(module, 'git')

        # Typical output from this command when --quiet flag is not used:
        #
        # - If there was an update:
        #  From git://github.com/openssl/openssl
        #     e0e920b..a043d0b  master     -> origin/master
        #
        # - If there was no update:
        # No output.
        #
        # Seeing repository URL is useful, but most of time there
        # will be no output.
        #
        # The URL can be reliably obtained elsewhere (from configuration)
        # thus I think that the use of --quiet flag by default is justified.

        refspec = '+refs/heads/' + module.getScm().getBranch() \
                + ':refs/remotes/origin/' + module.getScm().getBranch()

        cmd = Cmd('git', 'update_' + module.getName(), 
                  module.getSourceControlStagingDirectory())
        cmd.addParameter('fetch')
        maybe_make_quiet(module, cmd)
        cmd.addParameter('--no-tags')
        cmd.addParameter('origin')
        cmd.addParameter(refspec)
        return cmd

    def workspaceMatchesModule(self, module):
        """
            Run git branch and git config remote.origin.url
            to see whether the branch and URL match
        """
        return (False, 'Unconditionally forcing a fresh working copy. This is a temporary solution to clean stale checkouts and to update configuration of git. 2016-04-22.')

#
#       cmd = getCmdFromString('git branch',
#                              'check_workspace_branch_' + module.getName(), 
#                              module.getSourceControlStagingDirectory())
#       result = execute(cmd)
#
#       if not result.isOk():
#           return (False, 'git branch returned ' + str(result.exit_code))
#       elif not result.hasOutput():
#           return (False, 'git branch didn\'t return any output.')
#
#       current_branch = extract_URL(result, BRANCH_REGEX, 'git branch')
#       if module.getScm().getBranch() != current_branch:
#           return (False, 'Expected branch \'' + module.getScm().getBranch() \
#                       + '\' but working copy was \'' + current_branch + '\'')
#
#       return match_workspace_template(module, 'git config remote.origin.url',
#                                       lambda result:
#                                           tailFileToString(result.getOutput(),
#                                                            1).rstrip())

    def getPostProcessCommands(self, module, isUpdate):
        """
        Run git reset --hard and git submodule update --init if this
        has been an update.
        If it has been a clone command just before, its recursive flag
        will already have taken care of everything.
        """
        if isUpdate:

            # Typical output from this 'git reset --hard' command when
            # --quiet flag is not used (using openssl project as an example):
            #
            #  HEAD is now at a043d0b BIO socket connect failure was not handled correctly.
            #
            # That line can be preceded by several lines of progress output
            # such as
            #
            #  Checking out files:  28% (646/2237)   
            #
            # but that is rare. It happens only when there are hundreds of
            # changed files.
            #
            # This information is useful: it shows what source code is being
            # built by Gump, and it is short.
            #
            # I see no need to suppress it with --quiet,
            # thus maybe_make_quiet() call below is commented-out.

            rst = Cmd('git', 'reset_hard_' + module.getName(), 
                      module.getSourceControlStagingDirectory())
            rst.addParameter('reset')
            rst.addParameter('--hard')
            # maybe_make_quiet(module, rst)
            rst.addParameter('origin/' + module.getScm().getBranch())

            subs = Cmd('git', 'submodule_update_' + module.getName(), 
                      module.getSourceControlStagingDirectory())
            subs.addParameter('submodule')
            maybe_make_quiet(module, subs)
            subs.addParameter('update')
            subs.addParameter('--init')
            subs.addParameter('--recursive')
            return [rst, subs]
        return []
