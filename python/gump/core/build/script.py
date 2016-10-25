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
    The script builder runs a (platform specific) script
"""

import os.path

from gump.core.build.basebuilder import BaseBuilder, get_args, get_command_skeleton


###############################################################################
# Classes
###############################################################################

class ScriptBuilder(BaseBuilder):
    """
    The script builder runs a (platform specific) script
    """

    def __init__(self, run):
        """
        A script 'builder'
        """
        BaseBuilder.__init__(self, run, 'Project (as a script)')

    def get_command(self, project, language):
        """ Return the command object for a <script entry """
        script = project.script

        # Where to run this:
        basedir = script.getBaseDirectory() or project.getBaseDirectory()

        scriptfullname = script.getName()

        # The script
        scriptfile = os.path.abspath(os.path.join(basedir, scriptfullname))

        # If the script exists (and is a plain file, i.e. not a dir)
        # use it's exact name, else add a platform specific extension.
        if not os.path.exists(scriptfile) \
            or not os.path.isfile(scriptfile):
            # Add .sh  or .bat as appropriate to platform
            if os.name not in ['dos', 'nt']:
                scriptfullname += '.sh'
            else:
                scriptfullname += '.bat'

            # Recalculate with the script extension
            scriptfile = os.path.abspath(os.path.join(basedir, scriptfullname))

        # Needed for (at least) a compiler...
        (classpath, _bootclasspath) = language.getClasspaths(project)

        cmd = get_command_skeleton(project, scriptfile, script, {'CLASSPATH' : classpath})
        cmd.addParameters(get_args(script))

        return cmd
