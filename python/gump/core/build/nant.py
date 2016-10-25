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
"""
        A NAnt builder (uses nant to build projects)
"""

from gump import log
from gump.core.build.basebuilder import BaseBuilder, get_command_skeleton, \
    is_debug_enabled, is_verbose_enabled
from gump.core.model.state import REASON_PREBUILD_FAILED, STATE_FAILED
from gump.util.process.command import Parameters

def get_nant_properties(project):
    """ Get properties for a project """
    return collect_properties(project.getWorkspace().getProperties() + \
                                  project.getNAnt().getProperties())

def get_nant_sysproperties(project):
    """ Get sysproperties for a project """
    return collect_properties(project.getWorkspace().getSysProperties() + \
                                  project.getNAnt().getSysProperties())

def collect_properties(props):
    """ collect named properties for a project """
    properties = Parameters()
    for prop in props:
        properties.addPrefixedNamedParameter('-D:', prop.name, prop.value, '=')
    return properties

class NAntBuilder(BaseBuilder):
    """
        A NAnt builder (uses nant to build projects)
    """


    def __init__(self, run):
        """
                The NAnt Builder is a .NET Builder
        """
        BaseBuilder.__init__(self, run, 'NAnt')

    def get_command(self, project, _language):
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

        # Run NAnt...
        cmd = get_command_skeleton(project, self.run.env.get_nant_command(), nant)

        # Launch with specified framework (e.g. mono-1.0.1) if
        # required.
        workspace = self.run.getWorkspace()
        if workspace.hasDotNetInformation():
            dotnet_info = workspace.getDotNetInformation()
            if dotnet_info.hasFramework():
                cmd.addParameter('-t:', dotnet_info.getFramework(), '')

        # These are workspace + project system properties
        cmd.addNamedParameters(get_nant_sysproperties(project))

        # Allow NAnt-level debugging...
        if is_debug_enabled(project, nant):
            cmd.addParameter('-debug')
        if is_verbose_enabled(project, nant):
            cmd.addParameter('-verbose')

        # Some builds might wish for this information
        # :TODO: Grant greater access to Gump variables from
        # within.
        merge_file = project.getWorkspace().getMergeFile()
        if merge_file:
            cmd.addPrefixedParameter('-D:', 'gump.merge', str(merge_file), '=')
        # These are from the project and/or workspace
        # These are 'normal' properties.
        cmd.addNamedParameters(get_nant_properties(project))

        # Pass the buildfile
        if buildfile:
            cmd.addParameter('-buildfile', buildfile, ':')

        # End with the target (or targets)...
        if target:
            for single_target in target.split(','):
                cmd.addParameter(single_target)

        return cmd
