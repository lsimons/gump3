#!/usr/bin/env python

# Copyright 2004-2005 The Apache Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Provides an abstract plugin for Command processing with subclasses."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import os
import sys
from os.path import abspath, join, isfile
from tempfile import mkdtemp
import shutil

from gump.model import Script, Error, Project, Ant, Dependency
from gump.model.util import get_project_directory
from gump.plugins import AbstractPlugin
from gump.util.executor import Popen, PIPE, STDOUT

#DEFAULT_SCRIPT_SHELL = "sh"
if sys.platform == "win32":
    DEFAULT_SCRIPT_SHELL = "cmd"
else:
    DEFAULT_SCRIPT_SHELL = "sh"

class BuilderPlugin(AbstractPlugin):
    """Abstract class for creating plugins that handle the execution of Commands.

    To create a subclass, override __init__, then call it from the subclass with
    the method to call."""
    def __init__(self, log, cmd_clazz, method):
        """Create a new builder. Arguments:
        
          -- log = the Logger instance for debugging
          -- cmd_clazz = the Command subclass the plugin handles
          -- method = the python method (which must be a class method on
             the subclass) to call. It will be provided with a Project
             instance and with the relevant Command instance to process"""
        self.log = log
        self.cmd_clazz = cmd_clazz
        self.method = method             

    def initialize(self):
        self.tempdir = mkdtemp()

    def visit_project(self, project):
        """Dispatch for each matching command (matching by class type) """        
        assert isinstance(project, Project)
        #self.log.debug("Visit %s looking for %s" % (project,self.cmd_clazz))
        for command in [command for command in project.commands if isinstance(command,self.cmd_clazz)]:
            self.log.debug("Perform %s on %s" % (command, project))
            self.method(project, command)
    
    def _do_run_command(self, command, args, workdir, shell=False, no_cleanup=False):
        """Utility method for actually executing commands and storing their
           results within the model.
        
        Arguments:
          - command -- the model object instance (subclass of Command) this
                       action is associated with
          - args    -- the action to take (including, for example, a script
                       name)
        """
        # see gump.plugins.java.builder.AntPlugin for information on the
        # no_cleanup flag
        
        # running subprocess.Popen with shell=True results in "sh -c", which is
        # not what we want, since our shell=True indicates we're actually running
        # a shell script, and potentially using a different shell!
        if shell:
            myargs = ["/usr/bin/env", command.shell or "sh"]
            myargs.extend(args)
        else:
            myargs = args
        
        # unfortunately we can't use the communicate() method on the command
        # it seems that, when invoking python-in-bash-in-python-in-bash (eg
        # using Gump to run gump, for example) and similar complex setups,
        # deadlocking can occur, for example when calling select.select(). So
        # we send output to a temporary file. We can't use the regular "tmpfile"
        # because when we close that file it is removed. Hence, we resort to
        # using a temporary directory. *sigh*
        outputfilename = os.path.join(self.tempdir, "BuilderPlugin_%s.tmp-out" % command.project.name)
        outputfile = None
        try:
            outputfile = open(outputfilename,'wb')
            cmd = Popen(myargs,shell=False,cwd=workdir,stdout=outputfile,stderr=STDOUT,env=command.env, no_cleanup=no_cleanup)
            #command.build_log = cmd.communicate()[0]
            command.build_exit_status = cmd.wait()

            outputfile.close()
            outputfile = open(outputfilename,'rb')
            # we need to avoid Unicode errors when people put in 'fancy characters'
            # into build outputs
            command.build_log = unicode(outputfile.read(), 'iso-8859-1')
        finally:
            if outputfile:
                try: outputfile.close()
                except: pass
                
            try: os.remove(outputfilename)
            except: pass        
            
    def finalize(self, workspace):
        try: shutil.rmtree(self.tempdir)
        except: pass

class ScriptBuilderPlugin(BuilderPlugin):
    """Execute all "script" commands for all projects."""
    def __init__(self, log):
        BuilderPlugin.__init__(self, log, Script, self._do_script)
        
    def _do_script(self, project, script):
        # working directory
        projectpath = get_project_directory(project)
        if script.basedir:
            projectpath = os.path.join(projectpath, script.basedir)
        
        # command line
        myargs = []
        scriptfile = abspath(join(projectpath, script.name))
        
        # No extension is ok, otherwise guess at one, platform appropriately
        if not isfile(scriptfile):
            oldscriptfile = scriptfile
            if sys.platform == "win32":
                scriptfile += ".bat"
            else:
                scriptfile += ".sh"
            
            if not isfile(scriptfile):
                raise Error, "No script '%s' found!" % oldscriptfile
        
        myargs.append(scriptfile)
        myargs.extend(script.args)
        # run it
        self._do_run_command(script, myargs, projectpath, shell=True)
