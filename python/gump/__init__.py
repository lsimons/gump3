#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/__init__.py,v 1.6 2003/05/02 01:31:10 rubys Exp $
# $Revision: 1.6 $
# $Date: 2003/05/02 01:31:10 $
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
  Gump core functionality.

  It contains a sax dispatcher tool, a dependency
  walker, and an object model (GOM) which is built from an xmlfile using
  the sax dispatcher.

  The idea is that a subclass of GumpBase is used for each of the various
  xml tags which can appear in a gump profile, with a saxdispatcher
  generating a tree of GumpBase objects from the profile, dynamically
  merging as it finds href references.

  You can then use the dependencies() method to get an ordered, flat vector
  of the projects in the profile.

  Then there's some basic procedures to work with the GOM, like load().

  For basic usage patterns, look at the gump.view module or the gump.build
  module.
"""

import os.path
import os
import shutil
import string
import sys
import time
import urllib
import urlparse

# python-2.3 or http://www.red-dove.com/python_logging.html
import logging

from xml.sax import parse
from xml.sax.handler import ContentHandler

import gump.conf
from gump.conf import dir, default

###############################################################################
# Initialize
###############################################################################

# tell python what modules make up the gump package
__all__ = ["conf", "view", "build", "gen"]

# init logging
logging.basicConfig()

# base gump logger
log = logging.getLogger(__name__)

#set verbosity to show all messages of severity >= DEBUG
log.setLevel(default.logLevel)

# ensure dirs exists
conf.basicConfig()

###############################################################################
# SAX Dispatcher mechanism
###############################################################################

class SAXDispatcher(ContentHandler):
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

###############################################################################
# Base classes for the Gump object model
#
# This is actually where most of the logic and complexity is handled,
# allowing the actual model to be rather simple and compact. All
# elements of the GOM should extend GumpBase or a subclass of GumpBase.
###############################################################################

timestamp=os.path.join(dir.base,'.timestamp')
if os.path.exists(timestamp):
  mtime=time.localtime(os.path.getmtime(timestamp))
  default.date = time.strftime('%Y%m%d',mtime)

class GumpBase(object):
  """Base class for the entire Gump object model.

    Attributes become properties.  Characters become the string value
    of the element. An internal attribute with name '@text' is used
    for storing all the characters (as opposed to xml elements and xml
    attributes)."""

  def __init__(self,attrs):
    # parse out '@@DATE@@'
    for (name,value) in attrs.items():
      self.__dict__[name]=value.replace('@@DATE@@',default.date)

    # setup internal character field
    if not '@text' in self.__dict__: self.init()
    self.__dict__['@text']=''

  def startElement(self, name, attrs):
    try:
      # If we are dealing with a Single or Multiple,
      # return an instance.
      attr=self.__getattribute__(name)
      if isinstance(attr,Single): return attr(attrs)
      if isinstance(attr,Multiple): return attr(attrs)
    except AttributeError:
      # shouldn't happen? - it actually is OK if people extend the GOM -- rubys
      log.debug("Not handling attribute in GumpBase.startElement related to " +
                "name %s; current class is %s" % (name, self.__class__))

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

class DocRoot(GumpBase):
  """Document roots are workspaces or targets of hrefs."""

  def __init__(self,name,cls):
    GumpBase.__init__(self,{})
    self.name=name
    self.cls=cls
    self.element=None

  def startElement(self, name, attrs):
    if name<>self.name:
      raise "Incorrect element, expected %s, found %s" % (self.name,name)
    self.element=self.cls(attrs)
    return self.element

class Named(GumpBase):
  """Named elements (e.g., project,module,repository).

    Supports href and maintains a list of elements. Duplicate
    names get merged. Classes declared of this type must declare
    a static list property."""

  def __new__(cls,attrs):
    """In case of a href reference, download and process that file."""

    href=attrs.get('href')

    if href:
      newHref=gumpCache(href)
      log.debug('opening: ' + newHref + '\n')
      element=SAXDispatcher(open(newHref),cls.__name__.lower(),cls).docElement
    else:
      name=attrs.get('name')
      try:
        element=cls.list[name]
      except:
        element=GumpBase.__new__(cls,attrs)
      if name: cls.list[name]=element
    return element

class Single(object):
  """Properties which are only ever expected to hold a single value."""

  def __init__(self,cls=GumpBase):
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

class Multiple(list):
  """Properties which can hold multiple instances."""

  def __init__(self,cls=GumpBase):
    """The cls passed in determines what type the delegate instances will have."""

    list.__init__(self)
    self.cls=cls

  def __call__(self,attrs):
    result=self.cls(attrs)
    self.append(result)
    return result

###############################################################################
# Functions
###############################################################################

def gumpPath(path):
  """returns the path absolutized relative to the base gump dir"""

  return os.path.normpath(os.path.join(dir.base,path))

def gumpCache(href):
  """returns the path of the file in the href, cached if remote"""

  #if it's a local file get it locally
  if not href.startswith('http://'):
    newHref=gumpPath(href);
  else:
    log.debug('url: ' + href)
    if not os.path.exists(dir.cache):  os.mkdir(dir.cache)

    #the name of the cached descriptor
    quotedHref = urllib.quote_plus(href)
    #the path of the cached descriptor
    newHref = dir.cache+'/'+quotedHref

    #download the file if not present in the cache
    if os.path.exists(newHref):
      log.debug('using cached descriptor')
    else:
      log.debug('caching...')
      urllib.urlretrieve(href, newHref)
      log.debug('...done')

  return newHref

def load(file):
  """Run a file through a saxdispatcher.

    This builds a GOM in memory from the xml file. Return the generated GOM."""

  if not os.path.exists(file):
    log.error("""Workspace %s not found!

  You need to specify a valid workspace for Gump to run
  If you are new to Gump, simply copy minimal-workspace.xml
  to a file with the name of your computer (mycomputer.xml)
  and rerun this program.""" % file )

    raise IOError, 'workspace '+file+' not found'

  from gump.model import Workspace, Module, Project
  workspace=SAXDispatcher(file,'workspace',Workspace).docElement
  workspace.complete()

  for module in Module.list.values(): module.complete(workspace)
  for project in Project.list.values(): project.complete(workspace)
  return workspace

def buildSequence(todo):
  """Determine the build sequence for a given list of projects."""

  result=[]
  while todo:
    # one by one, remove the first ready project and append it to the result
    for project in todo:
      if project.isReady(todo):
        todo.remove(project)
        if project.ant or project.script: result.append(project)
        break
    else:
      # we have a circular dependency, remove all innocent victims
      while todo:
        for project in todo:
          if not project.isPrereq(todo):
            todo.remove(project)
            break
        else:
          loop=", ".join([project.name for project in todo])
          raise "circular dependency loop: " + str(loop)
  return result

###############################################################################
# Demonstration code
###############################################################################

if __name__=='__main__':
  from gump.core import *

  print
  print
  print "               *** starting DEMO ***"

  workspace=load(default.workspace)

  print
  print "workspace: "+default.workspace
  print
  print 'basedir:\t', workspace.basedir
  print 'pkgdir:\t\t', workspace.pkgdir
  for property in workspace.property: print 'Property:\t',property.name,property.value

  print
  print "*** JDBC ***"
  print
  jdbc=Project.list['jdbc']
  print 'Package:\t', jdbc.package
  for jar in jdbc.jar: print 'Jar:\t\t', jar.name, jar.id

  print
  print "*** Junit ***"
  print

  junit=Module.list['junit']
  print 'Description:\t', junit.description
  print 'Url:\t\t', junit.url.href
  print 'Cvs:\t\t', junit.cvs.repository

  junit=Project.list['junit']
  print 'Package:\t', junit.package[0]
  for depend in junit.depend: print 'Depend:\t\t',depend.project
  for jar in junit.jar: print 'Jar:\t\t', jar.name, jar.id

  print
  print "*** Gump ***"
  print
  gump=Project.list['gump']
  for depend in gump.depend: print 'Depend:\t\t',depend.project
  ant=gump.ant
  for property in ant.property: print 'Property:\t',property.name,property.value

  print
  print "*** krysalis-ruper-test ***"
  print
  krysalisrupertest=Project.list['krysalis-ruper-test']
  for depend in krysalisrupertest.depend: print 'Depend:\t\t',depend.project
  ant=krysalisrupertest.ant
  for property in ant.property: print 'Property:\t',property.name,property.value
