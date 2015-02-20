#!/usr/bin/env python

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

import os
import os.path
import tempfile
import time
import urllib

from gump import log
from gump.core.model.output import OUTPUT_POM
from gump.core.run.actor import AbstractRunActor, FinalizeRunEvent, \
    InitializeRunEvent

# list of tuples listing all snapshot repositories we want to mirror
#   each tuple consists of a name, the path prefix that identifies the
#   repository and the real repository URL without that prefix
#   (properly escaped to be used in a Java .properties file).
# Since different mvn projects use different names for the same
#  repository it is possible to have multiple listings for a single
#  repo.  Each name has to be unique as has to be the combination of
#  prefix and URL (i.e. each prefix must uniquely map to a real URL)
SNAPSHOT_PROXIES = [
    ('apache.snapshots', '/repo/m2-snapshot-repository',
     'http\://people.apache.org'),
    ('apache.snapshots.https', '/snapshots',
     'https://repository.apache.org'),
    ('sonatype-nexus-snapshots', '/content/repositories/snapshots',
     'https\://oss.sonatype.org')
    ]

# list of tuples listing all repositories we want to mirror
#   each tuple consists of a name, the path prefix that identifies the
#   repository and the real repository URL without that prefix
#   (properly escaped to be used in a Java .properties file).
# Since different mvn projects use different names for the same
#  repository it is possible to have multiple listings for a single
#  repo.  Each name has to be unique as has to be the combination of
#  prefix and URL (i.e. each prefix must uniquely map to a real URL)
PROXY_CONFIG = [
    ('central', '/maven2', 'http\://repo1.maven.org'),
    SNAPSHOT_PROXIES[0],
    ('maven2-repository.dev.java.net', '/maven/2', 'http\://download.java.net'),
    ('m2.dev.java.net', '/maven/2', 'http\://download.java.net'),
    SNAPSHOT_PROXIES[1],
    SNAPSHOT_PROXIES[2]
    ]

class MvnRepositoryProxyController(AbstractRunActor):
    """
       Starts/Stops the proxy, adds artifacts to it when a project has
       been built, collects the results.
    """

    def __init__(self, run, javaCommand = 'java'):
        AbstractRunActor.__init__(self, run)
        self.proxyURL = "http://localhost:%s/" \
            % (run.getWorkspace().mvnRepoProxyPort)
        self.java = javaCommand

    def processProject(self, project):
        """
        Process a project (i.e. publish it's artifacts to the proxy)
        """

        if project.okToPerformWork() and project.hasOutputs():
            groupId = project.getArtifactGroup()
            for output in project.getOutputs():
                if output.is_jar() or output.getType() == OUTPUT_POM:
                    fileName = os.path.abspath(output.getPath())
                    try:
                        log.debug('Publishing \'%s\' output \'%s\' to proxy'
                                  % (output.getType(), fileName))
                        self.publish(groupId, output.getId(), fileName)
                    except:
                        log.error('Failed to publish \'%s\' to proxy' %
                                  (fileName), exc_info = 1)

    def processOtherEvent(self, event):
        if isinstance(event, InitializeRunEvent):
            self.spawnProxy()
        elif isinstance(event, FinalizeRunEvent):
            self.saveLogAndStop()

    def publish(self, groupId, artifactId, fileName):
        urllib.urlopen(self.proxyURL + 'addartifact',
                       urllib.urlencode({'groupId': groupId,
                                         'artifactId': artifactId,
                                         'file': fileName}))

    def spawnProxy(self):
        log.info('Starting mvn repository proxy')
 
        propsfile = tempfile.NamedTemporaryFile(mode = 'w+',
                                                suffix = '.properties')
        known_prefixes = {}
        log.debug('Writing ' + propsfile.name)
        for (_name, prefix, url) in PROXY_CONFIG:
            if prefix not in known_prefixes:
                propsfile.write("%s=%s\n" % (prefix, url))
                known_prefixes[prefix] = True
        propsfile.flush()

        try:
            proxyJar = os.path.join(os.environ.get('MVN_PROXY_HOME'),
                                    'repoproxy.jar')
            log.info('Running: %s -jar %s %s %s'
                     % (self.java, proxyJar, self.workspace.mvnRepoProxyPort,
                        propsfile.name))
            # TODO emulate spawnlp on non-Unix platforms
            os.spawnlp(os.P_NOWAIT, self.java, self.java, '-jar', proxyJar,
                       self.workspace.mvnRepoProxyPort, propsfile.name)
            # Hang back for a bit while the proxy starts up
            for _pWait in range(10):
                try:
                    urllib.urlopen(self.proxyURL)
                    # Not reached until urlopen succeeds
                    log.info('mvn Repository proxy started')
                    break
                except IOError:
                    time.sleep(1)
                    continue
        except:
            log.error('--- Failed to start proxy', exc_info=1)
        propsfile.close()

    def saveLogAndStop(self):
        proxyLogFileName = 'proxyLog.html'

        log.info('Storing proxyLog to xdocs-work ...')
        try:
            proxyLogRequest = urllib.urlopen(self.proxyURL + proxyLogFileName)
            proxyLogContent = proxyLogRequest.read()
            proxyLogRequest.close()
            # TODO xdocs-Documenter is hard-coded here
            proxyLogFile = open(os.path.join(
                    os.path.join(self.workspace.getBaseDirectory(),
                                 'xdocs-work'),
                    proxyLogFileName), 'w')
            proxyLogFile.write(proxyLogContent)
            proxyLogFile.close()
        except:
            log.error('--- Failed to store ' + proxyLogFileName, exc_info = 1)

        log.info('Stopping mvn repository proxy')
        try:
            urllib.urlopen(self.proxyURL + 'stop', urllib.urlencode({}))
            # allow Java process to stop before the Python process terminates
            time.sleep(5)
        except:
            log.error('--- Failed to stop proxy', exc_info = 1)
