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

        Generates Classpaths for projects w/ dependencies

"""

from gump import log

import os
import os.path

import gump.core.run.gumprun
import gump.util.process.command

import gump.core.model.depend

from gump.core.language.path import AnnotatedPath, Classpath
from gump.core.model.output import OUTPUT_BOOTCLASSPATH_JAR

###############################################################################
# Classes
###############################################################################

class JavaHelper(gump.core.run.gumprun.RunSpecific):

    def __init__(self, run):
        gump.core.run.gumprun.RunSpecific.__init__(self, run)

        # Caches for classpaths
        self.classpaths = {}
        self.bootclasspaths = {}

    def getJVMArgs(self, project):

        """ 

        Get JVM arguments for a project 

        """
        args = project.jvmargs
        if 'GUMP_JAVA_ARGS' in os.environ:
            args = gump.util.process.command.Parameters()
            for p in os.environ['GUMP_JAVA_ARGS'].split(' '):
                args.addParameter(p)
            for p in list(project.jvmargs.items()) :
                args.addParameterObject(p)
        return args

    def getClasspaths(self, project, debug = False):
        """
        Get boot and regular classpaths for a project.

        Return a (classpath, bootclaspath) tuple for this project
        """
        # Calculate classpath and bootclasspath
        (classpath, bootclasspath) = self.getClasspathObjects(project, debug)

        # Return them simple/flattened
        return ( classpath.getFlattened(), bootclasspath.getFlattened() )

    def getBaseClasspath(self):
        """

        The basic classpath needs to include a compiler...

        Return a system classpath (to include $JAVA_HOME/lib/tools.jar'
        for a compiler).
        """
        sysClasspath = Classpath('System Classpath')
        javaHome = self.run.getEnvironment().getJavaHome()
        syscp = os.path.join(os.path.join(javaHome, 'lib'), 'tools.jar')
        if os.path.exists(syscp):
            sysClasspath.importFlattenedParts(syscp)
        return sysClasspath

    def getClasspathObjects(self, project, debug = False):
        """
        Get a TOTAL classpath for a project (including its dependencies)

        A tuple of (CLASSPATH, BOOTCLASSPATH) for a project
        """

        #
        # Do this once only... storing it on the context. Not as nice as 
        # doing it OO (each project context stores its own, but a step..)
        #
        if project in self.classpaths and \
                project in self.bootclasspaths :
            if debug:
                print("Classpath/Bootclasspath previously resolved...")
            return (self.classpaths[project], self.bootclasspaths[project])

        # Start with the system classpath (later remove this)
        classpath = self.getBaseClasspath()
        bootclasspath = Classpath('Boot Classpath')

        # Add this project's work directories (these go into
        # CLASSPATH, never BOOTCLASSPATH)
        for work in project.getWorks():
            path = work.getResolvedPath()
            if path:
                classpath.addPathPart(AnnotatedPath('', path, project, None,
                                                    'Work Entity'))
            else:
                log.error("<work element with neither 'nested' nor 'parent'" \
                              + " attribute on " \
                              + project.getName() + " in " \
                              + project.getModule().getName()) 

        # Append dependent projects (including optional)
        visited = []

        # Does it have any depends? Process all of them...
        for dependency in project.getDirectDependencies():
            (subcp, subbcp) = self._getDependOutputList(project, dependency,
                                                        visited, 1, debug)
            _importClasspaths(classpath, bootclasspath, subcp, subbcp)

        # Store so we don't do this twice.
        self.classpaths[project] = classpath
        self.bootclasspaths[project] = bootclasspath

        return ( classpath, bootclasspath )

    def _getDependOutputList(self, project, dependency, visited, depth = 0,
                             debug = 0):
        """

               Perform this 'dependency' (mandatory or optional)

            1) Bring in the JARs (or those specified by id in depend ids)
            2) Do NOT bring in the working entities (directories/jars)
            3) Bring in the sub-depends (or optional) if inherit = 'all' or 'hard'
            4) Bring in the runtime sub-depends if inherit = 'runtime'
            5) Also: *** Bring in any depenencies that the dependency inherits ***

           """

        # Skip ones that aren't here to affect the classpath
        if dependency.isNoClasspath():
            return (None, None)

        # Don't loop
        if (dependency in visited):
            # beneficiary.addInfo("Duplicated dependency [" + str(depend) + "]")
            if debug:
                print(str(depth) + ") Already Visited : " + str(dependency))
                print(str(depth) + ") Previously Visits  : ")
                for v in visited:
                    print(str(depth) + ")  - " + str(v))
            return (None, None)

        visited.append(dependency)

        if debug:
            print(str(depth) + ") Perform : " + repr(dependency))

        # 
        classpath = Classpath('Classpath for ' + repr(dependency))
        bootclasspath = Classpath('Bootclasspath for ' + repr(dependency))

        # Context for this dependecy project...
        project = dependency.getProject()

        # The dependency drivers...
        #
        # runtime (i.e. this is a runtime dependency)
        # inherit (i.e. inherit stuff from a dependency)
        #
        runtime = dependency.runtime
        inherit = dependency.inherit
        if dependency.ids:
            ids = dependency.ids.split()
        else:
            ids = None

        # Explain..
        dependStr = ''
        if inherit: 
            if dependStr:
                dependStr += ', '
            dependStr += 'Inherit:' + dependency.getInheritenceDescription()
        if runtime: 
            if dependStr:
                dependStr += ', '
            dependStr += 'Runtime'

        # Append JARS for this project
        #    (respect ids --- none means 'all)
        ####################################################
        # Note, if they don't come from the project outputs
        # (e.g. 'cos the project failed) attempt to get them
        # from the repository. [This has been done already, 
        # so is transparent here.]
        projectIds = []
        for jar in [o for o in project.getOutputs() if o.is_jar()]:
            # Store for double checking
            if jar.getId():
                projectIds.append(jar.getId())

            # If 'all' or in ids list:
            if (not ids) or (jar.getId() in ids):
                if ids:
                    dependStr += ' Id = ' + jar.getId()
                path = AnnotatedPath(jar.getId(), jar.path, project,
                                     dependency.getOwnerProject(), dependStr) 

                # Add to CLASSPATH
                if not jar.getType() == OUTPUT_BOOTCLASSPATH_JAR:
                    if debug:
                        print(str(depth) + ') Append JAR : ' + str(path))
                    classpath.addPathPart(path)
                else:
                    # Add to BOOTCLASSPATH
                    if debug:
                        print(str(depth) + ') Append *BOOTCLASSPATH* JAR : ' \
                            + str(path))
                    bootclasspath.addPathPart(path)

        # Double check IDs (to reduce stale ids in metadata)
        if ids:
            for id in ids:
                if not id in projectIds:
                    dependency.getOwnerProject()\
                        .addWarning("Invalid ID [" + id \
                                        + "] for dependency on [" \
                                        + project.getName() + "]")

        # Append sub-projects outputs, if inherited
        for subdependency in project.getDirectDependencies():
            #
            #   For the main project we working on, we care about it's
            #   request for inheritence but we don't recursively
            #   inherit. (i.e. we only do this at recursion depth 1).
            #

            #   If the dependency is set to 'all' (or 'hard') we
            #   inherit all dependencies.
            #   If the dependency is set to 'runtime' we inherit all
            #   runtime dependencies.
            #
            #   INHERIT_OUTPUTS (aka INHERIT_JARS) is more sticky, and
            #   we track that down (and down, ...).
            #
            if (
                ( ( 1 == depth ) and \
                       (inherit in [ gump.core.model.depend.INHERIT_ALL,
                                     gump.core.model.depend.INHERIT_HARD ]) \
                       or \
                       (inherit == gump.core.model.depend.INHERIT_RUNTIME \
                            and subdependency.isRuntime())
                  ) \
                    or \
                    (inherit in [ gump.core.model.depend.INHERIT_OUTPUTS ])
                ) :
                (subcp, subbcp) = self._getDependOutputList(project,
                                                            subdependency,
                                                            visited, depth + 1,
                                                            debug)
                _importClasspaths(classpath, bootclasspath, subcp, subbcp)
            elif debug:
                print(str(depth) + ') Skip : ' + str(subdependency) \
                    + ' in ' + project.name)

        return (classpath, bootclasspath)

def _importClasspaths(classpath, bootclasspath, cp, bcp):
    """
    Import cp and bcp into classpath and bootclasspath, 
    but do not accept duplicates. Report duplicates.
    """
    if cp:
        classpath.importPath(cp)
    if bcp:
        bootclasspath.importPath(bcp)

