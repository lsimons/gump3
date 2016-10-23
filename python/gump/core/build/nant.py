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
from gump.core.run.gumprun import RunSpecific

from gump.util.process.command import CMD_STATE_SUCCESS, CMD_STATE_TIMED_OUT, \
    Cmd, Parameters
from gump.util.process.launcher import execute
from gump.util.work import CommandWorkItem, WORK_TYPE_BUILD

from gump.core.model.state import REASON_BUILD_FAILED, REASON_BUILD_TIMEDOUT, \
    REASON_PREBUILD_FAILED, STATE_FAILED, STATE_SUCCESS

def getNAntProperties(project):
    """ Get properties for a project """
    return collect_properties(project.getWorkspace().getProperties() + \
                                  project.getNAnt().getProperties())

def getNAntSysProperties(project):
    """ Get sysproperties for a project """
    return collect_properties(project.getWorkspace().getSysProperties() + \
                                  project.getNAnt().getSysProperties())

def collect_properties(props):
    """ collect named properties for a project """
    properties = Parameters()
    for prop in props:
        properties.addPrefixedNamedParameter('-D:', prop.name, prop.value, '=')
    return properties

class NAntBuilder(RunSpecific):
    """
        A NAnt builder (uses nant to build projects)
    """


    def __init__(self, run):
        """
                The NAnt Builder is a .NET Builder
        """
        RunSpecific.__init__(self, run)

    def buildProject(self, project, _language, _stats):
        """
                Build a project using NAnt, based off the <nant metadata.

                Note: switch on -verbose|-debug based of the stats for this
                project, i.e. how long in a state of failure.
        """

        workspace = self.run.getWorkspace()

        log.info('Run NAnt on Project: #[' + `project.getPosition()` + \
                     '] : ' + project.getName())

        # Get the appropriate build command...
        cmd = self.getNAntCommand(project)

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

    def getNAntCommand(self, project):
        """
        Build an NANT command for this project, based on the <nant metadata
        select targets and build files as appropriate.
        """

        if not self.run.env.get_nant_command():
            message = "Can't run NAnt builds since NAnt hasn't been found"
            log.error(message)
            project.addError(message)
            project.setBuilt(True)
            project.changeState(STATE_FAILED, REASON_PREBUILD_FAILED)
            return None

        # The original model information...
        nant = project.nant
        # The nant target (or none == nant default target)
        target = nant.getTarget()

        # The nant build file (or none == build.xml)
        buildfile = nant.getBuildFile()

        # Optional 'verbose' or 'debug'
        verbose = nant.isVerbose()
        debug = nant.isDebug()

        # Where to run this:
        basedir = nant.getBaseDirectory() or project.getBaseDirectory()

        # Get properties
        properties = getNAntProperties(project)

        # Get system properties
        sysproperties = getNAntSysProperties(project)

        # Run NAnt...
        cmd = Cmd(self.run.env.get_nant_command(),
                  'build_' + project.getModule().getName() + '_' + \
                    project.getName(),
                  basedir)

        # Launch with specified framework (e.g. mono-1.0.1) if
        # required.
        workspace = self.run.getWorkspace()
        if workspace.hasDotNetInformation():
            dotnetInfo = workspace.getDotNetInformation()
            if dotnetInfo.hasFramework():
                cmd.addParameter('-t:', dotnetInfo.getFramework(), '')

        # These are workspace + project system properties
        cmd.addNamedParameters(sysproperties)

        # Allow NAnt-level debugging...
        if project.getWorkspace().isDebug() or project.isDebug() or debug:
            cmd.addParameter('-debug')
        if project.getWorkspace().isVerbose() or project.isVerbose() \
                or verbose:
            cmd.addParameter('-verbose')

        # Some builds might wish for this information
        # :TODO: Grant greater access to Gump variables from
        # within.
        mergeFile = project.getWorkspace().getMergeFile()
        if mergeFile:
            cmd.addPrefixedParameter('-D:', 'gump.merge', str(mergeFile), '=')
        # These are from the project and/or workspace
        # These are 'normal' properties.
        cmd.addNamedParameters(properties)

        # Pass the buildfile
        if buildfile:
            cmd.addParameter('-buildfile', buildfile, ':')

        # End with the target (or targets)...
        if target:
            for targetParam in target.split(', '):
                cmd.addParameter(targetParam)

        return cmd

    def preview(self, project, _language, _stats):
        """
                Preview what an NAnt build would look like.
        """
        cmd = self.getNAntCommand(project)
        cmd.dump()

