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


"""
    XDOC generation.
"""

import os
import StringIO
import sys
import time

from shutil import copyfile
from xml.sax.saxutils import escape

from gump import log
from gump.actor.document.documenter import Documenter
from gump.actor.document.text.documenter import TextDocumenter
from gump.actor.document.xdocs.config import XDocConfig
from gump.actor.document.xdocs.resolver import XDocResolver, \
    getDepthForObject, getRelativeLocation
from gump.actor.document.xdocs.xdoc import XDocDocument
from gump.core.config import default, dir, setting
from gump.core.language.path import AnnotatedPath
from gump.core.model.misc import Resultable
from gump.core.model.project import Project
from gump.core.model.repository import SCM_TYPE_CVS, SCM_TYPE_P4
from gump.core.model.state import REASON_BUILD_FAILED, REASON_PACKAGE, \
    REASON_UNSET, reasonDescription, STATE_COMPLETE, STATE_FAILED, \
    STATE_PREREQ_FAILED, STATE_SUCCESS, STATE_UNSET, stateDescription, stateName
from gump.core.model.stats import INSIGNIFICANT_DURATION, SIGNIFICANT_DURATION
from gump.core.model.workspace import Workspace
from gump.tool.guru.stats import StatisticsGuru
from gump.tool.guru.xref import XRefGuru
from gump.tool.shared.comparator import compareProjectsByFullDependeeCount
from gump.util import createOrderedList, getBeanAttributes, gumpSafeName, \
    inspectGarbageCollection
from gump.util.note import Annotatable, levelName
from gump.util.timing import getGeneralSinceDescription, secsToElapsedTimeString
from gump.util.tools import syncDirectories, copyDirectories, wipeDirectoryTree
from gump.util.work import CommandWorkItem, TimedWorkItem, Workable, \
    workTypeName

class XDocDocumenter(Documenter):

    def __init__(self, run, dirBase, urlBase):
        Documenter.__init__(self, run)

        # Configuration can be overridden to be
        # XDOCS, not the default of XHTML.
        self.config = XDocConfig(not run.getOptions().isXDocs())

        resolver = XDocResolver(dirBase, urlBase, self.config)
        self.setResolver(resolver)

    def prepareRun(self):

        log.debug('--- Prepare for Documenting Results')
        # Seed with default/site skins/etc.
        self.prepareXDoc()

    def processModule(self, module):
        self.documentModule(module, True)
        self.syncObject(module)

    def processProject(self, project):
        self.documentProject(project, True)
        self.syncObject(project)

        # Do once every ...
        if 0 == (project.getPositionIndex() % 5):
            self.documentBuildLog(True)
            self.syncBuildLog()

    def documentRun(self):

        log.debug('--- Documenting Results')

        # Document...
        self.documentRunDetails()
        self.documentWorkspace()
        self.documentEverythingElse()

        # Once a day...
        if self.run.getOptions().isOfficial():
            self.documentStatistics()
            self.documentXRef()

    #####################################################################
    #
    # XDocing...
    def getXDocWorkDirectory(self):
        if hasattr(self, 'workDir'):
            return self.workDir
        wdir = os.path.abspath(os.path.join(
                    self.workspace.getBaseDirectory(), 'xdocs-work'))
        if self.config.isXdocs():
            wdir = os.path.abspath(os.path.join(wdir, 'content'))
        if not os.path.exists(wdir):
            os.makedirs(wdir)
        self.workDir = wdir
        return self.workDir

    def getXDocLogDirectory(self):
        if hasattr(self, 'logDir'):
            return self.logDir
        ldir = self.workspace.getLogDirectory()
        if self.config.isXdocs():
            ldir = os.path.abspath(os.path.join(ldir, 'content'))
        if not os.path.exists(ldir):
            os.makedirs(ldir)
        self.logDir = ldir
        return self.logDir

    def getXDocTemplateDirectory(self):
        """ Template (XDoc skin/config) """
        templateName = 'forrest'
        if self.config.isXhtml():
            templateName = 'xhtml'
        fdir = os.path.abspath(os.path.join(dir.template, templateName))
        if self.config.isXdocs():
            fdir = os.path.abspath(os.path.join(fdir, 'content'))
        return fdir

    def getXDocSiteTemplateDirectory(self):
        """ Site Template (XDoc skin/config tweaks) """
        templateName = 'site-forrest'
        if self.config.isXhtml():
            templateName = 'site-xhtml'
        fdir = os.path.abspath(os.path.join(dir.template, templateName))
        if self.config.isXdocs():
            fdir = os.path.abspath(os.path.join(fdir, 'content'))
        return fdir

    def prepareXDoc(self):
        """

        Copy the main template (perhaps with site tweaks) to prepare

        """
        log.info('Prepare XDoc work with template')

        # First deleted the work tree (if exists), then ensure created
        xdocWorkDir = self.getXDocWorkDirectory()
        wipeDirectoryTree(xdocWorkDir)

        # Sync in the defaults [i.e. cleans also]
        xdocTemplate = self.getXDocTemplateDirectory()
        syncDirectories(xdocTemplate,
                        xdocWorkDir,
                        self.workspace)

        # Copy over the local site defaults (if any)
        xdocSiteTemplate = self.getXDocSiteTemplateDirectory()
        if os.path.exists(xdocSiteTemplate):
            log.info('Prepare XDoc work with *site* template')
            copyDirectories(xdocSiteTemplate,
                            xdocWorkDir,
                            self.workspace)

    def syncObject(self, obj):

        # Get relative path
        objDir = self.resolver.getDirectoryRelativePath(obj).serialize()

        # Get relative to (1) work [source] (2) log [target] & sync

        # Move xdocs from work directory to log
        xdocWorkDir = self.getXDocWorkDirectory()
        logDirectory = self.getXDocLogDirectory()

        workContents = os.path.abspath(os.path.join(xdocWorkDir, objDir))
        logContents = os.path.abspath(os.path.join(logDirectory, objDir))

        success = True
        try:
            if os.path.exists(workContents):
                # Sync over public pages...
                copyDirectories(workContents, logContents)
        except:
            log.error('--- Failed to sync [' + `objDir` + '] (work->log)',
                      exc_info = 1)
            success = False

        if self.config.isXdocs():
            # Move contents/xdocs from work directory to log
            # (Note: Forrest has contents/X and contents/xdocs/X)
            xdocWorkDir = os.path.abspath(os.path.join(xdocWorkDir, 'xdocs'))
            logDirectory = os.path.abspath(os.path.join(logDirectory, 'xdocs'))

            workContents = os.path.abspath(os.path.join(xdocWorkDir, objDir))
            logContents = os.path.abspath(os.path.join(logDirectory, objDir))

            try:
                if os.path.exists(workContents):
                    # Sync over public pages...
                    copyDirectories(workContents, logContents)
            except:
                log.error('--- Failed to sync xdocs [' + `objDir` + \
                              '] (work->log)', exc_info = 1)
                success = False

        return success

    def syncBuildLog(self):

        logSpec = self.resolver.getFileSpec(self.workspace, 'buildLog')

        xdocWorkDir = self.getXDocWorkDirectory()
        logDirectory = self.getXDocLogDirectory()

        if self.config.isXdocs():
            # Move contents/xdocs from work directory to log
            # (Note: Forrest has contents/X and contents/xdocs/X)
            xdocWorkDir = os.path.abspath(os.path.join(xdocWorkDir, 'xdocs'))
            logDirectory = os.path.abspath(os.path.join(logDirectory, 'xdocs'))

        # Current status
        logSource = os.path.abspath(
                    os.path.join(xdocWorkDir, logSpec.getDocument()))
        logTarget = os.path.abspath(
                    os.path.join(logDirectory, logSpec.getDocument()))

        # Do the transfer..
        success = True
        try:
            log.debug('Copy %s to %s' % (logSource, logTarget))
            copyfile(logSource, logTarget)
        except:
            log.error('--- Failed to sync buildLog work->log', exc_info = 1)
            success = False

        return success

    #####################################################################
    #
    # Workspace Pieces
    #
    def documentRunDetails(self):

        #
        # ----------------------------------------------------------------------
        #
        # Index.xml
        #
        spec = self.resolver.getFileSpec(self.run)

        document = XDocDocument('Gump Run',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        definitionSection = document.createSection('Run Details')

        if not self.gumpSet.isFull():
            self.documentPartial(definitionSection)

        definitionTable = definitionSection.createTable()
        definitionTable.createEntry('Gump Run GUID', self.run.getRunGuid())
        definitionTable.createEntry('Gump Run (Hex) GUID',
                                    self.run.getRunHexGuid())
        definitionTable.createEntry('Gump Version', setting.VERSION)

        # RSS|Atom|RDF
        self.documentXMLLinks(document, definitionTable,
                              depth = getDepthForObject(self.workspace))

        #rdfUrl = self.resolver.getUrl(self.workspace, 'gump', '.rdf')
        #rdfArea.createFork('http://www.feedvalidator.org/check.cgi?url=' + \
        #                       rdfUrl)\
        #                       .createIcon(self.resolver\
        #                                       .getImageUrl('valid-rdf.png'),
        #                                   alt='[Valid Atom]')
                                           #, title='Validate my Atom feed',
                                           #width='88', height='31')

        self.documentSummary(document, self.workspace.getProjectSummary())

        dtSection = definitionSection.createSection('Dates/Times')
        dtTable = dtSection.createTable()
        dtTable.createEntry('@@DATE@@', default.date_s)
        dtTable.createEntry('Start Date/Time (UTC)',
                            self.run.getStart().getUtc())
        dtTable.createEntry('End Date/Time (UTC)', self.run.getEnd().getUtc())
        dtTable.createEntry('Timezone', self.run.getEnvironment().getTimezone())
        dtTable.createEntry('Start Date/Time', self.run.getStart().getLocal())
        dtTable.createEntry('End Date/Time', self.run.getEnd().getLocal())
        dtTable.createEntry('Elapsed Time', self.run.getElapsedTimeString())

        pythonSection = definitionSection.createSection('Python Information')
        pythonTable = pythonSection.createTable()
        pythonTable.createEntry('Python', str(sys.version))
        pythonTable.createEntry('Operating System (Name)', str(os.name))
        tracked = inspectGarbageCollection()
        if tracked:
            pythonTable.createEntry('Garbage Collector Tracked', tracked)

        javaSection = definitionSection.createSection('Java Information')
        javaTable = javaSection.createTable()
        javaTable.createEntry('Java Command',
                              self.run.getEnvironment().javaCommand)
        javaproperties = self.run.getEnvironment().getJavaProperties()
        if javaproperties:
            for name in ['java.vendor', 'java.version', 'os.name', 'os.arch',
                         'os.version']:
                if name in javaproperties:
                    javaTable.createEntry(name, javaproperties[name])

        self.documentAnnotations(document, self.run)


        #
        # RunOptions
        #
        options = self.run.getOptions()

        optSection = document.createSection('Gump Run Options')
        optSection.createParagraph(
            """The options selected for this Gump run.""")

        #self.documentAnnotations(document, options)

        optTable = optSection.createTable(['Name', 'Value'])
        opts = 0

        descs = { 'Build':'Perform Build',
                  'XDocs':'Generate XDOCS',
                  'Statistics':'Update Statistics (to database)',
                  'Verbose':'Verbose Run',
                  'Cache':'Cache metadata (don\'t go to remote source)',
                  'Text':'Text Output',
                  'Official':'Official Run (e.g. nag notifies, etc.)',
                  'Results':'Generate Results' }

        # iterate over this suites properties
        for (name, value) in getBeanAttributes(options).items():
            desc = name
            if descs.has_key(name):
                desc = descs[name] + ' (' + name + ')'
            optTable.createEntry(desc, value)
            opts += 1

        if not opts:
            optTable.createEntry('None')

        #
        # Environment
        #
        environment = self.run.getEnvironment()

        envSection = document.createSection('Gump Environment')
        envSection.createParagraph(
            """The environment that this Gump run was within.""")

        propertiesSection = envSection.createSection('Properties')
        envTable = propertiesSection.createTable(['Name/Description', 'Value'])
        envs = 0
        # iterate over this suites properties
        for (name, value) in getBeanAttributes(environment).items():
            envTable.createEntry(name, str(value))
            envs += 1
        if not envs:
            envTable.createEntry('None')

        self.documentAnnotations(document, environment)
        #self.documentFileList(document, environment, 'Environment-level Files')
        self.documentWorkList(document, environment, 'Environment-level Work')

        document.serialize()
        document = None

    def documentXMLLinks(self, document = None, table = None, rdf = True,
                         depth = 0):
        """

        Show RSS|Atom|RDF.

        """
        if not table:
            table = document.createTable(['XML Description', 'Links'])

        rssSyndRow = table.createRow()
        rssSyndRow.createData().createStrong('RSS Syndication')
        rssArea = rssSyndRow.createData()
        rssArea.createFork('rss.xml', 'RSS')
        rssUrl = self.resolver.getUrl(self.workspace, 'rss', '.xml')
        rssArea.createFork('http://www.feedvalidator.org/check.cgi?url=' + \
                               rssUrl) \
                               .createIcon(self.resolver\
                                               .getImageUrl('valid-rss.png',
                                                            depth),
                                           alt = '[Valid RSS]')
                #, title = 'Validate my RSS feed', width = '88', height = '31')

        atomSyndRow = table.createRow()
        atomSyndRow.createData().createStrong('Atom Syndication')
        atomArea = atomSyndRow.createData()
        atomArea.createFork('atom.xml', 'Atom')
        atomUrl = self.resolver.getUrl(self.workspace, 'atom', '.xml')
        atomArea.createFork('http://www.feedvalidator.org/check.cgi?url=' + \
                                atomUrl) \
                                .createIcon(self.resolver\
                                                .getImageUrl('valid-atom.png',
                                                             depth),
                                            alt = '[Valid Atom]')
                #, title = 'Validate my Atom feed', width = '88', height = '31')

        if rdf:
            rdfRow = table.createRow()
            rdfRow.createData().createStrong('RDF Metadata')
            rdfArea = rdfRow.createData()
            rdfArea.createFork('gump.actor.rdf', 'RDF')

    def documentPartial(self, node):
        notice = node.createWarning()

        notice.createText(
            """This output does not represent the complete workspace,
            but part of it.
            Only projects, and their dependents, matching this regular expression """)
        notice.createStrong(self.gumpSet.projectexpression)
        notice.createBreak()
        notice.createBreak()
        notice.createStrong('Requested Projects: ')
        notice.createBreak()
        notice.createBreak()
        for project in self.gumpSet.projects:
            notice.createText(project.name)
            notice.createText(' ')

    def documentEverythingElse(self):

        self.documentRepositories()
        self.documentServers()
        self.documentTrackers()

        self.documentBuildLog()
        self.documentNotesLog()
        self.documentDiffsLog()

        self.documentProjects()
        self.documentModules()

        self.documentPackages()

        #
        # Document individual repositories
        #
        for repo in self.workspace.getRepositories():
            if not self.gumpSet.inRepositories(repo):
                continue
            self.documentRepository(repo)

        #
        # Document individual servers
        #
        for server in self.workspace.getServers():
            self.documentServer(server)

        # Document individual trackers
        for tracker in self.workspace.getTrackers():
            self.documentTracker(tracker)

        # Document individual modules
        for module in self.gumpSet.getCompletedModules():
            self.documentModule(module)

        # Document workspace 'Text'
        spec = self.resolver.getFileSpec(self.workspace, 'context')
        document = XDocDocument('Context',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())
        stream = StringIO.StringIO()
        texter = TextDocumenter(self.run, stream)
        texter.document()
        stream.seek(0)
        document.createSource(stream.read())
        stream.close()
        document.serialize()

        if not self.workspace.private:
            # Document the workspace XML
            spec = self.resolver.getFileSpec(self.workspace, 'workspace_defn')
            document = XDocDocument('Definition',
                                    spec.getFile(),
                                    self.config,
                                    spec.getRootPath())
            stream = StringIO.StringIO()
            try:
                self.workspace.dom.writexml(stream, indent = '   ', newl = '\n')
            except Exception, details:
                stream.write('Failed to XML serialize the data. ' \
                                 + str(details))
            stream.seek(0)
            document.createSource(stream.read())
            stream.close()
            document.serialize()

    #####################################################################
    #
    # Workspace
    #
    def documentWorkspace(self):


        #
        # ----------------------------------------------------------------------
        #
        # Index.xml
        #

        spec = self.resolver.getFileSpec(self.workspace)
        document = XDocDocument('Workspace',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        definitionSection = document.createSection('Workspace Definition')

        definitionTable = definitionSection.createTable()
        definitionTable.createEntry('Workspace Name',
                                    self.workspace.getName())
        if self.workspace.hasDomChild('description'):
            definitionTable.createEntry('Description',
                                        self.workspace\
                                            .getDomChildValue('description'))
        if self.workspace.hasDomChild('version'):
            definitionTable.createEntry('Workspace Version',
                self.workspace.getDomAttributeValue('version'))
        if not self.workspace.hasDomAttribute('version') \
            or not self.workspace.getDomAttributeValue('version') \
            == setting.WS_VERSION:
            definitionTable.createEntry('Gump Preferred Workspace Version',
                                        setting.WS_VERSION)
        definitionTable.createEntry('@@DATE@@', default.date_s)
        definitionTable.createEntry('Start Date/Time (UTC)',
                                    self.run.getStart().getUtc())
        definitionTable.createEntry('Start Date/Time',
                                    self.run.getStart().getLocal())
        definitionTable.createEntry('Timezone',
                                    self.run.getEnvironment().getTimezone())


        rssSyndRow = definitionTable.createRow()
        rssSyndRow.createData('Syndication')
        rssSyndRow.createData().createFork('rss.xml', 'RSS')
        atomSyndRow = definitionTable.createRow()
        atomSyndRow.createData('Syndication')
        atomSyndRow.createData().createFork('atom.xml', 'Atom')

        textRow = definitionTable.createRow()
        textRow.createData('Workspace Documentation')
        textRow.createData().createLink('context.html', 'Text')

        if not self.workspace.private:
            syndRow = definitionTable.createRow()
            syndRow.createData('Definition')
            syndRow.createData().createLink('workspace_defn.html', 'XML')

        self.documentAnnotations(document, self.workspace)
        #self.documentXML(document, self.workspace)

        detailsSection = document.createSection('Details')

        detailsTable = detailsSection.createTable()
        detailsTable.createEntry("State : ",
                                 self.workspace.getStateDescription())

        e = self.workspace.getElapsedTimeString()
        if e:
            detailsTable.createEntry("Elapsed Time : ", e)
        detailsTable.createEntry("Base Directory : ",
                                 self.workspace.getBaseDirectory())
        detailsTable.createEntry("Temporary Directory : ",
                                 self.workspace.tmpdir)
        #if self.workspace.scratchdir:
        #    detailsTable.createEntry("Scratch Directory : ",
        #                             self.workspace.scratchdir))
        # :TODO: We have duplicate dirs? tmp = scratch?
        detailsTable.createEntry("Log Directory : ",
                                 self.workspace.logdir)
        detailsTable.createEntry("Outputs Repository : ",
                                 self.workspace.repodir)
        detailsTable.createEntry("CVS Directory : ", self.workspace.cvsdir)
        detailsTable.createEntry("Package Directory : ", self.workspace.pkgdir)
        if not self.workspace.private:
            detailsTable.createEntry("E-mail Server: ",
                                     self.workspace.mailserver)
            detailsTable.createEntry("E-mail Port: ", self.workspace.mailport)
            detailsTable.createEntry("List Address: ",
                                     self.workspace.administrator)
            detailsTable.createEntry("E-mail Address: ", self.workspace.email)
            detailsTable.createEntry("Prefix: ", self.workspace.prefix)
            detailsTable.createEntry("Signature: ", self.workspace.signature)

        self.documentStats(document, self.workspace)
        self.documentProperties(detailsSection, self.workspace,
                                'Workspace Properties')

        # Does this self.workspace send notification (nag) mails?
        detailsTable.createEntry("Send Notification E-mails: ",
                                 `self.workspace.isNotify()`)

        detailsTable.createEntry("Multi-threading: ",
                                 `self.workspace.isMultithreading()`)
        if self.workspace.isMultithreading():
            detailsTable.createEntry("Updater Threads: ",
                                     `self.workspace.getUpdaters()`)
            detailsTable.createEntry("Builder Threads: ",
                                     `self.workspace.getBuilders()`)

        #document.createRaw('<p><strong>Context Tree:</strong> ' + \
        #                       '<link href=\'workspace.html\'>workspace' + \
        #                       '</link></p>')
        #x.write('<p><strong>Workspace Config:</strong> ' + \
        #            '<link href=\'xml.txt\'>XML</link></p>')
        #x.write('<p><strong>RSS :</strong> <link href=\'index.rss\'>' + \
        #            'News Feed</link></p>')

        self.documentFileList(document, self.workspace, 'Workspace-level Files')
        self.documentWorkList(document, self.workspace, 'Workspace-level Work')

        document.serialize()
        document = None


    def documentRepositories(self):

        #
        # ----------------------------------------------------------------------
        #
        # Repositories.xml
        #
        spec = self.resolver.getFileSpec(self.workspace, 'repositories')
        document = XDocDocument('All Repositories',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())


        reposSection = document.createSection('All Repositories')
        reposTable = reposSection.createTable(['Name'])

        # Pretty sorting...
        sortedRepositoryList = createOrderedList(self.gumpSet.getRepositories())

        rcount = 0
        for repo in sortedRepositoryList:
            if not self.gumpSet.inRepositories(repo):
                continue

            rcount += 1

            repoRow = reposTable.createRow()
            repoRow.createComment(repo.getName())

            self.insertLink(repo, self.workspace, repoRow.createData())

        if not rcount:
            reposTable.createLine('None')

        document.serialize()
        document = None

    def documentServers(self):

        #
        # ----------------------------------------------------------------------
        #
        # Servers.xml
        #
        spec = self.resolver.getFileSpec(self.workspace, 'servers')
        document = XDocDocument('All Servers',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        serversSection = document.createSection('All Servers')
        serversTable = serversSection.createTable(['Name', 'Status', 'Notes',
                                                   'Results', 'Start (Local)',
                                                   'Start (UTC)', 'End (UTC)',
                                                   'Offset (from UTC)'])

        sortedServerList = createOrderedList(self.workspace.getServers())

        scount = 0
        for server in sortedServerList:

            scount += 1

            serverRow = serversTable.createRow()
            serverRow.createComment(server.getName())

            self.insertLink(server, self.workspace, serverRow.createData())

            if server.isUp():
                serverRow.createData('Up')
            else:
                serverRow.createData().createStrong('Down')

            if server.hasNote():
                serverRow.createData(server.getNote())
            else:
                serverRow.createData('')

            if server.hasResultsUrl():
                serverRow.createData().createFork(server.getResultsUrl(),
                                                  'Results')
            else:
                serverRow.createData('Not Available')

            if server.hasResults():
                serverRow.createData(server.getResults().getStart().getLocal())
                serverRow.createData(server.getResults().getEnd().getLocal())
                serverRow.createData(server.getResults().getTimezoneOffset())
            else:
                serverRow.createData('N/A')
                serverRow.createData('N/A')
                serverRow.createData('N/A')
                serverRow.createData('N/A')


        if not scount:
            serversTable.createLine('None')

        document.serialize()

    def documentTrackers(self):
        #
        # ----------------------------------------------------------------------
        #
        # Trackers.xml
        #
        spec = self.resolver.getFileSpec(self.workspace, 'trackers')
        document = XDocDocument('All Trackers',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        trackersSection = document.createSection('All Trackers')
        trackersTable = trackersSection.createTable(['Name'])

        sortedTrackerList = createOrderedList(self.workspace.getTrackers())

        scount = 0
        for tracker in sortedTrackerList:

            scount += 1

            trackerRow = trackersTable.createRow()
            trackerRow.createComment(tracker.getName())

            self.insertLink(tracker, self.workspace, trackerRow.createData())

        if not scount:
            trackersTable.createLine('None')

        document.serialize()

    def documentBuildLog(self, realTime = False):
        #
        # buildLog.xml -- Modules/Projects in build order
        #
        spec = self.resolver.getFileSpec(self.workspace, 'buildLog')
        document = XDocDocument('Gump Build Log',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        if realTime:

            # Work done...
            modules = len(self.gumpSet.getCompletedModules())
            projects = len(self.gumpSet.getCompletedProjects())

            document.createWarning(
                """This Gump run is currently in progress.
            It started at %s. As of this moment (%s), %s modules have been updated, and %s projects built.""" \
                    % (self.run.getStart().getLocal(),
                       time.strftime('%H:%M:%S'), modules, projects ))

#            document.createNote(
#                """Only projects with significant information
#            (e.g a recent change of state, a failure, etc.) are listed at runtime.""")

        else:
            document.createNote("""This Gump run is complete.
            It started at %s and ended at %s."""
                % (self.run.getStart().getLocal(),
                    self.run.getEnd().getLocal()))

        if not self.gumpSet.isFull():
            self.documentPartial(document)

        if not realTime:
            self.documentSummary(document, self.workspace.getProjectSummary())

        if not realTime:
            #
            # Modules...
            #
            modulesSection = document.createSection('Modules (in update order)')
            modulesTable = modulesSection.createTable(['Index', 'Updated',
                                                       'Name', 'State',
                                                       'Duration\nin state',
                                                       'Last Modified',
                                                       'Notes'])
            mcount = 0
            for module in self.gumpSet.getCompletedModules():

                mcount += 1

                moduleRow = modulesTable.createRow()
                moduleRow.createComment(module.getName())

                self.setStyleFromState(moduleRow, module.getStatePair())

                moduleRow.createData(module.getPositionIndex())

                if module.hasStart():
                    startData = moduleRow.createData(module.getStart()\
                                                         .getLocal())
                else:
                    startData = moduleRow.createData('-')

                self.setStyleFromState(startData, module.getStatePair())

                self.insertLink(module, self.workspace, moduleRow.createData())
                self.insertStateIcon(module, self.workspace,
                                     moduleRow.createData())
                moduleRow.createData(module.getStats().sequenceInState)
                moduleRow.createData(
                    getGeneralSinceDescription(
                        module.getStats().getLastModified()))

                notes = ''
                if module.isVerbose():
                    if notes:
                        notes += ' '
                    notes += 'Verbose'
                if module.isDebug():
                    if notes:
                        notes += ' '
                    notes += 'Debug'
                moduleRow.createData(notes)

            if not mcount:
                modulesTable.createLine('None')

        #
        # Projects...
        #
        projectsSection = document.createSection('Projects (in build order)')
        projectsTable = projectsSection.createTable(['Index', 'Time', 'Name',
                                                     'State',
                                                     'Duration\nin state',
                                                     'Last Modified', 'Notes'])
        pcount = 0
        for project in self.gumpSet.getCompletedProjects():

            # Hack for bad data.
            if not project.inModule():
                continue

            #if realTime and \
            #        (project.getState()==STATE_FAILED or \
            #             ((project.getState()<>STATE_PREREQ_FAILED) and \
            #                  (project.getStats().sequenceInState \
            #                       < INSIGNIFICANT_DURATION))):
            #    continue

            pcount += 1

            projectRow = projectsTable.createRow()
            projectRow.createComment(project.getName())

            self.setStyleFromState(projectRow, project.getStatePair())

            projectRow.createData(project.getPositionIndex())

            if project.hasStart():
                projectRow.createData(project.getStart().getLocal())
            else:
                projectRow.createData('-')

            self.insertLink(project, self.workspace, projectRow.createData())
            self.insertStateIcon(project, self.workspace,
                                 projectRow.createData())
            projectRow.createData(project.getStats().sequenceInState)
            projectRow.createData(getGeneralSinceDescription(
                    project.getModule().getStats().getLastModified()))

            notes = ''
            if project.isVerbose():
                if notes:
                    notes += ' '
                notes += 'Verbose'
            if project.isDebug():
                if notes:
                    notes += ' '
                notes += 'Debug'
            projectRow.createData(notes)

        if not pcount:
            projectsTable.createLine('None')

        document.serialize()
        document = None

    def documentNotesLog(self):
        #
        # ----------------------------------------------------------------------
        #
        # notesLog.xml -- Notes log
        #
        spec = self.resolver.getFileSpec(self.workspace, 'notesLog')
        document = XDocDocument('Annotations',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        notesSection = document.createSection('Negative Annotations')
        notesSection.createParagraph(
            """This page displays entities with errors and/or warning annotations.""")

        ncount = 0
        for module in self.gumpSet.getCompletedModules():

            moduleSection = None

            if module.containsNasties():
                moduleSection = document.createSection('Module : ' \
                                                           + module.getName())
                # Link to the module
                self.insertLink(module, self.workspace,
                                moduleSection.createParagraph())

                # Display the module annotations
                self.documentAnnotations(moduleSection, module, 1)

            for project in module.getProjects():
                if not self.gumpSet.inProjectSequence(project):
                    continue
                if not project.containsNasties():
                    continue

                if not moduleSection:
                    moduleSection = document.createSection('Module : ' + \
                                                               module.getName())

                projectSection = moduleSection.createSection('Project : ' + \
                                                                 project\
                                                                 .getName())

                # Link to the project
                self.insertLink(project, self.workspace,
                                projectSection.createParagraph())

                # Display the annotations
                self.documentAnnotations(projectSection, project, 1)

                ncount += 1

        if not ncount:
            notesSection.createParagraph('None.')

        document.serialize()

    def documentDiffsLog(self):

        #
        # ----------------------------------------------------------------------
        #
        # diffsLog.xml -- Server Differences log
        #
        spec = self.resolver.getFileSpec(self.workspace, 'diffsLog')
        document = XDocDocument('Server Differences',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        diffsSection = document.createSection('Server Differences')
        diffsSection.createParagraph(\
            """This page displays entities with different states on different servers.""")

        dcount = 0
        for module in self.gumpSet.getCompletedModules():

            moduleSection = None
            if module.hasServerResults() \
                and module.getServerResults().hasDifferences() \
                and module.getServerResults().containsFailure() :
                moduleSection = document.createSection('Module : ' + \
                                                           module.getName())
                # Link to the module
                self.insertLink(module, self.workspace,
                                moduleSection.createParagraph())

                # Display the module server links
                self.documentServerLinks(moduleSection, module,
                                         getDepthForObject(self.workspace))

            for project in module.getProjects():
                if not self.gumpSet.inProjectSequence(project) \
                        or not project.hasServerResults() \
                        or not project.getServerResults().hasDifferences() \
                        or not project.getServerResults().containsFailure():
                    continue

                if not moduleSection:
                    moduleSection = document.createSection('Module : ' + \
                                                               module.getName())

                projectSection = moduleSection.createSection('Project : ' + \
                                                                 project\
                                                                 .getName())

                # Link to the project
                self.insertLink(project, self.workspace,
                                projectSection.createParagraph())

                # Display the project server links
                self.documentServerLinks(projectSection, project,
                                         getDepthForObject(self.workspace))

                dcount += 1

        if not dcount:
            diffsSection.createParagraph('None.')

        document.serialize()

    def documentProjects(self):

        sortedProjectList = createOrderedList(self.gumpSet.getProjectSequence())

        #
        # ----------------------------------------------------------------------
        #
        # project_todos.xml -- Projects w/ issues in build order
        #
        spec = self.resolver.getFileSpec(self.workspace, 'project_todos')
        document = XDocDocument('Projects with issues',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())
        self.documentSummary(document, self.workspace.getProjectSummary())

        totalAffected = 0

        projectsSection = document.createSection('Projects with issues...')
        projectsSection.createParagraph(\
            """These are the project that need 'fixing'.
This page helps Gumpmeisters (and others) locate the main areas to focus attention.""")
        projectsTable = projectsSection.createTable(['Name',
                                                     'Dependees', 'Affected',
                                                     'Project State',
                                                     'Duration\nin state'])
        pcount = 0

        depOrder = createOrderedList(sortedProjectList,
                                     compareProjectsByFullDependeeCount)

        for project in depOrder:
            # Hack for bad data
            if not project.inModule():
                continue

            if not self.gumpSet.inProjectSequence(project):
                continue

            if not project.getState() == STATE_FAILED:
                continue

            pcount += 1

            #
            # Determine the number of projects this module (or its projects)
            # cause not to be run.
            #
            affected = project.countAffectedProjects()

            totalAffected += affected


            projectRow = projectsTable.createRow()
            projectRow.createComment(project.getName())

            self.insertLink(project, self.workspace, projectRow.createData())

            projectRow.createData(project.getFullDependeeCount())
            projectRow.createData(affected)

            self.insertStateIcon(project, self.workspace,
                                 projectRow.createData())

            # How long been like this
            seq = project.getStats().sequenceInState
            projectRow.createData(seq)

        if not pcount:
            projectsTable.createLine('None')
        else:
            projectsSection.createParagraph(
                    'Total Affected Projects: ' + str(totalAffected))

        document.serialize()

        #
        # ----------------------------------------------------------------------
        #
        # project_fixes.xml -- Projects w/ fixes in build order
        #
        spec = self.resolver.getFileSpec(self.workspace, 'project_fixes')
        document = XDocDocument('Project Fixes',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())
        self.documentSummary(document, self.workspace.getProjectSummary())

        projectsSection = document.createSection('Projects recently fixed...')
        projectsSection.createParagraph(\
            """These are the projects that were 'fixed' (state changed to success from failed) within %s runs.
This page helps Gumpmeisters (and others) observe community progress.
        """ % INSIGNIFICANT_DURATION)

        projectsTable = projectsSection.createTable(['Name', 'Dependees',
                                                     'Project State',
                                                     'Duration\nin state'])
        pcount = 0
        for project in sortedProjectList:
            # Hack for bad data
            if not project.inModule():
                continue
            # Filter
            if not self.gumpSet.inProjectSequence(project):
                continue

            if not project.getState() == STATE_SUCCESS or \
                not project.getStats().previousState == STATE_FAILED or \
                not project.getStats().sequenceInState < INSIGNIFICANT_DURATION:
                continue

            pcount += 1

            projectRow = projectsTable.createRow()
            projectRow.createComment(project.getName())

            self.insertLink(project, self.workspace, projectRow.createData())

            projectRow.createData(project.getFullDependeeCount())

            self.insertStateIcon(project, self.workspace,
                                 projectRow.createData())

            # How long been like this
            seq = project.getStats().sequenceInState
            projectRow.createData(seq)

        if not pcount:
            projectsTable.createLine('None')

        document.serialize()

        #
        # ----------------------------------------------------------------------
        #
        # project_prereqs.xml -- Projects w/ prereqs in build order
        #
        spec = self.resolver.getFileSpec(self.workspace, 'project_prereqs')
        document = XDocDocument('Project Prerequisite Failures',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())
        self.documentSummary(document, self.workspace.getProjectSummary())

        projectsSection = document.createSection('Projects recently fixed...')
        projectsSection.createParagraph(\
            """These are the projects that depend upon others being fixed before they can be built.""")

        projectsTable = projectsSection.createTable(['Name', 'Depends',
                                                     'Not-Built Depends',
                                                     'Project State',
                                                     'Duration\nin state'])
        pcount = 0
        for project in sortedProjectList:
            # Hack for bad data
            if not project.inModule():
                continue
            # Filter
            if not self.gumpSet.inProjectSequence(project):
                continue

            if not project.getState() == STATE_PREREQ_FAILED:
                continue

            pcount += 1

            projectRow = projectsTable.createRow()
            projectRow.createComment(project.getName())

            self.insertLink(project, self.workspace, projectRow.createData())

            projectRow.createData(project.getFullDependencyCount())

            # Count unbuilt dependencies
            unbuilt = 0
            for dep in project.getFullDependencyProjectList():
                if not dep.isSuccess():
                    unbuilt += 1
            projectRow.createData(unbuilt)

            self.insertStateIcon(project, self.workspace,
                                 projectRow.createData())

            # How long been like this
            seq = project.getStats().sequenceInState
            projectRow.createData(seq)

        if not pcount:
            projectsTable.createLine('None')

        document.serialize()

    def documentModules(self):

        #
        # ----------------------------------------------------------------------
        #
        # module_todos.xml
        #
        spec = self.resolver.getFileSpec(self.workspace, 'module_todos')
        document = XDocDocument('Modules with issues',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        modulesSection = document.createSection('Modules with TODOs')
        modulesSection.createParagraph(\
            """These are the modules that need 'fixing', or contained projects that need fixing.
This page helps Gumpmeisters (and others) locate the main areas to focus attention.""")
        modulesTable = modulesSection.createTable(['Name', 'Duration\nin state',
                                                   'Module State',
                                                   'Project State(s)',
                                                   'Elapsed'])

        mcount = 0
        for module in self.gumpSet.getCompletedModules():

            #
            # Determine if there are todos, otherwise continue
            #
            todos = 0
            for pair in module.aggregateStates():
                if pair.state == STATE_FAILED:
                    todos = 1
            if not todos:
                continue
            # Shown something...
            mcount += 1

            # Determine longest sequence in this (failed) state...
            # for any of the projects
            seq = 0
            for project in module.getProjects():
                if project.getState() == STATE_FAILED:
                    stats = project.getStats()
                    if stats.sequenceInState > seq:
                        seq = stats.sequenceInState

            # Determine the number of projects this module (or its projects)
            # cause not to be run.

            # Display
            moduleRow = modulesTable.createRow()
            moduleRow.createComment(module.getName())
            self.insertLink(module, self.workspace, moduleRow.createData())

            moduleRow.createData(seq)

            self.insertStateIcon(module, self.workspace, moduleRow.createData())
            self.insertStateIcons(module, self.workspace,
                                  moduleRow.createData())

            moduleRow.createData(secsToElapsedTimeString(module\
                                                             .getElapsedSecs()))

        if not mcount:
            modulesTable.createLine('None')

        document.serialize()


        #
        # ----------------------------------------------------------------------
        #
        # module_fixes.xml
        #
        spec = self.resolver.getFileSpec(self.workspace, 'module_fixes')
        document = XDocDocument('Modules with fixes',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        modulesSection = document.createSection('Modules recently fixed')
        modulesSection.createParagraph(\
            """These are the modules that were 'fixed' (state changed to success), or contained projects that were fixed, within %s runs.
This page helps Gumpmeisters (and others) observe community progress.
        """ % INSIGNIFICANT_DURATION)

        modulesTable = modulesSection.createTable(['Name', 'Duration\nin state',
                                                   'Module State',
                                                   'Project State(s)',
                                                   'Elapsed'])

        mcount = 0
        for module in self.gumpSet.getCompletedModules():

            #
            # Determine if there are mcount, otherwise continue
            #
            mcount = 0
            for pair in module.aggregateStates():
                if pair.state == STATE_SUCCESS \
                    and module.getStats().sequenceInState < \
                    INSIGNIFICANT_DURATION:
                    mcount = 1

            if not mcount:
                continue

            # Shown something...
            mcount += 1

            # Determine longest sequence in this (failed) state...
            # for any of the projects
            seq = 0
            for project in module.getProjects():
                if project.getState() == STATE_FAILED:
                    stats = project.getStats()
                    if stats.sequenceInState > seq:
                        seq = stats.sequenceInState

            # Display
            moduleRow = modulesTable.createRow()
            moduleRow.createComment(module.getName())
            self.insertLink(module, self.workspace, moduleRow.createData())

            moduleRow.createData(seq)

            self.insertStateIcon(module, self.workspace, moduleRow.createData())
            self.insertStateIcons(module, self.workspace,
                                  moduleRow.createData())

            moduleRow.createData(secsToElapsedTimeString(module\
                                                             .getElapsedSecs()))

        if not mcount:
            modulesTable.createLine('None')

        document.serialize()


    def documentPackages(self):

        #
        # ----------------------------------------------------------------------
        #
        # Packages.xml
        #
        spec = self.resolver.getFileSpec(self.workspace, 'packages')
        document = XDocDocument('Packages',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        mpkgSection = document.createSection('Packaged Modules')
        mpkgTable = mpkgSection.createTable(['Name', 'State',
                                             'Project State(s)'])
        mcount = 0
        for module in self.gumpSet.getCompletedModules():

            packaged = 0
            #
            # Determine if there are packages, otherwise continue
            #
            if module.getState() == STATE_COMPLETE and \
                module.getReason() == REASON_PACKAGE:
                packaged = 1

            if not packaged:
                continue

            mcount += 1

            moduleRow = mpkgTable.createRow()
            moduleRow.createComment(module.getName())
            self.insertLink(module, self.workspace, moduleRow.createData())
            self.insertStateIcon(module, self.workspace, moduleRow.createData())
            self.insertStateIcons(module, self.workspace,
                                  moduleRow.createData())

        if not mcount:
            mpkgTable.createLine('None')

        pkgsSection = document.createSection('Packaged Projects')
        packages = self.gumpSet.getPackagedProjects()
        if packages:
            pkgsTable = pkgsSection.createTable(['Name', 'State', 'Location'])
            for project in self.gumpSet.getProjectSequence():
                if not self.gumpSet.inProjectSequence(project):
                    continue
                if not project.isPackaged():
                    continue

                packageRow = pkgsTable.createRow()
                packageRow.createComment(project.getName())

                self.insertLink(project, self.workspace,
                                 packageRow.createData())
                self.insertStateIcon(project, self.workspace,
                                      packageRow.createData())

                packageRow.createData(project.getHomeDirectory())
        else:
            pkgsSection.createNote('No packaged projects installed.')

        document.serialize()


    def documentRepository(self, repo):

        spec = self.resolver.getFileSpec(repo)
        document = XDocDocument('Repository : ' + repo.getName(),
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        # Provide a description/link back to the repo site.
        #descriptionSection = document.createSection('Description')
        #description = ''
        #if repo.hasDescription():
        #    description = escape(repo.getDescription())
        #    if not description.strip().endswith('.'):
        #        description += '. '
        #if not description:
        #    description = 'No description provided.'
        #if repo.hasURL():
        #    description += ' For more information, see: ' + \
        #        self.getFork(repo.getUrl())
        #else:
        #    description += ' (No repo URL provided).'
        #
        #descriptionSection.createParagraph().createRaw(description)

        self.documentAnnotations(document, repo)

        detailSection = document.createSection('Repository Details')
        detailList = detailSection.createList()

        if repo.hasTitle():
            detailList.createEntry('Title: ', repo.getTitle())

        if repo.hasScmType():
            detailList.createEntry('Type: ', repo.getScmType().name)

        if repo.hasHomePage():
            detailList.createEntry('Homepage: ') \
                .createLink(repo.getHomePage(), repo.getHomePage())

        if repo.hasWeb():
            detailList.createEntry('Web Interface: ') \
                .createLink(repo.getWeb(), repo.getWeb())

        detailList.createEntry('State: ' + repo.getStateDescription())
        if not repo.getReason() == REASON_UNSET:
            detailList.createEntry('Reason: ', repo.getReasonDescription())

        if repo.hasUser():
            detailList.createEntry('Username: ', repo.getUser())

        if repo.hasMethod():
            detailList.createEntry('Method: ', repo.getMethod())

        if repo.hasPath():
            detailList.createEntry('Path: ', repo.getPath())

        if repo.hasHostname():
            detailList.createEntry('Hostname: ', repo.getHostname())

        detailList.createEntry('Redistributable: ', `repo.isRedistributable()`)

        self.documentXML(document, repo)

        self.documentFileList(document, repo, 'Repository-level Files')
        self.documentWorkList(document, repo, 'Repository-level Work')

        document.serialize()

    def documentServer(self, server):

        spec = self.resolver.getFileSpec(server)
        document = XDocDocument('Server : ' + server.getName(),
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        # Provide a description/link back to the server site.
        #descriptionSection = document.createSection('Description')
        #description = ''
        #if server.hasDescription():
        #    description = escape(server.getDescription())
        #    if not description.strip().endswith('.'):
        #        description += '. '
        #if not description:
        #    description = 'No description provided.'
        #if server.hasURL():
        #    description += ' For more information, see: ' + \
        #        self.getFork(server.getUrl())
        #else:
        #    description += ' (No server URL provided).'
        #
        #descriptionSection.createParagraph().createRaw(description)

        self.documentAnnotations(document, server)

        detailSection = document.createSection('Server Details')
        detailList = detailSection.createList()

        detailList.createEntry('Name: ', server.getName())

        if server.isUp():
            detailList.createEntry('Status: ', 'Up')
        else:
            detailList.createEntry('Status: ', 'Down')

        if server.hasType():
            detailList.createEntry('Type: ', server.getType())

        if server.hasTitle():
            detailList.createEntry('Title: ', server.getTitle())

        if server.hasUrl():
            detailList.createEntry('URL: ').createFork(
                server.getUrl(), server.getUrl())

            # Parent 'site' (owner reference)
            if server.hasSite() and not server.getSite() == server.getUrl():
                detailList.createEntry('Site: ').createFork(
                    server.getSite(), server.getSite())

        if server.hasResults():
            # :TODO: Do a lot more ....
            if server.hasResultsUrl():
                detailList.createEntry('Results URL: ').createFork(
                    server.getResultsUrl(), server.getResultsUrl())

                detailList.createEntry('Timezone Offset: ',
                                       server.getResults().getTimezoneOffset())

                detailList.createEntry('Start Time: ',
                                       server.getResults().getStartDateTime() \
                                           + ' ' + \
                                           server.getResults().getTimezone())

                detailList.createEntry('End Time: ',
                                       server.getResults().getEndDateTime() \
                                           + ' ' + \
                                           server.getResults().getTimezone())

                detailList.createEntry('Start Time (UTC): ',
                                       server.getResults()\
                                           .getStartDateTimeUtc())
                detailList.createEntry('End Time (UTC): ',
                                       server.getResults().getEndDateTimeUtc())


        self.documentXML(document, server)

        self.documentFileList(document, server, 'Server-level Files')
        self.documentWorkList(document, server, 'Server-level Work')

        document.serialize()


    def documentTracker(self, tracker):

        spec = self.resolver.getFileSpec(tracker)
        document = XDocDocument('Tracker : ' + tracker.getName(),
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        # Provide a description/link back to the tracker site.
        #descriptionSection = document.createSection('Description')
        #description = ''
        #if tracker.hasDescription():
        #    description = escape(tracker.getDescription())
        #    if not description.strip().endswith('.'):
        #        description += '. '
        #if not description:
        #    description = 'No description provided.'
        #if tracker.hasURL():
        #    description += ' For more information, see: ' + \
        #        self.getFork(tracker.getUrl())
        #else:
        #    description += ' (No tracker URL provided).'
        #
        #descriptionSection.createParagraph().createRaw(description)

        self.documentAnnotations(document, tracker)

        detailSection = document.createSection('Tracker Details')
        detailList = detailSection.createList()

        detailList.createEntry('Name: ', tracker.getName())

        if tracker.hasType():
            detailList.createEntry('Type: ', tracker.getType())

        if tracker.hasTitle():
            detailList.createEntry('Title: ', tracker.getTitle())

        if tracker.hasUrl():
            detailList.createEntry('URL: ').createFork(
                tracker.getUrl(), tracker.getUrl())

            # Parent 'site' (owner reference)
            if tracker.hasSite() and not tracker.getSite() == tracker.getUrl():
                detailList.createEntry('Site: ').createFork(
                    tracker.getSite(), tracker.getSite())

        self.documentXML(document, tracker)

        self.documentFileList(document, tracker, 'Tracker-level Files')
        self.documentWorkList(document, tracker, 'Tracker-level Work')

        document.serialize()


    def documentModule(self, module, realTime = False):

        spec = self.resolver.getFileSpec(module)
        document = XDocDocument('Module : ' + module.getName(),
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        # Provide a description/link back to the module site.
        descriptionSection = document.createSection('Description')
        description = ''
        if module.hasDescription():
            description = escape(module.getDescription())
            if not description.strip().endswith('.'):
                description += '. '
        if not description:
            description = 'No description provided.'
        if module.hasUrl():
            description += ' For more information, see: ' \
                + self.getFork(module.getUrl())
        else:
            description += ' (No module URL provided).'

        descriptionSection.createParagraph().createRaw(description)

        metadataLocation = module.getMetadataLocation()
        metadataUrl = module.getMetadataViewUrl()
        if metadataLocation and metadataUrl:
            descriptionSection.createParagraph('Gump Metadata: ')\
                .createFork(metadataUrl, metadataLocation)

        # RSS|Atom
        self.documentXMLLinks(document, None, False,
                              depth = getDepthForObject(module))

        if module.cause and not module == module.cause:
            self.insertTypedLink(module.cause, module,
                                 document\
                                     .createNote("This module failed due to: "))

        if module.isPackaged():
            document.createNote('This is a packaged module, not Gumped.')

        stateSection = document.createSection('State')
        stateList = stateSection.createList()
        stateList.createEntry("State: " + module.getStateDescription())
        if not module.getReason() == REASON_UNSET:
            stateList.createEntry("Reason: ", module.getReasonDescription())
        if module.cause and not module == module.cause:
            self.insertTypedLink(module.cause, module,
                                 stateList.createEntry("Root Cause: "))

        self.documentAnnotations(document, module)
        self.documentServerLinks(document, module)

        if not realTime:
            projectsSection = document.createSection('Projects')
            if (len(module.getProjects()) > 1):
                self.documentSummary(projectsSection,
                                     module.getProjectSummary())

            if (len(module.getProjects()) > 1):
                ptodosSection = projectsSection\
                    .createSection('Projects with Issues')
                ptodosTable = ptodosSection.createTable(['Name', 'State',
                                                         'Elapsed'])
                pcount = 0
                for project in module.getProjects():
                    if not self.gumpSet.inProjectSequence(project):
                        continue

                    #
                    # Determine if there are todos, otherwise continue
                    #
                    todos = 0
                    for pair in project.aggregateStates():
                        if pair.state == STATE_FAILED:
                            todos = 1

                    if not todos:
                        continue

                    pcount += 1

                    projectRow = ptodosTable.createRow()
                    projectRow.createComment(project.getName())
                    self.insertLink(project, module, projectRow.createData())
                    self.insertStateIcon(project, module,
                                         projectRow.createData())
                    projectRow\
                        .createData(\
                        secsToElapsedTimeString(project.getElapsedSecs()))

                    if not pcount:
                        ptodosTable.createLine('None')

            pallSection = projectsSection.createSection('All Projects')
            pallTable = pallSection.createTable(['Name', 'State', 'Elapsed'])

            pcount = 0
            for project in module.getProjects():
                if not self.run.getGumpSet().inProjectSequence(project):
                    continue
                pcount += 1

                projectRow = pallTable.createRow()
                projectRow.createComment(project.getName())
                self.insertLink(project, module, projectRow.createData())
                self.insertStateIcon(project, module, projectRow.createData())
                projectRow\
                    .createData(secsToElapsedTimeString(project\
                                                            .getElapsedSecs()))

            if not pcount:
                pallTable.createLine('None')

        self.documentStats(document, module, realTime)
        self.documentFileList(document, module, 'Module-level Files')
        self.documentWorkList(document, module, 'Module-level Work')

        #addnSection = document.createSection('Additional Details')
        #addnPara = addnSection.createParagraph()
        #addnPara.createLink('index_details.html',
        #                    'More module details ...')
        #
        #document.serialize()
        #
        #document = XDocDocument('Module Details : ' + module.getName(),
        #            self.resolver.getFile(module,
        #                            'index_details'))

        detailsSection = None

        if module.hasRepository():

            if not detailsSection:
                detailsSection = document.createSection('Details')

            repoSection = detailsSection.createSection('Repository')
            repoList = repoSection.createList()
            self.insertLink(module.getRepository(),
                            module,
                            repoList.createEntry("Repository: ") )

            scm = module.getScm()
            if scm:
                scmName = scm.getScmType().displayName
                if scm.hasDir():
                    repoList.createEntry(scmName + " Directory: ",
                                         scm.getDir())
                if scm.getScmType() == SCM_TYPE_CVS:
                    if scm.hasModule():
                        repoList.createEntry(scmName + " Module: ",
                                             scm.getModule())

                    if scm.hasTag():
                        repoList.createEntry(scmName + " Tag: ", scm.getTag())

                    if scm.hasHostPrefix():
                        repoList.createEntry(scmName + " Host Prefix: ",
                                             scm.getHostPrefix())

                    repoList.createEntry("CVSROOT: ", scm.getCvsRoot())

                elif scm.getScmType() == SCM_TYPE_P4:
                    if scm.hasTag():
                        repoList.createEntry(scmName + " Tag: ", scm.getTag())

                    repoList.createEntry(scmName + " Port: ", scm.getPort())
                    repoList.createEntry(scmName + " Clientspec: ",
                                         scm.getClientspec())

                repoList.createEntry(scmName + " URL: ", scm.getRootUrl())


            repoList.createEntry('Redistributable: ',
                                 module.isRedistributable())

        document.serialize()
        document = None

        if not realTime:
            # Document Projects
            for project in module.getProjects():
                if not self.run.getGumpSet().inProjectSequence(project):
                    continue
                self.documentProject(project)

    # Document the module XML
    #    x = startXDoc(getModuleXMLDocument(self.workspace, modulename, mdir))
    #    headerXDoc('Module XML')
    #    x.write('<source>\n')
    #    xf = StringIO.StringIO()
    #    xml = xmlize('module', module, xf)
    #    x.write(escape(xml))
    #    x.write('</source>\n')
    #    footerXDoc(x)
    #    endXDoc(x)

    def documentProject(self, project, realTime = False):

        # Hack for bad data. Gump3 won't let it get this
        # far.
        if not project.inModule():
            return

        spec = self.resolver.getFileSpec(project)
        document = XDocDocument('Project : ' + project.getName(),
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        # Provide a description/link back to the module site.
        projectsSection = document.createSection('Description')
        description = ''
        if project.hasDescription():
            description = escape(project.getDescription())
        if not description.strip().endswith('.'):
            description += '. '
        if not description:
            description = 'No description provided.'
        if project.hasUrl():
            description += ' For more information, see: ' \
                + self.getFork(project.getUrl())
        else:
            description = ' (No project URL provided.)'

        projectsSection.createParagraph().createRaw(description)

        #
        # The 'cause' is something upstream.
        #
        if project.cause and not project == project.cause:
            self.insertTypedLink(project.cause, project,
                                 document.createNote("This project failed " + \
                                                         "due to: "))

        if project.isPackaged():
            document.createNote('This is a packaged project, not Gumped.')
        elif not project.hasBuilder():
            document.createNote('This project is not built by Gump.')

        stateSection = document.createSection('State')

        stateList = stateSection.createList()
        stateList.createEntry("Current State: ", project.getStateDescription())
        if not project.getReason() == REASON_UNSET:
            stateList.createEntry("Reason: " \
                                      + reasonDescription(project.getReason()))
        if project.cause and not project == project.cause:
            self.insertTypedLink(project.cause, project,
                                 stateList.createEntry("Root Cause: "))


        self.documentAnnotations(document, project)

        note = ''
        warn = ''
        if project.wasBuilt():
            if project.getReason() == REASON_BUILD_FAILED:
                warn = 'Project build output (failure) found here...'
            else:
                note = 'Project build output found here...'
        self.documentWorkList(document, project, 'Project-level Work', 0,
                              note, warn)
        self.documentServerLinks(document, project)

        # Project Details (main ones)
        detailsSection = document.createSection('Details')
        detailsList = detailsSection.createList()

        self.insertLink(project.getModule(), project,
                        detailsList.createEntry('Containing Module: '))

        if project.isSpliced():
            detailsList.createEntry('Metadata formed from multiple XML ' + \
                                        'pieces: ', `project.isSpliced()`)

        if project.hasHomeDirectory():
            detailsList.createEntry('Home Directory: ',
                                    project.getHomeDirectory())

        if project.hasBaseDirectory():
            detailsList.createEntry('Base Directory: ',
                                    project.getBaseDirectory())

        if project.hasCause() and not project == project.getCause():
            self.insertTypedLink(project.getCause(), project,
                                 detailsList.createEntry('Root Cause: '))

        e = secsToElapsedTimeString(project.getElapsedSecs())
        if e and project.isVerboseOrDebug():
            detailsList.createEntry("Elapsed: ", e)

        detailsList.createEntry('Redistributable: ',
                                `project.isRedistributable()`)

        # Display nag information
        if project.hasNotifys():
            for pair in project.getNotifys():
                toaddr = pair.getToAddress()
                fromaddr = pair.getFromAddress()
                detailsList.createEntry('Notify To: ')\
                    .createFork('mailto:' + toaddr, toaddr)
                detailsList.createEntry('Notify From: ')\
                    .createFork('mailto:' + fromaddr, fromaddr)

        elif not project.isPackaged() and project.hasBuilder():
            document\
                .createWarning('This project does not utilize ' + \
                                   'Gump notification.')

        metadataLocation = project.getMetadataLocation()
        metadataUrl = project.getMetadataViewUrl()
        if metadataLocation and metadataUrl:
            detailsList.createEntry('Gump Metadata: ')\
                .createFork(metadataUrl, metadataLocation)

        # RSS|Atom|RDF
        self.documentXMLLinks(document, depth = getDepthForObject(project))

        self.documentStats(document, project, realTime)

        self.documentFileList(document, project, 'Project-level Files')

        addnSection = document.createSection('Additional Details')
        addnPara = addnSection.createParagraph()
        addnPara.createLink('details.html',
             'For additional project details (including classpaths, ' + \
                                'dependencies) ...')

        document.serialize()

        if not realTime:
            self.documentProjectDetails(project, realTime)

    def documentProjectDetails(self, project, realTime = 0):

        spec = self.resolver.getFileSpec(project, 'details')
        document = XDocDocument('Project Details : ' + project.getName(),
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        #x.write('<p><strong>Project Config :</strong> <link href = \'%s\'' + \
        #            '>XML</link></p>' \
        #            % (getModuleProjectRelativeUrl(modulename, project.name)) )

        miscSection = document.createSection('Miscellaneous')

        #
        #       Outputs (e.g. Outputs)
        #
        if project.hasOutputs():
            outputSection = miscSection.createSection('Output Artifacts')
            outputTable = outputSection.createTable(['Name', 'Artifact Id'])

            for output in project.getOutputs():
                outputRow = outputTable.createRow()

                # The name (path) of the output
                outputRow.createData(output.getName())

                # The output id
                id = output.getId() or 'N/A'
                outputRow.createData(id)
        else:
            miscSection.createWarning('No output artifacts (e.g. outputs) ' + \
                                          'produced')

        if project.hasBuilder():

            if project.hasAnt():
                self.documentProperties(miscSection, project.getAnt(),
                                        'Ant Properties')
            elif project.hasNAnt():
                self.documentProperties(miscSection, project.getNAnt(),
                                        'NAnt Properties')
            # :TODO: Maven?

            language = project.getLanguageType()
            helper = self.run.getLanguageHelper(language)
            if Project.JAVA_LANGUAGE == language:
                javaHelper = helper
                (classpath, bootclasspath) = \
                    javaHelper.getClasspathObjects(project)
                self.displayClasspath(miscSection, classpath, 'Classpath',
                                      project)
                self.displayClasspath(miscSection, bootclasspath,
                                      'Boot Classpath', project)
            elif Project.CSHARP_LANGUAGE == language:
                csharpHelper = helper
                libpath = csharpHelper.getAssemblyPathObject(project)
                self.displayClasspath(miscSection, libpath, 'Assemblies',
                                      project)
        else:
            miscSection.createParagraph('No build command (so classpaths/' + \
                                            'assembly path irrelevant)')

        if project.isDebug():
            self.documentXML(miscSection, project)

        dependencySection = document.createSection('Dependency')

        deps = 0
        depens = 0
        depees = 0

        #
        # The 'cause' is something upstream. Possibly a project,
        # possibly a module (so determine paths to module projects).
        #


        #if project.cause and not project == project.cause:
        #    if isinstance(project.cause, Project):
        #        for path in project.getDependencyPaths(project.cause):
        #            self.documentDependenciesPath(dependencySection,
        #                                          'Root Cause Dependency Path',
        #                                          path, 0, 1, project,
        #                                          self.gumpSet)
        #    elif isinstance(project.cause, Module):
        #        for causeProject in project.cause.getProjects():
        #            for path in project.getDependencyPaths(causeProject):
        #                self.documentDependenciesPath(dependencySection,
        #                                              'Root Cause Module ' + \
        #                                                  'Dependency Path',
        #                                              path, 0, 1, project,
        #                                              self.gumpSet)


        depens += self.documentDependenciesList(dependencySection,
                                                'Project Dependencies',
                                                project\
                                                    .getDirectDependencies(),
                                                False, False,
                                                project)

        depees += self.documentDependenciesList(dependencySection,
                                                'Project Dependees',
                                                project.getDirectDependees(),
                                                True, False,
                                                project)

        # :TODO: Re-enable?
        if False:
            if project.isVerboseOrDebug():
                self.documentDependenciesList(dependencySection,
                                              'Full Project Dependencies',
                                              project.getFullDependencies(),
                                              False, True,
                                              project)

                self.documentDependenciesList(dependencySection,
                                              'Full Project Dependees',
                                              project.getFullDependees(),
                                              True, True,
                                              project)

        deps = depees + depens

        if not deps:
            dependencySection.createNote(
            """This project depends upon no others, and no others depend upon it.
            This project is an island...""")
        else:
            if realTime and not depees:
                dependencySection\
                    .createNote('No projects depend upon this project.')
            if not depens:
                dependencySection\
                    .createNote('This project depends upon no others.')


        if False and self.config.isXdocs():
            try:
                # Generate an SVG for Dependencies Diagram:
                (file, title) = self.diagramDependencies(project)
                if file:
                    para = dependencySection\
                        .createSection('Dependency Diagram')\
                        .createParagraph()
                    para.createFork(file).createIcon(file, title)
            except:
                log.error('Failed to diagram dependencies for [' + \
                              project.getName() + ']', exc_info = 1)

        document.serialize()
        document = None

        # Document the project XML
        #x = startXDoc(getProjectXMLDocument(self.workspace, modulename,
        #                                    project.name))
        #headerXDoc('Project XML')
        #x.write('<source>\n')
        #xf = StringIO.StringIO()
        #xml = xmlize('project', project, xf)
        #x.write(escape(xml))
        #x.write('</source>\n')
        #footerXDoc(x)
        #endXDoc(x)

    def documentStats(self, node, entity, realTime = False):

        # Note: Leverages previous extraction from project statistics DB
        stats = entity.getStats()

        statsSection = node.createSection('Statistics')

        # Start annotating with issues...
        if entity.isNotOk() and stats.sequenceInState >= SIGNIFICANT_DURATION:
            statsSection.createWarning(
                'This entity has existed in this failed state for a ' + \
                    'significant duration.')

        statsTable = statsSection.createTable()

        if not isinstance(entity, Workspace):
            if (not realTime) and self.config.isXdocs():
                # Generate an SVG for FOG:
                (file, title) = self.diagramFOG(entity)
                if file:
                    statsTable.createEntry("FOG Factor: ").createData()\
                        .createIcon(file, title)

        statsTable.createEntry("FOG Factor: ", '%02.2f' % stats.getFOGFactor())

        if isinstance(entity, Project):
            statsTable.createEntry('Dependency Depth: ',
                                   entity.getDependencyDepth())
            statsTable.createEntry('Total Dependency Depth: ',
                                   entity.getTotalDependencyDepth())

        statsTable.createEntry("Successes: ", stats.successes)
        statsTable.createEntry("Failures: ", stats.failures)

        if not isinstance(entity, Workspace):
            statsTable.createEntry("Prerequisite Failures: ", stats.prereqs)

        statsTable.createEntry("Current State: ",
                               stateDescription(stats.currentState))
        statsTable.createEntry("Duration in state: ", stats.sequenceInState)
        if stats.startOfState:
            statsTable.createEntry("Start of state: ",
                                   stats.startOfState.isoformat())
        if stats.previousState:
            statsTable.createEntry("Previous State: ", stats.previousState)

        if stats.first:
            statsTable.createEntry("First Success: ", stats.first.isoformat())
        if stats.last:
            statsTable.createEntry("Last Success: ", stats.last.isoformat())

    def displayClasspath(self, document, classpath, title, referencingObject):

        if not classpath.getPathParts():
            return

        pathSection = document.createSection(title)
        pathTable = pathSection.createTable(['Path Entry', 'Contributor',
                                             'Instigator', 'Id', 'Annotation'])
        paths = 0
        for path in classpath.getPathParts():
            if isinstance(path, AnnotatedPath):
                pathStr = path.getPath()
                contributor = path.getContributor()
                instigator = path.getInstigator()
                id = path.getId()
                note = path.note
            else:
                pathStr = path
                contributor = referencingObject.getWorkspace()
                instigator = None
                id = ''
                note = ''

            pathRow = pathTable.createRow()
            pathRow.createData(pathStr)

            # Contributor
            if contributor:
                self.insertLink(contributor, referencingObject,
                                pathRow.createData())
            else:
                pathRow.createData('')

            # Instigator (if not Gump)
            if instigator:
                self.insertLink(instigator, referencingObject,
                                pathRow.createData())
            else:
                pathRow.createData('')

            # The identifier....
            pathRow.createData(id)

            # Additional Notes...
            pathRow.createData(note)

            paths += 1

        if not paths:
            pathTable.createLine('No ' + title + ' entries')

        if classpath.containsNasties():
            self.documentAnnotations(pathSection, classpath)

    def documentDependenciesPath(self, xdocNode, title, path, dependees, full,
                                 referencingObject):
        # :TODO: show start and end?
        self.documentDependenciesList(xdocNode, title, path, dependees, full,
                                      referencingObject)

    def documentDependenciesList(self, xdocNode, title, dependencies,
                                 dependees, full, referencingObject):
        totalDeps = 0

        if dependencies:
            dependencySection = xdocNode.createSection(title)
            titles = ['Name', 'Type', 'Inheritence', 'Ids', 'State', 'FOG']
            if full:
                titles.append('Contributor')
            titles.append('Notes')
            dependencyTable = dependencySection.createTable(titles)
            for depend in dependencies:

                # Don't document out of scope...
                if not self.gumpSet.inProjectSequence(depend.getProject()) \
                    or not self.gumpSet\
                    .inProjectSequence(depend .getOwnerProject()) :
                    continue

                totalDeps += 1

                # Project/Owner
                if not dependees:
                    project = depend.getProject()
                else:
                    project = depend.getOwnerProject()
                dependencyRow = dependencyTable.createRow()
                dependencyRow.createComment(project.getName())
                self.insertLink(project, referencingObject,
                                dependencyRow.createData())

                # Type
                type = ''
                if depend.isRuntime():
                    if type:
                        type += ' '
                    type += 'Runtime'
                if depend.isOptional():
                    if type:
                        type += ' '
                    type += 'Optional'
                if depend.isNoClasspath():
                    if type:
                        type += ' '
                    type += 'NoClasspath'
                dependencyRow.createData(type)

                # Inheritence
                dependencyRow.createData(depend.getInheritenceDescription())

                # Ids
                ids = depend.getIds()

                if ids: # Make these stand out
                    dependencyRow.createData().createStrong(ids)
                else:
                    dependencyRow.createData('All')

                # State Icon
                self.insertStateIcon(project, referencingObject,
                                     dependencyRow.createData())

                # FOG Factor
                dependencyRow.createData('%02.2f' % project.getFOGFactor())

                if full:
                    # Contributor
                    if not dependees:
                        contributor = depend.getOwnerProject()
                    else:
                        contributor = depend.getProject()
                    self.insertLink(contributor, referencingObject,
                                    dependencyRow.createData())

                # Dependency Annotations
                noteData = dependencyRow.createData()
                if depend.getAnnotations():
                    for note in depend.getAnnotations():
                        noteData.createText(str(note))
                        noteData.createBreak()
                else:
                    noteData.createText('')

            dependencySection.createParagraph(
                    'Total ' + title + ' : ' + str(totalDeps))

        return totalDeps

    def documentAnnotations(self, xdocNode, annotatable, noWarn = 0):
        """
        Document the notes on an entity. Provide a table to level/message.
        """

        annotations = annotatable.getAnnotations()
        if not annotations:
            return

        annotationsSection = xdocNode.createSection('Annotations')

        if not self.config.isXhtml():
            if annotatable.containsNasties() and not noWarn:
                annotationsSection.createWarning(
                    'Some warnings and/or errors are present within these ' + \
                        'annotations.')

        annotationsTable = annotationsSection.createTable()
        for note in annotations:
            noteRow = annotationsTable.createRow()

            # Allow style
            noteRow.setStyle(levelName(note.level).upper())
            noteRow.createData(levelName(note.level))
            # TODO if 'text' is a list go through list and
            # when not string get the object link and <link it...
            noteRow.createData(note.text)

    def documentServerLinks(self, xdocNode, linkable, depth = -1):
        """
        Display links to this linkable entity but on remote servers
        """

        servers = self.workspace.getPythonServers()
        if not servers:
            return
        if len(servers) == 1:
            return # Assume this one.

        # Hack to keep 'tighter' in diffsLog page
        serversSection = xdocNode
        if -1 == depth:
            serversSection = xdocNode.createSection('Servers')
            serversSection.createParagraph('These links represent this ' + \
                                               'location (and, when ' + \
                                               'available, the status ' + \
                                               'and time) on other servers.')

        serversTable = serversSection.createTable()
        serverRow = serversTable.createRow()

        serverResults = None
        if isinstance(linkable, Resultable) and linkable.hasServerResults():
            serverResults = linkable.getServerResults()

        for server in servers:

            # If we know state on the other server.
            statePair = None
            utcTime = None
            if serverResults and serverResults.has_key(server):
                results = serverResults[server]
                if results:
                    statePair = results.getStatePair()
                    utcTime = results.getStartDateTimeUtc()

            # If we can resolve this object to a URL, then do
            if server.hasResolver() and server.isUp():
                dataNode = serverRow.createData()

                xdocNode = dataNode.createFork(
                        server.getResolver().getUrl(linkable))

                xdocNode.createText('On ' + server.getName())

                if statePair:
                    xdocNode.createBreak()
                    # Insert the Icon...
                    if -1 == depth:
                        depth = getDepthForObject(linkable)
                    self.insertStatePairIconAtDepth(xdocNode, statePair, depth)

                if utcTime:
                    xdocNode.createBreak()
                    xdocNode.createText(utcTime)

    def documentProperties(self, xdocNode, propertyContainer,
                           title = 'Properties'):
        """
        Create a table (or two) of name/value information for properties

        First system properties, second normal properties

        """

        properties = propertyContainer.getProperties()
        sysproperties = propertyContainer.getSysProperties()
        if not properties and not sysproperties:
            return

        # Start a section...
        propertiesSection = xdocNode.createSection(title)

        if sysproperties:
            # System Properties
            sysPropertiesSection = propertiesSection\
                .createSection('System Properties')
            syspropertiesTable = sysPropertiesSection.createTable(['Name',
                                                                   'Value'])
            for sysproperty in sysproperties:
                syspropertiesTable.createEntry(sysproperty.getName(),
                                               sysproperty.getValue())

        if properties:
            # Standard Properties
            standardPropertiesSection = propertiesSection\
                .createSection('Standard Properties')
            propertiesTable = standardPropertiesSection.createTable(['Name',
                                                                     'Value'])
            for prop in properties:
                propertiesTable.createEntry(prop.getName(),
                                            prop.getValue())

    def documentXML(self, xdocNode, xmlOwner):

        dom = xmlOwner.dom
        if not dom:
            return

        xmlSection = xdocNode.createSection('Definition')
        stream = StringIO.StringIO()
        try:
            dom.writexml(stream, indent = '   ', newl = '\n')
        except Exception, details:
            stream.write('Failed to XML serialize the data. ' + str(details))
        stream.seek(0)
        xmldata = stream.read()
        if (not self.config.isXdocs()) or (len(xmldata) < 32000):
            xmlSection.createSource(xmldata)
        else:
            xmlSection.createParagraph('XML Data too large to display ' + \
                                           'via Forrest.')
        stream.close()
        stream = None

    def documentSummary(self, xdocNode, summary,
                        description = 'Project Summary'):
        if not summary or not summary.projects \
            or not (summary.projects > 1):
            return

        summarySection = xdocNode.createSection(description)

        summarySection.createParagraph('Overall project success : ' + \
                                           '%02.2f' % \
                                           summary.overallPercentage + '%')

        successStyle = stateName(STATE_SUCCESS).upper()
        failedStyle = stateName(STATE_FAILED).upper()
        prereqStyle = stateName(STATE_PREREQ_FAILED).upper()
        noworkStyle = stateName(STATE_UNSET).upper()
        completeStyle = stateName(STATE_COMPLETE).upper()

        #:TODO: Link to the various pages.
        #successes = self.resolver.getUrl(self.workspace, 'project_fixes')
        #failures = self.resolver.getUrl(self.workspace, 'project_todos')
        #prereqs = self.resolver.getUrl(self.workspace, 'project_prereqs')
        # :TODO: Work these into here somewhere....

        summaryTable = summarySection.createTable(['Projects',
                                                   ('Successes', successStyle),
                                                   ('Failures', failedStyle),
                                                   ('Prereqs', prereqStyle),
                                                   ('No Works', noworkStyle),
                                                   ('Packages', completeStyle) ]
                                                  )

        summaryTable.createRow([ '%02d' % summary.projects,
                                ('%02d' % summary.successes + \
                                ' (' + '%02.2f' % summary.successesPercentage \
                                     + '%)',
                                    successStyle),
                                ('%02d' % summary.failures + \
                                ' (' + '%02.2f' % summary.failuresPercentage \
                                     + '%)',
                                    failedStyle),
                                ('%02d' % summary.prereqs + \
                                ' (' + '%02.2f' % summary.prereqsPercentage \
                                     + '%)',
                                    prereqStyle),
                                ('%02d' % summary.noworks + \
                                ' (' + '%02.2f' % summary.noworksPercentage \
                                     + '%)',
                                    noworkStyle),
                                ('%02d' % summary.packages + \
                                ' (' + '%02.2f' % summary.packagesPercentage \
                                     + '%)',
                                 completeStyle) ])


    def documentWorkList(self, xdocNode, workable, description = 'Work',
                         tailFail = 1, note = '', warn = ''):
        worklist = workable.getWorkList()

        if not worklist:
            return

        workSection = xdocNode.createSection(description)

        if note:
            workSection.createNote(note)

        if warn:
            workSection.createWarning(warn)

        workTable = workSection.createTable(['Name', 'State', 'Start',
                                             'Elapsed'])

        for work in worklist:
            workRow = workTable.createRow()
            workRow.createComment(work.getName())

            self.insertLink(work, workable, workRow.createData())
            workRow.createData(stateDescription(work.state))

            # Colour...
            workRow.setStyle(stateName(work.state).upper())

            if isinstance(work, TimedWorkItem):
                workRow.createData(work.getStart().getLocal())
                workRow\
                    .createData(secsToElapsedTimeString(work .getElapsedSecs()))
            else:
                workRow.createData('N/A')
                workRow.createData('N/A')

        if tailFail:
            #
            # Do a tail on all work that failed...
            #
            for work in worklist:
                if isinstance(work, CommandWorkItem):
                    if not STATE_SUCCESS == work.state:
                        if work.hasOutput():
                            tail = work.tail(20, 80, '...\n', '    ')
                            if tail:
                                #
                                # Write out the 'tail'
                                #
                                tailSection = \
                                    workSection.createSection(
                                        'Tail of ' + workTypeName(work.type) + \
                                            ' : ' + work.command.name)

                                # Attempt to ensure they don't
                                para = tailSection.createParagraph(
                                    'This is a very short tail of the log at ')
                                self.insertLink(work, workable, para)

                                tailSection.createSource(tail)


        #
        # Go document the others...
        #
        for work in worklist:
            self.documentWork(work)

    def documentWork(self, work):
        if isinstance(work, CommandWorkItem):
            spec = self.resolver.getFileSpec(work)
            wdocument = XDocDocument(
                workTypeName(work.type) + ' : ' + work.command.name,
                spec.getFile(),
                self.config,
                spec.getRootPath())

            workSection = wdocument.createSection('Details')

            workList = workSection.createList()
            workList.createEntry("State: ", stateDescription(work.state))

            self.insertTypedLink(work.getOwner(),
                                 work,
                                 workList.createEntry("For: "))

            # addItemXDoc("Command: ", work.command.name)
            if work.command.cwd:
                workList.createEntry("Working Directory: ", work.command.cwd)
            if work.result.output:
                workList.createEntry("Output: ", work.result.output)
            else:
                workList.createEntry("Output: ", "None")

            if work.result.signal:
                workList.createEntry("Termination Signal: ",
                                     str(work.result.signal))
            workList.createEntry("Exit Code: ", str(work.result.exit_code))

            workList.createEntry("Start Time: ", work.getStart().getLocal())
            workList.createEntry("End Time: ", work.getEnd().getLocal())
            e = secsToElapsedTimeString(work.getElapsedSecs())
            if e:
                workList.createEntry("Elapsed Time: ", e)

            #
            # Show parameters
            #
            if work.command.params:
                title = 'Parameter'
                if len(work.command.params.items()) > 1:
                    title += 's'
                parameterSection = wdocument.createSection(title)
                parameterTable = parameterSection.createTable(['Prefix',
                                                               'Name', 'Value'])

                for param in work.command.params.items():
                    paramRow = parameterTable.createRow()
                    paramRow.createData(param.prefix or '')

                    paramRow.createData(param.name)
                    val = param.value
                    # :TODO: Hack for BOOTCLASSPATH
                    if param.name.startswith('bootclasspath'):
                        val = default.classpathSeparator + \
                            '\n'.join(val.split(default.classpathSeparator))

                    paramRow.createData(val or'')

            #
            # Show ENV overrides
            #
            if work.command.env:
                envSection = wdocument.createSection('Environment Overrides')
                envTable = envSection.createTable(['Name', 'Value'])

                for (name, value) in work.command.env.iteritems():
                    envRow = envTable.createRow()
                    envRow.createData(name)
                    if value:
                        # :TODO: Hack for CLASSPATH
                        if name == "CLASSPATH":
                            value = default.classpathSeparator + \
                                '\n'.join(value.split(default\
                                                          .classpathSeparator))
                        envRow.createData(escape(value))
                    else:
                        envRow.createData('N/A')


            #
            # Wrap the command line..
            #
            parts = work.command.formatCommandLine().split(' ')
            line = ''
            commandLine = ''
            for part in parts:
                if (len(line) + len(part)) > 80:
                    commandLine += line
                    commandLine += '\n        '
                    line = part
                else:
                    if line:
                        line += ' '
                    line += part
            if line:
                commandLine += line

            #
            # Show the wrapped command line
            #
            wdocument \
                .createSection('Command Line') \
                .createSource(commandLine)

            #
            # Show the content...
            #
            outputSection = wdocument.createSection('Output')
            output = work.result.output
            if output:
                try:
                    if os.path.getsize(output) > 100000:
                        #
                        # This is *big* just copy/point to it
                        #
                        # Extract name, to make relative to group
                        outputBaseName = os.path.basename(output)
                        (outputName, outputExtn) = \
                            os.path.splitext(outputBaseName)
                        displayedOutput = self.resolver.getFile(work,
                                                                outputName,
                                                                outputExtn, 1)

                        # Do the transfer..
                        copyfile(output, displayedOutput)
                        outputSection.createParagraph()\
                            .createLink(outputBaseName, 'Complete Output File')

                    else:
                        #
                        # Display it 'prettily' in HTML
                        #
                        outputSource = outputSection.createSource()
                        o = None
                        try:
                            # Keep a length count to not exceed 32K
                            size = 0
                            o = open(output, 'r')
                            line = o.readline()
                            while line:
                                length = len(line)
                                size += length
                                # Crude to 'ensure' that escaped
                                # it doesn't exceed 32K.
                                if size > 20000:
                                    outputSection\
                                        .createParagraph('Continuation...')
                                    outputSource = outputSection.createSource()
                                    size = length
                                outputSource.createText(line)
                                line = o.readline()
                        finally:
                            if o:
                                o.close()

                except Exception, details:
                    outputSection.createParagraph('Failed to copy contents ' + \
                                                      'from :' + output + \
                                                      ' : ' + str(details))
            else:
                outputSection.createParagraph('No output to stdout/stderr ' + \
                                                  'from this command.')

            wdocument.serialize()
            wdocument = None

    def documentFileList(self, xdocNode, holder, description = 'Files'):
        filelist = holder.getFileList()

        if not filelist:
            return

        fileSection = xdocNode.createSection(description)
        fileTable = fileSection.createTable(['Name', 'Type', 'Path'])

        for listedFile in filelist:
            fileRow = fileTable.createRow()
            fileRow.createComment(listedFile.getName())
            self.insertLink(listedFile, holder, fileRow.createData())
            fileRow.createData(listedFile.getTypeDescription())
            fileRow.createData(listedFile.getPath())

        #
        # Go document the others...
        #
        for fileReference in filelist:
            self.documentFile(fileReference)

    def documentFile(self, fileReference):

        spec = self.resolver.getFileSpec(fileReference)
        fdocument = XDocDocument(
            fileReference.getTypeDescription() + ' : ' \
                + fileReference.getName(),
            spec.getFile(),
            self.config,
            spec.getRootPath())

        fileSection = fdocument.createSection('Details')

        fileList = fileSection.createList()
        fileList.createEntry("Type: ", fileReference.getTypeDescription())

        self.insertTypedLink(fileReference.getOwner(),
                             fileReference,
                             fileList.createEntry("Owner (Referencer): "))

        if fileReference.exists():
            try:
                if fileReference.isDirectory():

                    listingSection = fdocument\
                        .createSection('Directory Contents')
                    listingTable = listingSection.createTable(['Filename',
                                                               'Type', 'Size'])

                    directory = fileReference.getPath()

                    # Change to os.walk once we can move to Python 2.3
                    files = os.listdir(directory)
                    files.sort()
                    for listedFile in files:

                        filePath = os.path.abspath(os.path.join(directory,
                                                                listedFile))
                        listingRow = listingTable.createRow()

                        #
                        listingRow.createData(listedFile)

                        if os.path.isdir(filePath):
                            listingRow.createData('Directory')
                            listingRow.createData('N/A')
                        else:
                            listingRow.createData('File')
                            listingRow\
                                .createData(str(os.path.getsize(filePath)))
                else:

                    #
                    # Show the content...
                    #
                    outputSection = fdocument.createSection('File Contents')
                    output = fileReference.getPath()
                    if output:
                        try:
                            if os.path.getsize(output) > 100000:
                                #
                                # This is *big* just copy/point to it
                                #
                                # Extract name, to make relative to group
                                outputBaseName = os.path.basename(output)
                                (outputName, outputExtn) = \
                                    os.path.splitext(outputBaseName)
                                displayedOutput = \
                                    self.resolver.getFile(fileReference,
                                                          outputName,
                                                          outputExtn, 1)

                                # Do the transfer..
                                copyfile(output, displayedOutput)
                                outputSection.createParagraph()\
                                    .createLink(outputBaseName, 'Complete File')
                            else:
                                outputSource = outputSection.createSource()
                                o = None
                                try:
                                    # Keep a length count to not exceed 32K
                                    size = 0
                                    o = open(output, 'r')
                                    line = o.readline()
                                    while line:
                                        length = len(line)
                                        size += length
                                        # Crude to 'ensure' that escaped
                                        # it doesn't exceed 32K.
                                        if size > 20000:
                                            outputSection\
                                                .createParagraph('Continuation'\
                                                                     + '...')
                                            outputSource = \
                                                outputSection.createSource()
                                            size = length
                                        outputSource.createText(line)
                                        line = o.readline()
                                finally:
                                    if o:
                                        o.close()
                        except Exception, details:
                            outputSection.createParagraph('Failed to copy ' + \
                                                              'contents from :'\
                                                              + output + ' : ' \
                                                              + str(details))
                    else:
                        outputSection\
                            .createParagraph('No contents in this file.')
            except Exception, details:
                fdocument.createWarning('Failed documeting file or ' + \
                                            'directory. %s' % details)
        else:
            fdocument.createWarning('No such file or directory.')

        fdocument.serialize()
        fdocument = None

    def diagramFOG(self, obj, base = None):

        stats = obj.getStats()
        name = obj.getName()
        if not base:
            base = obj

        #
        # Generate an SVG: 'FOG'
        #
        if stats.successes + stats.failures + stats.prereqs > 0:
            svgFile = self.resolver.getFile(base, name + '_FOG', '.svg')
            svgBasename = os.path.basename(svgFile)
            pngBasename = svgBasename.replace('.svg', '.png')
            from gump.tool.svg.scale import ScaleDiagram
            diagram = ScaleDiagram([stats.successes, stats.prereqs,
                                    stats.failures])
            diagram.generateDiagram().serializeToFile(svgFile)

            fileBasename = pngBasename
            if self.config.isXhtml():
                fileBasename = svgBasename

            return (fileBasename, 'FOG Factor')

        return (None, None)

    def diagramDependencies(self, project, base = None):

        name = project.getName()
        if not base:
            base = project

        svgFile = self.resolver.getFile(base, name + '_depend', '.svg')
        svgBasename = os.path.basename(svgFile)
        pngBasename = svgBasename.replace('.svg', '.png')
        from gump.tool.svg.depdiag import DependencyDiagram
        diagram = DependencyDiagram(project)
        diagram.compute()
        diagram.generateDiagram().serializeToFile(svgFile)

        fileBasename = pngBasename
        if self.config.isXhtml():
            fileBasename = svgBasename

        return (fileBasename, 'Dependency Diagram')

    #####################################################################
    #
    # Helper Methods
    #
    def getFork(self, href, name = None):
        if not name:
            name = href
        if self.config.isXhtml():
            return '<a target = "_new" href = "%s">%s</a>' % (escape(href),
                                                              escape(name))
        return '<fork href = "%s">%s</fork>' % (escape(href), escape(name))

    def insertStateDescription(self, toObject, fromObject, xdocNode):
        node = xdocNode.createText(stateDescription(toObject.getState()))
        if not toObject.getReason() == REASON_UNSET:
            xdocNode.createText(' with reason ' + \
                                    reasonDescription(toObject.getReason()))

        if toObject.cause and not toObject.cause == toObject:

            givenCause = 0
            for cause in toObject.getCauses():
                if not cause == object:
                    if not givenCause:
                        xdocNode.createText(', caused by ')
                        givenCause = 1
                    else:
                        xdocNode.createText(' ')
                    self.insertStateLink(cause, fromObject, xdocNode, 1)

        return node

    def insertStateIcons(self, module, fromObject, xdocNode):
        icons = ''
        for project in module.getProjects():
            if not self.gumpSet.inProjectSequence(project):
                continue
            self.insertStateIcon(project, fromObject, xdocNode)
            # A separator, to allow line wrapping
            xdocNode.createText(' ')
        return icons

    def insertStateIcon(self, toObject, fromObject, xdocNode):
        return self.insertLink(toObject, fromObject, xdocNode, 1, 1, 1)

    def insertTypedLink(self, toObject, fromObject, xdocNode, state = 0,
                        icon = 0):
        return self.insertLink(toObject, fromObject, xdocNode, 1, state, icon)

    def insertStateLink(self, toObject, fromObject, xdocNode, typed = 0,
                        icon = 0):
        return self.insertLink(toObject, fromObject, xdocNode, typed, 1, icon)

    def insertLink(self, toObject, fromObject, xdocNode, typed = 0,
                   state = 0, icon = 0):
        description = ''
        if typed:
            description = toObject.__class__.__name__

        try: # Add a name, if present
            name = toObject.getName()
            if description:
                description += ': '
            description += name
        except:
            if not description:
                description = toObject.__class__.__name__

        # If showing 'state' then find the
        link = self.getLink(toObject, fromObject, state)

        if not state:
            # Just install the <link
            return xdocNode.createLink(link, description)
        else:
            # Install the <link with an <icon inside
            if icon:
                node = xdocNode.createLink(link)
                return self.insertStatePairIcon(node, toObject, fromObject)
            else:
                return xdocNode.createLink(link, description)


    def getLink(self, toObject, fromObject = None, state = 0):
        url = ''
        postfix = ''

        #
        # If we are looking for what set the state, look at
        # work first. Pick the first not working. If not found
        # link to the annotations section.
        #
        if state and isinstance(toObject, Workable):
            for work in toObject.getWorkList():
                if not url:
                    if not work.state == STATE_SUCCESS:
                        url = getRelativeLocation(work, fromObject,
                                                  '.html').serialize()

            # This assumes that if it failed, but doesn't have work that
            # mark's it as failed then something in the nasties must refer
            # to the problem.
            if not url:
                if isinstance(toObject, Annotatable) and \
                        toObject.containsNasties():
                    postfix = '#Annotations'

        if not url:
            if fromObject:
                url = getRelativeLocation(toObject, fromObject,
                                          '.html').serialize()
            else:
                url = self.resolver.getUrl(toObject)

        return url + postfix

    def setStyleFromState(self, xdocNode, statePair):
        # Set the style from the state name (right now)
        # maybe later do different for reason code.
        xdocNode.setStyle(statePair.getStateName().upper())

    def insertStatePairIcon(self, xdocNode, toObject, fromObject):
        pair = toObject.getStatePair()
        depth = getDepthForObject(fromObject)
        self.insertStatePairIconAtDepth(xdocNode, pair, depth)

    def insertStatePairIconAtDepth(self, xdocNode, pair, depth):
        # :TODO: Move this to some resolver, and share with RSS
        sname = stateDescription(pair.state)
        rstring = reasonDescription(pair.reason)

        description = sname
        uniqueName = sname
        if not pair.reason == REASON_UNSET:
            description += ' ' + rstring
            # Not yet, just have a few icons ... uniqueName += '_'+rstring

        # Build the URL to the icon
        iconName = gumpSafeName(uniqueName.replace(' ', '_').lower())
        url = self.resolver.getIconUrl(iconName + '.png', depth)

        # Build the <icon tag at location...
        return xdocNode.createIcon(url, description)

    #####################################################################
    #
    # Statistics Pages
    #
    def documentStatistics(self):

        log.info('Generate Statistic Guru')
        stats = StatisticsGuru(self.workspace)

        spec = self.resolver.getFileSpec(stats)
        document = XDocDocument('Statistics',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        document.createParagraph("""
        Statistics from Gump show the depth and health of inter-relationships.
        """)

        overviewSection = document.createSection('Overview')
        overviewList = overviewSection.createList()
        overviewList.createEntry('Modules: ', stats.wguru.modulesInWorkspace)
        overviewList.createEntry('Projects: ', stats.wguru.projectsInWorkspace)
        overviewList.createEntry('Avg Projects Per Module: ',
                                 stats.wguru.averageProjectsPerModule)

        self.documentSummary(overviewSection,
                             self.workspace.getProjectSummary())

        mstatsSection = document.createSection('Module Statistics')
        mstatsTable = mstatsSection.createTable(['Page', 'Description'])

        # Modules By Elapsed Time
        mByE = self.documentModulesByElapsed(stats)
        mstatsRow = mstatsTable.createRow()
        mstatsRow.createData().createLink(mByE, 'Modules By Elapsed Time')
        mstatsRow.createData('Time spent working on this module.')

        # Modules By Project #
        mByP = self.documentModulesByProjects(stats)
        mstatsRow = mstatsTable.createRow()
        mstatsRow.createData().createLink(mByP, 'Modules By Project #')
        mstatsRow.createData('Number of projects within the module.')

        # Modules By Dependencies
        mByDep = self.documentModulesByDependencies(stats)
        mstatsRow = mstatsTable.createRow()
        mstatsRow.createData().createLink(mByDep, 'Modules By Dependencies #')
        mstatsRow.createData('Number of dependencies within the module.')

        # Modules By Dependees
        mByDepees = self.documentModulesByDependees(stats)
        mstatsRow = mstatsTable.createRow()
        mstatsRow.createData().createLink(mByDepees, 'Modules By Dependees #')
        mstatsRow.createData('Number of dependees on the module.')

        # Modules By FOG Factor
        mByFOG = self.documentModulesByFOGFactor(stats)
        mstatsRow = mstatsTable.createRow()
        mstatsRow.createData().createLink(mByFOG, 'Modules By FOG Factor')
        mstatsRow.createData('Friend of Gump (FOG) Factor. A measure of' + \
                                 'dependability (for other Gumpers).')

        # Modules By Last Modified
        mByLU = self.documentModulesByLastModified(stats)
        mstatsRow = mstatsTable.createRow()
        mstatsRow.createData().createLink(mByLU, 'Modules By Last Modified')
        mstatsRow.createData('Best guess at last code change ' + \
                                 '(in source control).')

        pstatsSection = document.createSection('Project Statistics')
        pstatsTable = pstatsSection.createTable(['Page', 'Description'])

        # Projects By Elapsed
        pByE = self.documentProjectsByElapsed(stats)
        pstatsRow = pstatsTable.createRow()
        pstatsRow.createData().createLink(pByE, 'Projects By Elapsed Time')
        pstatsRow.createData('Time spent working on this project.')

        # Projects By Dependencies
        pByDep = self.documentProjectsByDependencies(stats)
        pstatsRow = pstatsTable.createRow()
        pstatsRow.createData().createLink(pByDep, 'Projects By Dependencies')
        pstatsRow.createData('Number of dependencies for the project.')

        # Projects By Dependees
        pByDepees = self.documentProjectsByDependees(stats)
        pstatsRow = pstatsTable.createRow()
        pstatsRow.createData().createLink(pByDepees, 'Projects By Dependees')
        pstatsRow.createData('Number of dependees for the project.')

        # Projects By FOG Factor
        pByFOG = self.documentProjectsByFOGFactor(stats)
        pstatsRow = pstatsTable.createRow()
        pstatsRow.createData().createLink(pByFOG, 'Projects By FOG Factor')
        pstatsRow.createData('Friend of Gump (FOG) Factor. A measure of ' + \
                                 'dependability (for other Gumpers).')

        # Projects By Sequence
        pBySeq = self.documentProjectsBySequenceInState(stats)
        pstatsRow = pstatsTable.createRow()
        pstatsRow.createData().createLink(pBySeq,
                                          'Projects By Duration in state')
        pstatsRow.createData('Duration in current state.')

        # Projects By Dependency Depth
        pByDepD = self.documentProjectsByDependencyDepth(stats)
        pstatsRow = pstatsTable.createRow()
        pstatsRow.createData().createLink(pByDepD,
                                          'Projects By Dependency Depth')
        pstatsRow.createData('Depth (in dependency tree) of the project.')

        # Projects By Dependency Depth
        pByTotDepD = self.documentProjectsByDependencyDepth(stats, 1)
        pstatsRow = pstatsTable.createRow()
        pstatsRow.createData().createLink(pByTotDepD,
                                          'Projects By Total Dependency Depth')
        pstatsRow.createData('Total Depth (sum of direct dependencies ' + \
                                 'depths) of the project.')

        document.serialize()

    def documentModulesByElapsed(self, stats):
        fileName = 'module_elapsed'
        spec = self.resolver.getFileSpec(stats, fileName)
        document = XDocDocument('Modules By Elapsed Time',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        elapsedTable = document.createTable(['Modules By Elapsed'])
        for module in stats.modulesByElapsed:
            if not self.gumpSet.inModuleSequence(module):
                continue
            elapsedRow = elapsedTable.createRow()
            self.insertLink(module, stats, elapsedRow.createData())
            elapsedRow\
                .createData(secsToElapsedTimeString(module.getElapsedSecs()))

        document.serialize()

        return fileName + '.html'

    def documentModulesByProjects(self, stats):
        fileName = 'module_projects'
        spec = self.resolver.getFileSpec(stats, fileName)
        document = XDocDocument('Modules By Project Count',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        mprojsTable = document.createTable(['Modules By Project Count'])
        for module in stats.modulesByProjectCount:
            if not self.gumpSet.inModuleSequence(module):
                continue
            mprojsRow = mprojsTable.createRow()

            self.insertLink(module, stats, mprojsRow.createData())

            mprojsRow.createData(len(module.getProjects()))

            #
            # :TODO:
            #projectsString = ''
            #for project in module.getProjects():
            #    projectsString += getContextLink(project)
            #    projectsString += ' '
            # mprojsRow.createData(projectsString)

        document.serialize()

        return fileName + '.html'

    def documentModulesByDependencies(self, stats):
        fileName = 'module_dependencies'
        spec = self.resolver.getFileSpec(stats, fileName)
        document = XDocDocument('Modules By Dependency Count',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        dependenciesTable = document.createTable(['Module',
                                                  'Full Dependency Count'])
        for module in stats.modulesByTotalDependencies:
            if not self.gumpSet.inModuleSequence(module):
                continue
            dependenciesRow = dependenciesTable.createRow()
            self.insertLink(module, stats, dependenciesRow.createData())
            dependenciesRow.createData(module.getFullDependencyCount())

            #projectsString = ''
            #for project in module.getDepends():
            #    projectsString += getContextLink(project)
            #    projectsString += ' '
            #dependenciesRow.createData(projectsString)

        document.serialize()

        return fileName + '.html'


    def documentModulesByDependees(self, stats):
        fileName = 'module_dependees'
        spec = self.resolver.getFileSpec(stats, fileName)
        document = XDocDocument('Modules By Dependee Count',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        dependeesTable = document.createTable(['Module', 'Full Dependee Count'])
        for module in stats.modulesByTotalDependees:
            if not self.gumpSet.inModuleSequence(module):
                continue
            dependeesRow = dependeesTable.createRow()
            self.insertLink(module, stats, dependeesRow.createData())
            dependeesRow.createData(module.getFullDependeeCount())

            #projectsString = ''
            #for project in module.getDependees():
            #    projectsString += getContextLink(project)
            #    projectsString += ' '
            #dependeesRow.createData(projectsString)

        document.serialize()

        return fileName + '.html'

    def documentModulesByFOGFactor(self, stats):
        fileName = 'module_fogfactor'
        spec = self.resolver.getFileSpec(stats, fileName)
        document = XDocDocument('Modules By FOG Factor',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())
        fogTable = document.createTable(['Module', 'FOG Factor'])
        for module in stats.modulesByFOGFactor:
            if not self.gumpSet.inModuleSequence(module):
                continue
            fogRow = fogTable.createRow()
            self.insertLink(module, stats, fogRow.createData())
            fogRow.createData('%02.2f' % module.getFOGFactor())

        document.serialize()

        return fileName + '.html'

    def documentModulesByLastModified(self, stats):
        fileName = 'module_modified'
        spec = self.resolver.getFileSpec(stats, fileName)
        document = XDocDocument('Modules By Last Modified',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())
        updTable = document.createTable(['Module', 'Last Modified Date',
                                         'Last Modified'])
        modules = 0
        for module in stats.modulesByLastModified:
            if not self.gumpSet.inModuleSequence(module):
                continue
            if module.isPackaged():
                continue
            updRow = updTable.createRow()
            self.insertLink(module, stats, updRow.createData())
            if module.hasLastModified():
                updRow.createData(module.getLastModified().isoformat())
                updRow.createData(
                    getGeneralSinceDescription(module.getLastModified()))
            else:
                updRow.createData('-')
                updRow.createData('-')

            modules += 1
        if not modules:
            updTable.createLine('None')

        document.serialize()

        return fileName + '.html'

    def documentProjectsByElapsed(self, stats):
        fileName = 'project_elapsed'
        spec = self.resolver.getFileSpec(stats, fileName)
        document = XDocDocument('Projects By Elapsed Time',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        elapsedTable = document.createTable(['Projects By Elapsed'])
        for project in stats.projectsByElapsed:
            if not self.gumpSet.inProjectSequence(project):
                continue
            elapsedRow = elapsedTable.createRow()
            self.insertLink(project, stats, elapsedRow.createData())
            elapsedRow\
                .createData(secsToElapsedTimeString(project.getElapsedSecs()))

        document.serialize()

        return fileName + '.html'

    def documentProjectsByDependencies(self, stats):
        fileName = 'project_dependencies'
        spec = self.resolver.getFileSpec(stats, fileName)
        document = XDocDocument('Projects By Dependency Count',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        dependenciesTable = document.createTable(['Project',
                                                  'Direct Dependency Count',
                                                  'Full Dependency Count'])
        for project in stats.projectsByTotalDependencies:
            if not self.gumpSet.inProjectSequence(project):
                continue
            dependenciesRow = dependenciesTable.createRow()
            self.insertLink(project, stats, dependenciesRow.createData())
            dependenciesRow.createData(project.getDependencyCount())
            dependenciesRow.createData(project.getFullDependencyCount())

            #projectsString = ''
            #for project in module.getDepends():
            #    projectsString += getContextLink(project)
            #    projectsString += ' '
            #dependenciesRow.createData(projectsString)

        document.serialize()

        return fileName + '.html'


    def documentProjectsByDependees(self, stats):
        fileName = 'project_dependees'
        spec = self.resolver.getFileSpec(stats, fileName)
        document = XDocDocument('Projects By Dependee Count',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        dependeesTable = document.createTable(['Project',
                                               'Direct Dependee Count',
                                               'Full Dependee Count'])
        for project in stats.projectsByTotalDependees:
            if not self.gumpSet.inProjectSequence(project):
                continue
            dependeesRow = dependeesTable.createRow()
            self.insertLink(project, stats, dependeesRow.createData())
            dependeesRow.createData(project.getDependeeCount())
            dependeesRow.createData(project.getFullDependeeCount())

            #projectsString = ''
            #for project in module.getDependees():
            #    projectsString += getContextLink(project)
            #    projectsString += ' '
            #dependeesRow.createData(projectsString)

        document.serialize()

        return fileName + '.html'

    def documentProjectsByFOGFactor(self, stats):
        fileName = 'project_fogfactor'
        spec = self.resolver.getFileSpec(stats, fileName)
        document = XDocDocument('Projects By FOG Factor',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())
        #fogTable = document.createTable(['Project', 'Successes', 'Failures',
        #                                 'Preq-Failures', 'FOG Factor'])
        fogTable = document.createTable(['Project', 'Successes', 'Failures',
                                         'Preq-Failures'])
        for project in stats.projectsByFOGFactor:
            if not self.gumpSet.inProjectSequence(project):
                continue
            fogRow = fogTable.createRow()
            self.insertLink(project, stats, fogRow.createData())

            pstats = project.getStats()

            fogRow.createData(pstats.successes)
            fogRow.createData(pstats.failures)
            fogRow.createData(pstats.prereqs)
            fogRow.createData('%02.2f' % pstats.getFOGFactor())

            # Generate an SVG for FOG:
            #(pngFile, pngTitle) = self.diagramFOG(project, stats)
            #if pngFile:
            #    fogRow.createData().createIcon(pngFile, pngTitle)
            #else:
            #    fogRow.createData('Not Available')

        document.serialize()

        return fileName + '.html'

    def documentProjectsBySequenceInState(self, stats):
        fileName = 'project_durstate'
        spec = self.resolver.getFileSpec(stats, fileName)
        document = XDocDocument('Projects By Duration In State',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())
        durTable = document.createTable(['Project', 'Duration\nIn State',
                                         'State'])
        for project in stats.projectsBySequenceInState:
            if not self.gumpSet.inProjectSequence(project):
                continue
            durRow = durTable.createRow()
            self.insertLink(project, stats, durRow.createData())

            pstats = project.getStats()

            durRow.createData(pstats.sequenceInState)
            durRow.createData(stateDescription(pstats.currentState))

        document.serialize()

        return fileName + '.html'

    def documentProjectsByDependencyDepth(self, stats, total = 0):
        if total:
            title = 'Projects By Total Dependency Depth'
            fileName = 'project_totdepdepth'
        else:
            title = 'Projects By Dependency Depth'
            fileName = 'project_depdepth'
        spec = self.resolver.getFileSpec(stats, fileName)
        document = XDocDocument(title,
                    spec.getFile(),
                    self.config,
                    spec.getRootPath())
        durTable = document.createTable(['Project', 'Dependency Depth',
                                         'Total Dependency Depth'])
        if total:
            list = stats.projectsByTotalDependencyDepth
        else:
            list = stats.projectsByDependencyDepth

        for project in list:
            if not self.gumpSet.inProjectSequence(project):
                continue
            durRow = durTable.createRow()
            self.insertLink(project, stats, durRow.createData())

            durRow.createData(project.getDependencyDepth())
            durRow.createData(project.getTotalDependencyDepth())

        document.serialize()

        return fileName + '.html'


    #####################################################################
    #
    # XRef Pages
    #
    def documentXRef(self):

        log.info('Generate XRef Guru')
        xref = XRefGuru(self.workspace)

        spec = self.resolver.getFileSpec(xref)
        document = XDocDocument('Cross Reference', self.resolver.getFile(xref),
                                self.config, spec.getRootPath())

        document.createParagraph("""
        Obscure views into projects/modules...
        """)

        ##################################################################3
        # Modules ...........
        mxrefSection = document.createSection('Module Cross Reference')
        mxrefTable = mxrefSection.createTable(['Page', 'Description'])

        # Modules By Repository
        mByR = self.documentModulesByRepository(xref)
        mxrefRow = mxrefTable.createRow()
        mxrefRow.createData().createLink(mByR, 'Modules By Repository')
        mxrefRow.createData('The repository that contains the module.')

        # Modules By Package
        mByP = self.documentModulesByPackage(xref)
        mxrefRow = mxrefTable.createRow()
        mxrefRow.createData().createLink(mByP, 'Modules By Package')
        mxrefRow.createData('The package(s) contained in the module.')

        # Modules By Description
        mByD = self.documentModulesByDescription(xref)
        mxrefRow = mxrefTable.createRow()
        mxrefRow.createData().createLink(mByD, 'Modules By Description')
        mxrefRow.createData('The descriptions for the module.')

        ##################################################################3
        # Projects ...........

        pxrefSection = document.createSection('Project Cross Reference')
        pxrefTable = pxrefSection.createTable(['Page', 'Description'])

        # Projects By Package
        pByP = self.documentProjectsByPackage(xref)
        pxrefRow = pxrefTable.createRow()
        pxrefRow.createData().createLink(pByP, 'Projects By Package')
        pxrefRow.createData('The package(s) contained in the project.')

        # Projects By Description
        pByD = self.documentProjectsByDescription(xref)
        pxrefRow = pxrefTable.createRow()
        pxrefRow.createData().createLink(pByD, 'Projects By Description')
        pxrefRow.createData('The descriptions for the project.')

        # Projects By Outputs
        pByO = self.documentProjectsByOutput(xref)
        pxrefRow = pxrefTable.createRow()
        pxrefRow.createData().createLink(pByO, 'Projects By Output')
        pxrefRow.createData('The outputs for the project, e.g. outputs.')

        # Projects By Output Ids
        pByOI = self.documentProjectsByOutputId(xref)
        pxrefRow = pxrefTable.createRow()
        pxrefRow.createData().createLink(pByOI, 'Projects By Output Identifier')
        pxrefRow.createData('The identifiers for outputs for the project, ' + \
                                'e.g. outputs.')

        # Projects By Descriptor Location
        pByDL = self.documentProjectsByDescriptorLocation(xref)
        pxrefRow = pxrefTable.createRow()
        pxrefRow.createData().createLink(pByDL,
                                         'Projects By Descriptor Location')
        pxrefRow.createData('The descriptor for the project.')

        document.serialize()

    def documentModulesByRepository(self, xref):
        fileName = 'repo_module'
        spec = self.resolver.getFileSpec(xref, fileName)
        document = XDocDocument('Modules By Repository',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        repoMap = xref.getRepositoryToModuleMap()
        repoList = createOrderedList(repoMap.keys())
        rcount = 0
        if repoList:
            for repo in repoList:
                if not self.gumpSet.inRepositories(repo):
                    continue
                rcount += 1

                moduleList = createOrderedList(repoMap.get(repo))
                repoSection = document.createSection(repo.getName())
                self.insertLink(repo, xref,
                                repoSection\
                                    .createParagraph('Repository Definition: '))

                moduleRepoTable = repoSection.createTable(['Modules'])
                for module in moduleList:
                    if not self.gumpSet.inModuleSequence(module):
                        continue
                    moduleRepoRow = moduleRepoTable.createRow()
                    self.insertLink(module, xref, moduleRepoRow.createData())

        if not rcount:
            document.createParagraph('No repositories')

        document.serialize()

        return fileName + '.html'

    def documentModulesByPackage(self, xref):
        fileName = 'package_module'
        spec = self.resolver.getFileSpec(xref, fileName)
        document = XDocDocument('Modules By Package',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        packageTable = document.createTable(['Modules By Package'])

        packageMap = xref.getPackageToModuleMap()
        for package in createOrderedList(packageMap.keys()):

            moduleList = createOrderedList(packageMap.get(package))

            hasSome = 0
            for module in moduleList:
                if not self.gumpSet.inModuleSequence(module):
                    continue
                hasSome = 1

            if hasSome:
                packageRow = packageTable.createRow()
                packageRow.createData(package)

                moduleData = packageRow.createData()
                for module in moduleList:
                    if not self.gumpSet.inModuleSequence(module):
                        continue
                    self.insertLink(module, xref, moduleData)
                    moduleData.createText(' ')

        document.serialize()

        return fileName + '.html'


    def documentModulesByDescription(self, xref):
        fileName = 'description_module'
        spec = self.resolver.getFileSpec(xref, fileName)
        document = XDocDocument('Modules By Description',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        descriptionTable = document.createTable(['Modules By Description'])

        descriptionMap = xref.getDescriptionToModuleMap()
        for description in createOrderedList(descriptionMap.keys()):

            moduleList = createOrderedList(descriptionMap.get(description))

            hasSome = 0
            for module in moduleList:
                if not self.gumpSet.inModuleSequence(module):
                    continue
                hasSome = 1

            if hasSome:
                descriptionRow = descriptionTable.createRow()
                descriptionRow.createData(description)

                moduleData = descriptionRow.createData()
                for module in moduleList:
                    if not self.gumpSet.inModuleSequence(module):
                        continue
                    self.insertLink(module, xref, moduleData)
                    moduleData.createText(' ')

        document.serialize()

        return fileName + '.html'

    def documentProjectsByPackage(self, xref):
        fileName = 'package_project'
        spec = self.resolver.getFileSpec(xref, fileName)
        document = XDocDocument('Projects By Package',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        packageTable = document.createTable(['Projects By Package'])

        packageMap = xref.getPackageToProjectMap()
        for package in createOrderedList(packageMap.keys()):

            projectList = createOrderedList(packageMap.get(package))

            hasSome = 0
            for project in projectList:
                if not self.gumpSet.inProjectSequence(project):
                    continue
                hasSome = 1

            if hasSome:
                packageRow = packageTable.createRow()
                packageRow.createData(package)

                projectData = packageRow.createData()
                for project in projectList:
                    if not self.gumpSet.inProjectSequence(project):
                        continue
                    self.insertLink(project, xref, projectData)
                    projectData.createText(' ')

        document.serialize()

        return fileName + '.html'

    def documentProjectsByDescription(self, xref):
        fileName = 'description_project'
        spec = self.resolver.getFileSpec(xref, fileName)
        document = XDocDocument('Projects By Description',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        descriptionTable = document.createTable(['Projects By Description'])

        descriptionMap = xref.getDescriptionToProjectMap()
        for description in createOrderedList(descriptionMap.keys()):

            projectList = createOrderedList(descriptionMap.get(description))

            hasSome = 0
            for project in projectList:
                if not self.gumpSet.inProjectSequence(project):
                    continue
                hasSome = 1

            if hasSome:
                descriptionRow = descriptionTable.createRow()
                descriptionRow.createData(description)

                projectData = descriptionRow.createData()
                for project in projectList:
                    if not self.gumpSet.inProjectSequence(project):
                        continue
                    self.insertLink(project, xref, projectData)
                    projectData.createText(' ')

        document.serialize()

        return fileName + '.html'


    def documentProjectsByOutput(self, xref):
        fileName = 'output_project'
        spec = self.resolver.getFileSpec(xref, fileName)
        document = XDocDocument('Projects By Outputs (e.g. Outputs)',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        outputTable = document.createTable(['Projects By Outputs ' + \
                                                '(e.g. Outputs)'])

        outputMap = xref.getOutputToProjectMap()
        for output in createOrderedList(outputMap.keys()):

            projectList = createOrderedList(outputMap.get(output))

            hasSome = 0
            for project in projectList:
                if not self.gumpSet.inProjectSequence(project):
                    continue
                hasSome = 1

            if hasSome:
                outputRow = outputTable.createRow()
                outputRow.createData(output)

                projectData = outputRow.createData()
                for project in projectList:
                    if not self.gumpSet.inProjectSequence(project):
                        continue
                    self.insertLink(project, xref, projectData)
                    projectData.createText(' ')

        document.serialize()

        return fileName + '.html'

    def documentProjectsByOutputId(self, xref):
        fileName = 'output_id_project'
        spec = self.resolver.getFileSpec(xref, fileName)
        document = XDocDocument('Projects By Output Identifiers',
                                spec.getFile(),
                                self.config,
                                spec.getRootPath())

        outputTable = document.createTable(['Projects By Output Identifiers'])

        outputMap = xref.getOutputIdToProjectMap()
        for outputId in createOrderedList(outputMap.keys()):

            projectList = createOrderedList(outputMap.get(outputId))

            hasSome = 0
            for project in projectList:
                if not self.gumpSet.inProjectSequence(project):
                    continue
                hasSome = 1

            if hasSome:
                outputRow = outputTable.createRow()
                outputRow.createData(outputId)

                projectData = outputRow.createData()
                for project in projectList:
                    if not self.gumpSet.inProjectSequence(project):
                        continue
                    self.insertLink(project, xref, projectData)
                    projectData.createText(' ')

        document.serialize()

        return fileName + '.html'

    def documentProjectsByDescriptorLocation(self, xref):
        fileName = 'descriptor_project'
        spec = self.resolver.getFileSpec(xref, fileName)
        document = XDocDocument('Projects By Descriptor Location',
                spec.getFile(),
                self.config,
                spec.getRootPath())

        descLocnTable = document.createTable(['Projects By Descriptor ' + \
                                                  'Location'])

        descLocnMap = xref.getDescriptorLocationToProjectMap()
        for descLocn in createOrderedList(descLocnMap.keys()):

            projectList = createOrderedList(descLocnMap.get(descLocn))

            hasSome = 0
            for project in projectList:
                if not self.gumpSet.inProjectSequence(project):
                    continue
                hasSome = 1

            if hasSome:
                descLocnRow = descLocnTable.createRow()
                descLocnRow.createData(descLocn)

                projectData = descLocnRow.createData()
                for project in projectList:
                    if not self.gumpSet.inProjectSequence(project):
                        continue
                    self.insertLink(project, xref, projectData)
                    projectData.createText(' ')

        document.serialize()

        return fileName + '.html'

