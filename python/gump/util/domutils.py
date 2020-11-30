#!/usr/bin/env python

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
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
class AbstractChildNodeIterator:
    """ Iterate over a some nodes """
    def __init__(self,element):
        self.element=element
        
    def __iter__(self):
        return self
        
class NamedChildElementNodeIterator(AbstractChildNodeIterator):
    """ Iterator over named child nodes """
    def __init__(self,element,name):
        AbstractChildNodeIterator.__init__(self,element)
        self.name=name
        self.iter=iter(element.childNodes)
        
    def __next__(self):
        nextNode=next(self.iter)
        while nextNode:
            # Skip all but elements
            if nextNode.nodeType == xml.dom.Node.ELEMENT_NODE:
                # Skip if not names as we want
                if self.name==nextNode.tagName:
                    return nextNode
            nextNode=next(self.iter)
            
        # Ought never get here, either return the node
        # or StopIterator ought be thrown

def transferDomInfo(element,target,mapping=None):
    set=0
    
    # Attributes
    if element.hasAttributes():  
        attrs=element.attributes
        for attrIndex in range(attrs.length):
            attr=attrs.item(attrIndex)
            name=attr.name
            value=attr.value        
            if name and value:
                set+=transferDomNameValue(target,name,value,mapping)
                
    # Child Nodes...
    if element.hasChildNodes():
        for node in element.childNodes:
            name=None
            value=None
                            
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                value=node.nodeValue
                name=node.tagName

            if name and value:
                set+=transferDomNameValue(target,name,value,mapping)
            
def transferDomNameValue(target,name,value,mapping=None):
        
    set=0
    
    # See what attribute we'd like to set with this
    attrName=name
    if mapping and name in mapping: attrName=mapping[name]
        
    # We have somewhere to put this value... 
    if hasattr(target,attrName):
        # Determine the type
        attrType=type(getattr(target,attrName))
        
        try: 
            if attrType is bool:
                if 'true' == value:
                    value=True
                else:
                    value=False
            elif attrType is int:
                value=int(value)            
            elif attrType is str or attrType is str:
                pass
            else:
                log.warn('Unknown Type %s for Attribute %s [on %s]' % (attrType, attrName, target))
                
            
            #print 'Transfer ', attrName, ' -> ', value, ' [', attrType, ']'
            setattr(target,attrName,value)
            set+=1
        except:
            log.warn('Error with Type %s for Attribute %s [on %s]' % (attrType, attrName, target))
            raise
            
    return set

def transferDomAttributes(sourceElement,targetElement):   
    if sourceElement.hasAttributes():  
        attrs=sourceElement.attributes    
        for attrIndex in range(attrs.length):
            attr=attrs.item(attrIndex)
            targetElement.setAttribute(attr.name,attr.value)     
            
def hasDomChild(element,name):
    if element.hasChildNodes():
        for node in element.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == name: return True
    return False

def getDomChild(element,name):
    if element.hasChildNodes():
        for node in element.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == name: return node

def getDomTextValue(element,default=None): 
    value=''
    for childNode in element.childNodes:    
        if childNode.nodeType == xml.dom.Node.TEXT_NODE:
            value+=childNode.nodeValue
    if value: 
        value=value.strip()
    return value or default
    
def getDomChildren(element,name):
    children=[]
    if element.hasChildNodes():
        for node in element.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == name:  
                    children.append(node)
    return children
    
def getDomChildIterator(element,name):
    return NamedChildElementNodeIterator(element,name)
    
def dumpDom(dom):
    print((dom.toprettyxml()))
    
def hasDomAttribute(element,name):
    if element.hasAttributes():
        return element.hasAttribute(name)
    return False
    
def domAttributeIsTrue(element,name):
    return hasDomAttribute(element,name) and \
               getDomAttributeValue(element,name) in ['true','True']
     

def getDomAttributeValue(element,name,default=None):
    return element.getAttribute(name) or default
    
def getDomChildValue(element,name,default=None):
    value=''
    for childNode in element.childNodes:    
        if childNode.nodeType == xml.dom.Node.ELEMENT_NODE:
            if childNode.tagName == name:
                text=getDomTextValue(childNode)
                if text: value+=text
    if value: 
        value=value.strip()
    return value or default
    
def getDomValue(element,name,default=None):  
    if hasDomAttribute(element,name):
        value=getDomAttributeValue(element,name,default)
    else:  
        value=getDomChildValue(element,name,default)
        
    return value
    

def spliceDom(targetElement,source):
    # The DOM model
    if source.nodeType==xml.dom.Node.DOCUMENT_NODE:
        sourceElement=source.documentElement
    else:
        sourceElement=source    

    # Splice Attributes
    # (i.e. copy over any we don't already have) 
    if sourceElement.hasAttributes():
        attrs=sourceElement.attributes    
        for attrIndex in range(attrs.length):
            attr=attrs.item(attrIndex)
            if not targetElement.hasAttribute(attr.name):
                targetElement.setAttribute(attr.name,attr.value)    
                
    # Splice Children 
    # (i.e. deep clone and copy into target) 
    if sourceElement.hasChildNodes():
        for childNode in sourceElement.childNodes:  
            clonedNode=childNode.cloneNode(True)
            targetElement.appendChild(clonedNode) 
    
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
