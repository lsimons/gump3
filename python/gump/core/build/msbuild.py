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
        A MSBuild builder (uses MSBuild or Mono's xbuild to build projects)
"""

from gump import log
from gump.core.build.basebuilder import BaseBuilder, get_command_skeleton, \
    is_debug_enabled, is_verbose_enabled
from gump.core.model.state import REASON_PREBUILD_FAILED, STATE_FAILED
from gump.util.process.command import Parameters

def get_msbuild_properties(project):
    """ Get properties for a project """
    properties = Parameters()
    props = project.getWorkspace().getProperties() + \
            project.getMSBuild().getProperties()
    for prop in props:
        properties.addPrefixedNamedParameter('/p:', prop.name, prop.value, '=')
    return properties

class MSBuildBuilder(BaseBuilder):
    """
        A MSBuild builder (uses MSBuild or Mono's xbuild to build projects)
    """


    def __init__(self, run):
        """
                The MSBuild Builder is a .NET Builder
        """
        BaseBuilder.__init__(self, run, 'MSBuild')

    def get_command(self, project, _language):
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

        # Run MSBuild...
        cmd = get_command_skeleton(project, self.run.env.get_msbuild_command(), msbuild)

        # Allow MSBuild-level debugging...
        if is_debug_enabled(project, msbuild):
            cmd.addParameter('/verbosity:diagnostic')
        if is_verbose_enabled(project, msbuild):
            cmd.addParameter('/verbosity:detailed')

        # These are from the project and/or workspace
        # These are 'normal' properties.
        cmd.addNamedParameters(get_msbuild_properties(project))

        # target (or targets)...
        if target:
            cmd.addParameter('/target:' + target)

        # Pass the buildfile
        if buildfile:
            cmd.addParameter(buildfile)

        return cmd
