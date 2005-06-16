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
    def __str__(self):
        typerep = str(self.__class__).split('.').pop()
        
        if hasattr(self, "name"):
            return "<%s: %s>" % (typerep, self.name)
        else:
            return "<%s>" % typerep


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
        assert isinstance(name, basestring)
    
        self.name = name
        self.repositories = {}
        self.modules = {}
        self.projects = {}
        self.dependencies = []
    
    def add_repository(self, repository):
        assert isinstance(repository, Repository)
        assert not self.repositories.has_key(repository.name)
        assert self == repository.workspace
        
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
        assert isinstance(workspace, Workspace)
        assert isinstance(name, basestring)
        
        self.workspace       = workspace
        self.name            = name
        self.title           = title
        self.home_page       = home_page
        self.cvsweb          = cvsweb
        self.redistributable = redistributable

        self.modules={}

    def add_module(self, module):
        assert isinstance(module, Module)
        assert not self.modules.has_key(module.name)
        assert not self.workspace.modules.has_key(module.name)
        assert self == module.repository
        
        self.modules[module.name] = module
        self.workspace.modules[module.name] = module

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
        assert isinstance(hostname,basestring), "Hostname should be a valid string, not '%s'" % hostname
        assert isinstance(path,basestring)
        Repository.__init__(self, workspace, name, title, home_page, cvsweb, redistributable)
        
        self.hostname = hostname
        self.path     = path
        self.method   = method
        self.user     = user
        self.password = password
    
    def to_url(self):
        url = ":%s:" % self.method
        if self.user:
            url = "%s%s@" % (url, self.user)
        url = "%s%s:%s" % (url, self.hostname, self.path)
        
        return url
            

class SvnRepository(Repository):
    """Model a subversion repository.

    Has the following properties:
        
        - all of the properties a Repository has
        - url      -- the address of the svn repository
        TODO: - user     -- the svn user to login as
        TODO: - password -- the svn password to login with
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
        assert isinstance(url, basestring)
        Repository.__init__(self, workspace, name, title, home_page, cvsweb, redistributable)
        if url.endswith("/"):
            self.url = url[:-1]
        else:
            self.url = url
        self.user     = user
        self.password = password

#TODO: class PerforceRepository

#TODO: suppport for configuring these needs to be built into gump, eg point at
#      /usr/local/gump/packages or a location of choice and create an instance.
#      Also, plugins must learn how to "consume" these.
class LocalRepository(Repository):
    """Model a "repository" that exists only locally (eg, "installed packages").

    Has the following properties:
        
        - all of the properties a Repository has
    """
    def __init__(self,
                 workspace,
                 name,
                 title = None,
                 home_page = None,
                 cvsweb = None):
        Repository.__init__(self, workspace, name, title, home_page, cvsweb, False)


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
        assert isinstance(repository, Repository)
        assert isinstance(name, basestring)
        self.repository  = repository
        self.name        = name
        self.url         = url
        self.description = description
        
        self.projects = {}

    def add_project(self, project):
        assert isinstance(project, Project)
        assert not self.projects.has_key(project.name)
        assert not self.repository.workspace.projects.has_key(project.name)
        assert self == project.module
        
        self.projects[project.name] = project
        self.repository.workspace.projects[project.name] = project

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
        self.path = path

#TODO: class PerforceModule

#TODO: suppport for configuring these needs to be built into gump, eg point at
#      /usr/local/gump/packages or a location of choice and create an instance.
#      Also, plugins must learn how to "consume" these.
class LocalModule(Module):
    """Model a module that is not within a version control repository."""
    def __init__(self,
                 repository,
                 name,
                 url = None,
                 description = None):
        Module.__init__(self, repository, name, url, description)

class Project(ModelObject):
    """Model a "project".

    As far as gump is concerned a project is the primary "unit of work",
    something to "build". Projects reside within modules.

    Has the following properties:
        
        - module       -- the containing module
        - name         -- per-run unique identifier
        - path         -- directory path within the containing module
        - dependencies -- list of Dependency instances describing what other
                          projects this project depends upon
        - dependees    -- list of Dependency instances describing what other
                          projects depend on this project
        - commands     -- ordered list of Commands instances that need to be
                          executed to build this project
        - homedir      -- None or a ResolvablePath (outputs are relative to this)
        - outputs      -- list of Output instances describing what results a
                          build of this project results in
        - workitems    -- list of WorkItem instances describing what directories/files
                          are used during the build of this project.
    """
    #TODO nice string representations of the entire model
    #def __str__(self):
    #    return "<Project: %s>" % self.name

    def __init__(self, module, name, path="."):
        assert isinstance(module, Module)
        assert isinstance(name, basestring)
        
        self.module = module
        self.name   = name
        self.path   = path
        self.homedir = None
        
        self.dependencies=[]
        self.dependees=[]
        self.commands=[]
        self.outputs=[]
        self.workitems=[]
    
    def add_dependency(self, relationship):
        assert isinstance(relationship, Dependency)
        # This can make your head hurt :-D
        # let's say that self is "Project A", and 'dependency' is "Project B"
        # Calling this method means that Project A depends on Project B, so
        # Project B is a dependency of Project A
        # Project A is a dependee of Project B
        self.module.repository.workspace.dependencies.append(relationship)
        self.dependencies.append(relationship)
        #print "%s is told %s depends on %s" % (self.name, self.name, relationship.dependency.name)
        
        # register Project A as a dependee of Project B
        # relationship.dependency is Project B
        # relationship.dependency.add_dependee() registers A with B
        #print "%s is telling %s that %s depends on %s" % (self.name, relationship.dependency.name, self.name, relationship.dependency.name)
        if isinstance(relationship.dependency, Project): # might be a string for a bad
                                                            # dependency
            relationship.dependency.add_dependee(relationship)
    
    def get_dependency_on_project(self, dependency):
        """Retrieve the relationship object for this dependency.
        
        If this project already has a declared relationship with the project
        specified as the dependency argument, return that relationship. If not,
        create a new relationship object, add it to "self", then return it."""
        assert isinstance(dependency, Project)
        
        for relationship in self.dependencies:
            if relationship.dependency == dependency:
                return relationship
        
        new_relationship = Dependency(dependency,self)
        self.add_dependency(new_relationship)
        return new_relationship
    
    def add_dependee(self, relationship):
        #print "%s is told that %s is a dependee of %s" % (self.name, relationship.dependee.name, self.name)
        self.dependees.append(relationship)
    
    def add_command(self, command):
        assert isinstance(command, Command)
        self.commands.append(command)
    
    def add_output(self, output):
        assert isinstance(output, Output)
        self.outputs.append(output)
        
    def add_work(self,work):
        assert isinstance(work,WorkItem)
        selfd.works.append(work)

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
        - dependencyInfo -- an array of DependencyInfo objects further
                            qualifying this dependency
    """
    def __init__(self,
                 dependency,
                 dependee,
                 dependencyInfo = []):
        assert isinstance(dependency, Project)
        assert isinstance(dependee, Project)
        for info in dependencyInfo:
            assert isinstance(info, DependencyInfo)
        self.dependency         = dependency
        self.dependee           = dependee
        self.dependencyInfo     = dependencyInfo
    
    def add_dependency_info(self, info):
        assert isinstance(info, DependencyInfo)
        self.dependencyInfo.append(info)
    
    def __str__(self):
        return "<Dependency:%s-->%s>" % (self.dependee, self.dependency)

class DependencyInfo(ModelObject):
    """Model information about a particular dependency.
    
    DependencyInfo objects are used to describe additional information about
    a dependency besides just what projects relate to each other. Each
    Dependency can have multiple DependencyInfo objects associated with it
    detailing exactly what is depended on in the dependency.
    
    Has the following properties:
        - dependency -- the Dependency instance this info is associated with
        - optional   -- flag indicating whether the dependee can be built and
                        used if this dependency cannot be satisfied
        - runtime    -- flag indicating whether the dependee needs this
                        dependency at runtime or just for building
        - inherit    -- option dictating whether this dependency should
                        "cascade" or "propagate in some form
        - specific_output_ids -- option that specifies output IDs from
                        the specified project that is depended on
    """
    def __init__(self,
                 dependency,
                 optional = False,
                 runtime  = False,
                 inherit  = DEPENDENCY_INHERIT_NONE,
                 specific_output_ids = None):
        assert isinstance(dependency, Dependency)
        self.dependency          = dependency
        self.optional            = optional
        self.runtime             = runtime
        self.inherit             = inherit
        self.specific_output_ids = specific_output_ids
    
    def __str__(self):
        return "<DependencyInfo:optional=%s,runtime=%s,inherit=%s,specific_output_ids=%s>" % \
               (self.optional, self.runtime, self.inherit, self.specific_output_ids)

class Command(ModelObject):
    """Model a command.
    
    A command is something to do as part of a build.

    Has the following properties:
        
        - project -- the containing project
    """
    def __init__(self, project):
        assert isinstance(project, Project)
        self.project = project
        
class Mkdir(Command):
    """Model a mkdir command.
    
    Command to create a directory. The directory is specified relative to the
    source directory of the project.

    Has the following properties:
        
        - all the properties a Command has
        - directory -- the directory to create
    """
    def __init__(self, project, directory):
        assert isinstance(directory, basestring)
        Command.__init__(self, project)
        self.directory = directory
    
    def __str__(self):
        return "<Mkdir:%s>" % self.directory

class Rmdir(Command):
    """Model a delete command.
    
    Command to delete a directory. The directory is specified relative to the
    source directory of the project.

    Has the following properties:
        
        - all the properties a Command has
        - directory -- the directory to delete
    """
    def __init__(self, project, directory):
        assert isinstance(directory,basestring)
        Command.__init__(self, project)
        self.directory = directory

    def __str__(self):
        return "<Rmdir:%s>" % self.directory

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
        assert isinstance(name, basestring)
        assert isinstance(args, list)
        for arg in args:
            assert isinstance(arg, basestring)
        Command.__init__(self, project)
        self.name = name
        self.args = args

class Ant(Command):
    """Command to run an Ant build.

    Has the following properties:
        
        - all the properties a Command has
        - name -- the name of the script to run
        - target -- the Ant target
        - buildfile -- the Ant build file
    """
    def __init__(self, project, name, target, buildfile="build.xml"):
        assert isinstance(name, basestring)
        assert isinstance(target, basestring)
        assert isinstance(buildfile, basestring)
        Command.__init__(self, project)
        self.name = name
        self.target = target
        self.buildfile = buildfile

    def __str__(self):
        return "<Ant:%s,target=%s,buildfile=%s>" % (self.name, self.target, self.buildfile)

#TODO: more Commands

class RelativePath(ModelObject):
    def __init__(self,model,path):
        assert isinstance(model, ModelObject)
        assert isinstance(path, basestring)
        self.model = model
        self.path  = path
        
    def resolve(self,workdir):
        from gump.model.util import get_module_directory,get_project_directory
        if isinstance(self.model,Module):
            base=get_module_directory(workdir,self.model)
        elif isinstance(self.model,Project):
            base=get_project_directory(workdir,self.model)
        else:
            pass #TODO Raise?
        import os.path
        return os.path.join(base,self.path)
    
    def __str__(self):
        return "RelativePath:%s:%s" % (self.model,self.path)

class WorkItem(ModelObject):
    """Model a directory containing stuff that can be used by other projects.

    Has the following properties:

        - project -- the containing project.
        - path -- the path to the directory or file.
    """
    def __init__(self, project, path):
        assert isinstance(path, RelativePath)
        self.project = project
        self.path = path
    
    def __str__(self):
        return "<WorkItem:%s>" % (self.path)

class Output(ModelObject):
    """Model an output, something a successful project build will yield.

    Outputs can be given an id to be able to distinguish multiple outputs from
    another.

    Has the following properties:
        
        - project -- the containing project
        - id      -- a per-project unique identifier
    """
    def __init__(self, project, id = None):
        assert isinstance(project, Project)
        self.project = project
        self.id      = id
    
    def __str__(self):
        return "<Output:%s>" % self.id
    
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
        assert isinstance(name, basestring)
        Output.__init__(self, project, id)
        self.name = name
        self.add_to_bootclass_path = add_to_bootclass_path
    
    def __str__(self):
        return "<Jar:%s,id=%s,add_to_bootclass_path=%s>" % (self.name, self.id, self.add_to_bootclass_path)

#TODO: more outputs