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

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

"""Provides plugins for handling java-based Commands such as <ant/>."""

import os
import sys
from os.path import abspath, join, isfile

from gump.model import Script, Error, Project, Ant, Dependency, Classdir, Jar, DEPENDENCY_INHERIT_ALL, DEPENDENCY_INHERIT_HARD, DEPENDENCY_INHERIT_JARS
from gump.model.util import get_project_directory,get_module_directory,get_jar_path,calculate_classpath
from gump.plugins import AbstractPlugin
from gump.plugins.builder import BuilderPlugin
from gump.util.executor import Popen, PIPE, STDOUT
from gump.util import ansicolor

class ClasspathPlugin(BuilderPlugin):
    """Generate the java build attributes (e.g. CLASSPATH) for the specified command."""
    def __init__(self, log, CommandClazz):
        BuilderPlugin.__init__(self, log, CommandClazz, self.set_classpath)
        
    def set_classpath(self, project, command):
        (classpath, bootclasspath) = calculate_classpath(project)
        command.classpath = classpath
        command.boot_classpath = bootclasspath
                
        
class AntPlugin(BuilderPlugin):
    """Execute all "ant" commands for all projects."""
    def __init__(self, log, debug=False):
        BuilderPlugin.__init__(self, log, Ant, self._do_ant)
        self.debug = debug
        
    def _do_ant(self, project, ant):                
        # environment
        self.log.debug("        CLASSPATH is '%s%s%s'" % \
                       (ansicolor.Blue, ":".join(ant.classpath), ansicolor.Black))
        ant.env['CLASSPATH'] = os.pathsep.join(ant.classpath)
        
        # working directory
        projectpath = get_project_directory(project)
        if ant.basedir:
            projectpath = os.path.join(projectpath, ant.basedir)
        
        # command line
        args = [join(ant.env["JAVA_HOME"], "bin", "java")]
        
        if ant.boot_classpath and len(ant.boot_classpath) > 0:
            args.append('-Xbootclasspath/p:' + ':'.join(ant.boot_classpath))

        args += ["org.apache.tools.ant.Main"]
        if ant.buildfile: args += ["-buildfile",ant.buildfile]
        if ant.target: args += [ant.target]
        if self.debug: args += ["-debug"]
        
        # TODO properties
        # TODO parse @@DATE@@ from properties
        
        # run it
        #
        # Setting the process group id (os.setpgrp()) as we do in
        # gump.util.executor sometimes causes a deadlock problem when ant
        # is forking off new java processes. This is because of problems with
        # Runtime.exec() (there are a few it seems, for example
        #   http://bugs.sun.com/bugdatabase/view_bug.do;:YfiG?bug_id=4052517)
        # Our (rather insane!) workaround is to not set the process group id,
        # which means our "get rid of all children" algorithm is disabled for
        # all ant-based builds.
        self._do_run_command(ant, args, projectpath, no_cleanup=True)
        
