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

"""This module replaces '@@VARIABLE@@' properties in an XML DOM."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

from xml import dom
from xml.dom import minidom

class AtParser:
    def __init__(self, dictionary):
        self.dictionary = dictionary
        
    def parse(self, document):
        replace_at_properties(document.documentElement, self.dictionary)
        return document


def replace_at_properties(node, dictionary):
    if node.hasAttributes():
        attributes = node.attributes
        i = 0
        while i < attributes.length:
            attribute = attributes.item(i)
            i = i + 1
            if not attribute: continue
            attribute.nodeValue = _replace_at_properties_in_string(attribute.nodeValue, dictionary)
    
    if node.hasChildNodes():
        children = node.childNodes
        i = 0
        while i < children.length:
            child = children.item(i)
            i = i + 1
            if not child: continue
            if child.nodeType == dom.Node.TEXT_NODE:
                child.nodeValue = _replace_at_properties_in_string(child.nodeValue, dictionary)
                continue

            # recurse
            if child.nodeType == dom.Node.ELEMENT_NODE:
                replace_at_properties(child, dictionary)
                continue
            

def _replace_at_properties_in_string(string, dictionary):
    if not isinstance(string, basestring):
        return string
    
    newstring = string
    for k,v in dictionary.iteritems():
        searchstring = "@@%s@@" % k
        newstring = newstring.replace(searchstring,v)
    return newstring