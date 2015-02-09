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

import os.path

from gump import log
#from gump.actor.mvnrepoproxy.proxycontrol import PROXY_CONFIG
from gump.core.model.workspace import CommandWorkItem, \
    REASON_BUILD_FAILED, REASON_BUILD_TIMEDOUT, REASON_PREBUILD_FAILED, \
    STATE_FAILED, STATE_SUCCESS, WORK_TYPE_BUILD
from gump.core.run.gumprun import RunSpecific
from gump.util.file import FILE_TYPE_CONFIG
from gump.util.process.command import Cmd, CMD_STATE_SUCCESS, \
    CMD_STATE_TIMED_OUT, Parameters
from gump.util.process.launcher import execute
from gump.util.tools import catFileToFileHolder

from time import strftime

###############################################################################
# Classes
###############################################################################

#def write_mirror_entry(props, prefix, mirror_of, port):
#    props.write("""
#    <mirror>
#      <id>gump-%s</id>
#      <name>Apache Gump proxying %s</name>
#      <url>http://localhost:%s%s</url>
#      <mirrorOf>%s</mirrorOf>
#    </mirror>""" % (mirror_of, mirror_of, port, prefix, mirror_of) )

def locateGradleProjectFile(project):
    """Return Gradle project file location"""
    basedir = project.gradle.getBaseDirectory() or project.getBaseDirectory()
    return os.path.abspath(os.path.join(basedir, 'build.gradle'))

#def locateMavenSettings(project):
#    #
#    # Where to put this:
#    #
#    basedir = project.mvn.getBaseDirectory() or project.getBaseDirectory()
#    return os.path.abspath(os.path.join(basedir, 'gump_mvn_settings.xml'))

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
    for property in project.getWorkspace().getSysProperties()+project.getGradle().getSysProperties():
        properties.addPrefixedNamedParameter('-D', property.name, \
                                                 property.value, '=')
    return properties

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

    #cmd.addParameter('--settings')
    #cmd.addParameter(locateGradleSettings(project))

    # End with the task...
    if task:
        for taskParam in task.split(','):
            cmd.addParameter(taskParam)

    return cmd

def needsSeparateLocalRepository(project):
    return project.gradle.needsSeparateLocalRepository()

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

        #self.performPreBuild(project, languageHelper, stats)

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
                if not cmdResult.state == CMD_STATE_SUCCESS:
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


    # Do this even if not ok
    #def performPreBuild(self, project, languageHelper, _stats):
    #
    #    # Gradle requires a build.properties to be generated...
    #    if project.okToPerformWork():
    #        try:
    #            settingsFile = self.generateMvnSettings(project, languageHelper)
    #            project.addDebug('(Apache Gump generated) Apache Gradle Settings in: ' + \
    #                                 settingsFile)
    #
    #            try:
    #                catFileToFileHolder(project, settingsFile,
    #                    FILE_TYPE_CONFIG,
    #                    os.path.basename(settingsFile))
    #            except:
    #                log.error('Display Settings [ ' + settingsFile + \
    #                              '] Failed', exc_info = 1)
    #
    #        except Exception, details:
    #            message = 'Generate Gradle Settings Failed:' + str(details)
    #            log.error(message, exc_info = 1)
    #            project.addError(message)
    #            project.changeState(STATE_FAILED, REASON_PREBUILD_FAILED)

    def preview(self, project, _languageHelper, _stats):
        command = getGradleCommand(project)
        command.dump()

#    def generateMvnSettings(self, project, _languageHelper):
#        """Set repository for a Gradle project"""
#
#        settingsFile = locateGradleSettings(project)
#        # Ensure containing directory exists, or make it.
#        settingsdir = os.path.dirname(settingsFile)
#        if not os.path.exists(settingsdir):
#            project.addInfo('Making directory for Gradle settings: [' \
#                                + settingsdir + ']')
#            os.makedirs(settingsdir)
#
#        if os.path.exists(settingsFile):
#            project.addWarning('Overriding Gradle settings: [' + settingsFile \
#                                   + ']')
#
#        if needsSeparateLocalRepository(project):
#            localRepositoryDir = self.locateLocalRepo(project)
#        else:
#            localRepositoryDir = os.path.abspath(\
#                os.path.join(self.run.getWorkspace()
#                             .getLocalRepositoryDirectory(), "shared")
#                )
#
#        props = open(settingsFile, 'w')
#
#        props.write(("""<?xml version="1.0"?>
#<!--
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#-->
#<!--
## DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT
##
## File Automatically Generated by Gump, see http://gump.apache.org/
##
## Generated For : %s
## Generated At  : %s
##
##
## DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT
#-->
#<settings>
#  <localRepository>%s</localRepository>""")
#                    % (project.getName(), strftime('%Y-%m-%d %H:%M:%S'),
#                       localRepositoryDir))
#        if not self.run.getEnvironment().noMvnRepoProxy:
#            props.write("<mirrors>")
#            for (name, prefix, _url) in PROXY_CONFIG:
#                write_mirror_entry(props, prefix, name, \
#                                       self.run.getWorkspace().mvnRepoProxyPort)
#            props.write("</mirrors>")
#
#        props.write("</settings>")
#
#        return settingsFile
#
#    def locateLocalRepo(self, project):
#        #
#        # Where to put the local repository
#        #
#        name = project.mvn.getLocalRepositoryName()
#        if not name:
#            name = project.getName() + ".mvnlocalrepo"
#        return os.path.abspath(os.path.join(self.run.getWorkspace()\
#                                                .getLocalRepositoryDirectory(),
#                                            name
#                                            ))
