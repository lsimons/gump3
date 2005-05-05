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

"""This module reads gump xml metadata."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import logging
import os

from xml import dom
from xml.dom import minidom

from gump.engine import EngineError
from gump.engine.modeller import _import_node
from gump.engine.modeller import _find_project_containing_node
from gump.engine.modeller import _find_document_containing_node
from gump.engine.modeller import _find_module_containing_node
from gump.engine.modeller import _do_drop

###
### Helper methods
###
def _resolve_hrefs_in_children(element, dropped_nodes, found_hrefs, download_func, error_func):
    """Recursively resolve all hrefs in all the children for a DOM node.
    
    The resolution is done in a resolve-then-recurse manner, so the end
    result is a dom tree without hrefs. Note that this method expects to
    be passed in a dom Element or something else which actually has children;
    passing in an Attr for example makes no sense and results in problems.
    
    The dropped_nodes argument should be a list that will be populated with
    nodes for which href resolution fails.
    
    The found_hrefs argument should be a list that will be populated with all
    the hrefs that have been resolved by the method that resolved hrefs for
    the parent. An error will be thrown when recursion is detected.
    """
    for child in element.childNodes:
        # only resolve hrefs for elements
        if not child.nodeType == dom.Node.ELEMENT_NODE: continue
        # there's a <url href=""/> element which is descriptive and should
        # not be resolved
        if child.tagName == 'url': continue
        if child.hasAttribute('href'):
            # yep, this is one to load...
            _resolve_href(child, dropped_nodes, found_hrefs, download_func, error_func)

        # now recurse to resolve any hrefs within this child
        # note that we duplicate the found_hrefs array. This means that the
        # same file can be imported multiple times, as long as it is imported
        # by siblings, rather than as part of some parent<->child relation.
        _resolve_hrefs_in_children(child, dropped_nodes, found_hrefs[:], download_func, error_func)

def _resolve_href(node, dropped_nodes, found_hrefs, download_func, error_func):
    """Resolve a href for the provided node.

    We merge in the referenced xml document into the provided node.
    The href attribute on the provided node will be removed if the merge
    succeeds. If the merge fails the provided node will be removed from
    its parent and appended to the dropped_nodes list.
    """
    href = node.getAttribute('href')
    if href in found_hrefs:
        raise EngineError, \
              """Recursive inclusion because files refer to each other. This href leads to
              a cycle: %s.""" % href
    found_hrefs.append(href)
    
    try:
        stream = download_func(href)
    except Exception, details:
        # swallow this in interest of log readability
        #_drop_module_or_project(node, dropped_nodes)
        error_func(href, node, dropped_nodes)
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

###
### Classes
###
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
    def __init__(self, log, vfs=None):
        """
        Create a new Loader.

        Arguments:
            
            - log -- the log to write debug and error messages to.
            - vfs -- the virtual file system to use for resolving hrefs. May
                     be None only if the workspace to load does not contain
                     any hrefs.
        """
        assert hasattr(log, "warning")
        assert callable(log.warning)
        if vfs:
            assert hasattr(vfs, "get_as_stream")
            assert callable(vfs.get_as_stream)
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
        _resolve_hrefs_in_children(ws, dropped_nodes, [], self.get_as_stream, self.handle_error)
        
        # the combined results
        return (wsdom, dropped_nodes)
    
    # callback interface for _resolve_hrefs_in_workspace
    def get_as_stream(self, href):
        self.log.debug( "Resolving HREF: %s" % href )
        return self.vfs.get_as_stream(href)

    def handle_error(self, href, node, dropped_nodes):
        """Finds the project associated with this node and removes it.
        
        If there is no associated project, the associated module is removed
        instead. If there is no module either, an exception is raised.
        """
        
        project = _find_project_containing_node(node)
        if project:
            doc = _find_document_containing_node(project)
            modulename = "Uknown"
            module = _find_module_containing_node(project)
            if module:
                modulename = module.getAttribute("name")
                comment = doc.createComment(" Part of module: %s " % modulename)
                project.appendChild(comment)
            name = project.getAttribute("name")
            self.log.warning("Dropping project '%s' from module '%s' because of href (%s) resolution error!" % (name , modulename, href))
    
            _do_drop(project, dropped_nodes)
        else:
            module = _find_module_containing_node(node)
            if module:
                doc = _find_document_containing_node(module)
                name = module.getAttribute("name")
                self.log.warning("Dropping module '%s' because of href resolution error!" % name)
    
                _do_drop(project, dropped_nodes)
            else:
                raise EngineError, \
                      "Problematic node has no parent <project/> or " + \
                      "<module/>, unable to recover! Node:\n%s" \
                      % node.toprettyxml()
