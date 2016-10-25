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
    A NuGet builder http://www.nuget.org/
"""

from gump.core.build.basebuilder import BaseBuilder, get_args, get_command_skeleton

###############################################################################
# Classes
###############################################################################

class NuGetBuilder(BaseBuilder):
    """
    A NuGet builder http://www.nuget.org/
    """

    def __init__(self, run):
        """
        A NuGet 'builder'
        """
        BaseBuilder.__init__(self, run, 'NuGet')

    def get_command(self, project, _language):
        """ Return the command object for a <nuget entry """
        nuget = project.nuget

        cmd = get_command_skeleton(project, self.run.env.get_nuget_command(), nuget)
        cmd.addParameter(nuget.getCommand())
        cmd.addParameters(get_args(nuget))
        if nuget.hasSolution():
            cmd.addParameter(nuget.getSolution())

        return cmd
