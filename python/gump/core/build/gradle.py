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
    A gradle builder - rewrites all dependencies to use SNAPSHOT
    dependencies, not the ones built by Gump, unfortunately.
"""

from time import strftime
import os.path

from gump import log
from gump.core.build.basebuilder import BaseBuilder, get_command_skeleton, \
    is_debug_enabled, is_verbose_enabled, needs_separate_local_repository
from gump.actor.mvnrepoproxy.proxycontrol import SNAPSHOT_PROXIES
from gump.core.build.mvn import local_mvn_repo
from gump.core.model.workspace import REASON_PREBUILD_FAILED, STATE_FAILED
from gump.util.file import FILE_TYPE_CONFIG
from gump.util.process.command import Parameters
from gump.util.tools import catFileToFileHolder

def record_proxy(init_file, name, prefix, uri):
    """ write repository information about a known SNAPSHOT repo """
    init_file.write("""
                maven {
                    name "%s"
                    url "%s%s"
                }""" % (name, uri.replace('\\', ''), prefix))

def locate_gradle_buildfile(project):
    """Return Gradle project file location"""
    basedir = project.gradle.getBaseDirectory() or project.getBaseDirectory()
    return os.path.abspath(os.path.join(basedir, 'build.gradle'))

def locate_init_script(project):
    """ returns absolute path of the generated init script """
    basedir = project.gradle.getBaseDirectory() or project.getBaseDirectory()
    return os.path.abspath(os.path.join(basedir, 'gump_init_script.gradle'))

def get_properties(project):
    """ Get properties for a project """
    properties = Parameters()
    for prop in project.getGradle().getProperties():
        properties.addPrefixedNamedParameter('-P', prop.name, prop.value, '=')
    return properties

def get_sys_properties(project):
    """ Get sysproperties for a project """
    properties = Parameters()
    for prop in project.getWorkspace().getSysProperties() + \
        project.getGradle().getSysProperties():
        properties.addPrefixedNamedParameter('-D', prop.name, prop.value, '=')
    return properties

def get_gradle_command(project, executable='gradle'):
    """ Build a Gradle command for this project """
    gradle = project.gradle

    # The gradle task (or none == gradle default task)
    task = gradle.getTask()

    # Run Gradle...
    cmd = get_command_skeleton(project, executable, gradle)

    #
    # Allow gradle-level debugging...
    #
    if is_debug_enabled(project, gradle):
        cmd.addParameter('--debug')
    if is_verbose_enabled(project, gradle):
        cmd.addParameter('--info')

    cmd.addNamedParameters(get_properties(project))
    cmd.addNamedParameters(get_sys_properties(project))

    if needs_separate_local_repository(project.gradle):
        local_repo = local_mvn_repo(project, gradle)
    else:
        local_repo = os.path.abspath(\
                os.path.join(project.getWorkspace()
                             .getLocalRepositoryDirectory(),
                             "shared"))
    cmd.addParameter("-Dmaven.repo.local=" + local_repo)
    cmd.addParameter('--refresh-dependencies')

    cmd.addParameter('--init-script')
    cmd.addParameter(locate_init_script(project))

    # End with the task...
    if task:
        for single_task in task.split(','):
            cmd.addParameter(single_task)

    return cmd

def generate_init_script(project):
    """Set repository for a Gradle project"""

    init_script = locate_init_script(project)
    # Ensure containing directory exists, or make it.
    init_script_dir = os.path.dirname(init_script)
    if not os.path.exists(init_script_dir):
        project.addInfo('Making directory for Gradle Init Script: [' \
                        + init_script_dir + ']')
        os.makedirs(init_script_dir)

    if os.path.exists(init_script):
        project.addWarning('Overriding Gradle Init Script: [' + init_script + ']')

    init_file = open(init_script, 'w')

    init_file.write("""/*
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
*/

/*
# DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT
#
# File Automatically Generated by Gump, see http://gump.apache.org/
#
# Generated For : %s
# Generated At  : %s
#
#
# DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT
*/
import org.gradle.api.internal.artifacts.dependencies.AbstractExternalModuleDependency

apply plugin:UseLatestSnapshots

class UseLatestSnapshots implements Plugin<Gradle> {

    void apply(Gradle gradle) {
        gradle.allprojects{ project ->
            project.repositories {""" % (project.getName(), strftime('%Y-%m-%d %H:%M:%S')))
    for (name, prefix, url) in SNAPSHOT_PROXIES:
        record_proxy(init_file, name, prefix, url)
    init_file.write("""
                mavenLocal()
            }
            project.configurations {
                all { config ->
                    config.allDependencies.whenObjectAdded {
                        if (it instanceof ExternalModuleDependency
                            && !(it instanceof GumpExternalModuleDependency)) {
                            config.dependencies.add(new GumpExternalModuleDependency(it))
                            config.dependencies.remove it
                        }
                    }
                }
            }
        }
    }
}

class GumpExternalModuleDependency extends AbstractExternalModuleDependency {
    GumpExternalModuleDependency(ExternalModuleDependency dep) {
        super(dep.group, dep.name, "latest.integration", dep.configuration)
    }
    @Override
    public boolean contentEquals(Dependency dependency) {
        if (this == dependency) {
            return true;
        }
        if (dependency == null || getClass() != dependency.getClass()) {
            return false;
        }

        ExternalModuleDependency that = (ExternalModuleDependency) dependency;
        return isContentEqualsFor(that);

    }

    @Override
    public GumpExternalModuleDependency copy() {
        GumpExternalModuleDependency copiedModuleDependency = new GumpExternalModuleDependency(this);
        copyTo(copiedModuleDependency);
        return copiedModuleDependency;
    }

}
""")

    return init_script

###############################################################################
# Classes
###############################################################################

class GradleBuilder(BaseBuilder):

    """
    A gradle builder - rewrites all dependencies to use SNAPSHOT
    dependencies, not the ones built by Gump, unfortunately.
    """

    def __init__(self, run):
        BaseBuilder.__init__(self, run, 'Gradle')

    def get_command(self, project, language):
        cmd = get_gradle_command(project)
        if cmd:
            jvmargs = language.getJVMArgs(project)
            if jvmargs and len(jvmargs.items()) > 0:
                cmd.addEnvironment('GRADLE_OPTS', jvmargs.formatCommandLine())
        return cmd

    def pre_build(self, project, _language, _stats):
        """
        Create an init script for the build.
        """
        try:
            init_script = generate_init_script(project)
            project.addDebug('(Apache Gump generated) Gradle Init Script in: ' + \
                                 init_script)

            try:
                catFileToFileHolder(project, init_script,
                                    FILE_TYPE_CONFIG,
                                    os.path.basename(init_script))
            except:
                log.error('Display Init Script [ ' + init_script + \
                              '] Failed', exc_info=1)

        except Exception, details:
            message = 'Generate Gradle Init Script Failed:' + str(details)
            log.error(message, exc_info=1)
            project.addError(message)
            project.changeState(STATE_FAILED, REASON_PREBUILD_FAILED)

    def post_build(self, project, _language, _stats):
        """
        Attach build file to output.
        """
        gradle_file = locate_gradle_buildfile(project)
        if os.path.exists(gradle_file):
            project.addDebug('Gradle build in: ' + gradle_file)
            catFileToFileHolder(project, gradle_file, FILE_TYPE_CONFIG)
