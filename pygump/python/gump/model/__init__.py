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

class ModelError(Exception):
    pass

class ModelObject:
    """
    Base object for all gump model elements.
    """
    pass

class Workspace(ModelObject):
    """
    Model gump workspace and profile. Has the following properties:
        
        - name     -- per-host unique identifier
        - repositories -- dictionary of contained repositories
        - servers  -- list of servers gump knows about (TODO: remove)
        - trackers -- list of issue trackers gump knows about (TODO: remove)
    """
    def __init__(self, name):
        self.name = name
        self.repositories={}

        self.servers={}
        self.trackers={}
    
    def add_repository(self, repository):
        self.repositories[repository.name] = repository
    
    def add_server(self, server):
        self.servers[server.name] = server
    
    def add_tracker(self, tracker):
        self.trackers[tracker.name] = tracker

class Repository(ModelObject):
    """
    Model a source control repository. Has the following properties:
        
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
    """
    Model a CVS repository. Has the following properties:
        
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

class SvnRepository(Repository):
    """
    Model a subversion repository. Has the following properties:
        
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

class Module(ModelObject):
    """
    Model a module within a source control repository. Has the following
    properties:
        
        - repository  -- the containing repository
        - name        -- per-run unique identifier
        - directory   -- base directory within the containing repository
                         for this module
        - url         -- web address of associated project
        - description -- human-readable description
    """
    def __init__(self,
                 repository,
                 name,
                 directory = None,
                 url = None,
                 description = None):
        """
        Create the module.
        """
        self.repository  = repository
        self.name        = name
        self.directory   = directory
        self.url         = url
        self.description = description
        
        self.projects = {}

    def add_project(self, project):
        self.projects[project.name] = project

class Project(ModelObject):
    """
    Model a "project", as far as gump is concerned this is the primary
    "unit of work", something to "build". Projects reside within modules. Has
    the following properties:
        
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
        self.dependencies.append(dependency)
        dependency.dependee.add_dependee(dependency)
    
    def add_dependee(self, dependee):
        self.dependees.append(dependee)
    
    def add_command(self, command):
        self.commands.append(command)
    
    def add_output(self, output):
        self.outputs.append(command)

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
    """
    A dependency is a directional link between two projects, where one
    project (the dependency) depends on another project (the dependee).
    Has the following properties:
        
        - dependency -- the project that is depending on the other project
        - dependee   -- the project that is being depended on by the
                        other project
        - optional   -- flag indicating whether the dependee can be built and
                        used if this dependency cannot be satisfied
        - runtime    -- flag indicating whether the dependee needs this
                        dependency at runtime or just for building
    """
    def __init__(dependency,
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
    """
    A command is something to do as part of a build. Has the following
    properties:
        
        - project -- the containing project
    """
    def __init__(self, project):
        self.project = project
    pass

class Mkdir(Command):
    """
    Create a directory. The directory is specified relative to the source
    directory of the project. Has the following properties:
        
        - all the properties a Command has
        - directory -- the directory to create
    """
    def __init__(self, project, directory):
        Command.__init__(self, project)
        self.directory = directory

class Rmdir(Command):
    """
    Delete a directory. The directory is specified relative to the source
    directory of the project. Has the following properties:
        
        - all the properties a Command has
        - directory -- the directory to delete
    """
    def __init__(self, project, directory):
        Command.__init__(self, project)
        self.directory = directory

class Script(Command):
    """
    Run a script. Has the following properties:
        
        - all the properties a Command has
        - name -- the name of the script to run
        - args -- a list of arguments to the command
    """
    def __init__(self, project, name, args=[]):
        Command.__init__(self, project)
        self.name = name
        self.args = args

OUTPUT_ID_HOME = "homedir"

class Output(ModelObject):
    """
    Something a successful project build will yield. Outputs can be given an
    id to be able to distinguish multiple outputs from another. Has the
    following properties:
        
        - project -- the containing project
        - id      -- a per-project unique identifier
    """
    def __init__(self, project, id = None):
        self.project = project
        self.id      = id

class Homedir(Output):
    """
    A directory containing stuff that can be used by other projects. Has the
    following properties:

        - all the properties an Output has
        - directory -- the directory that should be exported as this project
                       its homedirectory
    """
    def __init__(self, project, id, directory):
        Output.__init__(self, project, id)
        self.directory = directory

