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

"""This module reads, merges and converts gump xml metadata."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import logging
import os

from xml import dom
from xml.dom import minidom

from gump.model import *

###
### Utility methods shared between classes
###
def _find_element_text(parent, element_name):
    """Retrieves the text contents of an element like <blah>text</blah>."""
    return parent.getElementsByTagName(element_name).item(0).firstChild.data


def _do_drop(to_remove, dropped_nodes=None):
    """Remove node from its parent and add to dropped_nodes list."""
    
    node_to_remove_element_from = to_remove.parentNode
    node_to_remove_element_from.removeChild(to_remove)
    if dropped_nodes:
        dropped_nodes.append(to_remove)


def _find_ancestor_by_tag(node, tagName):
    """Walk up the DOM hierarchy to locate an element of the specified tag."""
    parent = node
    while parent.nodeType == dom.Node.ELEMENT_NODE:
        if parent.tagName == tagName:
            return parent
        parent = parent.parentNode
        if not parent:
            return None


def _find_document_containing_node(node):
    """Walk up the DOM hierarchy to locate a Document node."""
    parent = node
    while not parent.nodeType == dom.Node.DOCUMENT_NODE:
        parent = parent.parentNode
        if not parent: # really ought not happen I think...
            raise ModellerError, "Cannot find document containing this node!"
    
    return parent


def _find_project_containing_node(node):
    """Walk up the DOM hierarchy to locate a <project> Element."""
    return _find_ancestor_by_tag("project")


def _find_module_containing_node(node):
    """Walk up the DOM hierarchy to locate a <module> Element."""
    return _find_ancestor_by_tag("module")


def _find_repository_containing_node(node):
    """Walk up the DOM hierarchy to locate a <repository> Element."""
    return _find_ancestor_by_tag("repository")


def _import_node(target_node, new_node):
    """Combines two DOM trees together.

    The second argument is merged into the first argument, which is then
    returned.
    """
    self._import_attributes(target_node, new_node)
    self._import_children(target_node, new_node)

    
def _import_attributes(target_node, new_node):
    """Copy all attributes from the new node to the target node."""
    
    new_attributes = new_node.attributes
    if new_attributes:
        #if new_attributes.length > 0:
        i = 0
        while i < new_attributes.length: # for loops gives a KeyError,
            att = new_attributes.item(i) #   seems like a minidom bug!
            i = i + 1
            if not att: continue

            name = att.name.__str__()
            value = new_node.getAttribute(name).__str__()
            target_node.setAttribute(name, value)


def _import_children(target_node, new_node, filter=None):
    """Copy all children from the new node to the target node."""
    new_elements = new_node.childNodes
    if new_elements and new_elements.length > 0:
        for child in new_elements:
            if filter:
                if filter.exclude(child):
                    continue # skip this one
            clone = child.cloneNode(True)
            target_node.appendChild(clone)

###
### Classes
###

class _TagNameFilter:
    """Filter for use with _import_children."""
    def __init__(self, excludedTags):
        self.excludedTags = excludedTags

    def exclude(node):
        if not child.nodeType == dom.Node.ELEMENT_NODE:
            return False
        if node.tagName in self.excludedTags:
            return True
        
        return False


class ModellerError(Exception):
    """Generic error thrown for all internal Modeller module exceptions."""
    pass


class Loader:
    """Parses and resolves Gump XML metadata.

    The only "public" method of this class is get_workspace_tree. This method
    reads in a gump workspace. It then looks for any elements in that workspace
    that have a "href" attribute. This href attribute is resolved to a new XML
    file using the provided Virtual File System, which is then merged with the
    Element that has the attribute. That resolution process is continued until
    the entire workspace no longer contains any hrefs. At that point, the entire
    Workspace is returned as a DOM Element.

    If any HREFs fail to resolve properly, the associated projects (or if there
    are no associated projects, the associated modules) are removed from the
    workspace completely. If no associated project or module exists, the Loader
    will give up and raise an exception.
    
    Note that the loader does *not* do any verification of the XML it loads.
    The only thing it assumes is the existence of <project/> elements contained
    within <module/> elements, and that these elements have name attributes. So,
    for example, the following would be parsed without complaints by the loader:
        
        <bogus>
          <imagine>
            <any>
              <xml-data>
                <with>
                  <module name="foo">
                    <project name="bar">
                      <build href="somefile.xml"/>
                    </project>
                    <project href="otherfile.xml"/>
                  </module>
                  <module href="jo.xml"/>
                </with>
              </xml-data>
        </bogus>
    
    Of course, other parts of the modeller package are not so tolerant!
    """
    def __init__(self, log, vfs=None, merge_file_or_stream=None, drop_file_or_stream=None):
        """
        Create a new Loader.

        Arguments:
            
            - log -- the log to write debug and error messages to.
            - vfs -- the virtual file system to use for resolving hrefs. May
                     be None only if the workspace to load does not contain
                     any hrefs.
        """
        self.log = log
        self.vfs = vfs
    
    def get_workspace_tree(self, workspace):
        """Parse the provided workspace, then resolve all hrefs.
        
        Returns a tuple with the parsed workspace as a dom Element, and all
        the Nodes that were dropped because of problems as a list.
        """
        # get root <workspace/> element
        wsdom = minidom.parse(workspace)
        wsdom.normalize()
        ws = wsdom.documentElement
        
        dropped_nodes = [] # will be used for storing projects we drop...
        
        # resolve all hrefs in all elements, for example
        # <project href="blah.xml"/>; replaces that element with the
        # contents of blah.xml
        self._resolve_hrefs_in_workspace(ws, dropped_nodes)
        
        # the combined results
        return (wsdom, dropped_nodes)
    
    def _resolve_hrefs_in_workspace(self, ws, dropped_nodes):
        """Redirects to _resolve_hrefs_in_children."""
        self._resolve_hrefs_in_children(ws, dropped_nodes)
    
    def _resolve_hrefs_in_children(self, element, dropped_nodes):
        """Recursively resolve all hrefs in all the children for a DOM node.
        
        The resolution is done in a resolve-then-recurse manner, so the end
        result is a dom tree without hrefs. Note that this method expects to
        be passed in a dom Element or something else which actually has children;
        passing in an Attr for example makes no sense and results in problems.
        
        The dropped_nodes arguments should be a list that will be populated with
        nodes for which href resolution fails.
        """
        for child in element.childNodes:
            # only resolve hrefs for elements
            if not child.nodeType == dom.Node.ELEMENT_NODE: continue
            # there's a <url href=""/> element which is descriptive and should
            # not be resolved
            if child.tagName == 'url': continue
            if child.hasAttribute('href'):
                # yep, this is one to load...
                self._resolve_href(child, dropped_nodes)

            # now recurse to resolve any hrefs within this child
            self._resolve_hrefs_in_children(child, dropped_nodes)
        
        # we're now done with resolution
        #return node
    
    def _resolve_href(self, node, dropped_nodes):
        """Resolve a href for the provided node.

        We merge in the referenced xml document into the provided node.
        The href attribute on the provided node will be removed if the merge
        succeeds. If the merge fails the provided node will be removed from
        its parent and appended to the dropped_nodes list.
        """
        href = node.getAttribute('href')
        self.log.debug( "Resolving HREF: %s" % href )
        
        try:
            stream = self.vfs.get_as_stream(href)
        except Exception, details:
            # swallow this in interest of log readability
            self._drop_module_or_project(node, dropped_nodes)
            return # make sure to stop processing...
        
        new_dom = minidom.parse(stream)
        new_dom.normalize()
        stream.close() # close file immediately, we're done!
        new_root = new_dom.documentElement
        
        # we succeeded loading the new document, get rid of the href, save it
        # as "resolved"
        node.removeAttribute('href')
        node.setAttribute('resolved-from-href', href)
        
        _import_node(node, new_root)
        
        # we're done with the file now, allow GC
        new_root.unlink()
    
    def _drop_module_or_project(self, node, dropped_nodes):
        """Finds the project associated with this node and removes it.
        
        If there is no associated project, the associated module is removed
        instead. If there is no module either, an exception is raised.
        """
        
        project = _find_project_containing_node(node)
        if project:
            doc = _find_document_containing_node(project)
            module = _find_module_containing_node(project)
            modulename = module.getAttribute("name")
            comment = doc.createComment(" Part of module: %s " % modulename)
            project.appendChild(comment)
            name = project.getAttribute("name")
            self.log.warning("Dropping project '%s' from module '%s' because of href resolution error!" % (name , modulename))

            _do_drop(project, dropped_nodes)
        else:
            module = _find_module_containing_node(node)
            if module:
                doc = _find_document_containing_node(module)
                name = module.getAttribute("name")
                self.log.warning("Dropping module '%s' because of href resolution error!" % name)

                _do_drop(project, dropped_nodes)
            else:
                raise ModellerError, \
                      "Problematic node has no parent <project/> or " + \
                      "<module/>, unable to recover! Node:\n%s" \
                      % node.toprettyxml()


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
    
    Note that the introduction of the Notifier makes pygump more flexible than
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
        self.olddoc = olddoc
        self.oldroot = olddoc.documentElement
        self.impl = dom.getDOMImplementation()
        self.newdoc = self.impl.createDocument(None, "workspace", None)
        self.newroot = newdoc.documentElement
        
        self._copy_workspace_root_stuff()
        self._populate_newroot()
        self._parse_maven_projects()

        self._normalize_repositories()
        self._normalize_modules()
        self._normalize_projects()
        
        self._normalize_dependencies()
        
        doc = self.newdoc
        # allow GC
        self.repositories = None
        self.modules = None
        self.projects = None
        self.olddoc.unlink()
        self.olddoc = None
        self.oldroot = None
        self.newroot = None
        self.newdoc = none
        
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
        self.repositories = self.impl.createElement("repositories")
        self.newroot.appendChild(self.repositories)

        self.modules = self.impl.createElement("modules")
        self.newroot.appendChild(self.modules)
        
        self.projects = self.impl.createElement("projects")
        self.newroot.appendChild(self.projects)
    
    def _parse_maven_projects(self):
        """Looks for <project type="maven"> and converts those."""
        
        projects = self.projects.getElementsByTagName("project")
        for project in projects:
            if not project.getAttribute("type") == "maven":
                continue
            
            self._parse_maven_project(project)
    
    def _parse_maven_project(self, project):
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
        pass #TODO
    
    def _normalize_repositories(self):
        repos = self._get_list_merged_by_name("repository")
        exclude = ["project", "module", "repository"];
        for repo in repos:
            clone = repo.clone(True)
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
            
            clone = module.clone(True)
            self._clean_out_by_tag( clone, exclude )
            reporef = self.newdoc.createElement("repository")
            reporef.setAttribute("name", repository.getAttribute("name") )
            module.appendChild(reporef)
            
            self.modules.appendChild(module)

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
            module = self._find_module_for_project(module)
            if not module:
                name = project.getAttribute("name")
                self.log.warn("Dropping project '%s' because no corresponding module could be found!" % name)
                continue
            
            clone = project.clone(True)
            self._clean_out_by_tag( clone, exclude )
            moduleref = self.newdoc.createElement("module")
            moduleref.setAttribute("name", module.getAttribute("name") )
            project.appendChild(moduleref)
            
            self.projects.appendChild(project)
    
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
        for project in self.projects:
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
                new_dependency = dependency.clone(True)
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
        for dependency in dependencies:
            ids = dependency.getAttribute("name")
            if not ids: continue
            if ids.find(",") == -1: continue
            
            project.removeChild(dependency)
            list = ids.split(",")
            for id in list:
                new_dependency = dependency.clone(True)
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
                clone = elem.clone(True)
                newlist[name] = clone
        
        return newlist.values


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
        
        self.root = domtree.documentElement

        self._find_repository_definitions()
        self._find_module_definitions()
        self._find_project_definitions()
        
        self._create_workspace()
        self._create_repositories()
        self._create_modules()
        self._create_projects()

        workspace = self.workspace
        self.workspace = None
        self.root = None
        return workspace
    
    def _create_workspace(self):
        self.workspace = Workspace(self.root.getAttribute('name'))
    
    ###
    ### Searching
    ###
    def _find_repository_definitions(self):
        """Retrieves a list of <repository/> elements."""
        children = self.root.childNodes
        for child in children:
            if not child.nodeType == dom.Node.ELEMENT_NODE: continue
            if child.tagName == "repositories":
                self.repository_definitions = child.childNodes
                break

    def _find_module_definitions(self):
        """Retrieve a list of <module/> elements."""
        children = self.root.childNodes
        for child in children:
            if not child.nodeType == dom.Node.ELEMENT_NODE: continue
            if child.tagName == "modules":
                self.module_definitions = child.childNodes
                break

    def _find_project_definitions(self):
        """Retrieve a list of <project/> elements."""
        children = self.root.childNodes
        for child in children:
            if not child.nodeType == dom.Node.ELEMENT_NODE: continue
            if child.tagName == "projects":
                self.project_definitions = child.childNodes
                break

    ###
    ### Repository parsing
    ###
    def _create_repositories(self):
        """Creates all repositories and adds them to the workspace."""

        for repository_definition in self.repository_definitions:
            if not repository_definition.nodeType == dom.Node.ELEMENT_NODE: continue
            repository = self._create_repository(repository_definition)
            self.workspace.repositories[repository.name] = repository
    
    def _create_repository(self, repository_definition):
        name = repository_definition.getAttribute("name")
        self.log.debug("Converting repository definition '%s' into object form." % name)
        
        # parse the attributes and elements common to all repositories
        title = None
        try: title = self._find_element_text(repository_definition, "title")
        except: pass
        
        home_page = None
        try: home_page = self._find_element_text(repository_definition, "home-page")
        except: pass
        
        cvsweb = None
        try: cvsweb = self._find_element_text(repository_definition, "cvsweb")
        except:
            try: cvsweb = self._find_element_text(repository_definition, "web")
            except: pass
        
        redistributable = False
        if repository_definition.getElementsByTagName("redistributable").length > 0:
            redistributable = True
            
        # now delegate to _create methods for specific repositories to do the rest
        repository = None
        type = repository_definition.getAttribute("type").upper()
        if type == "CVS":
            repository = self._create_cvs_repository(name, title, home_page, cvsweb, redistributable, repository_definition)
        elif type == "SVN":
            repository = self._create_svn_repository(name, title, home_page, cvsweb, redistributable, repository_definition)
        else:
            raise ModellerError, "Unknown repository type '%s' for repository '%s'" % (type, name)
        #TODO perforce support
        
        return repository
    
    def _create_cvs_repository(self, name, title, home_page, cvsweb, redistributable, repository_definition):
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
        
        repository = CvsRepository(self.workspace,
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

    def _create_svn_repository(self, name, title, home_page, cvsweb, redistributable, repository_definition):
        url = _find_element_text(repository_definition, "url")

        user = None
        try: user = _find_element_text(repository_definition, "user")
        except: pass

        password = None
        try: password = _find_element_text(repository_definition, "password")
        except: pass
        
        repository = SvnRepository(self.workspace,
                                   name,
                                   url,
                                   title = title,
                                   home_page = home_page,
                                   cvsweb = cvsweb,
                                   redistributable = False,
                                   user = user,
                                   password = password)
        return repository
    
    ###
    ### Module parsing
    ###

    def _find_repository_for_module(self, module_definition):
        name = module_definition.getAttribute("name")
        repo_name = module_definition.getElementsByTagName("repository").item(0).getAttribute("name")
        repo = self.workspace.repositories[repo_name]
        return repo

    def _create_modules(self):
        for module_definition in self.module_definitions:
            if not module_definition.nodeType == dom.Node.ELEMENT_NODE: continue
            module = self._create_module(module_definition)
            module.repository.modules[module.name] = module
            self.workspace.modules[module.name] = module
        
    def _create_module(self, module_definition):
        name = module_definition.getAttribute("name")
        repository = self._find_repository_for_module(module_definition)
        
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
            module = self._create_cvs_module(repository, name, url, description, module_definition)
        elif isinstance(repository, SvnRepository):
            module = self._create_svn_module(repository, name, url, description, module_definition)
        else:
            raise ModellerError, "Unknown repository type '%s' referenced by module '%s'" % (repository.__class__,name)
        #TODO perforce support
        return module
    
    def _create_cvs_module(self, repository, name, url, description, module_definition):
        tag = module_definition.getAttribute("tag")
        return CvsModule(repository, name, tag, url, description)
    
    def _create_svn_module(self, repository, name, url, description, module_definition):
        path = module_definition.getAttribute("path")
        return SvnModule(repository, name, path, url, description)
    
    ###
    ### Project parsing
    ###
    
    def _find_module_for_project(self, project_definition):
        name = project_definition.getAttribute("name")
        module_name = project_definition.getElementsByTagName("module").item(0).getAttribute("name")
        module = self.workspace.modules[module_name]
        return module

    def _create_projects(self):
        for project_definition in self.project_definitions:
            if not project_definition.nodeType == dom.Node.ELEMENT_NODE: continue
            project = self._create_project(project_definition)
            project.module.projects[project.name] = project
            self.workspace.projects[project.name] = project

            self._create_commands(project,project_definition)
            self._create_outputs(project,project_definition)

        # wire up dependencies only after projects have been created
        for project_definition in self.project_definitions:
            if not project_definition.nodeType == dom.Node.ELEMENT_NODE: continue
            self._create_dependencies(project_definition)
        
    def _create_project(self, project_definition):
        name = project_definition.getAttribute("name")
        module = self._find_module_for_project(project_definition)
        
        project = Project(module, name)
        return project

    def _create_commands(self, project, project_definition):
        rmdirs = project_definition.getElementsByTagName("delete")
        for cmd in rmdirs:
            dir = cmd.getAttribute("dir")
            project.add_command(Rmdir(project, dir))
            
        mkdirs = project_definition.getElementsByTagName("mkdir")
        for cmd in mkdirs:
            dir = cmd.getAttribute("dir")
            project.add_command(Mkdir(project, dir))
        
        scripts = project_definition.getElementsByTagName("script")
        for cmd in scripts:
            name = cmd.getAttribute("name")
            args = []
            for arg in cmd.getElementsByTagName("arg"):
                name = arg.getAttribute("name")
                value = arg.getAttribute("value")
                args.append((name, value))
                
            project.add_command(Script(project, name, args))
        
        #TODO more commands
    
    def _create_outputs(self, project, project_definition):
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
    
    def _create_dependencies(self, project_definition):
        name = project_definition.getAttribute("name")
        project = self.workspace.projects[name]
            
        dependencies = project_definition.getElementsByTagName("depend")
        for dependency in dependencies:
            self._add_dependency(project, dependency)
    
    def _add_dependency(self, project, dependency):
        dependency_name = dependency.getAttribute("project")
        runtime = dependency.getAttribute("runtime") == "true"
        inherit = dependency.getAttribute("inherit")
        optional = dependency.getAttribute("optional") == "true"
        
        dependency_project = None
        try:
            dependency_project = self.workspace.projects[dependency_name]
        except KeyError:
            # we store the name instead. a Verifier should be used later to
            # fix this error.
            dependency_project = dependency_name
        
        id = dependency.getAttribute("id")
        project.add_dependency(Dependency(dependency_project,project,optional,runtime,inherit,id))


class Visitor:
    def __init__(self):
        # we keep a stack of the dependencies of a particular project,
        # adding an item as we traverse the graph. In the case of a cycle,
        # we track back through that stack to find it completely
        self.groups = []
        
        # we keep a flat list of all the projects we visit. IF we visit
        # a project twice, that indicates a cycle, since the topological
        # sort must have failed
        self.visited = []
        
        # when we find cycles, we store all the projects involved in this
        # array
        self.cycles = []
        
    def visit(self, project):
        if project in self.visited:
            self._find_cycle(project, [project], project)
        else:
            self.visited.append(project)
            self.groups.append(project.dependencies)
    
    def done(self, numberOfProjects):
        # check whether we visited all projects. If not,
        # the stack in the Verifier was empty before its
        # time, hence there were projects lying around
        # with dependencies that weren't satisfied, hence
        # we must have found a cycle!
        assert (numberOfProjects > self.visited) == \
               (len(self.cycles) > 0)
        
        if len(self.cycles) > 0:
            self._handle_cycles()
    
    def _find_cycle(self, project, cycle, first):
        group = self.groups.pop
        for dependency in group:
            if dependency.dependee == first:
                # that completes the cycle
                self.cycles.append(cycle)
                break
            if dependency.dependee == project:
                # this is the project that references us
                project_in_cycle = dependency.dependency
                cycle.append(project_in_cycle)
                self._handle_cycle(project_in_cycle, cycle, first)
    
    def _handle_cycles(self):
        pass # TODO: remove these projects and their dependendees

class Verifier:
    """Verifies an objectified gump workspace."""

    def verify(self, workspace):
        if True: return # TODO

        visitor = Visitor()
        self.topsortedTravesal(workspace, visitor)
    
    def topsortedTravesal(self, workspace, visitor):
        self._set_indegrees(workspace)
        # using a stack *should* ensure depth-first
        stack = self._get_initial_stack(workspace)

        while len(queue) > 0:
            project = stack.pop
            visitor.visit(project)
            
            for dependency in project.dependencies:
                dependency.dependency.indegree -= 1
                if dependency.dependency.indegrees == 0:
                    stack.append(dependency.dependency)
        
        visitor.done(len(workspace.projects))
        self._clear_indegrees(workspace)
    
    def _set_indegrees(projects):
        """Set the number of in-degrees for each project.
        
        The number of in-degrees is a measure of how many
        dependees a project has. The key bit is that the
        verifier decreases the number of in-degrees for each
        project as a dependency is handled.
        """
        for project in workspace.projects:
            project.indegree = 0
        
        for dependency in workspace.dependencies:
            dependency.dependency.indegree += 1
    
    def _clear_indegrees(projects):
        """Removes the in-degrees property from each project."""
        
        for project in workspace.proejcts:
            del project.indegree

    def _get_initial_stack(self, workspace):
        """Get the projects with an in-degree of 0.
        
        In other words, get the projects without dependees.
        """
        stack = []
        for project in workspace.projects:
            if project.indegree == 0:
                stack.append(project) 
        
        return stack