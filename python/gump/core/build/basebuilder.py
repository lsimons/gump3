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

"""Utility functions and a base class for Gump builders."""

from gump import log
from gump.core.model.state import REASON_BUILD_FAILED, REASON_BUILD_TIMEDOUT, \
    STATE_FAILED, STATE_SUCCESS
from gump.core.run.gumprun import RunSpecific
from gump.util.process.command import CMD_STATE_SUCCESS, CMD_STATE_TIMED_OUT, Cmd, \
    Parameters
from gump.util.process.launcher import execute
from gump.util.work import CommandWorkItem, WORK_TYPE_BUILD

def get_command_skeleton(project, cmd, builder, env=None):
    """
    Takes care of calculating the CWD and timeout of the command to run.
    """
    basedir = builder.getBaseDirectory() or project.getBaseDirectory()
    return Cmd(cmd, 'build_' + project.getModule().getName() + '_' + project.getName(),
               basedir, env, builder.getTimeout())

def is_debug_enabled(project, builder=None):
    """
    Has debug information been requested at the workspace, project or builder level?
    """
    return project.getWorkspace().isDebug() or project.isDebug() or \
        (builder and builder.isDebug())

def is_verbose_enabled(project, builder=None):
    """
    Has verbose information been requested at the workspace, project or builder level?
    """
    return project.getWorkspace().isVerbose() or project.isVerbose() or \
        (builder and builder.isVerbose())

def get_args(builder):
    """ Get command line args for a builder that supports args """
    args = Parameters()
    for arg in builder.getProperties():
        if arg.name.startswith('--') or not arg.name.startswith('-'):
            if arg.value and arg.value != "*Unset*": # TODO: fix this properly. Ugly!
                args.addNamedParameter(arg.name, arg.value, '=')
            else:
                args.addParameter(arg.name)
        else:
            args.addParameter(arg.name)
            args.addParameter(arg.value)
    return args

class BaseBuilder(RunSpecific):
    """
    Base class for all builders.
    """

    def __init__(self, run, name):
        RunSpecific.__init__(self, run)
        self.name = name

    def buildProject(self, project, language, stats):
        """
        Build the project using the configured command.
        """
        log.info('Run ' + self.name + ' on Project: #[' + `project.getPosition()` + \
                     '] : ' + project.getName())

        self.pre_build(project, language, stats)

        if project.okToPerformWork():
            self.execute_and_record_build_result(project,
                                                 self.get_command(project, language))
        if project.wasBuilt():
            self.post_build(project, language, stats)

    def preview(self, project, language, _stats):
        """
        Preview what a build would look like.
        """
        cmd = self.get_command(project, language)
        if cmd:
            cmd.dump()

    def execute_and_record_build_result(self, project, cmd):
        """
        Execute the given command and record its result with the project
        """
        workspace = self.run.getWorkspace()
        if cmd:
            # Execute the command ....
            result = execute(cmd, workspace.tmpdir)

            # Update context with the fact that this work was done
            work = CommandWorkItem(WORK_TYPE_BUILD, cmd, result)
            project.performedWork(work)
            project.setBuilt(True)

            # Update context state based of the result
            if result.state != CMD_STATE_SUCCESS:
                reason = REASON_BUILD_FAILED
                if result.state == CMD_STATE_TIMED_OUT:
                    reason = REASON_BUILD_TIMEDOUT
                project.changeState(STATE_FAILED, reason)
            else:
                # For now, things are going good...
                project.changeState(STATE_SUCCESS)

    #
    # methods that should be overridden in subclasses
    #
    def get_command(self, _project, _language):
        """
        Get the command that builds the project.
        """
        return None

    def pre_build(self, _project, _language, _stats):
        """
        Perform any actions required before starting the actual build command.
        """
        return None

    def post_build(self, _project, _language, _stats):
        """
        Perform any actions required to clean up after the actual build.
        """
        return None
