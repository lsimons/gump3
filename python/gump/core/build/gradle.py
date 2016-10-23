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

from time import strftime
import os.path

from gump import log
from gump.actor.mvnrepoproxy.proxycontrol import SNAPSHOT_PROXIES
from gump.core.build.mvn import local_mvn_repo
from gump.core.model.workspace import CommandWorkItem, \
    REASON_BUILD_FAILED, REASON_BUILD_TIMEDOUT, REASON_PREBUILD_FAILED, \
    STATE_FAILED, STATE_SUCCESS, WORK_TYPE_BUILD
from gump.core.run.gumprun import RunSpecific
from gump.util.file import FILE_TYPE_CONFIG
from gump.util.process.command import Cmd, CMD_STATE_SUCCESS, \
    CMD_STATE_TIMED_OUT, Parameters
from gump.util.process.launcher import execute
from gump.util.tools import catFileToFileHolder

###############################################################################
# Classes
###############################################################################

def record_proxy(init_file, name, prefix, uri):
    init_file.write("""
                maven {
                    name "%s"
                    url "%s%s"
                }""" % (name, uri.replace('\\', ''), prefix))

def locateGradleProjectFile(project):
    """Return Gradle project file location"""
    basedir = project.gradle.getBaseDirectory() or project.getBaseDirectory()
    return os.path.abspath(os.path.join(basedir, 'build.gradle'))

def locate_init_script(project):
    #
    # Where to put this:
    #
    basedir = project.gradle.getBaseDirectory() or project.getBaseDirectory()
    return os.path.abspath(os.path.join(basedir, 'gump_init_script.gradle'))

def getGradleProperties(project):
    """ Get properties for a project """
    properties = Parameters()
    for property in project.getGradle().getProperties():
        properties.addPrefixedNamedParameter('-P', property.name, \
                                                 property.value, '=')
    return properties

def getSysProperties(project):
    """ Get sysproperties for a project """
    properties = Parameters()
    for property in project.getWorkspace().getSysProperties() + \
        project.getGradle().getSysProperties():
        properties.addPrefixedNamedParameter('-D', property.name, \
                                                 property.value, '=')
    return properties

def needsSeparateLocalRepository(project):
    return project.gradle.needsSeparateLocalRepository()

def getGradleCommand(project, executable='gradle'):
    """ Build a Gradle command for this project """
    gradle = project.gradle

    # The gradle task (or none == gradle default task)
    task = gradle.getTask()

    # Optional 'verbose' or 'debug'
    verbose = gradle.isVerbose()
    debug = gradle.isDebug()

    #
    # Where to run this:
    #
    basedir = gradle.getBaseDirectory() or project.getBaseDirectory()

    # Run Gradle...
    cmd = Cmd(executable, 'build_' + project.getModule().getName() + '_' + \
                project.getName(), basedir)

    #
    # Allow gradle-level debugging...
    #
    if project.getWorkspace().isDebug() or project.isDebug() or debug:
        cmd.addParameter('--debug')
    if project.getWorkspace().isVerbose() \
            or project.isVerbose() or verbose:
        cmd.addParameter('--info')

    props = getGradleProperties(project)
    cmd.addNamedParameters(props)
    sysprops = getSysProperties(project)
    cmd.addNamedParameters(sysprops)

    if needsSeparateLocalRepository(project):
        localRepositoryDir = local_mvn_repo(project, gradle)
    else:
        localRepositoryDir = os.path.abspath(\
                os.path.join(project.getWorkspace()
                             .getLocalRepositoryDirectory(),
                             "shared"))
    cmd.addParameter("-Dmaven.repo.local=" + localRepositoryDir)
    cmd.addParameter('--refresh-dependencies')

    cmd.addParameter('--init-script')
    cmd.addParameter(locate_init_script(project))

    # End with the task...
    if task:
        for taskParam in task.split(','):
            cmd.addParameter(taskParam)

    return cmd

class GradleBuilder(RunSpecific):

    def __init__(self, run):
        RunSpecific.__init__(self, run)

    def buildProject(self, project, languageHelper, stats):
        """
        Build a Gradle project
        """

        workspace = self.run.getWorkspace()

        log.debug('Run Gradle on Project: #[' + `project.getPosition()` + '] '\
                  + project.getName())

        self.performPreBuild(project, languageHelper, stats)

        if project.okToPerformWork():

            #
            # Get the appropriate build command...
            #
            cmd = getGradleCommand(project)

            if cmd:
                # Get/set JVM properties
                jvmargs = languageHelper.getJVMArgs(project)
                if jvmargs and len(jvmargs.items()) > 0:
                    cmd.addEnvironment('GRADLE_OPTS',
                                       jvmargs.formatCommandLine())

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

        if project.wasBuilt():
            gradleFile = locateGradleProjectFile(project)
            if os.path.exists(gradleFile):
                project.addDebug('Gradle build in: ' + gradleFile)
                catFileToFileHolder(project, gradleFile, FILE_TYPE_CONFIG)


    def performPreBuild(self, project, _languageHelper, _stats):

        if project.okToPerformWork():
            try:
                init_script = self.generate_init_script(project)
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

    def preview(self, project, _languageHelper, _stats):
        command = getGradleCommand(project)
        command.dump()

    def generate_init_script(self, project):
        """Set repository for a Gradle project"""

        init_script = locate_init_script(project)
        # Ensure containing directory exists, or make it.
        init_script_dir = os.path.dirname(init_script)
        if not os.path.exists(init_script_dir):
            project.addInfo('Making directory for Gradle Init Script: [' \
                                + init_script_dir + ']')
            os.makedirs(init_script_dir)

        if os.path.exists(init_script):
            project.addWarning('Overriding Gradle Init Script: [' + init_script \
                                   + ']')

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
