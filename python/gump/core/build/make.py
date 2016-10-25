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
        An make builder (uses make to build projects)
"""

from gump.core.build.basebuilder import BaseBuilder, get_args, get_command_skeleton


###############################################################################
# Classes
###############################################################################

class MakeBuilder(BaseBuilder):
    """
        An make builder (uses make to build projects)
    """

    def __init__(self, run):
        """
        A make 'builder'
        """
        BaseBuilder.__init__(self, run, 'make')

    def get_command(self, project, _language):
        """ Return the command object for a <make entry """
        make = project.make

        # The make target (or none == ALL)
        target = make.getTarget()

        # The make file (or none == Makefile)
        makefile = make.getMakeFile()

        # The make command, defaults to "make"
        make_command = project.getWorkspace().getMakeCommand()

        cmd = get_command_skeleton(project, make_command, make)

        # Pass the makefile
        if makefile:
            cmd.addParameter('-f', makefile)

        cmd.addParameters(get_args(make))

        # End with the target (or targets)...
        if target:
            for single_target in target.split():
                cmd.addParameter(single_target)

        return cmd
