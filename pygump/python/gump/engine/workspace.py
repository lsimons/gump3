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

import logging
import os

from xml import dom
from xml.dom import minidom

from gump.model import Workspace # TODO

class WorkspaceError(Exception):
    pass

class WorkspaceLoader:
    """
    Parses XML, resolves HREFs, creates a big DOM tree.
    """
    def __init__(self,vfs,log,workspace):
        self.log = log
        self.vfs = vfs

    def get_workspace_tree(self,workspace):
        """
        Parse the workspace, then resolve all hrefs.
        
        Returns a tuple with the parsed dom and the nodes that were dropped
        because of problems.
        """
        dom = minidom.parse(workspace)
        dom.normalize()
        
        dropped_nodes = []
        self._resolve_hrefs_in_workspace(dom, dropped_nodes)
        
        return (dom, dropped_nodes)
    
    def _resolve_hrefs_in_workspace(self, dom, dropped_nodes):
        self._resolve_hrefs_in_children(self, dom, dropped_nodes)
    
    def _resolve_hrefs_in_children(self, node, dropped_nodes):
        """
        Recursively resolve all hrefs in all the children for a DOM node.
        
        The resolution is done in a resolve-then-recurse manner, so the end
        result is a dom tree without hrefs.
        """
        for child in node.documentElement.childNodes:
            # retrieve the referenced document and merge it in
            if child.nodeType == node.Node.ELEMENT_NODE:
                if child.hasAttribute('href'):
                    if not 'url' == child.tagName: # make exception for the <url/> tag, which
                                                   # documents an url for a project
                        self._resolve_href(child, dropped_nodes)

                # now recurse to resolve any hrefs within this child
                self._resolve_hrefs_in_children(child, dropped_nodes)
        
        return node
    
    def _resolve_href(self, node, dropped_nodes):
        """
        Resolve a href for the current node by merging the referenced xml
        document with the provided node. The href attribute on the provided
        node will be removed. The modified node is then returned.
        """
        href = node.getAttribute('href')
        try:
            stream = self.vfs.get_as_stream(href) #TODO
        except Exception, details:
            self.log.exception("VFS error while merging in a node!")
            self._drop_module_or_project(node, dropped_nodes)
            
        new_node = minidom.parse(stream)
        new_node.normalize()
        stream.close()
        
        node.removeAttribute('href')
        return self._merge_nodes(node, new_node)
    
    def _merge_nodes(self, target_node, new_node):
        """
        Combines two DOM trees together. The second argument is merged into
        the first argument, which is then returned.
        """
        
        # copy attributes from the new node to the target node
        new_attributes = new_node.attributes
        length = new_attributes.length
        i = 0
        while i < length:
            attribute = new_attributes.item(i)
            target_node.setAttributeNode(attribute)
        
        # copy elements from the new node to the target node
        new_elements = new_node.childNodes
        for child in new_elements:
            target_node.appendChild( child )
        
        return target_node
    
    def _drop_module_or_project(self, node, dropped_nodes):
        """
        Finds the project associated with this node and removes it from the dom tree.
        If there is no associated project, the associated module is removed instead. If
        there is no module either, an exception is raised.
        """
        
        # find the offending project or module
        parent = None
        if node.tagName == "project" or node.tagName == "module":
            parent = node # remove ourself
        else:
            parent = node.parentNode
            while parent and not node.tagName == "project":
                parent = parent.parentNode
            
            if not parent: # no <project/>, look for <module/>
                parent = node.parentNode
                while parent and not node.tagName == "module":
                    parent = parent.parentNode

        if not parent:
            # TODO provide more info
            raise WorkspaceError, "Unresolvable HREF found outside a <project/> or <module/>."
        
        # remove that project or module from its parent
        node_to_remove_element_from = parent.parentNode
        if not node_to_remove_element_from:
            # TODO provide more info
            raise WorkspaceError, "Rogue <project/> or <module/> (without a parent)."
        node_to_remove_element_from.removeChild(parent)
        
        # but save it off for error reporting
        dropped_nodes.append(parent)

class WorkspaceObjectifier:
    """
    Turns DOM workspace into Pythonified workspace.
    """
    def get_workspace(self, config, dom):
        workspace = self._create_workspace(dom, config)
        workspace.profile = self._create_profile(dom)
        
        raise RuntimeError, "not implemented!" # TODO
    
    def _create_workspace(self, dom):
        workspace = Workspace()