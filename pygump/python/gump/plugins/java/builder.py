#!/usr/bin/env python

# Copyright 2004-2005 The Apache Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import os
import sys
from os.path import abspath, join, isfile

from gump.model import Script, Error, Project, Ant, Dependency, Homedir, Jar
from gump.model.util import get_project_directory
from gump.plugins import AbstractPlugin
from gump.plugins.builder import BuilderPlugin
from gump.util.executor import Popen, PIPE, STDOUT



class ArtifactPath(object):
    """Represents an artifact within a path"""
    def __init__(self,id,path,description=None):
        self.id=id
        self.path = path
        self.description=description
        
    def __eq__(self,other):
        return (self.path == other.path)
    
    def __str__(self):
        return self.path
        
class Classpath(object):
    """Represents a list of artifacts

    Has the following properties:
        
        - id -- identifier
        - parts -- an array of ArtifactPath objects
        - state -- state of Artifacts:
                    unknown
                    complete
                    stale (some from repository)
                    incomplete (some missing)"""
    def __init__(self, id):
        self.id = id
        self.parts = []
        self.state='unknown'
    
    def __nonzero__(self) :
        if self.parts: return True
        return False
    
    def __len__(self):
        return len(self.parts)
    
    def __add__(self,other):
        if not isinstance(other,ArtifactPath):
             other=ArtifactPath("Unknown",other,"Unspecified")
        if not other in self.parts:
            self.parts.append(other)
        return self
    
    def __str__(self):
        return self.join(os.pathsep)
    
    def join(self,sep):
        import string
        return string.join([ part.path for part in self.parts ], sep)
    
class ClasspathPlugin(BuilderPlugin):
    """Generate build attributes (e.g. CLASSAPATH) for a builder."""
    def __init__(self, workdir, log):
        BuilderPlugin.__init__(self, workdir, log, Ant, self._forge_classpaths)
        
    def _forge_classpaths(self, project, ant):               

        # Stub them out...
        ant.classpath=Classpath('Standard')
        ant.boot_classpath=Classpath('Boot')
        
        # Flesh them out...
        self._calculateClasspaths(project,ant)

    def _calculateClasspaths(self, project, ant):
        """Generate the classpath lists"""
        #TODO This ought be under "java" not under "Ant".        
        
        #TODO Need "<work> elements
        
        # Recurse into dependencies
        visited=[]
        for dependency in project.dependencies:
            self._calculateDependencyContributions(ant,dependency,1,visited)
            
    def _calculateDependencyContributions(self,ant,dependency,depth,visited):        
        assert isinstance(dependency, Dependency)
        
        #TODO Check NO_CLASSPATH if dependency.dependencyInfo
        if dependency in visited: return

        # Access the players
        project=dependency.dependency
        projectpath = get_project_directory(self.workdir,project)
        
        #TODO Do we need a filter here? Are all dependency infos
        # appropriate, or not?
        for info in [info for info in dependency.dependencyInfo]:           
                    
            # The dependency drivers...
            #
            # runtime (i.e. this is a runtime dependency)
            # inherit (i.e. inherit stuff from a dependency)
            # ids (i.e. what output ids to select)
            #
            runtime=info.runtime
            inherit=info.inherit
            ids=info.specific_output_ids
      
            # Explain..
            depend_str=''
            if inherit: 
                if depend_str: depend_str += ', '
                depend_str += 'Inherit:'+dependency.inherit
            if runtime: 
                if depend_str: depend_str += ', '
                depend_str += 'Runtime'
            
            # Append Outputs for this project
            #    (respect ids --- none means 'all)
            project_ids=[]
            for output in project.outputs:
                # Store for double checking
                if output.id: project_ids.append(output.id)
                
                # If 'all' or in ids list:
                if (not ids) or (output.id in ids):   
                    if ids: depend_str += ' ID = ' + output.id
                    
                    if isinstance(output,Homedir):
                        path = os.path.join(projectpath,output.directory)
                    elif isinstance(output,Jar):
                        path = os.path.join(projectpath,output.name)
                    else:
                        raise Error, "Unknown Output Type for %s: %s" % (self.__class__.__name__, output.__class__.__name__)

                    self.log.debug('Contribution : %s' % path)
                    artifact_path=ArtifactPath(output.id,path,depend_str) 
              
                    # Add to CLASSPATH (or BOOTCLASSPATH)
                    if not isinstance(output,Jar) or not output.add_to_bootclass_path:
                        ant.classpath += artifact_path
                    else:
                        ant.boot_classpath += artifact_path

        # Double check IDs (to reduce stale IDs in metadata)
        if ids:
            for id in ids:
                if not id in project_ids:
                    self.log.warn("Invalid ID [" + id + "] for dependency on [" + project.name + "]")

        visited.append(dependency)  
        
        # Append sub-projects outputs, if inherited
        for subdependency in project.dependencies:        
            #
            # 	For the main project we working on, we care about it's request for inheritence
            #	but we don't recursively inherit. (i.e. we only do this at recursion depth 1).
            #
            #   If the dependency is set to 'all' (or 'hard') we inherit all dependencies.
            # 	If the dependency is set to 'runtime' we inherit all runtime dependencies.
            #
            #	INHERIT_OUTPUTS (aka INHERIT_JARS) is more sticky, and we track that down (and down, ...).
            #
            for subinfo in subdependency.dependencyInfo:
                if   (  ( ( 1 == depth ) and \
                        (inherit in [ 'all', 'hard' ]) \
                    or \
                          (inherit == 'runtime' and subdependency.isRuntime()) ) \
                    or \
                        ( inherit in [ 'outputs' ] ) ) :      
                    self._calculateDependencyContributions(ant,subdependency,depth+1,visited)
                    
        
class ArtifactPlugin(BuilderPlugin):
    """Resolve all entries in the CLASSPATH|BOOT_CLASSPATH checking for existence. 
    When absent see if recent copies can be acquired from a repository."""
    def __init__(self,workdir, log):
        BuilderPlugin.__init__(self, workdir, log, Ant, self._resolve_classpaths)
        
    def _resolve_classpaths(self, project, ant):           
        
        projectpath = get_project_directory(self.workdir,project)
        
        self._resolve_classpath(ant.classpath)
        self._resolve_classpath(ant.boot_classpath)
        
    def _resolve_classpath(classpath):        
        for artifact_path in ant.classpath:
            if not os.path.exists(artifact_path.path):
                #TODO Go find from Repository...
                classpath.state='incomplete'
        
class AntPlugin(BuilderPlugin):
    """Execute all "ant" commands for all projects."""
    def __init__(self, workdir, log, debug=False):
        BuilderPlugin.__init__(self, workdir, log, Ant, self._do_ant)
        self.debug = debug

        # Clone the environment, so we can squirt CLASSPATH into it.
        self.tmp_env = dict(os.environ)
        
    def _do_ant(self, project, ant):                
        projectpath = get_project_directory(self.workdir,project)
        
        # TODO get proper classpath
        self.log.debug('CLASSPATH %s' % ant.classpath)
        self.log.debug('BOOTCLASSPATH %s' % ant.boot_classpath)
        
        # Create an Environment
        self.tmp_env['CLASSPATH'] = str(ant.classpath)
        
        # TODO test this
        # TODO sysclasspath only
        # TODO more options
        
        # Build the command line.
        args = ["java"]
        
        # Allow bootclasspath
        if ant.boot_classpath:
            args += ['-X','bootclasspath/p',ant.boot_classpath.join(':')]

        # Ant's entry point, and main options.
        args += ["org.apache.tools.ant.Main"]
                 
        # Specify a build file.
        if ant.buildfile: args += ["-buildfile",ant.buildfile]

        # Override the default target
        if ant.target: args += [ant.target]
        
        # Allow debugging
        if self.debug: args += ["-debug"]
        
        self.log.debug("Command : %s " % (args))
        self.log.debug("        : %s " % ant.classpath)
        #self.log.debug("        : %s " % self.tmp_env)
        cmd = Popen(args,shell=False,cwd=projectpath,stdout=PIPE,stderr=STDOUT,env=self.tmp_env)

        ant.build_log = cmd.communicate()[0]
        ant.build_exit_status = cmd.wait()
