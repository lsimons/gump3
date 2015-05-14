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

    The model for a 'Project'

"""

import glob
import os
import sys
import gump.util.process.command

from gump import log
from gump.core.config import default
from gump.core.model.builder import Ant, NAnt, Maven1, Maven, MvnInstall, \
    MVN_VERSION2, MVN_VERSION3, Script, Configure, Make, Gradle, MSBuild, \
    NuGet
from gump.core.model.depend import Dependable, importDomDependency
from gump.core.model.misc import AddressPair, \
    Resultable, Positioned, Mkdir, Delete, Report, Work
from gump.core.model.object import NamedModelObject
from gump.core.model.output import Output
from gump.core.model.state import REASON_CONFIG_FAILED, STATE_FAILED, \
    STATE_PREREQ_FAILED, REASON_MISSING_OUTPUTS
from gump.core.model.stats import Statable, Statistics
from gump.util import getIndent, getStringFromUnicode
from gump.util.domutils import transferDomInfo, hasDomAttribute, \
    getDomAttributeValue, getDomTextValue, getDomChildIterator
from gump.util.note import transferAnnotations

class Project(NamedModelObject, Statable, Resultable, Dependable, Positioned):
    """ A Single project """

    UNSET_LANGUAGE = 0
    JAVA_LANGUAGE = 1
    CSHARP_LANGUAGE = 2

    LANGUAGE_MAP = {
        'java' : JAVA_LANGUAGE, 
        'csharp' : CSHARP_LANGUAGE
    }

    def __init__(self, name, xml, owner):
        NamedModelObject.__init__(self, name, xml, owner)

        Statable.__init__(self)
        Resultable.__init__(self)
        Dependable.__init__(self)
        Positioned.__init__(self)

        # Navigation
        self.module = None # Module has to claim ownership
        self.workspace = None

        self.home = None
        self.basedir = None

        self.license = None

        self.languageType = Project.JAVA_LANGUAGE

        self.affectedProjects = []

        #############################################################
        #
        # Sub-Components
        #
        self.ant = None
        self.nant = None
        self.msbuild = None
        self.nuget = None
        self.maven = None
        self.mvn = None
        self.script = None
        self.configure = None
        self.make = None
        self.gradle = None
        self.builder = []

        self.works = []
        self.mkdirs = []
        self.deletes = []
        self.reports = []
        self.notifys = []

        self.url = None
        self.desc = ''
        self.groupId = ''

        self.redistributable = False
        self.packageMarker = None
        self.jvmargs = gump.util.process.command.Parameters()
        self.packageNames = None

        #############################################################
        # Outputs (like jars, assemblies, poms ...)
        #
        # kept as {type => [outputs of that type]}
        self.outputs = {}
        self.outputs_expanded = False

        #############################################################
        # Misc
        #
        self.honoraryPackage = False
        self.built = False

        # removed dependencies
        self.removes = []

    def __del__(self):
        NamedModelObject.__del__(self)
        Statable.__del__(self)
        Resultable.__del__(self)
        Dependable.__del__(self)
        Positioned.__del__(self)

    def hasNotifys(self):
        """
        Does this project have any notification addresses, and if not
        does the module?

        boolean true if some
        """
        if self.notifys:
            return True
        if self.module:
            return self.module.hasNotifys()
        return False

    def getNotifys(self):
        """
                Return the list of notification addresses for this project
                but if none, see if the module has any.
        """
        if not self.notifys: 
            if self.module:
                return self.module.getNotifys()
        return self.notifys

    def getArtifactGroup(self):
        """
        What do this project's artifacts group under?
        Ask the module unless overridden

        Return String
        """
        if self.groupId:
            return self.groupId
        return self.getModule().getArtifactGroup()

    def hasAnt(self):
        if self.ant:
            return True
        return False

    def hasNAnt(self):
        if self.nant:
            return True
        return False

    def hasMSBuild(self):
        if self.msbuild:
            return True
        return False

    def hasNuGet(self):
        if self.nuget:
            return True
        return False

    def hasMaven(self):
        if self.maven:
            return True
        return False

    def hasMvn(self):
        if self.mvn:
            return True
        return False

    def hasScript(self):
        if self.script:
            return True
        return False

    def hasConfigure(self):
        if self.configure:
            return True
        return False

    def hasMake(self):
        if self.make:
            return True
        return False

    def hasGradle(self):
        if self.gradle:
            return True
        return False

    def getAnt(self):
        return self.ant

    def getNAnt(self):
        return self.nant

    def getMSBuild(self):
        return self.msbuild

    def getNuGet(self):
        return self.nuget

    def getMaven(self):
        return self.maven

    def getMvn(self):
        return self.mvn

    def getScript(self):
        return self.script

    def getConfigure(self):
        return self.configure

    def getMake(self):
        return self.make

    def getGradle(self):
        return self.gradle

    def hasUrl(self):
        if self.url or self.getModule().hasUrl():
            return True
        return False

    def getUrl(self):
        return self.url or self.getModule().getUrl()

    def hasDescription(self):
        if self.desc or self.getModule().hasDescription():
            return True
        return False

    def getDescription(self):
        return self.desc or self.getModule().getDescription()

    def getLimitedDescription(self, limit = 60):
        desc = self.getDescription()
        if len(desc) > limit:
            desc = desc[:limit]
            desc += '...'
        return desc

    def getMetadataLocation(self):
        return self.metadata or self.getModule().getMetadataLocation()

    def getMetadataViewUrl(self):
        if self.metadata:
            location = self.metadata
            if location.startswith('http'):
                return location
            # :TODO: Make configurable
            return 'http://svn.apache.org/repos/asf/gump/metadata/' + location
        return self.getModule().getMetadataViewUrl()

    def getViewUrl(self):
        # :TODO: if a basedir then offset?
        return self.getModule().getViewUrl()

    def addOutput(self, output):
        if output.getType() not in self.outputs:
            self.outputs[output.getType()] = []
        self.outputs[output.getType()].append(output)

    def hasLicense(self):
        if self.license:
            return True
        return False

    def getLicense(self):
        return self.license

    def getDeletes(self):
        return self.deletes
    def getMkDirs(self):
        return self.mkdirs
    def getWorks(self):
        return self.works

    def hasOutputs(self):
        if self.outputs:
            return True
        return False

    def getOutputs(self):
        self.expand_outputs()
        return reduce(lambda l1, l2: l1 + l2, self.outputs.itervalues(), [])

    def expand_outputs(self):
        """ expands glob patterns in output names """
        if (self.built or not self.hasBuilder()) and not self.outputs_expanded:
            for l in self.outputs.itervalues():
                for output in l:
                    path = output.getPath()
                    log.debug("glob expanding " + path)
                    expansions = glob.glob(path)
                    count = len(expansions)
                    if count > 1:
                        self.changeState(STATE_FAILED, REASON_MISSING_OUTPUTS)
                        self.addError("%s matched %d files." % (path, count))
                    elif count == 1:
                        log.debug("replacing " + path + " with " \
                                      + expansions[0])
                        output.setPath(expansions[0])
                    else:
                        log.debug("didn't find any match for " + path)
            self.outputs_expanded = True

    def hasAnyOutputs(self):
        """
        Does this project generate outputs (currently JARs)
        """
        return self.hasOutputs() or self.hasLicense()

    def hasPackageNames(self):
        if self.packageNames:
            return True
        return False

    def getPackageNames(self):
        return self.packageNames

    def isRedistributable(self):
        return self.redistributable or \
            (self.module and self.module.isRedistributable())

    def wasBuilt(self):
        """ Was a build attempt made? """
        return self.built

    def setBuilt(self, built = True):
        self.built = built

    def hasReports(self):
        if self.reports:
            return True
        return False

    def getReports(self):
        return self.reports

    def getFOGFactor(self):
        return self.getStats().getFOGFactor()

    def getHistoricalOddsOfSuccess(self):
        return self.getStats().getHistoricalOddsOfSuccess()

    # Only modules get Modified.
    def getLastModified(self):
        return self.getModule().getStats().getLastModified()

    def countAffectedProjects(self):
        return len(self.affectedProjects)

    def getAffectedProjects(self):
        return self.affectedProjects

    def addAffected(self, project):
        self.affectedProjects.append(project)
        self.affectedProjects.sort()

    def propagateErrorStateChange(self, _state, reason, cause, message):

        #
        # Mark depend*ee*s as failed for this cause...
        # Warn option*ee*s
        #
        for dependee in self.getDirectDependees():

            # This is a backwards link, so use the owner
            dependeeProject = dependee.getOwnerProject()

            if dependee.isOptional():
                dependeeProject.addInfo("Optional dependency " + self.name + \
                                            " " + message)
            else:
                dependee.addInfo("Dependency " + self.name + " " + message)
                dependeeProject.changeState(STATE_PREREQ_FAILED, reason, cause)
    #
    # We have a potential clash between the <project package attribute and
    # the <project <package element. The former indicates a packages install
    # the latter the (Java) package name for the project contents. 
    #
    def isPackaged(self):
        return self.isPackageMarked() or self.honoraryPackage

    def isPackageMarked(self):
        if self.packageMarker:
            return True
        return False

    def getPackageMarker(self):
        return self.packageMarker

    def setHonoraryPackage(self, honorary = True):
        self.honoraryPackage = honorary

    def isGumped(self):
        return (not self.isPackaged()) and self.hasBuilder()

    # provide elements when not defined in xml
    def complete(self, workspace, visited = None): 

        # Give some indication when spinning on
        # circular dependencies, 'cos even though we
        # have code in to not spin, never assume never...
        log.debug('Complete: %s, Path: %s' % (self, visited))

        if self.isComplete():
            return

        # Create a copy, for recursion, and
        # detection of circular paths.
        new_visited = [self]
        if visited:
            new_visited += visited

        if not self.inModule():
            self.changeState(STATE_FAILED, REASON_CONFIG_FAILED)
            self.addError("Not in a module")
            return

        # :TODO: hacky
        self.workspace = workspace

        # Import overrides from DOM
        transferDomInfo(self.element, self, {})

        # Somebody overrode this as a package
        if self.hasDomAttribute('package'):
            self.packageMarker = self.getDomAttributeValue('package')

        # Packaged Projects don't need the full treatment..
        packaged = self.isPackaged()

        # Import any <ant part [if not packaged]
        if self.hasDomChild('ant') and not packaged:
            self.ant = Ant(self.getDomChild('ant'), self)
            self.builder.append(self.ant)

            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.ant, self)

        # Import any <nant part [if not packaged]
        if self.hasDomChild('nant') and not packaged:
            self.nant = NAnt(self.getDomChild('nant'), self)
            self.builder.append(self.nant)

            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.nant, self)

        # Import any <msbuild part [if not packaged]
        if self.hasDomChild('msbuild') and not packaged:
            self.msbuild = MSBuild(self.getDomChild('msbuild'), self)
            self.builder.append(self.msbuild)

        # Import any <nuget part [if not packaged]
        if self.hasDomChild('nuget') and not packaged:
            self.msbuild = NuGet(self.getDomChild('nuget'), self)
            self.builder.append(self.nuget)

        # Import any <maven part [if not packaged]
        for tag in ['maven', 'mvn1']:
            if self.hasDomChild(tag) and not packaged:
                self.maven = Maven1(self.getDomChild(tag), self)
                self.builder.append(self.maven)

            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.maven, self)

        # Import any <mvn part [if not packaged]
        for tag in ['mvn', 'mvn2']:
            if self.hasDomChild(tag) and not packaged:
                self.mvn = Maven(self.getDomChild(tag), self, MVN_VERSION2)
                self.builder.append(self.mvn)

            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.maven, self)

        # Import any <mvninstall part [if not packaged]
        for tag in ['mvninstall', 'mvn2install']:
            if self.hasDomChild(tag) and not packaged:
                self.mvn = MvnInstall(self.getDomChild(tag), self, MVN_VERSION2)
                self.builder.append(self.mvn)

            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.maven, self)

        # Import any <mvn3 part [if not packaged]
        if self.hasDomChild('mvn3') and not packaged:
            self.mvn = Maven(self.getDomChild('mvn3'), self, MVN_VERSION3)
            self.builder.append(self.mvn)

        # Import any <mvn3install part [if not packaged]
        if self.hasDomChild('mvn3install') and not packaged:
            self.mvn = MvnInstall(self.getDomChild('mvn3install'), self,
                                  MVN_VERSION3)
            self.builder.append(self.mvn)

            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.maven, self)

        # Import any <script part [if not packaged]
        if self.hasDomChild('script') and not packaged:
            self.script = Script(self.getDomChild('script'), self)
            self.builder.append(self.script)

            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.script, self)

        # Import any <make part [if not packaged]
        if self.hasDomChild('make') and not packaged:
            self.make = Make(self.getDomChild('make'), self)
            self.builder.append(self.make)

            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.make, self)

        # Import any <configure part [if not packaged]
        if self.hasDomChild('configure') and not packaged:
            self.configure = Configure(self.getDomChild('configure'), self)
            self.builder.append(self.configure)

            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.configure, self)

        # Import any <gradle part [if not packaged]
        if self.hasDomChild('gradle') and not packaged:
            self.gradle = Gradle(self.getDomChild('gradle'), self)
            self.builder.append(self.gradle)

            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.gradle, self)

        # Set this up to be the base directory of this project, 
        # if one is set
        self.basedir = os.path.abspath(os.path.join(
                self.getModule().getWorkingDirectory() or dir.base,
                self.getDomAttributeValue('basedir', '')))

        # Compute home directory
        if self.isPackaged():
            # Installed below package directory
            if self.isPackageMarked():
                self.home = os.path.abspath(
                    os.path.join(
                        workspace.pkgdir, 
                        self.getDomAttributeValue('package')))
            else:
                self.home = os.path.abspath(workspace.pkgdir)
        elif self.hasDomChild('home'):
            home = self.getDomChild('home')
            if hasDomAttribute(home, 'nested'):
                nested = self.expandVariables(
                    getDomAttributeValue(home, 'nested'))
                self.home = os.path.abspath(
                    os.path.join(self.getModule().getWorkingDirectory(), 
                                    nested))
            elif hasDomAttribute(home, 'parent'):
                parent = self.expandVariables(
                    getDomAttributeValue(home, 'parent'))
                self.home = os.path.abspath(
                    os.path.join(workspace.getBaseDirectory(), parent))
            else:
                message = ('Unable to complete project.home for %s' +
                           ' [not nested/parent] : %s') \
                           % (self.name, home)
                self.addError(message)
                log.warning(message)
                self.home = None
        else:
            if self.module:
                module = self.getModule()
                self.home = os.path.abspath(module.getWorkingDirectory())
            else:
                self.home = os.path.abspath(
                            os.path.join(
                                workspace.getBaseDirectory(), 
                                self.name))
        # Forget how this could be possible...
        #else:
        #    message = 'Unable to complete project.home for: ' + self.name 
        #    self.addError(message)
        #    self.home = None


        # The language type java or CSharp or ...
        if self.hasDomAttribute('language'):
            self.setLanguageTypeFromString(self
                                           .getDomAttributeValue('language'))


        # Extract license 
        if self.hasDomChild('license'):
            license = self.getDomChild('license')
            if hasDomAttribute(license, 'name'):
                self.license = getDomAttributeValue(license, 'name')
            else:
                self.addError('Missing \'name\' on <license')

        #
        # Resolve outputs
        #
        self.handle_outputs()

        # Grab all the work
        for w in self.getDomChildIterator('work'):
            work = Work(w, self)
            work.complete()
            self.works.append(work)

        # Grab all the mkdirs
        for m in self.getDomChildIterator('mkdir'):
            mkdir = Mkdir(m, self)
            mkdir.complete()
            self.mkdirs.append(mkdir)

        # Grab all the deleted
        for d in self.getDomChildIterator('delete'):
            delete = Delete(d, self)
            delete.complete()
            self.deletes.append(delete)

        # Grab all the reports (junit for now)
        for r in self.getDomChildIterator('junitreport'):
            self._add_report(r)
        for r in self.getDomChildIterator('report'):
            self._add_report(r)

        # Grab all notifications
        for notifyEntry in self.getDomChildIterator('nag'):
            # Determine where to send
            toaddr = getDomAttributeValue(notifyEntry, 'to', 
                                        workspace.administrator)
            fromaddr = getDomAttributeValue(notifyEntry, 'from',
                                            workspace.email)
            self.notifys.append(
                    AddressPair(
                        getStringFromUnicode(toaddr), 
                        getStringFromUnicode(fromaddr)))

        # Build Dependencies Map [including depends from
        # <ant|maven/<property/<depend
        if not packaged:
            (badDepends, badOptions) = self.importDependencies(workspace)

        # Expand <ant <depends/<properties...
        [b.expand(self, workspace) for b in self.builder]

        if not packaged:
            self.removes = []

            # Complete dependencies so properties can reference the, 
            # completed metadata within a dependent project
            for dependency in self.getDirectDependencies():
                depProject = dependency.getProject()
                if depProject in new_visited:
                    for circProject in new_visited:
                        circProject.changeState(STATE_FAILED, 
                                                REASON_CONFIG_FAILED)
                        circProject.addError("Circular Dependency. Path: " + \
                                                 "%s -> %s." % \
                                                 (new_visited,
                                                  depProject.getName()))

                    self.addError("Dependency broken, removing dependency " + \
                                      "on %s from %s." % \
                                      (depProject.getName(), self.getName()))

                    self.removes.append(dependency)
                else:
                    # Don't redo what is done.
                    if not depProject.isComplete():
                        # Recurse, knowing which project
                        # is in this list.
                        depProject.complete(workspace, new_visited)

            # Remove circulars...
            for dependency in self.removes:
                self.removeDependency(dependency)

            self.buildDependenciesMap(workspace)

        if self.hasDomChild('url'):
            url = self.getDomChild('url')
            self.url = getDomAttributeValue(url, 'href')

        if self.hasDomChild('description'):
            self.desc = self.getDomChildValue('description')

        jvmargs_parents = ['ant', 'maven', 'mvn', 'mvn1', 'mvn2', 'mvn3', 'gradle']
        for tag in jvmargs_parents:
            if self.hasDomChild(tag):
                self.addJVMArgs(self.getDomChild(tag))

        #
        # complete properties
        #
        [self.completeAndTransferAnnotations(b, workspace) \
             for b in self.builder]

        if not packaged:
            #
            # TODO -- move these back?
            #
            if badDepends or badOptions: 
                for badDep in badDepends:
                    (xmldepend, reason) = badDep
                    self.changeState(STATE_FAILED, REASON_CONFIG_FAILED)
                    self.addError("Bad Dependency. Project: %s : %s " \
                            % (getDomAttributeValue(xmldepend, 'project'), 
                               reason))

                for badOpt in badOptions:
                    (xmloption, reason) = badOpt
                    self.addWarning("Bad *Optional* Dependency. " + \
                                        "Project: %s : %s" \
                                        % (getDomAttributeValue(xmloption,
                                                                'project'), 
                                           reason))
        else:
            self.addInfo("This is a packaged project, location: " + self.home)

        # Copy over any XML errors/warnings
        # :TODO:#1: transferAnnotations(self.xml, self)

        #if not self.home:
        #    raise RuntimeError, 'A home directory is needed on ' + `self`

        # Existence means 'true'
        self.redistributable = self.hasDomChild('redistributable')

        # Store any 'Java Package names'
        for pdom in self.getDomChildIterator('package'):
            packageName = getDomTextValue(pdom)
            if packageName:
                if not self.packageNames:
                    self.packageNames = []
                if not packageName in self.packageNames:
                    self.packageNames.append(packageName)

        # Close down the DOM...
        self.shutdownDom()

        # Done so don't redo
        self.setComplete(True)

    # turn the <jvmarg> children of domchild into jvmargs
    def addJVMArgs(self, domChild):
        for jvmarg in getDomChildIterator(domChild, 'jvmarg'):
            if hasDomAttribute(jvmarg, 'value'):
                self.jvmargs.addParameter(getDomAttributeValue(jvmarg, 'value'))
            else:
                log.error('Bogus JVM Argument w/ Value')

    def importDependencies(self, workspace):
        badDepends = []
        # Walk the DOM parts converting
        for ddom in self.getDomChildIterator('depend'):
            dependProjectName = getDomAttributeValue(ddom, 'project')
            if workspace.hasProject(dependProjectName):
                dependProject = workspace.getProject(dependProjectName)

                # Import the dependency
                dependency = importDomDependency(self, dependProject, ddom, 0)

                # Add a dependency
                self.addDependency(dependency)
            else:
                badDepends.append((ddom, "unknown to *this* workspace"))

        # Walk the XML parts converting
        badOptions = []
        for odom in self.getDomChildIterator('option'):
            optionProjectName = getDomAttributeValue(odom, 'project')
            if workspace.hasProject(optionProjectName):
                optionProject = workspace.getProject(optionProjectName)

                # Import the dependency
                dependency = importDomDependency(self, optionProject, odom, 1)

                # Add a dependency
                self.addDependency(dependency)
            else:
                badOptions.append((odom, "unknown to *this* workspace"))

        return (badDepends, badOptions)

    def get_removed_dependencies(self):
        """
        ProjectDependencies that have been removed in order to break
        circular dependencies.
        """
        return self.removes

    def hasBaseDirectory(self):
        if self.basedir:
            return True
        return False

    def getBaseDirectory(self):
        return self.basedir

    def hasHomeDirectory(self):
        if self.home:
            return True
        return False

    def getHomeDirectory(self):
        return self.home

    def inModule(self):
        return hasattr(self, 'module') and self.module

    def setModule(self, module):
        if self.module:
            raise RuntimeError, \
                'Project [' + self.name + '] already has a module set'
        self.module = module

    def getModule(self):
        if not self.inModule():
            raise RuntimeError, 'Project [' + self.name + '] not in a module.]'
        return self.module 

    def getWorkspace(self):
        return self.workspace

    def hasBuilder(self):
        """
        Does this project have a builder?
        """
        if len(self.builder) > 0:
            return 1
        else:
            return 0

    def dump(self, indent = 0, output = sys.stdout):
        """ 
        Display the contents of this object 
        """
        i = getIndent(indent)
        i1 = getIndent(indent + 1)
        output.write(i + 'Project: ' + self.getName() + '\n')
        NamedModelObject.dump(self, indent + 1, output)

        if self.isPackageMarked():
            output.write(i1 + 'Packaged: ' + self.getPackageMarker() + '\n')

        Dependable.dump(self, indent, output)

        [b.dump(indent + 1, output) for b in self.builder + self.works \
             + self.getOutputs()]

    def getAnnotatedOutputsList(self): 
        """
        Return a list of the outputs this project generates
        """
        outs = []
        for output in self.getOutputs():
            path = output.getPath()
            outs.append(gump.core.language.path.AnnotatedPath(output.getId(), 
                                                              path, self, None, 
                                                              "Project output"))
        return outs

    def setLanguageTypeFromString(self, lang = None):
        try:
            self.languageType = Project.LANGUAGE_MAP[lang]
        except:
            message = 'Language %s not in supported %s.' \
                % (lang, Project.LANGUAGE_MAP.keys())
            self.addWarning(message)
            log.warning(message)

    def getLanguageType(self):
        return self.languageType

    def setLanguageType(self, langType):
        self.languageType = langType

    def completeAndTransferAnnotations(self, b, workspace):
        b.complete(self, workspace)
        transferAnnotations(b, self)

    def handle_outputs(self):
        """
        Parse all child elements that define outputs and resolve their ids
        """
        output_tags = ['jar',
                       'assembly',
                       'output',
                       'pom']
        rawOutputs = []
        outputCountByType = {}

        for tag in output_tags:
            for tdom in self.getDomChildIterator(tag):
                name = self.expandVariables(getDomAttributeValue(tdom, 'name'))

                if self.home and name:
                    output = Output(name, tdom, self)
                    output.complete()
                    output.setPath(os.path.abspath(os.path.join(self.home,
                                                                name)))
                    if not output.getType() and tag != 'output':
                        output.setType(tag)
                    rawOutputs.append(output)
                    if output.getType() not in outputCountByType:
                        outputCountByType[output.getType()] = 1
                    else:
                        outputCountByType[output.getType()] = \
                            outputCountByType[output.getType()] + 1
                else:
                    self.addError('Missing \'name\' on <' + tag)


        # Fix 'ids' on all outputs which don't have them
        for output in rawOutputs:
            if not output.hasId():
                if 1 == outputCountByType[output.getType()]:
                    self.addDebug('Sole ' + output.getType() + ' output [' + \
                                      os.path.basename(output.getPath()) + \
                                      '] identifier set to project name')
                    output.setId(self.getName())
                else:
                    # :TODO: A work in progress, not sure how
                    # we ought 'construct' ids.
                    basename = os.path.basename(output.getPath())
                    newId = basename
                    # Strip off .jar or .lib (note: both same length)
                    if newId.endswith('.jar') or newId.endswith('.lib'):
                        newId = newId[:-4]
                    # Strip off -@@DATE@@
                    datePostfix = '-' + str(default.date_s)
                    if newId.endswith(datePostfix):
                        reduction = -1 * len(datePostfix)
                        newId = newId[:reduction]
                    # Assign...
                    self.addDebug('Output [' + basename + \
                                      '] identifier set to output ' + \
                                      'basename: [' + newId + ']')
                    output.setId(newId)
            self.addOutput(output)

        # ensure id is unique per output type
        for output_type in self.outputs.keys():
            d = {}
            remove = []
            for o in self.outputs[output_type]:
                if o.getId() in d:
                    self.addWarning("Multiple " + output_type + " outputs " \
                                        + " use id " + o.getId() \
                                        + " dropping " + o.getPath())
                    remove.append(o)
                else:
                    d[o.getId()] = True
            for o in remove:
                self.outputs[output_type].remove(o)

    def _add_report(self, report_dom):
        report = Report(report_dom, self)
        report.complete()
        self.reports.append(report)

class ProjectStatistics(Statistics):
    """Statistics Holder"""
    def __init__(self, projectName):
        Statistics.__init__(self, projectName)

    def getKeyBase(self):
        return 'project:' + self.name


class ProjectSummary:
    """ Contains an overview """
    def __init__(self, projects = 0, successes = 0, failures = 0,
                 prereqs = 0, noworks = 0, packages = 0,
                 others = 0, statepairs = None):

        # Counters
        self.projects = projects
        self.successes = successes
        self.failures = failures
        self.prereqs = prereqs
        self.noworks = noworks
        self.packages = packages
        self.others = others
        self.statepairs = statepairs

        # Percentages
        self.overallPercentage = 0
        self.successesPercentage = 0
        self.failuresPercentage = 0
        self.prereqsPercentage = 0
        self.noworksPercentage = 0
        self.packagesPercentage = 0
        self.othersPercentage = 0

        #
        if not self.statepairs:
            self.statepairs = []

        self.calculatePercentages()

    def addState(self, state):
        # Stand up and be counted
        if state.isSuccess():
            self.successes += 1
        elif state.isPrereqFailed():
            self.prereqs += 1
        elif state.isFailed():
            self.failures += 1
        elif state.isUnset():
            self.noworks += 1
        elif state.isComplete():
            # :TODO: Accurate?
            self.packages += 1
        else:
            self.others += 1

        # One more project...
        self.projects += 1

        # Add state, if not already there
        if not state.isUnset() and not state in self.statepairs:
            self.statepairs.append(state)

        self.calculatePercentages()

    def addSummary(self, summary):

        self.projects += summary.projects

        self.successes += summary.successes
        self.failures += summary.failures
        self.prereqs += summary.prereqs
        self.noworks += summary.noworks
        self.packages += summary.packages
        self.others += summary.others

        # Add state pair, if not already there
        for pair in summary.statepairs:
            if not pair.isUnset() and not pair in self.statepairs:
                self.statepairs.append(pair)

        self.calculatePercentages()

    def calculatePercentages(self):
        """ Keep counters correct """
        if self.projects > 0:
            self.successesPercentage = (float(self.successes)*100)/self.projects
            self.failuresPercentage = (float(self.failures)*100)/self.projects
            self.prereqsPercentage = (float(self.prereqs)*100)/self.projects
            self.noworksPercentage = (float(self.noworks)*100)/self.projects
            self.packagesPercentage = (float(self.packages)*100)/self.projects
            self.othersPercentage = (float(self.others)*100)/self.projects

            # This is the overall success of a run...
            self.overallPercentage = (float(self.successes + self.packages) \
                                        *100)/self.projects

    def getOverallPercentage(self):
        """ Return the overall success """
        return self.overallPercentage
