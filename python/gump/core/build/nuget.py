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

__copyright__ = "Copyright (c) 1999-2015 Apache Software Foundation"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"

from gump import log
from gump.core.build.script import getArgs
from gump.core.config import setting
from gump.core.model.state import REASON_BUILD_FAILED, REASON_BUILD_TIMEDOUT, \
    STATE_FAILED, STATE_SUCCESS
from gump.core.run.gumprun import RunSpecific
from gump.util.process.command import CMD_STATE_SUCCESS, CMD_STATE_TIMED_OUT, \
    Cmd
from gump.util.process.launcher import execute
from gump.util.work import CommandWorkItem, WORK_TYPE_BUILD

###############################################################################
# Classes
###############################################################################

class NuGetBuilder(RunSpecific):
    """
    A NuGet builder http://www.nuget.org/
    """

    def __init__(self, run):
        """
        A NuGet 'builder'
        """
        RunSpecific.__init__(self, run)

    def buildProject(self, project, _languageHelper, _stats):
        """
        Run a NuGet command
        """

        workspace = self.run.getWorkspace()

        log.info('Run NuGet on: #[' + `project.getPosition()` + '] : ' + \
                 project.getName())

        #
        # Get the appropriate build command...
        #
        cmd = self.getNuGetCommand(project)

        if cmd:
            # Execute the command ....
            cmdResult = execute(cmd, workspace.tmpdir)

            # Update Context
            work = CommandWorkItem(WORK_TYPE_BUILD, cmd, cmdResult)
            project.performedWork(work)
            project.setBuilt(True)

            # Update Context w/ Results
            if cmdResult.state != CMD_STATE_SUCCESS:
                reason = REASON_BUILD_FAILED
                if cmdResult.state == CMD_STATE_TIMED_OUT:
                    reason = REASON_BUILD_TIMEDOUT
                project.changeState(STATE_FAILED, reason)

            else:
                # For now, things are going good...
                project.changeState(STATE_SUCCESS)

    def getNuGetCommand(self, project):
        """ Return the command object for a <nuget entry """
        nuget = project.nuget

        # Where to run this:
        basedir = nuget.getBaseDirectory() or project.getBaseDirectory()

        # Optional 'timeout'
        if nuget.hasTimeout():
            timeout = nuget.getTimeout()
        else:
            timeout = setting.TIMEOUT

        cmd = Cmd(self.run.env.get_nuget_command(),
                  'buildscript_' + project.getModule().getName() + '_' + \
                  project.getName(), basedir, timeout)
        cmd.addParameter(nuget.getCommand())
        cmd.addParameters(getArgs(nuget))
        if nuget.hasSolution():
            cmd.addParameter(nuget.getSolution())

        return cmd

    def preview(self, project, _languageHelper, _stats):
        """
        Preview what this would do
        """
        command = self.getNuGetCommand(project)
        command.dump()
