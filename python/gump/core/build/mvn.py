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
    Builder for Maven 2.x/3.x using Gump's repository proxy.
"""

from time import strftime
import os.path

from gump import log
from gump.core.build.basebuilder import BaseBuilder, get_command_skeleton, \
    is_debug_enabled, is_verbose_enabled, local_mvn_repo, \
    needs_separate_local_repository
from gump.actor.mvnrepoproxy.proxycontrol import PROXY_CONFIG
from gump.core.model.builder import MVN_VERSION2, MVN_VERSION3
from gump.core.model.workspace import REASON_PREBUILD_FAILED, STATE_FAILED
from gump.util.file import FILE_TYPE_CONFIG
from gump.util.process.command import Parameters
from gump.util.tools import catFileToFileHolder

def write_mirror_entry(props, prefix, mirror_of, port):
    """ adds an entry for a repository mirror """
    props.write("""
    <mirror>
      <id>gump-%s</id>
      <name>Apache Gump proxying %s</name>
      <url>http://localhost:%s%s</url>
      <mirrorOf>%s</mirrorOf>
    </mirror>""" % (mirror_of, mirror_of, port, prefix, mirror_of))

def locate_pom(project):
    """Return Maven project file location"""
    basedir = project.mvn.getBaseDirectory() or project.getBaseDirectory()
    return os.path.abspath(os.path.join(basedir, 'pom.xml'))

def locate_settings(project):
    """ absolute path to the generated mvn settings """
    basedir = project.mvn.getBaseDirectory() or project.getBaseDirectory()
    return os.path.abspath(os.path.join(basedir, 'gump_mvn_settings.xml'))

def get_properties(project):
    """ Get properties for a project """
    properties = Parameters()
    for prop in project.getMvn().getProperties():
        properties.addPrefixedNamedParameter('-D', prop.name, prop.value, '=')
    return properties

def get_mvn_command(project, executable='mvn'):
    """ Build an Maven command for this project """
    maven = project.mvn

    # The maven goal (or none == maven default goal)
    goal = maven.getGoal()

    # Run Maven...
    cmd = get_command_skeleton(project, executable, maven)

    cmd.addParameter('--batch-mode')

    #
    # Allow maven-level debugging...
    #
    if is_debug_enabled(project, maven):
        cmd.addParameter('--debug')
    if is_verbose_enabled(project, maven):
        cmd.addParameter('--exception')

    cmd.addNamedParameters(get_properties(project))

    cmd.addParameter('--settings')
    cmd.addParameter(locate_settings(project))

    profile = maven.getProfile()
    if profile:
        cmd.addPrefixedParameter('-P', profile)

    # End with the goal...
    if goal:
        for single_goal in goal.split(','):
            cmd.addParameter(single_goal)

    return cmd

###############################################################################
# Classes
###############################################################################

class MavenBuilder(BaseBuilder):

    """
    Builder for Maven 2.x/3.x using Gump's repository proxy.
    """

    def __init__(self, run):
        BaseBuilder.__init__(self, run, 'Maven')

    def get_command(self, project, language):
        """
        Build a Maven 2.x/3.x project
        """

        #
        # Get the appropriate build command...
        #
        home = None
        if project.getMvn().getVersion() == MVN_VERSION2:
            home = self.run.env.m2_home
        elif project.getMvn().getVersion() == MVN_VERSION3:
            home = self.run.env.m3_home

        if home:
            cmd = get_mvn_command(project, home + '/bin/mvn')
            cmd.addEnvironment('M2_HOME', home)
        else:
            cmd = get_mvn_command(project)

        if cmd:
            # Get/set JVM properties
            jvmargs = language.getJVMArgs(project)
            if jvmargs and len(jvmargs.items()) > 0:
                cmd.addEnvironment('MAVEN_OPTS', jvmargs.formatCommandLine())
        return cmd

    def pre_build(self, project, language, _stats):
        try:
            settings = self.generate_mvn_settings(project, language)
            project.addDebug('(Apache Gump generated) Apache Maven Settings in: ' + \
                             settings)

            try:
                catFileToFileHolder(project, settings, FILE_TYPE_CONFIG,
                                    os.path.basename(settings))
            except:
                log.error('Display Settings [ ' + settings + \
                          '] Failed', exc_info=1)

        except Exception, details:
            message = 'Generate Maven Settings Failed:' + str(details)
            log.error(message, exc_info=1)
            project.addError(message)
            project.changeState(STATE_FAILED, REASON_PREBUILD_FAILED)

    def post_build(self, project, _language, _stats):
        """
        Attach pom to output.
        """
        pom = locate_pom(project)
        if os.path.exists(pom):
            project.addDebug('Maven POM in: ' + pom)
            catFileToFileHolder(project, pom, FILE_TYPE_CONFIG)


    def generate_mvn_settings(self, project, _language):
        """Set repository for a Maven project"""

        settings = locate_settings(project)
        # Ensure containing directory exists, or make it.
        settingsdir = os.path.dirname(settings)
        if not os.path.exists(settingsdir):
            project.addInfo('Making directory for Maven settings: [' \
                                + settingsdir + ']')
            os.makedirs(settingsdir)

        if os.path.exists(settings):
            project.addWarning('Overriding Maven settings: [' + settings \
                                   + ']')

        if needs_separate_local_repository(project.mvn):
            local_repo = local_mvn_repo(project, project.mvn)
        else:
            local_repo = os.path.abspath(\
                os.path.join(self.run.getWorkspace()
                             .getLocalRepositoryDirectory(), "shared"))

        props = open(settings, 'w')

        props.write(("""<?xml version="1.0"?>
<!--
  Licensed to the Apache Software Foundation (ASF) under one or more
  contributor license agreements.  See the NOTICE file distributed with
  this work for additional information regarding copyright ownership.
  The ASF licenses this file to You under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with
  the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->
<!--
# DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT
#
# File Automatically Generated by Gump, see http://gump.apache.org/
#
# Generated For : %s
# Generated At  : %s
#
#
# DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT
-->
<settings>
  <localRepository>%s</localRepository>""")
                    % (project.getName(), strftime('%Y-%m-%d %H:%M:%S'), local_repo))
        if not self.run.getEnvironment().noMvnRepoProxy:
            props.write("""
  <mirrors>""")
            for (name, prefix, _url) in PROXY_CONFIG:
                write_mirror_entry(props, prefix, name, \
                                       self.run.getWorkspace().mvnRepoProxyPort)
            props.write("""
  </mirrors>""")

        props.write("""
</settings>""")

        return settings

