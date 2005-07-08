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


class ClasspathPlugin(BuilderPlugin):
    """Generate the java build attributes (e.g. CLASSPATH) for the specified command."""
    def __init__(self, workdir, log, CommandClazz):
        BuilderPlugin.__init__(self, workdir, log, CommandClazz, self.set_classpath)
        
    def set_classpath(self, project, command):
        (classpath, bootclasspath) = calculate_classpath(self.workdir, project)
        command.classpath = classpath
        command.boot_classpath = bootclasspath
                
        
class AntPlugin(BuilderPlugin):
    """Execute all "ant" commands for all projects."""
    def __init__(self, workdir, log, debug=False):
        BuilderPlugin.__init__(self, workdir, log, Ant, self._do_ant)
        self.debug = debug
        
    def _do_ant(self, project, ant):                
        projectpath = get_project_directory(self.workdir,project)
        if ant.basedir:
            projectpath = os.path.join(projectpath, ant.basedir)
        
        self.log.debug('CLASSPATH %s' % ant.classpath)
        self.log.debug('BOOTCLASSPATH %s' % ant.boot_classpath)
        
        # Create an Environment
        project.env['CLASSPATH'] = os.pathsep.join(ant.classpath)
        
        # TODO test this
        # TODO sysclasspath only
        # TODO more options
        
        # Build the command line.
        args = [join(os.environ["JAVA_HOME"], "bin", "java")]
        
        # Allow bootclasspath
        if ant.boot_classpath:
            args += ['-Xbootclasspath/p',':'.join(ant.boot_classpath)]

        # Ant's entry point, and main options.
        args += ["org.apache.tools.ant.Main"]
                 
        # Specify a build file.
        if ant.buildfile: args += ["-buildfile",ant.buildfile]

        # Override the default target
        if ant.target: args += [ant.target]
        
        # Allow debugging
        if self.debug: args += ["-debug"]
        
        self.log.debug("Command : %s " % (args))
        self.log.debug("        : %s " % ant.classpath)
        #self.log.debug("        : %s " % self.tmp_env)
        cmd = Popen(args,shell=False,cwd=projectpath,stdout=PIPE,stderr=STDOUT,env=project.env)

        ant.build_log = cmd.communicate()[0]
        ant.build_exit_status = cmd.wait()
