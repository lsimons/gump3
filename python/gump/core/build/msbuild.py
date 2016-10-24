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
from gump.core.config import setting
from gump.core.model.state import REASON_BUILD_FAILED, REASON_BUILD_TIMEDOUT, \
    REASON_PREBUILD_FAILED, STATE_FAILED, STATE_SUCCESS
from gump.core.run.gumprun import RunSpecific
from gump.util.process.command import CMD_STATE_SUCCESS, CMD_STATE_TIMED_OUT, \
    Cmd, Parameters
from gump.util.process.launcher import execute
from gump.util.work import CommandWorkItem, WORK_TYPE_BUILD

def getMSBuildProperties(project):
    """ Get properties for a project """
    properties = Parameters()
    props = project.getWorkspace().getProperties() + \
            project.getMSBuild().getProperties()
    for prop in props:
        properties.addPrefixedNamedParameter('/p:', prop.name, prop.value, '=')
    return properties

class MSBuildBuilder(RunSpecific):
    """
        A MSBuild builder (uses MSBuild or Mono's xbuild to build projects)
    """


    def __init__(self, run):
        """
                The MSBuild Builder is a .NET Builder
        """
        RunSpecific.__init__(self, run)

    def buildProject(self, project, _language, _stats):
        """
                Build a project using MSBuild, based off the <msbuild metadata.

                Note: switch on -verbose|-debug based of the stats for this
                project, i.e. how long in a state of failure.
        """

        workspace = self.run.getWorkspace()

        log.info('Run MSBuild on Project: #[' + `project.getPosition()` + \
                     '] : ' + project.getName())

        # Get the appropriate build command...
        cmd = self.getMSBuildCommand(project)

        if cmd:
            # Execute the command ....
            cmdResult = execute(cmd, workspace.tmpdir)

            # Update context with the fact that this work was done
            work = CommandWorkItem(WORK_TYPE_BUILD, cmd, cmdResult)
            project.performedWork(work)
            project.setBuilt(True)

            # Update context state based of the result
            if cmdResult.state != CMD_STATE_SUCCESS:
                reason = REASON_BUILD_FAILED
                if cmdResult.state == CMD_STATE_TIMED_OUT:
                    reason = REASON_BUILD_TIMEDOUT
                project.changeState(STATE_FAILED, reason)
            else:
                # For now, things are going good...
                project.changeState(STATE_SUCCESS)

    def getMSBuildCommand(self, project):
        """
        Build an MSBuild command for this project, based on the <msbuild metadata
        select targets and build files as appropriate.
        """

        if not self.run.env.get_msbuild_command():
            message = "Can't run MSBuild builds since MSBuild hasn't been found"
            log.error(message)
            project.addError(message)
            project.setBuilt(True)
            project.changeState(STATE_FAILED, REASON_PREBUILD_FAILED)
            return None

        # The original model information...
        msbuild = project.msbuild
        # The msbuild target (or none == msbuild default target)
        target = msbuild.getTarget()

        # The msbuild build file (or none == Solution/Project in current folder)
        buildfile = msbuild.getBuildFile()

        # Optional 'verbose' or 'debug'
        verbose = msbuild.isVerbose()
        debug = msbuild.isDebug()

        # Where to run this:
        basedir = msbuild.getBaseDirectory() or project.getBaseDirectory()

        # Get properties
        properties = getMSBuildProperties(project)

        # Optional 'timeout'
        if msbuild.hasTimeout():
            timeout = msbuild.getTimeout()
        else:
            timeout = setting.TIMEOUT

        # Run MSBuild...
        cmd = Cmd(self.run.env.get_msbuild_command(),
                  'build_' + project.getModule().getName() + '_' + \
                  project.getName(),
                  basedir, timeout=timeout)

        # Allow MSBuild-level debugging...
        if project.getWorkspace().isDebug() or project.isDebug() or debug:
            cmd.addParameter('/verbosity:diagnostic')
        if project.getWorkspace().isVerbose() or project.isVerbose() \
                or verbose:
            cmd.addParameter('/verbosity:detailed')

        # These are from the project and/or workspace
        # These are 'normal' properties.
        cmd.addNamedParameters(properties)

        # target (or targets)...
        if target:
            cmd.addParameter('/target:' + target)

        # Pass the buildfile
        if buildfile:
            cmd.addParameter(buildfile)

        return cmd

    def preview(self, project, _language, _stats):
        """
                Preview what an MSBuild build would look like.
        """
        cmd = self.getMSBuildCommand(project)
        cmd.dump()

