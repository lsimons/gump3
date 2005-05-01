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

from xml import dom
from xml.dom import minidom

from gump.model import *

from gump.engine import EngineError
from gump.engine.modeller import _find_element_text

###
### Creation
###
def _create_workspace(workspace_definition):
    return Workspace(workspace_definition.getAttribute('name'))


def _create_repository(workspace, repository_definition):
    name = repository_definition.getAttribute("name")
    
    # parse the attributes and elements common to all repositories
    title = None
    try: title = _find_element_text(repository_definition, "title")
    except: pass #TODO don't catch everything
    
    home_page = None
    try: home_page = _find_element_text(repository_definition, "home-page")
    except: pass #TODO don't catch everything
    
    cvsweb = None
    try: cvsweb = _find_element_text(repository_definition, "cvsweb")
    except:
        try: cvsweb = _find_element_text(repository_definition, "web")
        except: pass #TODO don't catch everything
    
    redistributable = False
    if repository_definition.getElementsByTagName("redistributable").length > 0:
        redistributable = True
        
    # now delegate to _create methods for specific repositories to do the rest
    repository = None
    type = repository_definition.getAttribute("type").upper()
    if type == "CVS":
        repository = _create_cvs_repository(workspace, name, title, home_page, \
                                            cvsweb, redistributable, repository_definition)
    elif type == "SVN":
        repository = _create_svn_repository(workspace, name, title, home_page, \
                                            cvsweb, redistributable, repository_definition)
    else:
        raise EngineError, "Unknown repository type '%s' for repository '%s'" % (type, name)
    #TODO perforce support
    
    return repository


def _create_cvs_repository(workspace, name, title, home_page, cvsweb, redistributable, repository_definition):
    hostname = _find_element_text(repository_definition, "hostname")
    path = _find_element_text(repository_definition, "path")

    method = CVS_METHOD_PSERVER
    try: method = _find_element_text(repository_definition, "method")
    except: pass
    
    user = None
    try: user = _find_element_text(repository_definition, "user")
    except: pass

    password = None
    try: password = _find_element_text(repository_definition, "password")
    except: pass
    
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

    user = None
    try: user = _find_element_text(repository_definition, "user")
    except: pass

    password = None
    try: password = _find_element_text(repository_definition, "password")
    except: pass
    
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
    url = None
    try: url = _find_element_text(module_definition, "url")
    except: pass
    
    description = None
    try: description = _find_element_text(module_definition, "description")
    except: pass
    
    # now delegate to _create methods for specific modules to do the rest
    module = None
    if isinstance(repository, CvsRepository):
        module = _create_cvs_module(repository, name, url, description, module_definition)
    elif isinstance(repository, SvnRepository):
        module = _create_svn_module(repository, name, url, description, module_definition)
    else:
        raise EngineError, "Unknown repository type '%s' referenced by module '%s'" % (repository.__class__,name)
    #TODO perforce support
    return module


def _create_cvs_module(repository, name, url, description, module_definition):
    tag = module_definition.getAttribute("tag")
    return CvsModule(repository, name, tag, url, description)


def _create_svn_module(repository, name, url, description, module_definition):
    path = module_definition.getAttribute("path")
    return SvnModule(repository, name, path, url, description)


def _create_project(module, project_definition):
    name = project_definition.getAttribute("name")
    
    project = Project(module, name)
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
            name = arg.getAttribute("name")
            value = arg.getAttribute("value")
            args.append((name, value))
            
        project.add_command(Script(project, name, args))


def _create_ant_commands(project, project_definition):
    ants = project_definition.getElementsByTagName("ant")
    for cmd in ants:
        name = cmd.getAttribute("name")
        buildfile = cmd.getAttribute("target")
        target = cmd.getAttribute("target")
            
        project.add_command(Ant(project, name, target, buildfile))
        #TODO 


def _create_outputs(project, project_definition):
    homes = project_definition.getElementsByTagName("home")
    if homes.length > 0:
        home = homes.item(0).getAttribute("directory")
        project.add_output(Homedir(project,home))
    
    jars = project_definition.getElementsByTagName("jar")
    for jar in jars:
        name = jar.getAttribute("name")
        id = jar.getAttribute("id")
        add_to_bootclass_path = jar.getAttribute("type") == "boot"
        project.add_output(Jar(project,name,id,add_to_bootclass_path))
        
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
        raise MissingDependencyError(project, dependency_name), "Dependency '%s' specified by '%s' cannot be found!" % (dependency_name, project)
    
    idList = dependency.getAttribute("ids")
    if idList:
        ids=idList.split(' ')        
    else:
        ids=[]
    
    relationship = project.get_dependency_on_project(dependency_project)
    relationship.add_dependency_info(DependencyInfo(relationship,optional,runtime,inherit,ids))

###
### Searching
###
def _find_repository_definitions(root):
    """Retrieves a list of <repository/> elements."""
    children = root.childNodes

    for child in children:
        if not child.nodeType == dom.Node.ELEMENT_NODE: continue
        if child.tagName == "repositories":
            return child.childNodes
        
    raise EngineError, "No <repository/> found!"


def _find_module_definitions(root):
    """Retrieve a list of <module/> elements."""
    children = root.childNodes
    for child in children:
        if not child.nodeType == dom.Node.ELEMENT_NODE: continue
        if child.tagName == "modules":
            return child.childNodes
    
    raise EngineError, "No <module/> found!"


def _find_project_definitions(root):
    """Retrieve a list of <project/> elements."""
    children = root.childNodes
    for child in children:
        if not child.nodeType == dom.Node.ELEMENT_NODE: continue
        if child.tagName == "projects":
            return child.childNodes

    raise EngineError, "No <project/> found!"


###
### Classes
###
class MissingDependencyError(EngineError):
    """Exception that's raised if a dependency is declared on a project that doesn't exist."""
    def __init__(project, dependency_name):
        self.project = project
        self.dependency_name = dependency_name


class Objectifier:
    """Turns a *normalized* gump DOM workspace into a pythonified workspace.

    The input for the objectifier is a (potentially rather big) DOM tree that
    contains normalized gump project definitions. From this tree, it starts
    building a python object model graph consisting of instances of the
    classes found in the gump.model package.

    Also note that the Objectifier is purely single-threaded, since it stores
    intermediate results during parsing as properties for convenience.
    """
    
    def __init__(self, log):
        """Store all settings and dependencies as properties."""
        self.log = log

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

        for repository_definition in repository_definitions:
            if not repository_definition.nodeType == dom.Node.ELEMENT_NODE: continue
            name = repository_definition.getAttribute("name")
            self.log.debug("Converting repository definition '%s' into object form." % name)
            repository = _create_repository(workspace, repository_definition)
            workspace.repositories[repository.name] = repository
    
    def _find_repository_for_module(self, workspace, module_definition):
        name = module_definition.getAttribute("name")
        repo_name = module_definition.getElementsByTagName("repository").item(0).getAttribute("name")
        repo = workspace.repositories[repo_name]
        return repo

    def _create_modules(self, workspace, module_definitions):
        for module_definition in module_definitions:
            if not module_definition.nodeType == dom.Node.ELEMENT_NODE: continue
            name = module_definition.getAttribute("name")
            self.log.debug("Converting module definition '%s' into object form." % name)
            repository = self._find_repository_for_module(workspace, module_definition)
            module = _create_module(repository, module_definition)
            module.repository.modules[module.name] = module
            workspace.modules[module.name] = module
        
    def _find_module_for_project(self, workspace, project_definition):
        name = project_definition.getAttribute("name")
        module_name = project_definition.getElementsByTagName("module").item(0).getAttribute("name")
        module = workspace.modules[module_name]
        return module

    def _create_projects(self, workspace, project_definitions):
        for project_definition in project_definitions:
            if not project_definition.nodeType == dom.Node.ELEMENT_NODE: continue
            name = project_definition.getAttribute("name")
            self.log.debug("Converting project definition '%s' into object form." % name)
            module = self._find_module_for_project(workspace, project_definition)
            project = _create_project(module, project_definition)
            project.module.projects[project.name] = project
            workspace.projects[project.name] = project

            _create_commands(project, project_definition)
            _create_outputs(project, project_definition)

        # wire up dependencies only after projects have been created
        for project_definition in project_definitions:
            if not project_definition.nodeType == dom.Node.ELEMENT_NODE: continue
            _create_dependencies(project_definition, workspace.projects)
