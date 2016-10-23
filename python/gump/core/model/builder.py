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

    This module contains information on builders (ant/maven/script)

"""

import os
import sys
import xml.dom.minidom
from xml.dom import getDOMImplementation

from gump.util import getIndent
from gump.util.domutils import domAttributeIsTrue, getDomAttributeValue, \
    getDomChild, getDomTextValue, hasDomAttribute, hasDomChild, \
    transferDomAttributes

from gump.core.model.depend import INHERIT_NONE, ProjectDependency
from gump.core.model.object import ModelObject
from gump.core.model.property import Property, PropertyContainer

# represents a generic build (e.g. <ant/>) element
class Builder(ModelObject, PropertyContainer):
    """ A build command (within a project)"""
    def __init__(self, dom, project):
        ModelObject.__init__(self, dom, project)
        PropertyContainer.__init__(self)

        self.basedir = None

        # Store owning project
        self.project = project

        # Import the timeout
        self.timeout = self.getDomAttributeValue('timeout')
        if self.timeout is not None:
            self.timeout = float(self.timeout)

    def __str__(self):
        """
        Display what project this is on, if possible.
        """
        if not self.project:
            return self.__class__.__name__
        else:
            return self.__class__.__name__ + ' on ' + `self.project`

    #
    # expand properties - in other words, do everything to complete the
    # entry that does NOT require referencing another project
    #
    def expand(self, project, workspace):
        self.expandDomDependencies(project, workspace)
        self.expandDomProperties(project, workspace)

    def expandDomDependencies(self, project, workspace):
        """
            Convert all depend elements into property elements, and
            move the dependency onto the project
        """
        impl = getDOMImplementation()

        for ddom in self.getDomChildIterator('depend'):

            pdom = impl.createDocument(None, 'property', None)
            pelement = pdom.documentElement

            # Transfer depend attributes over as a basis for
            # the property
            transferDomAttributes(ddom, pelement)

            # Fix the reference to a outputpath
            pelement.setAttribute('reference', 'outputpath')

            # Name the xmlproperty...
            if hasDomAttribute(ddom, 'property'):
                pelement.setAttribute('name',
                                      getDomAttributeValue(ddom, 'property'))
            elif not hasDomAttribute(pelement, 'name'):
                pname = getDomAttributeValue(ddom, 'project')
                pelement.setAttribute('name', pname)
                project.addWarning('Unnamed property for [' + project.name \
                                       + '] in depend on: ' + pname)

            # :TODO: AJ added this, no idea if it is right/needed.
            if hasDomAttribute(ddom, 'id'):
                pelement.setAttribute('ids', getDomAttributeValue(ddom, 'id'))

            # <depend wants the classpath, unless <noclasspath/> stated
            # as a child element or attribute.
            if not hasDomChild(ddom, 'noclasspath') \
                    and not hasDomAttribute(ddom, 'noclasspath'):
                pelement.setAttribute('classpath', 'add')

            # Store it
            self.expandDomProperty(pelement, project, workspace)
            self.importProperty(pelement)

            # Stash the constructed property DOM (the doc above the element)
            if not hasattr(project, 'extraDoms'):
                project.extraDoms = []
            project.extraDoms.append(pdom)

    def expandDomProperties(self, project, workspace):
        #
        # convert Ant property elements which reference a project
        # into dependencies
        #
        for pdom in self.getDomChildIterator('property'):
            self.expandDomProperty(pdom, project, workspace)
            self.importProperty(pdom)

        #
        # convert Ant sysproperty elements which reference a project
        # into dependencies
        #
        for spdom in self.getDomChildIterator('sysproperty'):
            self.expandDomProperty(spdom, project, workspace)
            self.importSysProperty(spdom)

    #
    # Expands
    #
    def expandDomProperty(self, pdom, project, workspace):

        # :TODO: Cleanup this Workaround
        name = getDomAttributeValue(pdom, 'name',
                                    getDomAttributeValue(pdom, 'project'))

        # Check if the pdom comes from another project
        if not hasDomAttribute(pdom, 'project'):
            return
        projectName = getDomAttributeValue(pdom, 'project')
        # If that project is the one we have in hand
        if projectName == project.getName():
            return

        # If the pdom is not as simple as srcdir
        reference = getDomAttributeValue(pdom, 'reference')
        if reference == 'srcdir':
            return

        # If it isn't already a classpath dependency
        if project.hasFullDependencyOnNamedProject(projectName):
            self.addDebug('Dependency on ' + projectName + \
                    ' exists, no need to add for property ' + \
                        name + '.')
            return

        # If there are IDs specified
        ids = getDomAttributeValue(pdom, 'id', '')

        # Runtime?
        runtime = domAttributeIsTrue(pdom, 'runtime')

        if workspace.hasProject(projectName):

            # A Property
            noclasspath = not hasDomAttribute(pdom, 'classpath')

            # Add a dependency (to bring property)
            dependency = ProjectDependency(project,
                                           workspace.getProject(projectName),
                                           INHERIT_NONE,
                                           runtime,
                                           False,
                                           ids,
                                           noclasspath,
                                           'Property Dependency for ' + name)


            # Add depend to project...
            # :TODO: Convert to ModelObject
            project.addDependency(dependency)
        else:
            project.addError('No such project [' + projectName \
                                 + '] for property.')

    def complete(self, _project, workspace):
        """
        Complete the model from XML
        """
        if self.isComplete():
            return

        # Import the properties..
        PropertyContainer.importProperties(self, self.dom)

        # Complete them all
        self.completeProperties(workspace)

        if self.hasDomAttribute('basedir'):
            self.basedir = os.path.abspath(os.path.join(
                self.project.getModule().getWorkingDirectory()
                or dir.base,
                self.getDomAttributeValue('basedir')
            ))
        else:
            self.basedir = self.project.getBaseDirectory()

        # Check for debugging properties
        self.setDebug(self.domAttributeIsTrue('debug'))
        self.setVerbose(self.domAttributeIsTrue('verbose'))

        self.setComplete(True)

    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        i = getIndent(indent)
        output.write(i + self.__class__.__name__ + '\n')
        ModelObject.dump(self, indent + 1, output)
        # Dump all properties...
        PropertyContainer.dump(self, indent + 1, output)

    def getBaseDirectory(self):
        return self.basedir

    def hasTimeout(self):
        if self.timeout:
            return True
        return False

    def getTimeout(self):
        return self.timeout

# represents an <ant/> element
class BaseAnt(Builder):
    """ An Ant command (within a project)"""
    def __init__(self, dom, project):
        Builder.__init__(self, dom, project)

        # Import the target
        self.target = self.getDomAttributeValue('target')
        # Import the buildfile
        self.buildfile = self.getDomAttributeValue('buildfile')

    def hasTarget(self):
        if self.target:
            return True
        return False

    def getTarget(self):
        return self.target

    def hasBuildFile(self):
        if self.buildfile:
            return True
        return False

    def getBuildFile(self):
        return self.buildfile

    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        Builder.dump(self, indent, output)
        i = getIndent(indent+1)
        if self.hasTarget():
            output.write(i+'Target: ' + self.getTarget() + '\n')
        if self.hasBuildFile():
            output.write(i+'BuildFile: ' + self.getBuildFile() + '\n')
        if self.timeout():
            output.write(i+'Timeout: ' + self.getTimeout() + '\n')

class Ant(BaseAnt):
    """ An Ant command (within a project) """
    pass

# represents a <nant/> element
class NAnt(BaseAnt):
    """ A NAnt command (within a project) """
    pass

# represents a <msbuild/> element
class MSBuild(BaseAnt):
    """ A MSBuild command (within a project) """
    pass

# represents an <maven/> element
class Maven1(Builder):
    """ A Maven 1.x command (within a project)"""
    def __init__(self, dom, project):
        Builder.__init__(self, dom, project)

        # Import the goal
        self.goal = self.getDomAttributeValue('goal', 'jar')

    def getGoal(self):
        return self.goal

    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        Builder.dump(self, indent, output)
        i = getIndent(indent + 1)
        output.write(i + 'Goal: ' + self.getGoal() + '\n')

MVN_VERSION2 = '2'
MVN_VERSION3 = '3'

# represents an <mvn/> element
class Maven(Builder):

    """ A Maven 2.x/3.x command (within a project)"""

    def __init__(self, dom, project, version=MVN_VERSION2):
        Builder.__init__(self, dom, project)

        self.goal = self.getDomAttributeValue('goal', 'package')

        self.local_repo = self.getDomAttributeValue('separateLocalRepository',
                                                    'False')
        self.profile = self.getDomAttributeValue('profile')
        self.version = version

    def getGoal(self):
        """ The goal to execute """
        return self.goal

    def getProfile(self):
        """ The profile to use, may be None """
        return self.profile

    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        Builder.dump(self, indent, output)
        i = getIndent(indent + 1)
        output.write(i + 'Goal: ' + self.getGoal() + '\n')
        if self.profile:
            output.write(i + 'Profile: ' + self.getProfile() + '\n')
        else:
            output.write(i + 'using default profile.\n')

    def needsSeparateLocalRepository(self):
        """ Whether a separate local repository will be used for this build """
        return self.local_repo and self.local_repo not in ['False', 'false']

    def getLocalRepositoryName(self):
        """ Name of the local repository if one has been given """
        if not self.needsSeparateLocalRepository() \
                or self.local_repo in ['True', 'true']:
            return None
        return self.local_repo

    def getVersion(self):
        """ The configured version of Maven to use """
        return self.version

class MvnInstall(Maven):
    """ Installs a single file into the local mvn repository """

    ARTIFACT_ID = 'artifactId'
    FILE = 'file'
    GOAL = 'install:install-file'
    PACKAGING = 'packaging'
    PARENT = 'parent'
    POM = 'pom'
    VERSION = 'version'
    GROUP_ID = 'groupId'

    def __init__(self, dom, project, version=MVN_VERSION2):
        Maven.__init__(self, dom, project, version)
        self.goal = MvnInstall.GOAL
        self.packaging = self.getDomAttributeValue(MvnInstall.PACKAGING,
                                                   MvnInstall.POM)
        self.file = self.getDomAttributeValue(MvnInstall.FILE, 'pom.xml')
        self.artifactVersion = self.getDomAttributeValue(MvnInstall.VERSION)
        self.artifactId = self.getDomAttributeValue(MvnInstall.ARTIFACT_ID)
        self.groupId = self.getDomAttributeValue(MvnInstall.GROUP_ID)

    def expand(self, project, workspace):
        """ Turns the builder's attributes into properties """
        Builder.expand(self, project, workspace)

        impl = getDOMImplementation()
        self._add_property(impl, MvnInstall.ARTIFACT_ID,
                           self.artifactId or project.getName())
        self._add_property(impl, MvnInstall.GROUP_ID,
                           self.groupId or project.getArtifactGroup())
        self._add_property(impl, MvnInstall.PACKAGING, self.packaging)
        self._add_property(impl, MvnInstall.FILE, self.file)
        if self.artifactVersion:
            self._add_property(impl, MvnInstall.VERSION, self.artifactVersion)
        elif self.packaging != MvnInstall.POM:
            project.addError("version attribute is mandatory if the file is"
                             + " not a POM.")

    def getProperties(self):
        """
        Get a list of all the property objects - potentially parse POM
        for version
        """
        props = PropertyContainer.getProperties(self)[:]

        if not self.artifactVersion and self.packaging == MvnInstall.POM:
            try:
                pomDoc = self._read_pom()
                root = pomDoc.documentElement
                if root.tagName != 'project':
                    self.project.addError('file is not a POM, its root element'
                                          + ' is ' + root.tagName)
                    return

                version = _extract_version_from_pom(root)

                if not version:
                    self.project.addError("POM doesn't specify a version,"
                                          + " you must provide the version"
                                          + " attribute.")
                    return

                version_text = getDomTextValue(version)
                if '${' in version_text:
                    self.project.addError('POM uses a property reference as'
                                          + ' version which is not supported'
                                          + ' by Gump.  You must provide an'
                                          + ' explicit version attribute to'
                                          + ' mvninstall.')
                else:
                    impl = getDOMImplementation()
                    dom = _create_dom_property(impl, MvnInstall.VERSION,
                                               version_text)
                    prop = Property(MvnInstall.VERSION, dom, self.project)
                    prop.complete(self.project, self.project.getWorkspace())
                    props.append(prop)
            except Exception, details:
                self.project.addError('failed to parse POM because of '
                                      + str(details))
        return props

    def _add_property(self, impl, name, value):
        """ Adds a named property """
        self.importProperty(_create_dom_property(impl, name, value))

    def _read_pom(self):
        """ locates the POM, parses it and returns it as DOM Document """
        pom = os.path.join(self.getBaseDirectory(), self.file)
        return xml.dom.minidom.parse(pom)

def _create_dom_property(impl, name, value):
    """ creates and returns a DOM element for a named property """
    doc = impl.createDocument(None, 'property', None)
    prop = doc.documentElement
    prop.setAttribute('name', name)
    prop.setAttribute('value', value)
    return prop

def _extract_version_from_pom(root):
    """ Tries to extract the version DOM element from a POM DOM tree """
    version = None
    if hasDomChild(root, MvnInstall.VERSION):
        version = getDomChild(root, MvnInstall.VERSION)
    elif hasDomChild(root, MvnInstall.PARENT):
        parent = getDomChild(root, MvnInstall.PARENT)
        if hasDomChild(parent, MvnInstall.VERSION):
            version = getDomChild(parent, MvnInstall.VERSION)
    return version

# represents an <configure/> element
class Configure(Builder):
    """ A configure command (within a project)"""

    def __init__(self, dom, project):
        Builder.__init__(self, dom, project)

    def expandDomProperties(self, project, workspace):
        #
        # convert Ant property elements which reference a project
        # into dependencies
        #
        for pdom in self.getDomChildIterator('arg'):
            self.expandDomProperty(pdom, project, workspace)
            self.importProperty(pdom)

# represents a <make/> element
# will probably need to extend Builder directly later
class Make(Configure):
    """ A make command (within a project) """

    def __init__(self, dom, project):
        Configure.__init__(self, dom, project)
        # Import the target
        self.target = self.getDomAttributeValue('target')
        # Import the makefile
        self.makefile = self.getDomAttributeValue('makefile')

    def hasTarget(self):
        if self.target:
            return True
        return False

    def getTarget(self):
        return self.target

    def hasMakeFile(self):
        if self.makefile:
            return True
        return False

    def getMakeFile(self):
        return self.makefile

# represents an <script/> element
class Script(Configure):
    """ A script command (within a project)"""
    def __init__(self, dom, project):
        Configure.__init__(self, dom, project)

        # Get the name
        self.name = self.getDomAttributeValue('name', 'unset')

    def getName(self):
        return self.name

# represents an <gradle/> element
class Gradle(Builder):

    """ A gradle command (within a project)"""

    def __init__(self, dom, project):
        Builder.__init__(self, dom, project)

        self.task = self.getDomAttributeValue('task', 'build')

        self.local_repo = self.getDomAttributeValue('separateLocalRepository',
                                                    'False')

    def getTask(self):
        """ The task to execute """
        return self.task

    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        Builder.dump(self, indent, output)
        i = getIndent(indent + 1)
        output.write(i + 'Task: ' + self.getTask() + '\n')

    def needsSeparateLocalRepository(self):
        """ Whether a separate local repository will be used for this build """
        return self.local_repo and self.local_repo not in ['False', 'false']

    def getLocalRepositoryName(self):
        """ Name of the local repository if one has been given """
        if not self.needsSeparateLocalRepository() \
                or self.local_repo in ['True', 'true']:
            return None
        return self.local_repo

# represents an <nuget/> element
class NuGet(Builder):
    """ A NuGet command (within a project)"""
    def __init__(self, dom, project):
        Builder.__init__(self, dom, project)

        # Import the command
        self.command = self.getDomAttributeValue('command', 'restore')
        self.solution = self.getDomAttributeValue('solution')

    def hasCommand(self):
        if self.command:
            return True
        return False

    def getCommand(self):
        return self.command

    def hasSolution(self):
        if self.solution:
            return True
        return False

    def getSolution(self):
        return self.solution

    def expandDomProperties(self, project, workspace):
        for pdom in self.getDomChildIterator('arg'):
            self.expandDomProperty(pdom, project, workspace)
            self.importProperty(pdom)

    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        Builder.dump(self, indent, output)
        i = getIndent(indent+1)
        if self.hasCommand():
            output.write(i+'Command: ' + self.getCommand() + '\n')
        if self.hasSolution():
            output.write(i+'Solution: ' + self.getSolution() + '\n')

