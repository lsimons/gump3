#!/usr/bin/env python

# $Header: /home/cvspublic/jakarta-gump/python/gump/conf.py,v 1.7 2003/05/10 18:20:36 nicolaken Exp $
# $Revision: 1.7 $
# $Date: 2003/05/10 18:20:36 $
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

import logging
import types, StringIO

from xml.sax import parse
from xml.sax.handler import ContentHandler, ErrorHandler
from xml.sax.saxutils import escape

from gump.conf import default
from gump import log
from gump.utils import *

###############################################################################
# SAX Dispatcher mechanism
###############################################################################
   
class SAXDispatcher(ContentHandler,ErrorHandler):
  """a stack of active xml elements"""

  def __init__(self,file,name,cls):
    """Creates a DocRoot and parses the specified file into a GOM tree.

      The GOM tree is stored in the self.docElement attribute.
    """
    
    self.topOfStack=DocRoot(name,cls)
    self.elementStack=[self.topOfStack]
    parse(file,self)
    
    self.docElement=self.topOfStack.element

  def startElement (self, name, attrs):
    """See ContentHandler class."""
    if self.topOfStack: self.topOfStack=self.topOfStack.startElement(name,attrs)
    self.elementStack.append(self.topOfStack);

  def characters(self, string):
    """See ContentHandler class."""
    if self.topOfStack: self.topOfStack.characters(string)

  def endElement (self, name):
    """See ContentHandler class."""
    del self.elementStack[-1]
    self.topOfStack=self.elementStack[-1]
 
  def error(self, exception):
        log.error("Handle a recoverable error.")
        raise exception

  def fatalError(self, exception):
        log.error("Handle a non-recoverable error.")
        raise exception

  def warning(self, exception):
        log.warn("Handle a warning.")
        print exception

###############################################################################
# Base classes for the Gump object model
#
# This is actually where most of the logic and complexity is handled,
# allowing the actual model to be rather simple and compact. All
# elements of the GOM should extend GumpXMLObject or a subclass of GumpXMLObject.
###############################################################################
class GumpXMLObject(object):
  """Helper XML Object.

    Attributes become properties.  Characters become the string value
    of the element. An internal attribute with name '@text' is used
    for storing all the characters (as opposed to xml elements and xml
    attributes)."""

  def __init__(self,attrs):
    # Transfer attributes
    for (name,value) in attrs.items():
      self.__dict__[name]=value
    # setup internal character field
    if not '@text' in self.__dict__: self.init()
    self.__dict__['@text']=''
    
  def startElement(self, name, attrs):
    """See ContentHandler class."""
    try:
      # If we are dealing with a Single or Multiple,
      # return an instance.
      attr=self.__getattribute__(name)
      if isinstance(attr,Single): return attr(attrs)
      if isinstance(attr,Multiple): return attr(attrs)
      return attr # :TODO: Get this checked out
    except AttributeError:
      # shouldn't happen? - it actually is OK if people extend the GOM -- rubys
      log.debug("No handling attribute related to " +
                "name '%s'\r\n\tCurrent class is %s" % (name, self.__class__))

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
      raise "Incorrect element, expected %s, found %s" % (self.name,name)
    self.element=self.cls(attrs)
    return self.element


class Named(GumpXMLObject):
  """Named elements (e.g., project,module,repository).

    Supports href and maintains a list of elements. Duplicate
    names get merged. Classes declared of this type must declare
    a static list property."""

  def __new__(cls,attrs):
    """In case of a href reference, download and process that file."""
    href=attrs.get('href')
    if href:
      from gump import gumpCache
      newHref=gumpCache(href)
      if newHref:
        log.debug('opening: ' + newHref + '\n')
        try:
            element=SAXDispatcher(open(newHref),cls.__name__.lower(),cls).docElement        
        except Exception, detail:
            log.error('Failed to parse [' + newHref + ']. Details: ' + str(detail))   
            element=None 
      else:
        # :TODO: Set any object "invalid"?
        log.warn("href:"+newHref+" not loaded")
    else:
      name=attrs.get('name')
      try:
        element=cls.list[name]
      except:
        element=GumpXMLObject.__new__(cls,attrs)
      if name: cls.list[name]=element
    return element

class Single(object,GumpXMLObject):
  """Properties which are only ever expected to hold a single value."""

  def __init__(self,cls=GumpXMLObject):
    """The cls passed in determines what type the delegate instance will have."""
    self.delegate=None
    self.cls=cls

  def __call__(self,attrs):
    if self.delegate:
      self.delegate.__dict__.update(dict(attrs))
    else:
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
    return self.delegate

  def __setitem__(self,name,value):
    self.delegate[name]=value

  def __getitem__(self,name):
    if name in self.delegate.__dict__: return self.delegate.__dict__[name]

class Multiple(list,GumpXMLObject):
  """Properties which can hold multiple instances."""

  def __init__(self,cls=GumpXMLObject):
    """The cls passed in determines what type the delegate instances will have."""
    list.__init__(self)
    self.cls=cls

  def __call__(self,attrs):
    result=self.cls(attrs)
    self.append(result)
    return result

def xmlize(nodeName,object,f=None,indent='',delta='  '):

  if f==None: f=StringIO.StringIO()

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
      f.write( '%s<%s>%s</%s>\n' % (indent,' '.join(attrs).encode(encoding),
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
  if isinstance(f,StringIO.StringIO):
    f.seek(0)
    return f.read()
      
      
def xmlwrite(filename,tag,obj):
  f=open( filename, 'w')
  try:
    xmlize(tag,obj,f)
    print "Generated [" + filename + "] successfully."
  finally:
    # Since we may exit via an exception, close fp explicitly.
    f.close()
      

if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)
   
  
  
