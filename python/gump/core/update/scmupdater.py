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

import os.path
import StringIO

from gump import log

from gump.core.model.workspace import CommandWorkItem, \
    REASON_UPDATE_FAILED, STATE_FAILED, STATE_SUCCESS, WORK_TYPE_UPDATE
from gump.core.run.gumprun import RunSpecific
from gump.util.process.launcher import execute
from gump.util.tools import catFile, wipeDirectoryTree
from gump.util.process.command import getCmdFromString

def should_be_quiet(module):
    """
    Whether the configuration asks for a quiet update
    (it does so by default)
    """
    return not module.isDebug() \
        and not module.isVerbose() \
        and not module.getScm().isDebug() \
        and not module.getScm().isVerbose()

def match_workspace_template(module, cmd_string, extract_url,
                             expectedURL = None):
    """
    Template for the common run-a-command-and-extract-URL-from-output logic
    for workspaceMatchesModule Method of ScmUpdater
    """
    if not expectedURL:
        expectedURL = module.getScm().getRootUrl()

    cmd = getCmdFromString(cmd_string, 'check_workspace_' + module.getName(), 
                           module.getSourceControlStagingDirectory())

    result = execute(cmd)

    if not result.isOk():
        return (False, cmd_string + ' returned ' + str(result.exit_code))

    elif not result.hasOutput():
        return (False, cmd_string + ' didn\'t return any output.')

    actualURL = extract_url(result)
    return (expectedURL == actualURL, 'Expected URL \'' + expectedURL + \
                '\' but working copy was \'' + actualURL + '\'')

def log_repository_and_url(module, scmType):
    repository = module.repository
    url = module.getScm().getRootUrl()
    log.debug(scmType + " URL: [" + url + "] on Repository: " + \
                  repository.getName())

def extract_URL(result, regex, command):
    """
    Extracs the URL from result
    """
    stream = StringIO.StringIO()
    catFile(stream, result.getOutput())
    output = stream.getvalue()
    stream.close()
    match = regex.search(output)
    if not match:
        return 'Couldn\'t find URL in ' + command + ' output ' + output
    return match.group(1)

                  
###############################################################################
# Classes
###############################################################################
class ScmUpdater(RunSpecific):
    """
    Base class for a SCM specific updaters.

    Provides helpers and template method implementations.
    """

    def __init__(self, run):
        RunSpecific.__init__(self, run)

    #
    # "public" interface of ScmUpdater
    #

    def preview(self, module):
        """
        Supposed to preview what needs to be done.

        For most SCMs it doesn't say much and this method is never
        called during a normal Gump run.
        """
        (cmd, isUpdate) = self.getCommandAndType(module)
        if cmd:
            cmd.dump()

    def updateModule(self, module):
        """
        Performs a fresh check-out or an update of an existing wrokspace.
        """

        log.info('Perform ' + module.getScm().getScmType().displayName + \
                     ' Checkout/Update on #[' + `module.getPosition()` + \
                     '] : ' + module.getName())

        (cmd, isUpdate) = self.getCommandAndType(module)

        if cmd:
            if isUpdate:
                log.debug(module.getScm().getScmType().displayName + \
                              " Module Update : " + \
                              module.getName() + ", Repository Name: " + \
                              module.repository.getName())
            else:
                log.debug(module.getScm().getScmType().displayName + \
                              " Module Checkout : " + module.getName() + \
                              ", Repository Name: " + \
                              module.repository.getName())

            # Execute the command and capture results
            cmdResult = execute(cmd, module.getWorkspace().tmpdir)

            # Store this as work, on both the module and (cloned) on the repo
            work = CommandWorkItem(WORK_TYPE_UPDATE, cmd, cmdResult)
            module.performedWork(work)
            module.repository.performedWork(work.clone())

            if cmdResult.isOk():
                # Execute any postprocessing that may be required
                cmdPost = self.getPostProcessCommand(module, isUpdate)
                if cmdPost:
                    log.debug(module.getScm().getScmType().displayName + \
                              " Module PostProcess : " + \
                              module.getName() + ", Repository Name: " + \
                              module.repository.getName())
                    cmdResult = execute(cmdPost, module.getWorkspace().tmpdir)
                    work = CommandWorkItem(WORK_TYPE_UPDATE, cmdPost, cmdResult)
                    module.performedWork(work)
                    module.repository.performedWork(work.clone())

            # Update Context w/ Results
            if not cmdResult.isOk():
                log.error('Failed to checkout/update module: ' + module.name)
                module.changeState(STATE_FAILED, REASON_UPDATE_FAILED)
            else:
                module.changeState(STATE_SUCCESS)

            return module.okToPerformWork()

        log.error("Don't know how to to checkout/update module: " + \
                      module.name)
        module.changeState(STATE_FAILED, REASON_UPDATE_FAILED)
        return False

    #
    # helpers
    #

    def getCommandAndType(self, module):
        """
        Checks whether an update or a fresh checkout is needed and
        returns a command to perform the required action.

        Returns a tuple (command, isUpdate)
        """
        exists = os.path.exists(module.getSourceControlStagingDirectory())

        if exists:
            (matches, reason) = self.workspaceMatchesModule(module)
            if not matches:
                msg = 'The working copy \'' + \
                    module.getSourceControlStagingDirectory() + \
                    '\' doesn\'t match the module definition, reason: \'' + \
                    reason + '\'. Removing it.'
                log.warn(msg)
                module.addWarning(msg)
                wipeDirectoryTree(module.getSourceControlStagingDirectory(),
                                  False)
                exists = False

        cmd = None
        if exists:
            cmd = self.getUpdateCommand(module)
        else:
            cmd = self.getCheckoutCommand(module)
        return (cmd, exists)


    #
    # methods that should be overridden in subclasses
    #

    def getCheckoutCommand(self, module):
        """
        Create the command needed to obtain a fresh working copy.
        """
        return None

    def getUpdateCommand(self, module):
        """
        Create the command needed to update an existing working copy.
        """
        return None


    def workspaceMatchesModule(self, module):
        """
        Whether the working copy matches what the updater expects it to
        be - like being a working copy of the module's svn URL or
        CVS Root etc.

        Must return a tuple (matches, reason) with a bool indicating
        whether the workspace matches the module defintion and a reason
        string if it doesn't.

        This base implementation returns (True, '')
        """
        return (True, '')

    def getPostProcessCommand(self, module, isUpdate):
        """
        Get a command that is supposed to post-process a checked-out
        or updated working copy.

        This has been introduced in order to update git submodules and
        is currently not used by any other scm updater.

        This base implementation returns None
        """
        return None
