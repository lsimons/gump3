#!/usr/bin/python


# Copyright 2003-2004 The Apache Software Foundation
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

"""

	Generates paths for projects w/ dependencies

"""

from gump import log

import os.path

import gump.run.gumprun
import gump.process.command

import gump.model.depend

import gump.language.path

###############################################################################
# Classes
###############################################################################

class CSharpHelper(gump.run.gumprun.RunSpecific):
    
    def __init__(self,run):
        gump.run.gumprun.RunSpecific.__init__(self,run)
        
        # Caches for paths
        self.paths={}     
        
    def getAssemblyPath(self,project,debug=False):
        """
        Get boot and regular classpaths for a project.
        
        Return a path for this project
        """
        # Calculate path
        libpath = self.getAssemblyPathObject(project,debug)
        
        # Return them simple/flattened
        return libpath.getFlattened()

    def getAssemblyPathObject(self,project,debug=False):
        """
        Get a TOTAL path for a project (including its dependencies)
        
        A path object for a project
        """

        #
        # Do this once only... storing it on the context. Not as nice as 
        # doing it OO (each project context stores its own, but a step..)
        #
        if self.paths.has_key(project) :
          if debug: print "Path previously resolved..."
          return self.paths[project]
  
        # Start with the system classpath (later remove this)
        libpath=gump.language.path.AssemblyPath('Assembly Path')

        # Add this project's work directories
        workdir=project.getModule().getWorkingDirectory()          
        for work in project.getWorks():
            path=work.getResolvedPath()
            if path:
                libpath.addPathPart(gump.language.path.AnnotatedPath('',path,project,None,'Work Entity'))   
            else:
                log.error("<work element with neither 'nested' nor 'parent' attribute on " \
                        + project.getName() + " in " + project.getModule().getName()) 
              
        # Append dependent projects (including optional)
        visited=[]
  
        # Does it have any depends? Process all of them...
        for dependency in project.getDirectDependencies():
            subp = self._getDependOutputList(project,dependency,visited,1,debug)
            if subp:  libpath.importPath(subp)   
    
        # Store so we don't do this twice.
        self.paths[project] = libpath
        
        return libpath

    def _getDependOutputList(self,project,dependency,visited,depth=0,debug=0):      
        """
        
               Perform this 'dependency' (mandatory or optional)
               
            1) Bring in the JARs (or those specified by id in depend ids)
            2) Do NOT bring in the working entities (directories/libs)
            3) Bring in the sub-depends (or optional) if inherit='all' or 'hard'
            4) Bring in the runtime sub-depends if inherit='runtime'
            5) Also: *** Bring in any depenencies that the dependency inherits ***
            
           """            
   
        # Skip ones that aren't here to affect the classpath
        if dependency.isNoClasspath():  
            return None
            
        # Don't loop
        if (dependency in visited):
            # beneficiary.addInfo("Duplicated dependency [" + str(depend) + "]")          
            if debug:
                print str(depth) + ") Already Visited : " + str(dependency)
                print str(depth) + ") Previously Visits  : "
                for v in visited:
                    print str(depth) + ")  - " + str(v)
            return None
            
        visited.append(dependency)
        
        if debug:
            print str(depth) + ") Perform : " + `dependency`
                  
        # 
        libpath=gump.language.path.AssemblyPath('Assembly Path for ' + `dependency`)

        # Context for this dependecy project...
        project=dependency.getProject()
  
        # The dependency drivers...
        #
        # runtime (i.e. this is a runtime dependency)
        # inherit (i.e. inherit stuff from a dependency)
        #
        runtime=dependency.runtime
        inherit=dependency.inherit
        if dependency.ids:
            ids=dependency.ids.split()
        else:
            ids=None
  
        # Explain..
        dependStr=''
        if inherit: 
            if dependStr: dependStr += ', '
            dependStr += 'Inherit:'+dependency.getInheritenceDescription()
        if runtime: 
            if dependStr: dependStr += ', '
            dependStr += 'Runtime'
  
        # Append JARS for this project
        #    (respect ids --- none means 'all)
        ####################################################
        # Note, if they don't come from the project outputs
        # (e.g. 'cos the project failed) attempt to get them
        # from the repository. [This has been done already,
        # so is transparent here.]
        projectIds=[]
        for output in project.getOutputs():
            # Store for double checking
            if output.getId(): projectIds.append(output.getId())
            
            # If 'all' or in ids list:
            if (not ids) or (output.getId() in ids):   
                if ids: dependStr += ' Id = ' + output.getId()
                path=gump.language.path.AnnotatedPath(output.getId(),output.path,project,dependency.getOwnerProject(),dependStr) 
          
                # Add to CLASSPATH
                if debug:   print str(depth) + ') Append JAR : ' + str(path)
                libpath.addPathPart(path)

        # Double check IDs (to reduce stale ids in metadata)
        if ids:
            for id in ids:
                if not id in projectIds:
                    dependency.getOwnerProject().addWarning("Invalid ID [" + id \
                          + "] for dependency on [" + project.getName() + "]")

        # Append sub-projects outputs, if inherited
        for subdependency in project.getDirectDependencies():        
            #    If the dependency is set to 'all' (or 'hard') we inherit all dependencies
            # If the dependency is set to 'runtime' we inherit all runtime dependencies
            # If the dependent project inherited stuff, we inherit that...
            if        (inherit==gump.model.depend.INHERIT_ALL or inherit==gump.model.depend.INHERIT_HARD) \
                    or (inherit==gump.model.depend.INHERIT_RUNTIME and subdependency.isRuntime()) \
                    or (subdependency.inherit > gump.model.depend.INHERIT_NONE):      
                subp = self._getDependOutputList(project,subdependency,visited,depth+1,debug)                
                if subp:  libpath.importPath(subp)   
            elif debug:
                print str(depth) + ') Skip : ' + str(subdependency) + ' in ' + project.name

        return libpath
                  
        