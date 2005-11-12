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

"""This module converts gump xml metadata to object form."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import logging
import os
import sys

from xml import dom
from xml.dom import minidom

from gump.model import *
from gump.model.util import *

from gump.engine import EngineError
from gump.engine.modeller import _find_element_text

from gump.util import ansicolor

DEFAULT_GUMP_LOCAL_REPOSITORY_NAME = "DEFAULT_GUMP_LOCAL_REPOSITORY"
DEFAULT_GUMP_LOCAL_MODULE_NAME = "DEFAULT_GUMP_LOCAL_MODULE"
###
### Utility
###
def _extract_path(project, element):
    """ Extract directory relative to module or project, based
        upon which attribute (parent or nested) is present."""
    parent = element.getAttribute("parent")
    nested = element.getAttribute("nested")
    
    if parent:
        return os.path.join(get_module_directory(project.module), parent)
    elif nested:
        return os.path.join(get_project_directory(project), nested)
    else:
        raise Error, "Unknown relative path entry (no parent or nested): %s" % (element)


###
### Creation
###
def _create_workspace(workspace_definition, workdir):
    name = workspace_definition.getAttribute('name')
    assert isinstance(name, basestring)
    
    wd = os.path.join(workdir, name)
    if not os.path.exists(wd):
        os.makedirs(wd)
    return Workspace(name, wd)


def _create_repository(workspace, repository_definition):
    name = repository_definition.getAttribute("name")
    
    # parse the attributes and elements common to all repositories
    title = _find_element_text(repository_definition, "title")
    home_page = _find_element_text(repository_definition, "home-page")
    cvsweb = _find_element_text(repository_definition, "cvsweb")
    if cvsweb == None:
        cvsweb = _find_element_text(repository_definition, "web")
    redistributable = repository_definition.getElementsByTagName("redistributable").length > 0
        
    # now delegate to _create methods for specific repositories to do the rest
    type = repository_definition.getAttribute("type").upper()
    if type == "CVS":
        return _create_cvs_repository(workspace, name, title, home_page, \
                                      cvsweb, redistributable, repository_definition)
    elif type == "SVN":
        return _create_svn_repository(workspace, name, title, home_page, \
                                      cvsweb, redistributable, repository_definition)
    else:
        raise EngineError, "Unknown repository type '%s' for repository '%s'" % (type, name)
    #TODO perforce support


def _create_cvs_repository(workspace, name, title, home_page, cvsweb, \
                           redistributable, repository_definition):
    hostname = _find_element_text(repository_definition, "hostname")
    path = _find_element_text(repository_definition, "path")
    method = _find_element_text(repository_definition, "method") or CVS_METHOD_PSERVER
    user = _find_element_text(repository_definition, "user")
    password = _find_element_text(repository_definition, "password")
    
    repository = CvsRepository(workspace,
                               name,
                               hostname,
                               path,
                               title = title,
                               home_page = home_page,
                               cvsweb = cvsweb,
                               redistributable = False,
                               method = CVS_METHOD_PSERVER,
                               user = user,
                               password = password)
    return repository


def _create_svn_repository(workspace, name, title, home_page, cvsweb, redistributable, repository_definition):
    url = _find_element_text(repository_definition, "url")
    user = _find_element_text(repository_definition, "user")
    password = _find_element_text(repository_definition, "password")
    
    repository = SvnRepository(workspace,
                               name,
                               url,
                               title = title,
                               home_page = home_page,
                               cvsweb = cvsweb,
                               redistributable = False,
                               user = user,
                               password = password)
    return repository


def _create_module(repository, module_definition):
    name = module_definition.getAttribute("name")
    
    # parse the attributes and elements common to all modules
    url = _find_element_text(module_definition, "url")
    description = _find_element_text(module_definition, "description")
    
    # now delegate to _create methods for specific modules to do the rest
    if isinstance(repository, CvsRepository):
        return _create_cvs_module(repository, name, url, description, module_definition)
    elif isinstance(repository, SvnRepository):
        return _create_svn_module(repository, name, url, description, module_definition)
    elif isinstance(repository, LocalRepository):
        return _create_local_module(repository, name, url, description, module_definition)
    else:
        raise EngineError, \
              "Unknown repository type '%s' referenced by module '%s'" % \
              (repository.__class__,name)
    #TODO perforce support
    return module


def _create_cvs_module(repository, name, url, description, module_definition):
    tag = module_definition.getAttribute("tag")
    return CvsModule(repository, name, tag, url, description)


def _create_svn_module(repository, name, url, description, module_definition):
    path = module_definition.getAttribute("path")
    return SvnModule(repository, name, path, url, description)


def _create_local_module(repository, name, url, description, module_definition):
    return LocalModule(repository, name, url, description)


def _create_project(module, project_definition):
    name = project_definition.getAttribute("name")
    path = project_definition.getAttribute("path")
    
    project = Project(module, name, path)

    homes = project_definition.getElementsByTagName("home")
    if homes.length > 0:
        project.homedir = _extract_path(project, homes.item(0))

    return project


def _create_commands(project, project_definition, log=None):
    _create_rmdir_commands(project, project_definition)
    _create_mkdir_commands(project, project_definition)
    _create_script_commands(project, project_definition, log=log)
    _create_specific_script_commands(project, project_definition, "configure", Configure, log=log)
    _create_make_commands(project, project_definition, log=log)
    _create_specific_script_commands(project, project_definition, "autoconf", Autoconf, log=log)
    _create_specific_script_commands(project, project_definition, "automake", Automake, log=log)
    _create_ant_commands(project, project_definition, log=log)
    _create_maven_commands(project, project_definition, log=log)
    #TODO more commands


def _get_property(command, prop):
    name = prop.getAttribute("name")
    propvalue = None

    value = prop.getAttribute("value")
    project = prop.getAttribute("project")
    reference = prop.getAttribute("reference")
    path = prop.getAttribute("path")
    id = prop.getAttribute("id")
    
    # TODO: *seriously* clean this up. Sheesh. Shame on whoever wrote it (me,
    #   Leo Simons. I take full responsibility).
    # The horrendous piece of logic below is dictated by
    #   http://gump.apache.org/metadata/builder.html#property%2Farg
    if not name:
        raise Error, "Need to specify a name for property of command %s" % command
    if project:
        if value:
            raise Error, "Can't specify both a value and a project for property %s of command %s" % (name, command)
        if path:
            raise Error, "Can't specify both a path and a project for property %s of command %s" % (name, command)
        if not reference:
            raise Error, "Must specify either a reference or a path for property %s of command %s referencing project %s" % (name, command, project)
        if id and not (reference == "jar" or reference == "jarpath"):
            raise Error, "Can't specify an id %s for property %s of command %s unless reference is 'jar', instead of '%s'" % (id, name, command, reference)
        
        if not project in command.project.module.repository.workspace.projects.keys():
            raise Error, "Can't reference non-existent project '%s' from property %s of command %s" % (project, name, command)
    if path:
        if value:
            raise Error, "Can't specify both a value and a path for property %s of command %s" % (name, command)
            
    if project:
        referenced_project = command.project.module.repository.workspace.projects[project]
        
        if not has_dependency_on(dependee=command.project, dependency=referenced_project):
            raise Error, "Can't refer to project %s from property %s of command %s because that is not a declared dependency" % (referenced_project, name, command)
        
        if reference == "jar" or reference == "jarpath":
            jars = [o for o in referenced_project.outputs if isinstance(o, Jar)]
            if id:
                for jar in jars:
                    if jar.id == id:
                        propvalue = jar
                
                if not propvalue:
                    raise Error, "Project %s does not export jar with id %s referenced in property %s of command %s" % (project, id, name, command)
            else:
                if len(jars) > 1:
                    raise Error, "Project %s exports more than one jar but property %s of command %s does not specify an id" % (project, name, command)
                if len(jars) < 1:
                    raise Error, "Project %s exports does not export a jar but property %s of command %s tries to reference them" % (project, name, command)
                
                propvalue = jars[0]
            
            if reference == "jarpath":
                propvalue = get_jar_path(propvalue)
            else:
                propvalue = jar.name
        elif reference == "home":
            propvalue = get_project_home_directory(referenced_project)
        elif reference == "srcdir":
            propvalue = get_project_directory(referenced_project)
        elif reference == "path":
            outputs = [o for o in referenced_project.outputs if isinstance(o, BinariesPath)]
            if id:
                for o in outputs:
                    if o.id == id:
                        propvalue = join(get_project_home_directory(referenced_project), o.name)
            else:
                if len(jars) > 1:
                    raise Error, "Project %s exports more than one path containing binaries but property %s of command %s does not specify an id" % (project, name, command)
                if len(jars) < 1:
                    raise Error, "Project %s exports does not export a path containing binaries but property %s of command %s tries to reference them" % (project, name, command)
        elif reference == "includes":
            outputs = [o for o in referenced_project.outputs if isinstance(o, IncludesPath)]
            if id:
                for o in outputs:
                    if o.id == id:
                        propvalue = join(get_project_home_directory(referenced_project), o.name)
            else:
                if len(jars) > 1:
                    raise Error, "Project %s exports more than one path containing header files but property %s of command %s does not specify an id" % (project, name, command)
                if len(jars) < 1:
                    raise Error, "Project %s exports does not export a path containing header files but property %s of command %s tries to reference them" % (project, name, command)
        elif reference == "dynamic-libraries":
            outputs = [o for o in referenced_project.outputs if isinstance(o, DynamicLibrariesPath)]
            if id:
                for o in outputs:
                    if o.id == id:
                        propvalue = join(get_project_home_directory(referenced_project), o.name)
            else:
                if len(jars) > 1:
                    raise Error, "Project %s exports more than one path containing dynamic libraries but property %s of command %s does not specify an id" % (project, name, command)
                if len(jars) < 1:
                    raise Error, "Project %s exports does not export a path containing dynamic libraries but property %s of command %s tries to reference them" % (project, name, command)
        else:
            raise Error, "Command %s has a property %s with an unknown reference type of %s" % (command, name, reference)
    elif value:
        propvalue = value
    elif path:
        propvalue = os.path.join(get_project_directory(command.project), path)

    return (name, propvalue)

ENV_DELETION_MARKER="gumpobjectifierdeletethisvariableplease"
def _create_env_vars(command, cmd, log=None):
    env = {}
    for env in cmd.getElementsByTagName("env"):
        (name, value) = _get_property(command, env)
        if log: log.debug("Environment variable %s = '%s' for command %s" % (name, value, command))
        if value:
            command.env[name] = value
        else:
            if command.env.has_key(name):
                command.env.pop(name)


def _create_properties(command, cmd, log=None):
    properties = {}
    for prop in cmd.getElementsByTagName("property"):
        (name, value) = _get_property(command, prop)
        if log: log.debug("Property %s = '%s' for command %s" % (name, value, command))
        properties[name] = value
    command.properties = properties
                
def _create_args(command, cmd, log=None):
    args = []
    for arg in cmd.getElementsByTagName("arg"):
        (name, value) = _get_property(command, arg)
        if log: log.debug("Argument %s = '%s' for command %s" % (name, value, command))
        if name:
            if name.startswith("--"):
                if value:
                    args.append("%s=%s" % (name, value))
                else:
                    args.append(name)
            elif name.startswith("-"):
                args.append(name)
                if value:
                    args.append(value)
            else:
                args.append(name)
                if value:
                    args.append(value)
        else:
            if value:
                args.append(value)
    command.args = command.args + args


def _enable_debug(command, cmd):
    if cmd.getAttribute("debug"):
        command.debug = True
    else:
        command.debug = False


def _create_rmdir_commands(project, project_definition):
    rmdirs = project_definition.getElementsByTagName("delete")
    for cmd in rmdirs:
        dir = cmd.getAttribute("dir")
        project.add_command(Rmdir(project, dir))


def _create_mkdir_commands(project, project_definition):
    mkdirs = project_definition.getElementsByTagName("mkdir")
    for cmd in mkdirs:
        dir = cmd.getAttribute("dir")
        project.add_command(Mkdir(project, dir))


def _create_script_commands(project, project_definition, log=None):
    scripts = project_definition.getElementsByTagName("script")
    for cmd in scripts:
        name = cmd.getAttribute("name")
        shell = cmd.getAttribute("shell")
        basedir = cmd.getAttribute("basedir")
        command = Script(project, name, shell=shell, basedir=basedir)
        _create_args(command, cmd, log=log)
        _create_env_vars(command, cmd, log=log)
        
        project.add_command(command)


def _create_specific_script_commands(project, project_definition, element_name, class_name, log=None):
    scripts = project_definition.getElementsByTagName(element_name)
    for cmd in scripts:
        shell = cmd.getAttribute("shell")
        basedir = cmd.getAttribute("basedir")
        command = class_name(project, shell=shell, basedir=basedir)
        _create_args(command, cmd, log=log)
        _create_env_vars(command, cmd, log=log)
        
        project.add_command(command)


def _create_make_commands(project, project_definition, log=None):
    scripts = project_definition.getElementsByTagName("make")
    for cmd in scripts:
        shell = cmd.getAttribute("shell")
        basedir = cmd.getAttribute("basedir")
        makefile = cmd.getAttribute("makefile")
        targets = cmd.getAttribute("target")
        if targets:
            targets = targets.split(",")
        command = Make(project, makefile=makefile, targets=targets, shell=shell, basedir=basedir)
        _create_args(command, cmd, log=log)
        _create_env_vars(command, cmd, log=log)
        
        project.add_command(command)


def _create_ant_commands(project, project_definition, log=None):
    ants = project_definition.getElementsByTagName("ant")
    for cmd in ants:
        buildfile = cmd.getAttribute("buildfile")
        target = cmd.getAttribute("target")
        basedir = cmd.getAttribute("basedir")
        command = Ant(project, target, buildfile=buildfile, basedir=basedir)
        _create_properties(command, cmd, log=log)
        _enable_debug(command, cmd)

        project.add_command(command)

def _create_maven_commands(project, project_definition, log=None):
    mavens = project_definition.getElementsByTagName("maven")
    for cmd in mavens:
        buildfile = cmd.getAttribute("buildfile")
        target = cmd.getAttribute("target")
        basedir = cmd.getAttribute("basedir")
        command = Maven(project, target, buildfile=buildfile, basedir=basedir)
        _create_properties(command, cmd, log=log)
        _enable_debug(command, cmd)
        project.add_command(command)

def _create_outputs(project, project_definition):    
    _create_work_outputs(project, project_definition)
    _create_jar_outputs(project, project_definition)
    _create_path_outputs(project, project_definition, "path", BinariesPath)
    _create_path_outputs(project, project_definition, "include", IncludesPath)
    _create_path_outputs(project, project_definition, "dynamic-libraries", DynamicLibrariesPath)
    #TODO more outputs


def _create_work_outputs(project, project_definition):
    works = project_definition.getElementsByTagName("work")
    for work in works:
        path = _extract_path(project, work)
        project.add_output(Classdir(project, path))


def _create_jar_outputs(project, project_definition):
    jars = project_definition.getElementsByTagName("jar")
    for jar in jars:
        name = jar.getAttribute("name")
        id = jar.getAttribute("id")
        add_to_bootclass_path = jar.getAttribute("type") == "boot"
        project.add_output(Jar(project, name, id, add_to_bootclass_path))


def _create_path_outputs(project, project_definition, element_name, class_name):
    paths = project_definition.getElementsByTagName(element_name)
    for path in paths:
        name = path.getAttribute("name")
        id = path.getAttribute("id")
        project.add_output(class_name(project, name, id=id))


def _create_dependencies(project_definition, projectlist):
    name = project_definition.getAttribute("name")
    project = projectlist[name]
        
    dependencies = project_definition.getElementsByTagName("depend")
    for dependency in dependencies:
        _add_dependency(project, dependency, projectlist)


def _add_dependency(project, dependency, projectlist):
    dependency_name = dependency.getAttribute("project")
    runtime = dependency.getAttribute("runtime") == "true"
    inherit = dependency.getAttribute("inherit")
    optional = dependency.getAttribute("optional") == "true"
    
    dependency_project = None
    try:
        dependency_project = projectlist[dependency_name]
    except KeyError:
        raise MissingDependencyError(project, dependency_name)
    
    idList = dependency.getAttribute("ids")
    if idList:
        ids=idList.split(' ')        
    else:
        ids=[]
    
    relationship = project.get_dependency_on_project(dependency_project)
    info = DependencyInfo(relationship,optional,runtime,inherit,ids)
    relationship.add_dependency_info(info)

###
### Searching
###
def _find_child_definitions(root, parent_element_name):
    """Retrieves a list of elements that have a particular parent."""
    children = root.childNodes

    for child in [c for c in children \
            if c.nodeType == dom.Node.ELEMENT_NODE]:
        if child.tagName == parent_element_name:
            return child.childNodes
        
    raise EngineError, "No <%s/> found!" % parent_element_name
    

def _find_repository_definitions(root):
    """Retrieves a list of <repository/> elements."""
    return _find_child_definitions(root, "repositories")


def _find_module_definitions(root):
    """Retrieve a list of <module/> elements."""
    return _find_child_definitions(root, "modules")


def _find_project_definitions(root):
    """Retrieve a list of <project/> elements."""
    return _find_child_definitions(root, "projects")


###
### Classes
###
class MissingDependencyError(EngineError):
    """Exception that's raised if a dependency is declared on a project that doesn't exist."""
    def __init__(self, project, dependency_name):
        self.project = project
        self.dependency_name = dependency_name
    
    def __str__(self):
        return "%sDependency '%s' specified by '%s' cannot be found!%s" % \
               (ansicolor.Red, self.dependency_name, self.project, ansicolor.Black)


class Objectifier:
    """Turns a *normalized* gump DOM workspace into a pythonified workspace.

    The input for the objectifier is a (potentially rather big) DOM tree that
    contains normalized gump project definitions. From this tree, it starts
    building a python object model graph consisting of instances of the
    classes found in the gump.model package.

    Also note that the Objectifier is purely single-threaded, since it stores
    intermediate results during parsing as properties for convenience.
    """
    
    def __init__(self, log, workdir):
        """Store all settings and dependencies as properties."""
        assert hasattr(log,"debug") and callable(log.debug)
        assert os.path.isdir(workdir)
        
        self.log = log
        self.workdir = workdir

    def get_workspace(self, domtree):
        """Transforms a workspace xml document into object form."""
        root = domtree.documentElement
        workspace = _create_workspace(root, self.workdir)

        self._create_repositories(workspace, _find_repository_definitions(root))
        self._create_modules(workspace, _find_module_definitions(root))
        self._create_projects(workspace, _find_project_definitions(root), log=self.log)

        return workspace
    
    def _create_repositories(self, workspace, repository_definitions):
        """Creates all repositories and adds them to the workspace."""
        
        # Create a "default repository" for modules that don't actually live in
        # version control (aka installed packages)
        repository = LocalRepository(workspace, DEFAULT_GUMP_LOCAL_REPOSITORY_NAME)
        workspace.repositories[repository.name] = repository

        for repository_definition in [r for r in repository_definitions \
                if r.nodeType == dom.Node.ELEMENT_NODE]:
            name = repository_definition.getAttribute("name")
            #self.log.debug("Converting repository definition '%s' into object form." % name)
            try:
                repository = _create_repository(workspace, repository_definition)
                workspace.repositories[repository.name] = repository
            except:
                self.log.exception(
                    "%sFailed to convert repository definition '%s' into object form.%s" % \
                    (ansicolor.Bright_Red, name, ansicolor.Black))
    
    def _find_repository_for_module(self, workspace, module_definition):
        try:
            name = module_definition.getAttribute("name")
            repo_name = module_definition.getElementsByTagName("repository").item(0).getAttribute("name")
            repo = workspace.repositories[repo_name]
            return repo
        except:
            # If we can't find a repository, then we're dealing with an installed
            # package
            self.log.warn("Could not find a corresponding repository, so %smodule '%s' will be treated as an installed package%s" % \
                          (ansicolor.Yellow, name, ansicolor.Black))
            return workspace.repositories[DEFAULT_GUMP_LOCAL_REPOSITORY_NAME]

    def _create_modules(self, workspace, module_definitions):
        # Create a "default module" for projects that don't actually live in
        # version control (aka installed packages)
        repository = workspace.repositories[DEFAULT_GUMP_LOCAL_REPOSITORY_NAME]
        module = LocalModule(repository, DEFAULT_GUMP_LOCAL_MODULE_NAME)
        repository.add_module(module)
        workspace.modules[module.name] = module

        for module_definition in [m for m in module_definitions \
                if m.nodeType == dom.Node.ELEMENT_NODE]:
            name = module_definition.getAttribute("name")
            #self.log.debug("Converting module definition '%s' into object form." % name)
            try:
                repository = self._find_repository_for_module(workspace, module_definition)
                module = _create_module(repository, module_definition)
                module.repository.modules[module.name] = module
                workspace.modules[module.name] = module
            except:
                self.log.exception("%sFailed to convert module definition '%s' into object form.%s" % \
                                   (ansicolor.Bright_Red, name, ansicolor.Black))
        
    def _find_module_for_project(self, workspace, project_definition):
        try:
            name = project_definition.getAttribute("name")
            module_name = project_definition.getElementsByTagName("module").item(0).getAttribute("name")
            module = workspace.modules[module_name]
            return module
        except:
            # If we can't find a module, then we're dealing with an installed
            # package
            self.log.warn("Could not find a corresponding module, so %sproject '%s' will be treated as an installed package%s" % \
                          (ansicolor.Yellow, name, ansicolor.Black))
            return workspace.modules[DEFAULT_GUMP_LOCAL_MODULE_NAME]

    def _create_projects(self, workspace, project_definitions, log=None):
        project_definitions = [p for p in project_definitions \
                if p.nodeType == dom.Node.ELEMENT_NODE]
        failures = []
        
        # TODO rewrite this function. Its way ugly.
        
        for project_definition in project_definitions:
            name = project_definition.getAttribute("name")
            if not name:
                self.log.error("%sCan't convert project definition because it does not have a name!%s" % \
                               (ansicolor.Bright_Red, ansicolor.Black))
                failures.append(project_definition)
                continue
            #self.log.debug("Converting project definition '%s' into object form." % name)
            try:
                module = self._find_module_for_project(workspace, project_definition)
                project = _create_project(module, project_definition)
                project.module.projects[project.name] = project
                _create_outputs(project, project_definition)

                workspace.projects[project.name] = project
            except:
                self.log.exception("%sFailed to convert project definition '%s' into object form.%s" % \
                                   (ansicolor.Bright_Red, name, ansicolor.Black))
                failures.append(project_definition)
        
        # wire up dependencies only after projects have been created
        for project_definition in [p for p in project_definitions \
                if not p in failures]:
            try:
                _create_dependencies(project_definition, workspace.projects)
            except:
                failures.append(project_definition)
                
                from gump.model.util import mark_failure
                from gump.engine.algorithm import ExceptionInfo
                (type, value, traceback) = sys.exc_info()
                cause = ExceptionInfo(type, value, traceback)
                self.log.error(cause)
                name = project_definition.getAttribute("name")
                project = workspace.projects[name]
                mark_failure(project, cause)
                
        # wire up properties only after dependencies are fully set up
        for project_definition in [p for p in project_definitions \
                if not p in failures]:
            name = project_definition.getAttribute("name")
            project = workspace.projects[name]
            try:
                _create_commands(project, project_definition, log=log)
            except:
                failures.append(project_definition)

                from gump.model.util import mark_failure
                from gump.engine.algorithm import ExceptionInfo
                (type, value, traceback) = sys.exc_info()
                cause = ExceptionInfo(type, value, traceback)
                self.log.error(cause)
                name = project_definition.getAttribute("name")
                project = workspace.projects[name]
                mark_failure(project, cause)
