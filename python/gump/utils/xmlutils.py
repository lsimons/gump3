#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/utils/Attic/xmlutils.py,v 1.5 2003/12/15 19:36:52 ajack Exp $
# $Revision: 1.5 $
# $Date: 2003/12/15 19:36:52 $
#
# ====================================================================
#
# The Apache Software License, Version 1.1
#
# Copyright (c) 2003 The Apache Software Foundation.  All rights
# reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. The end-user documentation included with the redistribution, if
#    any, must include the following acknowlegement:
#       "This product includes software developed by the
#        Apache Software Foundation (http://www.apache.org/)."
#    Alternately, this acknowlegement may appear in the software itself,
#    if and wherever such third-party acknowlegements normally appear.
#
# 4. The names "The Jakarta Project", "Alexandria", and "Apache Software
#    Foundation" must not be used to endorse or promote products derived
#    from this software without prior written permission. For written
#    permission, please contact apache@apache.org.
#
# 5. Products derived from this software may not be called "Apache"
#    nor may "Apache" appear in their names without prior written
#    permission of the Apache Group.
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
# ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# ====================================================================
#
# This software consists of voluntary contributions made by many
# individuals on behalf of the Apache Software Foundation.  For more
# information on the Apache Software Foundation, please see
# <http://www.apache.org/>.

"""
    Simple Object to/from XML Utilities (for Gump)
"""

import os.path
import logging
import types, StringIO

from xml.sax import parse
from xml.sax.handler import ContentHandler, ErrorHandler
from xml.sax.saxutils import escape

from gump import log
from gump.utils.http import cacheHTTP
from gump.utils.note import *
from gump.config import gumpPath

###############################################################################
# SAX Dispatcher mechanism
###############################################################################
   
class SAXDispatcher(ContentHandler,ErrorHandler,Annotatable):
  """a stack of active xml elements"""

  def __init__(self,file,name,cls,basedir=None):
      
    Annotatable.__init__(self)
    
    """    
        Creates a DocRoot and parses the specified file into a GOM tree.

        The GOM tree is stored in the self.docElement attribute.
    """
    
    if not basedir:
        self.basedir=os.path.dirname(file)
    else:
        self.basedir=basedir

    log.debug('Parse XML File: ' + str(file) + ' with basedir of ' + str(self.basedir))
    
    self.topOfStack=DocRoot(name,cls)
    self.elementStack=[self.topOfStack]
    parse(file,self)
    
    self.docElement=self.topOfStack.element

  def startElement (self, name, attrs):
    """See ContentHandler class."""
    if self.topOfStack:     
        # Hack to pass thss context about..
        attributes=dict(attrs)
        attributes['@basedir']=self.basedir
        
        # The newly loaded object moves to top of stack
        extractedObject=self.topOfStack.startElement(name,attributes)
        if not isinstance(extractedObject,Annotation):
            self.topOfStack=extractedObject
        else:
            # Nasty hack to try to return/annotate errors
            if self.topOfStack and isinstance(self.topOfStack,Annotatable):  
                self.topOfStack.addAnnotationObject(extractedObject)
                self.topOfStack.dump()
        
    self.elementStack.append(self.topOfStack)

  def characters(self, string):
    """See ContentHandler class."""
    if self.topOfStack: self.topOfStack.characters(string)

  def endElement (self, name):
    """See ContentHandler class."""
    del self.elementStack[-1]
    self.topOfStack=self.elementStack[-1]
 
  def error(self, exception):
    self.addError('XML error : ' + str(exception))
    log.error("Handle a recoverable error." + str(exception), exc_info=1)
    raise exception
    
  def fatalError(self, exception):
    self.addError('XML error : ' + str(exception))
    log.error("Handle a non-recoverable error." + str(exception), exc_info=1)
    raise exception

  def warning(self, exception):
    self.addWarning('XML warning' + str(exception))
    log.warn("Handle a warning." + str(exception), exc_info=1)
    
###############################################################################
# Base classes for the Gump object model
#
# This is actually where most of the logic and complexity is handled,
# allowing the actual model to be rather simple and compact. All
# elements of the GOM should extend GumpXMLObject or a subclass of GumpXMLObject.
###############################################################################
class GumpXMLObject(Annotatable,object):
  """Helper XML Object.

    Attributes become properties.  Characters become the string value
    of the element. An internal attribute with name '@text' is used
    for storing all the characters (as opposed to xml elements and xml
    attributes)."""

  def __init__(self,attrs):
      
    Annotatable.__init__(self)    
    
    # Transfer attributes
    for (name,value) in attrs.items():
        if not name == '@basedir' and not name=='annotations':
            self.__dict__[name]=value
    # Setup internal character field
    if not '@text' in self.__dict__: self.init()
    self.__dict__['@text']=''
    
  def __len__(self):
      return len(self.__dict__)
      
  def __nonzero__(self):
      return (len(self) > 0)
    
  def getTagName(self):
      return self.__class__.__name__.lower().replace('xml','')
 
  def startElement(self, name, attrs):
    """ Handles XML events via a series of delegations based upon
        the tag, and the 'metadata' (typed member data) on this
        object (i.e. the sub-class additions)        
    
        See ContentHandler class."""
    try:
      # If we are dealing with a Single or Multiple,
      # return an instance.
      attr=self.__getattribute__(name)
      
      # These are delegated to objects
      if isinstance(attr,Single): return attr(attrs)
      if isinstance(attr,Multiple): return attr(attrs)
      
      # Simple attributes
      
      return attr # :TODO: Get this checked out
    except AttributeError:
      # It is OK if people extend the GOM...
      log.debug("No metadata related to " +
                "name '%s' on %s" % \
                (name, self.__class__.__name__))

  #
  # Process characters...
  #
  def characters(self,string):
    """See ContentHandler class."""
    self.__dict__['@text']+=string

  def __setitem__(self,name,value):
    self.__dict__[name]=value

  def __getitem__(self,name):
    if name in self.__dict__: return self.__dict__[name]

  def __delitem__(self,name):
    del self.__dict__[name]

  def __getattr__(self,name):
    pass

  def __str__(self):
    """String representation of the element is the element content."""
    return self.__dict__['@text'].strip()

  def init(self):
    pass
 
class DocRoot(GumpXMLObject):
  """Document roots are workspaces or targets of hrefs."""

  def __init__(self,name,cls):
    GumpXMLObject.__init__(self,{})
    self.name=name
    self.cls=cls
    self.element=None

  def startElement(self, name, attrs):
    if name<>self.name:
      raise RuntimeError, "Incorrect element, expected %s, found %s" % (self.name,name)
    self.element=self.cls(attrs)
    return self.element

class Named(GumpXMLObject):
  """Named elements (e.g., project,module,repository).

    Supports href and maintains a list of elements. Duplicate
    names get merged. Classes declared of this type must declare
    a static list property."""

  def __new__(cls,attrs):
    """ A Named element """   
     
    #
    # Note: The first time a named is imported it is probably
    # not 'named' but with an 'href' to the 'remote' metadata.
    #
    name=attrs.get('name')
    
    #   
    # A 'named' element can also be 'downloaded' via an href
    # to the full metadata, as such we have an interesting
    # 'bootstrap' that
    #      
    href=attrs.get('href')
    
    log.debug('New Named [' + cls.__name__ + '] name=[' + str(name) + '] href=[' + str(href) + ']')
    
    if href:
        log.debug('Download metadata from : [' + href + ']')    
    
        # Stored by caller...
        basedir=attrs.get('@basedir')      
        del attrs['@basedir']
        
        # Download (relative to base)
        if not href.startswith('http://'):
            newHref=gumpPath(href,basedir);
        else:
            newHref=cacheHTTP(href)
          
        if newHref:
            # Get a tag name from a classname
            tag =  cls.__name__.lower().replace('xml','')
                        
            try:
                parser=SAXDispatcher(newHref, \
                                  tag, cls,\
                                  basedir)
                                  
                element=parser.docElement     
                
                # Copy over any XML errors/warnings
                transferAnnotations(parser, element)  
                
            except Exception, detail:
                message='Failed to parse XML @ [' + newHref + ']. Details: ' + str(detail)
                log.error(message, exc_info=1)   
                element=Annotation(LEVEL_ERROR, message)
        else:
            # :TODO: Set any object "invalid"?
            log.warn("HREF: ["+href+"] not loaded", exc_info=1)
            element=Annotation(LEVEL_ERROR, message)
        
        #
        # Stash for general reference/interest
        #
        if element and not isinstance(element,Annotation):
            element.href=href                    
        
        # Return the downloaded element instead...
        return element        
    else:
    
        try:
          # We've this already?
          element=cls.map[name]
        except:
          # Create it first time...
          element=GumpXMLObject.__new__(cls,attrs)
      
        # Store in class map
        if name: 
            cls.map[name]=element
      
    return element
                
    # Same if same type, and same name
    # i.e project context X is not equals to module context X
  def __eq__(self,other):
    return self.__class__ == other.__class__ and self.name == other.name
        
  def __cmp__(self,other):
    return cmp(self.name,other.name)
         
  def __hash__(self):
    return hash(self.name)
            
  def __repr__(self):
    return str(self.__class__)+':'+self.name
        
  def __str__(self):
    return str(self.__class__)+':'+self.name
        
  def getName(self):
    return self.name
    
class Single(GumpXMLObject):
  """Properties which are only ever expected to hold a single value."""

  def __init__(self,cls=GumpXMLObject):
    GumpXMLObject.__init__(self,{})
    """The cls passed in determines what type the delegate instance will have."""
    self.delegate=None
    self.cls=cls

  def __call__(self,attrs):
    if self.delegate:
      # Update the attributes on the instance
      if attrs.get('@basedir'): del attrs['@basedir']
      self.delegate.__dict__.update(dict(attrs))
    else:
      # Construct and instance of this
      self.delegate=self.cls(attrs)
    return self.delegate

  def __getattr__(self,name):
    if self.delegate:
      try:
        return self.delegate.__getattribute__(name)
      except:
        return self.delegate[name]

  def __str__(self):
    if self.delegate: return self.delegate.__str__()
    return ''

  def __nonzero__(self):
    if self.delegate: 
        return self.delegate.__nonzero__()
    return 0

  def __setitem__(self,name,value):
    self.delegate[name]=value

  def __getitem__(self,name):
    if name in self.delegate.__dict__: return self.delegate.__dict__[name]

class Multiple(list,GumpXMLObject):
  """Properties which can hold multiple instances."""

  def __init__(self,cls=GumpXMLObject):
    """The cls passed in determines what type the delegate instances will have."""
    list.__init__(self)
    
    # Store the type of class we are a multiple of..
    self.cls=cls

  def __call__(self,attrs):
    # Construct a new instance
    object=self.cls(attrs)
    # Stash it into the list
    self.append(object)
    # Return it (to handle more XML events)
    return object

def xmlize(nodeName,object,f=None,indent='',delta='  '):

  if f==None: f=StringIO.StringIO()

  # :TODO: Do hack for when content is bad and a parse fails
  # so the XML loader has to set element=None
  if not object: return
      
  attrs=[nodeName]
  elements=[]
  text=''
  encoding='latin-1'

  # iterate over the object properties
  for name in object.__dict__:
    if name.startswith('__') and name.endswith('__'): continue
    var=getattr(object,name)

    # avoid nulls, metadata, and methods
    if not var: continue
    if isinstance(var,types.TypeType): continue
    if isinstance(var,types.MethodType): continue

    # determine if the property is text, attribute, or element
    if name=='@text':
      text=var
    elif isinstance(var,types.StringTypes):
      attrs.append('%s="%s"' % (name,escape(var)))
    else:
      elements.append((name,var))

  # format for display
  if not elements:
    # use compact form for elements without children
    if text.strip():
      f.write( '%s<%s>%s</%s>\n' % \
          (indent,' '.join(attrs).encode(encoding),	\
                text.strip().encode(encoding),nodeName))
    else:
      f.write( '%s<%s/>\n' % (indent,' '.join(attrs).encode(encoding)))
  else:
    # use full form for elements with children
    f.write( '%s<%s>\n' % (indent,' '.join(attrs).encode(encoding)))
    newindent=indent+delta
    for (name,var) in elements:
      if isinstance(var,list):
        # multiple valued elements
        for e in var: xmlize(name,e,f,newindent,delta)
      elif isinstance(var,Single):
        # single valued elements
        xmlize(name,var.delegate,f,newindent,delta)
    f.write( '%s</%s>\n' % (indent,nodeName.encode(encoding)))

  # if the file is a StringIO buffer, return the contents
  # as a stream (cool feature, especially for testing)
  if isinstance(f,StringIO.StringIO):
    f.seek(0)
    return f.read()      
      
#
# Serialize an object to XML (to a stream/file)
#      
def xmlwrite(filename,tag,obj):
  f=open( filename, 'w')
  try:
    xmlize(tag,obj,f)
    # print "Generated [" + filename + "] successfully."
  finally:
    # Since we may exit via an exception, close fp explicitly.
    f.close()