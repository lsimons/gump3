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
from xml.dom import getDOMImplementation

from gump.util import getIndent
from gump.util.domutils import domAttributeIsTrue, getDomAttributeValue, \
    hasDomAttribute, hasDomChild, transferDomAttributes

from gump.core.model.depend import INHERIT_NONE, ProjectDependency
from gump.core.model.object import ModelObject
from gump.core.model.property import PropertyContainer

# represents a generic build (e.g. <ant/>) element
class Builder(ModelObject, PropertyContainer):
    """ A build command (within a project)"""
    def __init__(self, dom, project):
        ModelObject.__init__(self, dom, project)
        PropertyContainer.__init__(self)

        self.basedir = None

        # Store owning project
        self.project = project

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
                                       + '] in depend on: ' + pname )

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
            dependency = ProjectDependency(project,       \
                            workspace.getProject(projectName),  \
                            INHERIT_NONE,       \
                            runtime,
                            False,      \
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

        # Set this up...
        if self.hasDomAttribute('basedir'):
            self.basedir = os.path.abspath(os.path.join(
                    self.project.getModule().getWorkingDirectory() or dir.base,
                    self.getDomAttributeValue('basedir')
                    ))
        else:
            self.basedir = self.project.getBaseDirectory()

        # Check for debugging properties
        self.setDebug(self.domAttributeIsTrue('debug'))
        self.setVerbose(self.domAttributeIsTrue('verbose'))

        self.setComplete(True)

    def dump(self, indent = 0, output = sys.stdout):
        """ Display the contents of this object """
        i = getIndent(indent)
        output.write(i + self.__class__.__name__ + '\n')
        ModelObject.dump(self, indent + 1, output)
        # Dump all properties...
        PropertyContainer.dump(self, indent + 1, output)

    def getBaseDirectory(self):
        return self.basedir

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

    def dump(self, indent = 0, output = sys.stdout):
        """ Display the contents of this object """
        Builder.dump(self, indent, output)
        i = getIndent(indent+1)
        if self.hasTarget():
            output.write(i+'Target: ' + self.getTarget() + '\n')
        if self.hasBuildFile():
            output.write(i+'BuildFile: ' + self.getBuildFile() + '\n')

class Ant(BaseAnt): 
    """ An Ant command (within a project) """
    pass

# represents a <nant/> element
class NAnt(BaseAnt):
    """ A NAnt command (within a project) """
    pass

# represents an <maven/> element
class Maven(Builder):
    """ A Maven command (within a project)"""
    def __init__(self, dom, project):
        Builder.__init__(self, dom, project)

        # Import the goal
        self.goal = self.getDomAttributeValue('goal', 'jar')

    def getGoal(self):
        return self.goal

    def dump(self, indent = 0, output = sys.stdout):
        """ Display the contents of this object """
        Builder.dump(self, indent, output)
        i = getIndent(indent + 1)
        output.write(i + 'Goal: ' + self.getGoal() + '\n')

# represents an <mvn/> element
class Maven2(Builder):
    """ A Maven command (within a project)"""
    def __init__(self, dom, project):
        Builder.__init__(self, dom, project)

        # Import the goal
        self.goal = self.getDomAttributeValue('goal', 'package')

        self.local_repo = self.getDomAttributeValue('separateLocalRepository',
                                                    'False')

    def getGoal(self):
        return self.goal

    def dump(self, indent = 0, output = sys.stdout):
        """ Display the contents of this object """
        Builder.dump(self, indent, output)
        i = getIndent(indent + 1)
        output.write(i + 'Goal: ' + self.getGoal() + '\n')

    def needsSeparateLocalRepository(self):
        """ Whether a separate local repository will be used for this build """
        return self.local_repo and self.local_repo not in ['False', 'false']

    def getLocalRepositoryName(self):
        """ Name of the local repository if one has been given """
        if not self.needsSeparateLocalRepository() \
                or self.local_repo in ['True', 'true']:
            return None
        return self.local_repo


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

