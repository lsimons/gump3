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

"""This module defines an object-oriented representation of gump metadata."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

class Error(Exception):
    """Generic error thrown for all internal model module exceptions."""
    pass


class ModelObject:
    """Base object for all gump model elements."""
    pass


class Workspace(ModelObject):
    """Model gump workspace and profile.

    Has the following properties:
        
        - name     -- per-host unique identifier
        - repositories -- dictionary of contained repositories
        - modules -- dictionary of contained modules
        - projects -- dictionary of contained projects
        - dependencies -- list of all dependencies between projects
    """
    def __init__(self, name):
        self.name = name
        self.repositories = {}
        self.modules = {}
        self.projects = {}
        self.dependencies = []
    
    def add_repository(self, repository):
        self.repositories[repository.name] = repository

class Repository(ModelObject):
    """Model a source control repository.

    Has the following properties:
        
        - workspace -- reference to the containing workspace
        - name      -- per-run unique identifier
        - title     -- human-readable identifier
        - home_page -- web address of associated project or organisation
        - cvsweb    -- web address for online viewing of this repository
        - redistributable -- flag indicating whether this project can be
                       redistributed under AL-compatible terms
        - modules   -- dictionary of contained modules
    """
    def __init__(self,
                 workspace,
                 name,
                 title = None,
                 home_page = None,
                 cvsweb = None,
                 redistributable = False):
        self.workspace       = workspace
        self.name            = name
        self.title           = title
        self.home_page       = home_page
        self.cvsweb          = cvsweb
        self.redistributable = redistributable

        self.modules={}

    def add_module(self, module):
        self.modules[module.name] = module
    

CVS_METHOD_PSERVER="pserver"

class CvsRepository(Repository):
    """Model a CVS repository.

    Has the following properties:
        
        - all of the properties a Repository has
        - hostname -- the address of the cvs server
        TODO: - port
        - path     -- the path to the cvs repository on the server
        - method   -- the cvs connection method to use
        - user     -- the cvs user to login as
        - password -- the cvs password to login with
    """
    def __init__(self,
                 workspace,
                 name,
                 hostname,
                 path,
                 title = None,
                 home_page = None,
                 cvsweb = None,
                 redistributable = False,
                 method = CVS_METHOD_PSERVER,
                 user = None,
                 password = None):
        Repository.__init__(self, workspace, name, title, home_page, cvsweb, redistributable)
        self.hostname = hostname
        self.path     = path,
        self.method   = method,
        self.user     = user,
        self.password = password
    
    def to_url(self):
        url = method + ':'
        if user:
            url += user + '@'
        url += hostname + ':' + path
        
        return url
            

class SvnRepository(Repository):
    """Model a subversion repository.

    Has the following properties:
        
        - all of the properties a Repository has
        - url      -- the address of the svn repository
        TODO: - user     -- the cvs user to login as
        TODO: - password -- the cvs password to login with
    """
    def __init__(self,
                 workspace,
                 name,
                 url,
                 title = None,
                 home_page = None,
                 cvsweb = None,
                 redistributable = False,
                 user = None,
                 password = None):
        Repository.__init__(self, workspace, name, title, home_page, cvsweb, redistributable)
        self.url      = url
        self.user     = user,
        self.password = password

#TODO: class PerforceRepository

class Module(ModelObject):
    """Model a module within a source control repository.

    Has the following properties:
        
        - repository  -- the containing repository
        - name        -- per-run unique identifier
        - url         -- web address of associated project
        - description -- human-readable description
    
    TODO: doesn't fully support the current GOM mess. Figure out what to do.
    """
    def __init__(self,
                 repository,
                 name,
                 url = None,
                 description = None):
        self.repository  = repository
        self.name        = name
        self.url         = url
        self.description = description
        
        self.projects = {}

    def add_project(self, project):
        self.projects[project.name] = project

class CvsModule(Module):
    """Model a module within a cvs repository.
    
    TODO: doesn't fully support the current mess that the GOM spec
          supports. Figure out what to do.
    """
    def __init__(self,
                 repository,
                 name,
                 tag = None,
                 url = None,
                 description = None):
        Module.__init__(self, repository, name, url, description)
        self.tag = tag

class SvnModule(Module):
    """Model a module within a svn repository.
    
    Since subversion doesn't have modules, this element in some ways seems
    rather silly. What we do is represent an actually seperate subversion
    repository with a single Repository element, and then we use the
    "path" property to refer to locations within that repository.
    
    TODO: current GOM spec uses absolute URL instead of path. Figure out what
          to do.
    """
    def __init__(self,
                 repository,
                 name,
                 path, # path within the repository to this module
                 url = None,
                 description = None):
        Module.__init__(self, repository, name, url, description)
        self.directory = directory

#TODO: class PerforceModule

class Project(ModelObject):
    """Model a "project".

    As far as gump is concerned a project is the primary "unit of work",
    something to "build". Projects reside within modules.

    Has the following properties:
        
        - module       -- the containing module
        - name         -- per-run unique identifier
        - dependencies -- list of Dependency instances describing what other
                          projects this project depends upon
        - dependees    -- list of Dependency instances describing what other
                          projects depend on this project
        - commands     -- ordered list of Commands instances that need to be
                          executed to build this project
        - outputs      -- list of Output instances describing what results a
                          build of this project results in
    """
    def __init__(self, module, name):
        self.module = module
        self.name   = name
        
        self.dependencies=[]
        self.dependees=[]
        self.commands=[]
        self.outputs=[]
    
    def add_dependency(self, dependency):
        self.module.repository.workspace.dependencies.append(dependency)
        self.dependencies.append(dependency)
        if type(dependency.dependency) == type(self): # might be a string for a bad
                                                      # dependency
            dependency.dependency.add_dependee(dependency)
    
    def add_dependee(self, dependee):
        self.dependees.append(dependee)
    
    def add_command(self, command):
        self.commands.append(command)
    
    def add_output(self, output):
        self.outputs.append(output)

DEPENDENCY_INHERIT_NONE          = "none"
DEPENDENCY_INHERIT_RUNTIME       = "runtime"
DEPENDENCY_INHERIT_ALL           = "all"
DEPENDENCY_INHERIT_HARD          = "hard"

# "copy-outputs" inheritance means that all the outputs of the dependee should
# be made into outputs of the dependency. For java projects this is known as
# "jars" inheritance.
DEPENDENCY_INHERIT_COPY_OUTPUTS  = "copy-outputs"
DEPENDENCY_INHERIT_JARS          = DEPENDENCY_INHERIT_COPY_OUTPUTS

class Dependency(ModelObject):
    """Model a dependency.
    
    A dependency is a directional link between two projects, where one
    project (the dependency) depends on another project (the dependee).
    
    Has the following properties:
        
        - dependency -- the project that is being depended on by the
                        other project, or the name of that project if
                        it doesn't actually exist (ie that's an error
                        condition).
        - dependee -- the project that is depending on the other project
        - optional   -- flag indicating whether the dependee can be built and
                        used if this dependency cannot be satisfied
        - runtime    -- flag indicating whether the dependee needs this
                        dependency at runtime or just for building
    """
    def __init__(self,
                 dependency,
                 dependee,
                 optional = False,
                 runtime  = False,
                 inherit  = DEPENDENCY_INHERIT_NONE,
                 specific_output_id = None):
        self.dependency         = dependency
        self.dependee           = dependee
        self.optional           = optional
        self.runtime            = runtime
        self.inherit            = inherit
        self.specific_output_id = specific_output_id

class Command(ModelObject):
    """Model a command.
    
    A command is something to do as part of a build.

    Has the following properties:
        
        - project -- the containing project
    """
    def __init__(self, project):
        self.project = project
    pass

class Mkdir(Command):
    """Model a mkdir command.
    
    Command to create a directory. The directory is specified relative to the
    source directory of the project.

    Has the following properties:
        
        - all the properties a Command has
        - directory -- the directory to create
    """
    def __init__(self, project, directory):
        Command.__init__(self, project)
        self.directory = directory

class Rmdir(Command):
    """Model a delete command.
    
    Command to delete a directory. The directory is specified relative to the
    source directory of the project.

    Has the following properties:
        
        - all the properties a Command has
        - directory -- the directory to delete
    """
    def __init__(self, project, directory):
        Command.__init__(self, project)
        self.directory = directory

class Script(Command):
    """Command to run a script.

    Has the following properties:
        
        - all the properties a Command has
        - name -- the name of the script to run
        - args -- a list of arguments to the command,
                  where each element is a (name, value)
                  tuple
    """
    def __init__(self, project, name, args=[]):
        Command.__init__(self, project)
        self.name = name
        self.args = args

#TODO: more Commands

OUTPUT_ID_HOME = "homedir"

class Output(ModelObject):
    """Model an output, something a successful project build will yield.

    Outputs can be given an id to be able to distinguish multiple outputs from
    another.

    Has the following properties:
        
        - project -- the containing project
        - id      -- a per-project unique identifier
    """
    def __init__(self, project, id = None):
        self.project = project
        self.id      = id

class Homedir(Output):
    """Model a directory containing stuff that can be used by other projects.

    Has the following properties:

        - all the properties an Output has
        - directory -- the directory that should be exported as this project
                       its homedirectory
    """
    def __init__(self, project, directory):
        Output.__init__(self, project, OUTPUT_ID_HOME)
        self.directory = directory

class Jar(Output):
    """Model a java archive that can be used by other projects.

    Has the following properties:

        - all the properties an Output has
        - name -- the path to the jar relative to the project is home
                directory.
        - add_to_bootclass_path -- flag specifying if this jar should be
                added 
    """
    def __init__(self, project, name, id = None, add_to_bootclass_path = False ):
        Output.__init__(self, project, id)
        self.name = name
        self.add_to_bootclass_path = add_to_bootclass_path

#TODO: more outputs