#!/usr/bin/env python

# Copyright 2003-2004 The Apache Software Foundation
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

"""
    Simple Object to/from XML Utilities (for Gump)
"""

import xml.dom

from gump import log

###############################################################################
#
# DOM Utilities
#
###############################################################################


def transferInfo(element,target,mapping=None):
    set=0
    
    # Attributes
    if element.hasAttributes():  
        attrs=element.attributes
        for attrIndex in range(attrs.length):
            attr=attrs.item(attrIndex)
            name=attr.name
            value=attr.value        
            if name and value:
                set+=transferNameValue(target,name,value,mapping)
                
    # Child Nodes...
    if element.hasChildNodes():
        for node in element.childNodes:
            name=None
            value=None
                            
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                value=node.nodeValue
                name=node.tagName

            if name and value:
                set+=transferNameValue(target,name,value,mapping)
            
def transferNameValue(target,name,value,mapping=None):
        
    set=0
    
    # See what attribute we'd like to set with this
    attrName=name
    if mapping and mapping.has_key(attrName): attrName=mapping[tag]
        
    # We have somewhere to put this value... 
    if hasattr(target,attrName):
        # Determine the type
        attrType=type(getattr(target,attrName))
            
        if attrType is bool:
            if 'true' == value:
                value=True
            else:
                value=False
        elif attrType is int:
            value=int(value)            
        elif attrType is str or attrType is unicode:
            pass
        else:
            log.warn('Unknown Type %s for Attribute %s' % (attrType, attrName))
            
        print 'Transfer ', attrName, ' -> ', value, ' [', attrType, ']'
        setattr(target,attrName,value)
        set+=1
            
    return set

def hasChild(element,name):
    if element.hasChildNodes():
        for node in element.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == name: return True
    return False

def getChild(element,name):
    if element.hasChildNodes():
        for node in element.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == name: return node

def getChildren(element,name):
    children=[]
    if element.hasChildNodes():
        for node in element.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == name:  
                    children.append(node)
    return children
    
def dumpDom(dom):
    print dom.toprettyxml()
    
def hasAttribute(element,name):
    if element.hasAttributes():
        if element.getAttribute(name): return True
    return False
    
def getValue(element,name,default=None):  
    if hasAttribute(element,name):
        value=element.getAttribute(name) or default
    else:  
        value=''
        for childNode in element.childNodes:    
            if node.nodeType == xml.dom.Node.TEXT_NODE:
                value+=node.nodeValue
    return value
    

    
#    
#def getAttrValue(node,attrName):
#    """
#        Get a value from a node...
#        
#    """
#    if node.nodeType == xml.dom.Node.ELEMENT_NODE:
#        value=node.getAttribute(attrName)
#        
#    return value
#        
#    
#def getValue(node)
#    """
#        Get a value from a node...
#        
#    """
#    
#    value=None
#    
#    if node.nodeType == xml.dom.Node.ELEMENT_NODE:
#        value=node.nodeValue
#    elif node.nodeType == xml.dom.Node.COMMENT_NODE:
#        pass # log.debug("Skip Comment: " + `node.nodeType`) 
#    elif node.nodeType == xml.dom.Node.ATTRIBUTE_NODE:
#        value=
#            elif node.nodeType == xml.dom.Node.TEXT_NODE:
#                pass # log.debug("Skip Text: " + `node.nodeType`)          
#            else:
#                log.debug("Skip Node: " + `node.nodeType` + ' ' + `node`)                       
#    