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
    def __init__(self, log, vfs=None, mergefile=None, dropfile=None):
        """
        Create a new Loader.

        Arguments:
            
            - log -- the log to write debug and error messages to.
            - vfs -- the virtual file system to use for resolving hrefs. May
                     be None only if the workspace to load does not contain
                     any hrefs.
            - mergefile -- the full path to the file to write the merged
                           workspace xml to. If None, no such file will be
                           written.
            - dropfile -- the full path to the file to write the xml
                           describing dropped projects to. If None, no such
                           file will be written.
        """
        self.log = log
        self.vfs = vfs
        self.mergefile = mergefile
        self.dropfile = dropfile

    def get_workspace_tree(self, workspace):
        """Parse the provided workspace, then resolve all hrefs.
        
        Returns a tuple with the parsed workspace as a dom Element, and all
        the Nodes that were dropped because of problems as a list.
        
        The provided workspace argument can either be a stream or a path to
        a file.
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
        
        # write the merged xml tree to a file
        self._write_merge_files(wsdom, dropped_nodes)
        
        # the combined results
        return (ws, dropped_nodes)
    
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
        
        # we succeeded loading the new document, get rid of the href
        node.removeAttribute('href')
        
        self._import_node(node, new_root)
        
        # we're done with the file now, allow GC
        new_root.unlink()
    
    def _import_node(self, target_node, new_node):
        """Combines two DOM trees together.

        The second argument is merged into the first argument, which is then
        returned.
        """
        self._import_attributes(target_node, new_node)
        self._import_children(target_node, new_node)
    
    def _import_attributes(self, target_node, new_node):
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
    
    def _import_children(self, target_node, new_node):
        """Copy all children from the new node to the target node."""
        new_elements = new_node.childNodes
        if new_elements and new_elements.length > 0:
            for child in new_elements:
                clone = child.cloneNode(True)
                target_node.appendChild( clone )
    
    def _drop_module_or_project(self, node, dropped_nodes):
        """Finds the project associated with this node and removes it.
        
        If there is no associated project, the associated module is removed
        instead. If there is no module either, an exception is raised.
        """
        
        project = self._find_project_containing_node(node)
        if project:
            doc = self._find_document_containing_node(project)
            module = self._find_module_containing_node(project)
            modulename = module.getAttribute("name")
            comment = doc.createComment(" Part of module: %s " % modulename)
            project.appendChild(comment)
            name = project.getAttribute("name")
            self.log.warning("Dropping project '%s' from module '%s' because of href resolution error!" % (name , modulename))

            self._do_drop(project, dropped_nodes)
        else:
            module = self._find_module_containing_node(node)
            if module:
                doc = self._find_document_containing_node(module)
                name = module.getAttribute("name")
                self.log.warning("Dropping module '%s' because of href resolution error!" % name)

                self._do_drop(project, dropped_nodes)
            else:
                raise ModellerError, \
                      "Problematic node has no parent <project/> or " + \
                      "<module/>, unable to recover! Node:\n%s" \
                      % node.toprettyxml()
    
    def _do_drop(self, to_remove, dropped_nodes):
        """Remove node from its parent and add to dropped_nodes list."""
        
        node_to_remove_element_from = to_remove.parentNode
        node_to_remove_element_from.removeChild(to_remove)
        dropped_nodes.append(to_remove)
    
    def _find_document_containing_node(self, node):
        """Walk up the DOM hierarchy to locate a Document node."""
        parent = node
        while not parent.nodeType == dom.Node.DOCUMENT_NODE:
            parent = parent.parentNode
            if not parent: # really ought not happen I think...
                raise ModellerError, "Cannot find document containing this node!"
        
        return parent
    
    def _find_project_containing_node(self, node):
        """Walk up the DOM hierarchy to locate a <project> Element."""
        
        parent = node
        while parent.nodeType == dom.Node.ELEMENT_NODE:
            if parent.tagName == "project":
                return parent
            parent = parent.parentNode
            if not parent:
                return None
    
    def _find_module_containing_node(self, node):
        """Walk up the DOM hierarchy to locate a <module> Element."""
        parent = node
        while parent.nodeType == dom.Node.ELEMENT_NODE:
            if parent.tagName == "module":
                return parent
            parent = parent.parentNode
            if not parent:
                return None
    
    def _write_merge_files(self, wsdom, dropped_nodes):
        """Write the fully resolved DOM tree to a file.
        
        Also writes an XML file detailing any projects and modules that were
        dropped because of a HREF resolution issue.
        """
        if self.mergefile:
            merged = open(self.mergefile, 'w')
            merged.write( wsdom.toprettyxml() )
            merged.close()
        
        if self.dropfile and len(dropped_nodes) > 0:
            impl = dom.getDOMImplementation()
            dropdoc = impl.createDocument(None, "dropped-projects-and-modules", None)
            dropdocroot = dropdoc.documentElement
            for node in dropped_nodes:
                dropdocroot.appendChild(node)
            dropped = open(self.dropfile, 'w')
            dropped.write( dropdoc.toprettyxml() )
            dropped.close()        

class Objectifier:
    """Turns DOM workspace into Pythonified workspace."""
    
    def __init__(self, log):
        self.log = log

    def get_workspace(self, dom):
        raise RuntimeError, "not implemented!" # TODO

        workspace = self._create_workspace(dom)
        self._create_repositories(workspace, dom)
        self._create_modules(workspace, dom)
        self._create_projects(workspace, dom)
        
    
    def _create_workspace(self, root):
        workspace = Workspace(root.getAttribute('name'))
        
        
    def _create_repositories(self, workspace, root):
        repository_definitions = self._find_repository_definitions(root)
        
        undefined = []
        
        for repository_definition in repository_definitions:
            if not repository_definition.hasChildNodes(): # hope it gets defined later
                if not repository.getAttribute("name"):
                    raise ModellerError, "Encountered a repository without a name!"
                undefined.append(repository_definition)
                continue
            
            name = repository_definition.getAttribute("name")
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
                
            repository = None
            
            type = repository_definition.getAttribute("type").upper()
            if type == "CVS":
                repository = _create_cvs_repository(workspace, name, title, home_page, cvsweb, redistributable, repository_definition)
            elif type == "SVN":
                repository = _create_svn_repository(workspace, name, title, home_page, cvsweb, redistributable, repository_definition)
            else:
                raise ModellerError, "Unknown repository type '%s' for repository '%s'" % (type, name)

            workspace.repositories[name] = repository
        
        # TODO: add support for maven repository definitions here as found
        # inside maven project.xml files...
        
        # walk the undefined repository list to make sure they're all defined
        # now. If that's not the case, we'll complain about it right here.
        for repository_definition in undefined:
            name = repository_definition.getAttribute("name")
            if not workspace.repositories.has_key(name):
                # TODO: drop associated modules and projects instead
                raise ModellerError, "Repository '%s' is referenced but never defined!" % name
        
        undefined = None # clean up just to be sure...
    
    def _create_cvs_repository(self, workspace, name, title, home_page, cvsweb, redistributable, repository_definition):
        hostname = self._find_element_text(repository_definition, "hostname")
        path = self._find_element_text(repository_definition, "path")

        method = CVS_METHOD_PSERVER
        try: method = self._find_element_text(repository_definition, "method")
        except: pass
        
        user = None
        try: user = self._find_element_text(repository_definition, "user")
        except: pass

        password = None
        try: password = self._find_element_text(repository_definition, "password")
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

    def _find_repository_definitions(self, root):
        return root.getElementsByTagName("repository")

    def _find_element_text(self, parent, element_name):
        return parent.getElementsByTagName(element_name).item(0).firstChild.data
    
    def _create_modules(self, repositories, root):
        module_definitions = self._find_module_definitions(root)
        
        for module_definition in module_definitions:
            name = module_definition.getAttribute("name")
            repository = self._find_repository_for_module(repositories, module_definition)
            module = Module(repository)
            if repository:
                repository.modules[name] = module
    
    def _create_projects(self, modules, root):
        project_definitions = self._find_project_definitions(root)
        
        for project_definition in project_definitions:
            name = project_definition.getAttribute("name")
            module = self._find_module_for_project(modules, project_definition)
            project = Project(module)
            if module:
                module.projects[name] = project