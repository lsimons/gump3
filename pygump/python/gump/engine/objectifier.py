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

DEFAULT_GUMP_LOCAL_REPOSITORY_NAME = "DEFAULT_GUMP_LOCAL_REPOSITORY"
DEFAULT_GUMP_LOCAL_MODULE_NAME = "DEFAULT_GUMP_LOCAL_MODULE"
###
### Utility
###
def _extract_path(workdir, project, element):
    """ Extract directory relative to module or project, based
        upon which attribute (parent or nested) is present."""
    parent = element.getAttribute("parent")
    nested = element.getAttribute("nested")
    
    if parent:
        return os.path.join(get_module_directory(workdir, project.module), parent)
    elif nested:
        return os.path.join(get_project_directory(workdir, project), nested)
    else:
        raise Error, "Unknown relative path entry (no parent or nested): %s" % (element)


###
### Creation
###
def _create_workspace(workspace_definition):
    return Workspace(workspace_definition.getAttribute('name'))


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


def _create_project(module, project_definition, workdir):
    name = project_definition.getAttribute("name")
    path = project_definition.getAttribute("path")
    
    project = Project(module, name, path)

    homes = project_definition.getElementsByTagName("home")
    if homes.length > 0:
        project.homedir = _extract_path(workdir, project, homes.item(0))

    return project


def _create_commands(project, project_definition):
    _create_rmdir_commands(project, project_definition)
    _create_mkdir_commands(project, project_definition)
    _create_script_commands(project, project_definition)
    _create_ant_commands(project, project_definition)
    #TODO more commands


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


def _create_script_commands(project, project_definition):
    scripts = project_definition.getElementsByTagName("script")
    for cmd in scripts:
        name = cmd.getAttribute("name")
        args = []
        for arg in cmd.getElementsByTagName("arg"):
            # TODO parse "-", "--", etc
            argname = arg.getAttribute("name")
            argvalue = arg.getAttribute("value")
            if argname:
                args.append(argname)
            if argvalue:
                args.append(argvalue)
            
        project.add_command(Script(project, name, args))


def _create_ant_commands(project, project_definition):
    ants = project_definition.getElementsByTagName("ant")
    for cmd in ants:
        buildfile = cmd.getAttribute("buildfile")
        target = cmd.getAttribute("target")
            
        project.add_command(Ant(project, target, buildfile))

def _create_outputs(project, project_definition, workdir):    
    # Working directories for this project (containing java classes)
    works = project_definition.getElementsByTagName("work")
    for work in works:
        path = _extract_path(workdir, project_definition, work)
        project.add_output(Classdir(project, path))

    # Jars
    jars = project_definition.getElementsByTagName("jar")
    for jar in jars:
        name = jar.getAttribute("name")
        id = jar.getAttribute("id")
        add_to_bootclass_path = jar.getAttribute("type") == "boot"
        project.add_output(Jar(project, name, id, add_to_bootclass_path))
    
    #TODO more outputs


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
        return "Dependency '%s' specified by '%s' cannot be found!" % (self.dependency_name, self.project)


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
        workspace = _create_workspace(root)

        self._create_repositories(workspace, _find_repository_definitions(root))
        self._create_modules(workspace, _find_module_definitions(root))
        self._create_projects(workspace, _find_project_definitions(root))

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
            self.log.debug("Converting repository definition '%s' into object form." % name)
            try:
                repository = _create_repository(workspace, repository_definition)
                workspace.repositories[repository.name] = repository
            except:
                self.log.exception(
                    "Failed to convert repository definition '%s' into object form." % name)
    
    def _find_repository_for_module(self, workspace, module_definition):
        try:
            name = module_definition.getAttribute("name")
            repo_name = module_definition.getElementsByTagName("repository").item(0).getAttribute("name")
            repo = workspace.repositories[repo_name]
            return repo
        except:
            # If we can't find a repository, then we're dealing with an installed
            # package
            self.log.debug("It seems that the module '%s' is an installed package" % name)
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
            self.log.debug("Converting module definition '%s' into object form." % name)
            try:
                repository = self._find_repository_for_module(workspace, module_definition)
                module = _create_module(repository, module_definition)
                module.repository.modules[module.name] = module
                workspace.modules[module.name] = module
            except:
                self.log.exception("Failed to convert module definition '%s' into object form." % name)
        
    def _find_module_for_project(self, workspace, project_definition):
        try:
            name = project_definition.getAttribute("name")
            module_name = project_definition.getElementsByTagName("module").item(0).getAttribute("name")
            module = workspace.modules[module_name]
            return module
        except:
            # If we can't find a module, then we're dealing with an installed
            # package
            self.log.debug("It seems that the project '%s' is an installed package" % name)
            return workspace.modules[DEFAULT_GUMP_LOCAL_MODULE_NAME]

    def _create_projects(self, workspace, project_definitions):
        project_definitions = [p for p in project_definitions \
                if p.nodeType == dom.Node.ELEMENT_NODE]
        failures = []
        
        for project_definition in project_definitions:
            name = project_definition.getAttribute("name")
            if not name:
                self.log.error("Can't convert project definition because it does not have a name!")
                failures.append(project_definition)
                continue
            self.log.debug("Converting project definition '%s' into object form." % name)
            try:
                module = self._find_module_for_project(workspace, project_definition)
                project = _create_project(module, project_definition, self.workdir)
                project.module.projects[project.name] = project
                self.log.debug("Adding %s to workspace project list" % project.name)
                workspace.projects[project.name] = project
    
                _create_commands(project, project_definition)
                _create_outputs(project, project_definition, self.workdir)
            except:
                self.log.exception("Failed to convert project definition '%s' into object form." % name)
                failures.append(project_definition)
        
        # wire up dependencies only after projects have been created
        for project_definition in [p for p in project_definitions \
                if not p in failures]:
            try:
                _create_dependencies(project_definition, workspace.projects)
            except:
                from gump.model.util import mark_failure
                from gump.engine.algorithm import ExceptionInfo
                (type, value, traceback) = sys.exc_info()
                cause = ExceptionInfo(type, value, traceback)
                self.log.error(cause)
                name = project_definition.getAttribute("name")
                #self.log.exception("Failed to set up dependencies for project %s" % name)
                project = workspace.projects[name]
                mark_failure(project, cause)
