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

"""

import os.path

from gump import log
from gump.core.run.gumprun import RunSpecific
from gump.core.config import setting
from gump.core.model.state import REASON_BUILD_FAILED, REASON_BUILD_TIMEDOUT, STATE_FAILED,\
    STATE_SUCCESS
from gump.util.process.command import CMD_STATE_SUCCESS, CMD_STATE_TIMED_OUT, Cmd, Parameters
from gump.util.process.launcher import execute
from gump.util.work import CommandWorkItem, WORK_TYPE_BUILD


###############################################################################
# Functions
###############################################################################
def getArgs(script):
    """ Get command line args for a script builder (or other arg supporters) """
    args = Parameters()
    for arg in script.getProperties():
        if arg.name.startswith('--') or not arg.name.startswith('-'):
            if arg.value and arg.value != "*Unset*": # TODO: fix this properly. Ugly!
                args.addNamedParameter(arg.name, arg.value, '=')
            else:
                args.addParameter(arg.name)
        else:
            args.addParameter(arg.name)
            args.addParameter(arg.value)
    return args

###############################################################################
# Classes
###############################################################################

class ScriptBuilder(RunSpecific):

    def __init__(self, run):
        """
        A script 'builder'
        """
        RunSpecific.__init__(self, run)

    def buildProject(self, project, languageHelper, stats):
        """
        Run a project's script (a .bat or a .sh as appropriate)
        """

        workspace = self.run.getWorkspace()

        log.info('Run Project (as a script): #[' + `project.getPosition()` +\
                 '] : ' + project.getName())

        #
        # Get the appropriate build command...
        #
        cmd = self.getScriptCommand(project, languageHelper)

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
                project.changeState(STATE_FAILED, reason)

            else:
                # For now, things are going good...
                project.changeState(STATE_SUCCESS)

    def getScriptCommand(self, project, languageHelper):
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
        (classpath, bootclasspath) = languageHelper.getClasspaths(project)

        # Optional 'timeout'
        if script.hasTimeout():
            timeout = script.getTimeout()
        else:
            timeout = setting.TIMEOUT

        cmd = Cmd(scriptfile,
                  'buildscript_'+project.getModule().getName()+'_'+project.getName(),
                  basedir, {'CLASSPATH':classpath}, timeout)

        cmd.addParameters(getArgs(script))

        return cmd

    def preview(self, project, languageHelper, stats):
        """
        Preview what this would do
        """
        cmd = self.getScriptCommand(project, languageHelper) 
        cmd.dump()
