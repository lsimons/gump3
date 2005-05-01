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
from gump.engine import EngineError
## more imports atthe bottom...

###
### Utility methods shared between classes
###
def _find_element_text(parent, element_name):
    """Retrieves the text contents of an element like <blah>text</blah>."""
    elem = parent.getElementsByTagName(element_name).item(0).firstChild
    if elem:
        return elem.data
    else:
        return ""


def _do_drop(to_remove, dropped_nodes=None):
    """Remove node from its parent and add to dropped_nodes list."""
    
    node_to_remove_element_from = to_remove.parentNode
    node_to_remove_element_from.removeChild(to_remove)
    
    if dropped_nodes != None:
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
        if not parent: # this indicates a bug in the DOM implementation as
                       # its illegal
            raise EngineError, "Cannot find document containing this node!"
    
    return parent


def _find_project_containing_node(node):
    """Walk up the DOM hierarchy to locate a <project> Element."""
    return _find_ancestor_by_tag(node, "project")


def _find_module_containing_node(node):
    """Walk up the DOM hierarchy to locate a <module> Element."""
    return _find_ancestor_by_tag(node, "module")


def _find_repository_containing_node(node):
    """Walk up the DOM hierarchy to locate a <repository> Element."""
    return _find_ancestor_by_tag(node, "repository")


def _import_node(target_node, new_node):
    """Combines two DOM trees together.

    The second argument is merged into the first argument, which is then
    returned.
    """
    _import_attributes(target_node, new_node)
    _import_children(target_node, new_node)

    
def _import_attributes(target_node, new_node):
    """Copy all attributes from the new node to the target node."""
    new_attributes = new_node.attributes
    if new_attributes:
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
    """Filter for use with _import_children().

    This filter can be configured to filter out certain
    elements based on the element name."""
    def __init__(self, excludedTags):
        """Create a new instance. The excludeTags argument
        should be an array of strings specifying element
        names to exclude."""
        self.excludedTags = excludedTags

    def exclude(self, node):
        if not node.nodeType == dom.Node.ELEMENT_NODE:
            return False
        if node.tagName in self.excludedTags:
            return True
        
        return False

##
## These at bottom to closely mimick old format of this file where they were
## defined right here
##
#TODO remove these
#from gump.engine.loader import Loader
#from gump.engine.normalizer import Normalizer
#from gump.engine.objectifier import Objectifier
#from gump.engine.verifier import Verifier
