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
	An Ant builder (uses ant to build projects)
"""

from gump.core.build.basebuilder import BaseBuilder, get_command_skeleton, \
    is_debug_enabled, is_verbose_enabled
from gump.util.process.command import Parameters

def get_ant_properties(project):
    """ Get properties for a project """
    properties = Parameters()
    for prop in project.getWorkspace().getProperties() + project.getAnt().getProperties():
        properties.addPrefixedNamedParameter('-D', prop.name, prop.getValue(), '=')
    return properties

def get_ant_sysproperties(project):
    """ Get sysproperties for a project """
    properties = Parameters()
    for prop in project.getWorkspace().getSysProperties() + project.getAnt().getSysProperties():
        properties.addPrefixedNamedParameter('-D', prop.name, prop.value, '=')
    return properties

class AntBuilder(BaseBuilder):
    """
	An Ant builder (uses ant to build projects)
    """

    def __init__(self, run):
        """
        	The Ant Builder is a Java Builder
    	"""
        BaseBuilder.__init__(self, run, 'Ant')

    def get_command(self, project, language):
        """
        	Build an ANT command for this project, based on the <ant metadata
   			select targets and build files as appropriate.
        """
        # The original model information...
        ant = project.ant
        # The ant target (or none == ant default target)
        target = ant.getTarget()

        # The ant build file (or none == build.xml)
        buildfile = ant.getBuildFile()

        # Build a classpath (based upon dependencies)
        (classpath, bootclasspath) = language.getClasspaths(project)

        # Run java on apache Ant...
        cmd = get_command_skeleton(project, self.run.getEnvironment().getJavaCommand(),
                                   ant, {'CLASSPATH' : classpath})

        # These are workspace + project system properties
        cmd.addNamedParameters(get_ant_sysproperties(project))

        # Add BOOTCLASSPATH
        if bootclasspath:
            cmd.addPrefixedParameter('-X', 'bootclasspath/p', bootclasspath, ':')

        # Get/set JVM properties
        jvmargs = language.getJVMArgs(project)
        if jvmargs:
            cmd.addParameters(jvmargs)

        # The Ant interface
        cmd.addParameter('org.apache.tools.ant.Main')

        # Allow ant-level debugging...
        if is_debug_enabled(project, ant):
            cmd.addParameter('-debug')
        if is_verbose_enabled(project, ant):
            cmd.addParameter('-verbose')

        # Some builds might wish for this information
        # :TODO: Grant greater access to Gump variables from
        # within.
        merge_file = project.getWorkspace().getMergeFile()
        if merge_file:
            cmd.addPrefixedParameter('-D', 'gump.merge', str(merge_file), '=')

        # These are from the project and/or workspace
        # These are 'normal' properties.
        cmd.addNamedParameters(get_ant_properties(project))

        # Pass the buildfile
        if buildfile:
            cmd.addParameter('-f', buildfile)

        # End with the target (or targets)...
        if target:
            for single_target in target.split(','):
                cmd.addParameter(single_target)

        return cmd
