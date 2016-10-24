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

__revision__  = "$Rev: 36667 $"
__date__      = "$Date: 2004-08-20 08:55:45 -0600 (Fri, 20 Aug 2004) $"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"


"""
        An make builder (uses make to build projects)
"""

from gump import log
from gump.core.run.gumprun import RunSpecific
from gump.core.build.script import getArgs
from gump.core.config import setting
from gump.core.model.state import REASON_BUILD_FAILED, REASON_BUILD_TIMEDOUT, STATE_FAILED,\
    STATE_SUCCESS
from gump.util.process.command import CMD_STATE_SUCCESS, CMD_STATE_TIMED_OUT, Cmd
from gump.util.process.launcher import execute
from gump.util.work import CommandWorkItem, WORK_TYPE_BUILD



###############################################################################
# Classes
###############################################################################

class MakeBuilder(RunSpecific):

    def __init__(self, run):
        """
        A make 'builder'
        """
        RunSpecific.__init__(self, run)

    def buildProject(self, project, languageHelper, stats):
        """
        Run a project's make file
        """

        workspace = self.run.getWorkspace()

        log.info('Run make on project: #[' + `project.getPosition()` + '] : ' + project.getName())

        #
        # Get the appropriate build command...
        #
        cmd = self.getMakeCommand(project)

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
                project.changeState(STATE_FAILED,reason)

            else:
                # For now, things are going good...
                project.changeState(STATE_SUCCESS)

    def getMakeCommand(self, project):
        """ Return the command object for a <make entry """
        make = project.make

        # Where to run this:
        basedir = make.getBaseDirectory() or project.getBaseDirectory()

        # The make target (or none == ALL)
        target = make.getTarget()

        # The make file (or none == Makefile)
        makefile = make.getMakeFile()

        # The make command, defaults to "make"
        makeCommand = project.getWorkspace().getMakeCommand()

        # Optional 'timeout'
        if make.hasTimeout():
            timeout = make.getTimeout()
        else:
            timeout = setting.TIMEOUT

        cmd = Cmd(makeCommand, 'build_'+project.getModule().getName()+'_'+project.getName(),
                  basedir, timeout=timeout)

        # Pass the makefile
        if makefile:
            cmd.addParameter('-f', makefile)

        cmd.addParameters(getArgs(make))

        # End with the target (or targets)...
        if target:
            for targetParam in target.split():
                cmd.addParameter(targetParam)

        return cmd


    def preview(self, project, languageHelper, stats):
        """
        Preview what this would do
        """
        cmd = self.getMakeCommand(project)
        cmd.dump()
