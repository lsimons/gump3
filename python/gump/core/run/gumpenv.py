#!/usr/bin/python
#
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
    A gump environment (i.e. what tools are available in this machine's
    environment, and so forth).

    TODO: a lot of this stuff needs to be available in other environments
    as well, for example when we run dynagump or the unit tests we also
    want to know about our environment. Either this class is refactored so
    as to be much more decoupled from the rest of gump or we simply move
    this functionality out into the shell script code so we can get rid of
    it here.
"""

import os.path
import sys
from types import NoneType

from gump.core.config import dir, EXIT_CODE_BAD_ENVIRONMENT, \
    EXIT_CODE_MISSING_UTILITY, time

from gump.util.note import Annotatable

import gump.util.process.command
import gump.util.process.launcher

from gump.util.tools import CommandWorkItem, execute, STATE_SUCCESS, \
    tailFileToString, Workable, WORK_TYPE_CHECK

from gump.core.model.propagation import Propogatable


#TODO: any reason checkEnvironment can't simply be called once (on __init__)
#      and after that simply used? It'd certainly simplify the code a bit..
class GumpEnvironment(Annotatable, Workable, Propogatable):
    """
    Represents the environment that Gump is running within.

    What environment variables are set, what tools are
    available, what Java command to use, etc.

    If some required bit of environment is missing, this class will actually
    short-circuit gump and call sys.exit.
    """

    def __init__(self, log = None):
        Annotatable.__init__(self)
        Workable.__init__(self)
        Propogatable.__init__(self)
        #Stateful.__init__(self) -- redundant, already called from
        #Propogatable.__init__

        if not log:
            from gump import log
        self.log = log

        self.checked = False
        self.set = False

        self.noMono = False
        self.noNAnt = False
        self.nant_command = None
        self.noMaven = False
        self.noMaven2 = False
        self.noMaven3 = False
        self.m2_home = None
        self.m3_home = None
        self.noSvn = False
        self.noCvs = False
        self.noP4 = False
        self.noJava = False
        self.noJavac = False
        self.noMake = False
        self.noMvnRepoProxy = False
        self.noGit = False
        self.noDarcs = False
        self.noHg = False
        self.noBzr = False
        self.noGradle = False

        self.javaProperties = None

        # GUMP_HOME
        self.gumpHome = None

        # JAVACMD can override this, see checkEnvironment
        self.javaHome = None
        self.javaCommand = 'java'
        self.javacCommand = 'javac'

        # Timezone and offset from UTC
        self.timezone = time.tzname
        self.timezoneOffset = time.timezone

    def checkEnvironment(self, exitOnError = False):
        """
        Take a look at the environment and populate this object's
        properties based on that.
        """

        if self.checked:
            return

        # Check for directories

        self._checkEnvVariable('GUMP_HOME')
        self.gumpHome = os.environ['GUMP_HOME']

        # JAVA_CMD can be set (perhaps for JRE verse JDK)
        if os.environ.has_key('JAVA_CMD'):
            self.javaCommand  = os.environ['JAVA_CMD']
            self.addInfo('JAVA_CMD environmental variable setting java' + \
                             ' command to ' + self.javaCommand )

        # JAVAC_CMD can be set (perhaps for JRE verse JDK)
        if os.environ.has_key('JAVAC_CMD'):
            self.javacCommand  = os.environ['JAVAC_CMD']
            self.addInfo('javaCommand environmental variable setting javac' + \
                             ' command to ' + self.javacCommand )
        else:
            # Default to $JAVA_HOME/bin/java, can be overridden with $JAVA_CMD.
            if os.environ.has_key('JAVA_HOME'):
                self.javaCommand  = os.path.join(os.environ['JAVA_HOME'],
                                                 'bin', self.javaCommand)
                self.addInfo('javaCommand set to $JAVA_HOME/bin/java = ' + \
                                 self.javaCommand )

        self._checkEnvVariable('JAVA_HOME')

        if os.environ.has_key('JAVA_HOME'):
            self.javaHome  = os.environ['JAVA_HOME']
            self.addInfo('JAVA_HOME environmental variable setting java' + \
                             ' home to ' + self.javaHome )

        if not self.noMaven and not self._checkEnvVariable('MAVEN_HOME', False):
            self.noMaven = True
            self.addWarning('MAVEN_HOME environmental variable not found, ' + \
                                ' no maven builds.')

        if not self.noMaven2 and not self._checkEnvVariable('M2_HOME', False):
            self.noMaven2 = True
            self.addWarning('M2_HOME environmental variable not found, ' + \
                                ' no mvn2 builds.')
        else:
            self.m2_home = os.environ['M2_HOME']

        if not self.noMaven3 and not self._checkEnvVariable('M3_HOME', False):
            self.noMaven3 = True
            self.addWarning('M3_HOME environmental variable not found, ' + \
                                ' no mvn3 builds.')
        else:
            self.m3_home = os.environ['M3_HOME']

        if not self.noMvnRepoProxy \
                and not self._checkEnvVariable('MVN_PROXY_HOME', False):
            self.noMvnRepoProxy = True
            self.addWarning('MVN_PROXY_HOME environmental variable not' + \
                                ' found, not using a proxy for Maven' + \
                                ' repository')

        # Check for executables

        self._checkExecutable('env', '', False)

        if not self.noJava and not self._checkExecutable(self.javaCommand,
                                                         '-version',
                                                         exitOnError, 1):
            self.noJava = True
            self.noJavac = True

        if not self.noJavac and not self._checkExecutable('javac',
                                                          '-help', False):
            self.noJavac = True

        if not self.noJavac and \
                not self._checkExecutable('java com.sun.tools.javac.Main',
                                          '-help', False, False,
                                          'check_java_compiler'):
            self.noJavac = True

        self.noCvs = self._checkWithDashVersion('cvs',
                                                'no CVS repository updates')

        self.noSvn = self._checkWithDashVersion('svn',
                                                'no svn repository updates')

        self.noP4 = self._checkWithDashVersion('p4',
                                               'no Perforce repository updates',
                                               '-V')

        self.noMaven = not self.noMaven and not \
            self._checkWithDashVersion('maven', "no Maven 1.x builds")


        self.noMaven2 = not self.noMaven2 and not \
            self._checkWithDashVersion(self.m2_home + '/bin/mvn',
                                       "no Maven 2.x builds")

        self.noMaven3 = not self.noMaven3 and not \
            self._checkWithDashVersion(self.m3_home + '/bin/mvn',
                                       "no Maven 3.x builds",
                                       cmd_env = {'M2_HOME' : self.m3_home})

        self._check_nant()
        self.noMono = self._checkWithDashVersion('mono', "no Mono runtime")

        self.noMake = self._checkWithDashVersion('make', "no make builds")

        self.noGit = self._checkWithDashVersion('git',
                                                'no git repository updates')

        self.noDarcs = self._checkWithDashVersion('darcs',
                                                  'no darcs repository updates')

        self.noHg = self._checkWithDashVersion('hg',
                                               'no Mercurial repository ' + \
                                                   'updates')

        self.noBzr = self._checkWithDashVersion('bzr',
                                                'no Bazar repository updates')

        self.noGradle = self._checkWithDashVersion('gradle',
                                                   'no gradle builds')

        self.checked = True

        self.changeState(STATE_SUCCESS)

    def setEnvironment(self):
        """
        Customize the actual environment to reflect the way gump needs
        things to be.
        """

        if self.set:
            return

        # Blank the CLASSPATH
        os.environ['CLASSPATH'] = ''

        self.set = True

    def getGumpHome(self):
        # Ensure we've determined the Gump Home
        self.checkEnvironment()
        return self.gumpHome

    def getJavaHome(self):
        # Ensure we've determined the Java Home
        self.checkEnvironment()
        return self.javaHome

    def getJavaProperties(self):
        """
        Ask the JAVA instance what it's system properties are,
        primarily so we can log/display them (for user review).
        """

        if not isinstance(self.javaProperties, NoneType):
            return self.javaProperties

        # Ensure we've determined the Java Compiler to use
        self.checkEnvironment()

        if self.noJavac:
            self.log.error("Can't obtain Java properties since Java " + \
                               "Environment was not found")
            return {}

        import commands, re

        JAVA_SOURCE = dir.tmp + '/sysprop.java'

        source = open(JAVA_SOURCE, 'w')
        source.write("""
          import java.util.Enumeration;
          public class sysprop {
            public static void main(String [] args) {
              Enumeration e = System.getProperties().propertyNames();
              while (e.hasMoreElements()) {
                String name = (String) e.nextElement();
                System.out.println(name + ": " + System.getProperty(name));
              }
            }
          }
        """)
        source.close()

        cmd = self.javacCommand + " " + JAVA_SOURCE
        os.system(cmd)
        os.unlink(JAVA_SOURCE)

        cmd = self.javaCommand + ' -cp ' + dir.tmp + ' sysprop'
        result = commands.getoutput(cmd)
        self.javaProperties = dict(re.findall('(.*?): (.*)', result))
        JAVA_CLASS = JAVA_SOURCE.replace('.java', '.class')
        if os.path.exists(JAVA_CLASS):
            os.unlink(JAVA_CLASS)

        for (name, value) in self.javaProperties.items():
            self.log.debug("Java Property: " + name + " = > " + value)

        return self.javaProperties

    def _checkWithDashVersion(self, commandName, consequence,
                              version = '--version',
                              cmd_env = None):
        """
        Determine whether a particular command is or is not available
        by using the --version switch
        """
        ok = self._checkExecutable(commandName, version, False, False,
                                   'check_' + commandName, cmd_env)
        if not ok:
            self.addWarning('"' + commandName + '" command not found, '
                            + consequence)
        return ok

    def _checkExecutable(self, exe, options, mandatory, logOutput = False,
                         name = None, cmd_env = None):
        """
        Determine whether a particular command is or is not available.
        """
        ok = False
        try:
            if not name:
                name = 'check_' + exe
            cmd = gump.util.process.command.getCmdFromString(exe + " " + \
                                                                 options,
                                                             name)
            if cmd_env:
                for env_key in cmd_env.keys():
                    cmd.addEnvironment(env_key, cmd_env[env_key])

            result = execute(cmd)
            ok = result.isOk()
            if ok:
                self.log.warning('Detected [' + exe + ' ' + options + ']')
            else:
                self.log.warning('Failed to detect [' + exe + ' ' + \
                                     options + ']')
        except Exception, details:
            ok = False
            self.log.error('Failed to detect [' + exe + ' ' + options + \
                               '] : ' + str(details))
            result = None

        # Update
        self.performedWork(CommandWorkItem(WORK_TYPE_CHECK, cmd, result))

        if not ok and mandatory:
            print
            print "Unable to detect/test mandatory [" + exe + "] in path:"
            for p in sys.path:
                print "  " + str(os.path.abspath(p))
            sys.exit(EXIT_CODE_MISSING_UTILITY)

        # Store the output
        if logOutput and result.output:
            out = tailFileToString(result.output, 10)
            self.addInfo(name + ' produced: \n' + out)

        return ok

    def _checkEnvVariable(self, envvar, mandatory = True):
        """
        Determine whether a particular environment variable is set.
        """
        ok = False
        try:
            ok = os.environ.has_key(envvar)
            if not ok:
                self.log.info('Failed to find environment variable [' + \
                                  envvar + ']')

        except Exception, details:
            ok = False
            self.log.error('Failed to find environment variable [' + envvar + \
                               '] : ' + str(details))

        if not ok and mandatory:
            print
            print "Unable to find mandatory [" + envvar + "] in environment:"
            for e in os.environ.keys():
                try:
                    v = os.environ[e]
                    print "  " + e + " = " + v
                except:
                    print "  " + e
            sys.exit(EXIT_CODE_BAD_ENVIRONMENT)

        return ok

    def getJavaCommand(self):
        return self.javaCommand

    def getTimezone(self):
        return self.timezone

    def getTimezoneOffset(self):
        return self.timezoneOffset

    def _check_nant(self):
        if not self.checked:
            if not self._checkWithDashVersion('NAnt', "no NAnt builds", '-help'):
                if not self._checkWithDashVersion('NAnt.exe', "no NAnt builds", '-help'):
                    self.noNAnt = self._checkWithDashVersion('nant',
                                                             "no NAnt builds",
                                                             '-help')
                    if self.noNAnt:
                        self.nant_command = 'nant'
                    else:
                        self.nant_command = 'NAnt.exe'
                else:
                    self.nant_command = 'NAnt'

    def get_nant_command(self):
        self._check_nant()
        if not self.noNAnt:
            return None
        return self.nant_command

if __name__ == '__main__':
    env = GumpEnvironment()
    env.checkEnvironment()
    env.getJavaProperties()
