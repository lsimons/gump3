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

"""This module converts gump xml metadata into a standard form."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import logging
import os

from xml import dom
from xml.dom import minidom

from gump.engine.modeller import _import_attributes
from gump.engine.modeller import _import_node
from gump.engine.modeller import _TagNameFilter
from gump.engine.modeller import _import_children
from gump.engine.modeller import _find_element_text
from gump.engine.modeller import _find_repository_containing_node
from gump.engine.modeller import _find_module_containing_node
from gump.engine.modeller import _find_module_containing_node
from gump.engine.modeller import _do_drop

class Normalizer:
    """Turns a messy gump DOM workspace into a simplified and normalized form.
    
    The normalized form is as follows:
        
        <workspace name="1">
          <other-stuff .../>
          
          <repositories>
            <repository name="1">
              <full-repo-definition-without-modules-or-projects/>
            </repository>
            <repository name="2" ...>
            <repository name="..." ...>
            <repository name="N" ...>
          </repositories>
          
          <modules>
            <module name="1">
              <repository name=""/><!-- not "url"... -->
              <full-module-definition-without-repositories-or-projects/>
            </module>
            <module name="2" ...>
            <module name="..." ...>
            <module name="N" ...>
          </modules>
          
          <projects>
            <project name="1">
              <module name=""/>
              <full-project-definition-without-repositories-or-modules/>
              
              <depend name="1" id="one-id-only"/>
              <depend name="1" id="one-id-only-per-tag"/>
              <depend name="2" optional="true"/>
              <depend name="..." ...>
              <depend name="N" ...>
            </project>
            <project name="2" ...>
            <project name="..." ...>
            <project name="N" ...>
          </projects>
          
        </workspace>
    
    Note that the introduction of the Normalizer makes pygump more flexible than
    the current gump model is specced in several ways:

        * All named elements (repositories, modules, projects) can appear
        anywhere within the graph. This allows, for example, repositories defined
        within projects or modules.
        
        * Relationships between named elements can be established "by inverse".
        The "child" (module to repository, project to module, ...) element can
        appear outside the parent, then reference its parent by name. For example,
        
          <project name="bootstrap-ant">
            <module name="ant"/>
          </project>
        
        is valid. Of course, the reverse
        
          <module name="ant>
            <project name="bootstrap-ant"/>
          </module>
        
        is also still valid.
    
    TODO: support for 0.4 model and earlier...
    """
    def __init__(self, log):
        self.log = log
    
    def normalize(self, olddoc):
        """Turns a messy gump DOM workspace into a simplified and normalized form."""
        self.olddoc = olddoc
        self.oldroot = olddoc.documentElement
        self.impl = dom.getDOMImplementation()
        self.newdoc = self.impl.createDocument(None, "workspace", None)
        self.newroot = self.newdoc.documentElement
        
        self._copy_workspace_root_stuff()
        self._populate_newroot()
        self._parse_maven_projects()

        self._normalize_repositories()
        self._normalize_modules()
        self._normalize_projects()
        
        self._normalize_dependencies()
        
        self._pretty_xml()
        
        doc = self.newdoc
        # allow GC
        self.repositories = None
        self.modules = None
        self.projects = None
        self.olddoc.unlink()
        self.olddoc = None
        self.oldroot = None
        self.newroot = None
        self.newdoc = None
        
        return doc
    
    def _copy_workspace_root_stuff(self):
        """Copies over the unnamed config bits and properties."""
        # copy all ws attributes
        _import_attributes(self.newroot, self.oldroot)
        
        # these elements are to be filtered out completely
        # at all levels
        exclude = ["repositories",
                   "repository",
                   "modules",
                   "module",
                   "projects",
                   "project"]
        
        # try to avoid cloning most of them
        filter = _TagNameFilter(exclude)
        _import_children(self.newroot, self.oldroot, filter)
        
        # now get rid of the excluded tags that were lower down the tree
        # (for example in a <profile/> or somethin')
        self._clean_out_by_tag( self.newroot, exclude )
        
    def _populate_newroot(self):
        """Creates the main containers like <repositories/>."""
        self.repositories = self.newdoc.createElement("repositories")
        self.newroot.appendChild(self.repositories)

        self.modules = self.newdoc.createElement("modules")
        self.newroot.appendChild(self.modules)
        
        self.projects = self.newdoc.createElement("projects")
        self.newroot.appendChild(self.projects)
    
    def _parse_maven_projects(self):
        """Looks for <project type="maven"> and converts those."""
        
        projects = self.projects.getElementsByTagName("project")
        for project in projects:
            if not project.getAttribute("type") == "maven":
                continue
            
            self._parse_maven_project(project)
    
    def _parse_maven_project(self, project):
        #TODO: implement this!
        if True: return

        self._resolve_maven_imports(project)
        
        id = _find_element_text(project, "id")
        groupid = _find_element_text(project, "groupId")
        name = "%s-%s" % (groupid,id)

        title = _find_element_text(project, "title")
        url = _find_element_text(project, "url")
        cvsweb = _find_element_text(project.getElementsByTagName("repository").item(0), "url")
        description = _find_element_text(project, "description")
        
        repository = _find_element_text(project, "gumpRepositoryId")
        if not repository:
            # create repository and module
            connection = _find_element_text(project.getElementsByTagName("repository").item(0), "connection")
            connection = connection[4:] # get rid of "scm:"
            provider = connection[:connection.index(':')] # "cvs" or "svn" or "starteam"
            if provider.upper() == "cvs".upper():
                repository = connection[connection.index(':')+1:]
                parts = repository.split(':')
                user = parts[1][:connection.index('@')]
                host = parts[1][connection.index('@')+1:]
                path = parts[2]
                module = parts[3]

                            
        #new_project = self.newdoc.createElement("project")
        #new_project.setAttribute("name", name)
        #new_command = self.newdoc.createElement("maven")
        #new_project.appendChild(new_command)
    
    def _resolve_maven_imports(self, project):
        pass #TODO: implement this!
    
    def _normalize_repositories(self):
        repos = self._get_list_merged_by_name("repository")
        exclude = ["project", "module", "repository"];
        for repo in repos:
            clone = repo.cloneNode(True)
            self._clean_out_by_tag(clone, exclude)
            self.repositories.appendChild(clone)
    
    def _normalize_modules(self):
        modules = self._get_list_merged_by_name("module")
        
        exclude = ["project", "module", "repository"];
        for module in modules:
            repository = self._find_repository_for_module(module)
            if not repository:
                name = module.getAttribute("name")
                self.log.warn("Dropping module '%s' because no corresponding repository could be found!" % name)
                continue
            
            clone = module.cloneNode(True)
            self._clean_out_by_tag( clone, exclude )
            reporef = self.newdoc.createElement("repository")
            reporef.setAttribute("name", repository.getAttribute("name") )
            clone.insertBefore(reporef, clone.firstChild)
            
            self.modules.appendChild(clone)

    def _find_repository_for_module(self, module):
        repo = None

        # look within module
        repos = module.getElementsByTagName("repository")
        if repos.length > 0:
            return repos.item(0)
        
        # look upward
        return _find_repository_containing_node(module)

    def _normalize_projects(self):
        projects = self._get_list_merged_by_name("project")
        exclude = ["project", "module", "repository"];
        for project in projects:
            module = self._find_module_for_project(project)
            if not module:
                name = project.getAttribute("name")
                self.log.warn("Dropping project '%s' because no corresponding module could be found!" % name)
                continue
            
            clone = project.cloneNode(True)
            self._clean_out_by_tag( clone, exclude )
            moduleref = self.newdoc.createElement("module")
            moduleref.setAttribute("name", module.getAttribute("name") )
            clone.insertBefore(moduleref, clone.firstChild)
            
            self.projects.appendChild(clone)
    
    def _find_module_for_project(self, project):
        repo = None

        # look within module
        modules = project.getElementsByTagName("module")
        if modules.length > 0:
            return modules.item(0)
        
        # look upward
        return _find_module_containing_node(project)

    def _normalize_dependencies(self):
        """Converts <depend/> and <option/> elements into normalized form."""
        for project in self.projects.getElementsByTagName("project"):
            self._normalize_optional_depend(project)
            dependencies = project.getElementsByTagName("depend")
            if dependencies.length > 0:
                self._normalize_depend_inside_ant(project, dependencies)
                self._normalize_depend_on_multiple_ids(project, dependencies)

    def _normalize_optional_depend(self, project):
        """Replace an <option/> with a <depend optional=""/>."""
        options = project.getElementsByTagName("option")
        if options.length > 0:
            for option in options:
                depend = self.newdoc.createElement("depend")
                _import_attributes(depend, option)
                depend.setAttribute("optional", "true")
                project.appendChild(depend)
                _do_drop(option)

    def _normalize_depend_inside_ant(self, project, dependencies):
        """Split <depend/> inside <ant/> out into a <depend/> and a <property/>."""
        for dependency in dependencies:
            if dependency.parentNode.tagName in ["ant","maven"]:
                new_dependency = dependency.cloneNode(True)
                new_dependency.removeAttribute("property")
                project.appendChild(new_dependency)
                
                new_property = self.newdoc.createElement("property")
                new_property.setAttribute("name", dependency.getAttribute("property"))
                new_property.setAttribute("project", dependency.getAttribute("project"))
                new_property.setAttribute("reference", "jarpath")
                if dependency.getAttribute("id"):
                    new_property.setAttribute("id", dependency.getAttribute("id"))
                
                dependency.parentNode.appendChild(new_property)
                _do_drop(dependency)

    def _normalize_depend_on_multiple_ids(self, project, dependencies):
        """Split one <depend/> out into multiple, one for each id."""
        #TODO: reverse that!
        for dependency in dependencies:
            ids = dependency.getAttribute("name")
            if not ids: continue
            if ids.find(",") == -1: continue
            
            project.removeChild(dependency)
            list = ids.split(",")
            for id in list:
                new_dependency = dependency.cloneNode(True)
                new_dependency.setAttribute("ids",id)
                project.appendChild(new_dependency)

    def _clean_out_by_tag(self, root, exclude):
        for tagname in exclude:
            elems_to_remove = root.getElementsByTagName(tagname)
            if elems_to_remove.length > 0:
                for to_remove in elems_to_remove:
                    _do_drop(to_remove)
        
    def _get_list_merged_by_name(self, tagName):
        list = self.oldroot.getElementsByTagName(tagName)
        newlist = {}
        for elem in list:
            name = elem.getAttribute('name')
            if not name:
                self.log.warning( "Dropping a %s because it has no name!" % tagName )
                continue
            
            if newlist.has_key(name):
                _import_node(newlist[name], elem)
            else:
                clone = elem.cloneNode(True)
                newlist[name] = clone
        
        return newlist.values()
    
    def _pretty_xml(self):
        """Adds in some newlines."""
        
        self.newroot.insertBefore(self.newdoc.createTextNode("\n"), self.modules)
        self.newroot.insertBefore(self.newdoc.createTextNode("\n"), self.modules)
        self.newroot.insertBefore(self.newdoc.createTextNode("\n"), self.modules)
        self.newroot.insertBefore(self.newdoc.createTextNode("\n"), self.projects)
        self.newroot.insertBefore(self.newdoc.createTextNode("\n"), self.projects)
        self.newroot.insertBefore(self.newdoc.createTextNode("\n"), self.projects)

        self.repositories.insertBefore(self.newdoc.createTextNode("\n"), self.repositories.firstChild)
        self.repositories.appendChild(self.newdoc.createTextNode("\n"))

        self.modules.insertBefore(self.newdoc.createTextNode("\n"), self.modules.firstChild)
        self.modules.appendChild(self.newdoc.createTextNode("\n"))

        self.projects.insertBefore(self.newdoc.createTextNode("\n"), self.projects.firstChild)
        self.projects.appendChild(self.newdoc.createTextNode("\n"))
