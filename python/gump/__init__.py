#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/__init__.py,v 1.3 2003/04/28 21:49:31 rubys Exp $
# $Revision: 1.3 $
# $Date: 2003/04/28 21:49:31 $
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
# Gump Object Model
#
# All intelligence and functionality is provided in the base classes
# above, allowing the actual model to be rather simple and compact.
###############################################################################

class Workspace(GumpBase):
  """Represents a <workspace/> element."""

  def init(self):
    self.property=Multiple(Property)
    self.project=Multiple(Project)
    self.module=Multiple(Module)
    self.repository=Multiple(Repository)
    self.profile=Multiple(Profile)

  # provide default elements when not defined in xml
  def complete(self):
    if not self['banner-image']:
      self['banner-image']="http://jakarta.apache.org/images/jakarta-logo.gif"
    if not self['banner-link']: self['banner-link']="http://jakarta.apache.org"
    if not self.logdir: self.logdir=os.path.join(self.basedir,"log")
    if not self.cvsdir: self.cvsdir=os.path.join(self.basedir,"cvs")
    if not self.pkgdir: self.pkgdir=self.basedir
    if self.deliver:
      if not self.scratchdir: self.scratchdir=os.path.join(self.basedir,"scratch")

# represents a <profile/> element
class Profile(Named):
  list={}
  def init(self): 
    self.project=Multiple(Project)
    self.module=Multiple(Module)
    self.repository=Multiple(Repository)

# represents a <module/> element
class Module(Named):
  list={}
  def init(self): 
    self.cvs=Single()
    self.url=Single()
    self.description=Single()
    self.redistributable=Single()
    self.project=Multiple(Project)

  # provide default elements when not defined in xml
  def complete(self,workspace):
    self.srcdir=os.path.join(str(workspace.basedir),self.srcdir or self.name)
    for project in self.project: 
      if not project.module: project.module=self.name

# represents a <repository/> element
class Repository(Named):
  list={}
  def init(self):
    self['home-page']=Single()
    self.title=Single()
    self.cvsweb=Single()
    self.root=Single(RepositoryRoot)
    self.redistributable=Single()

# represents a <root/> element within a <repository/> element
class RepositoryRoot(GumpBase):
  def init(self): 
    self.method=Single()
    self.user=Single()
    self.password=Single()
    self.hostname=Single()
    self.path=Single()

# represents a <project/> element
class Project(Named):
  list={}
  def init(self): 
    self.isComplete=0
    self.ant=Single(Ant)
    self.script=Single()
    self.depend=Multiple(Depend)
    self.description=Single()
    self.url=Single()
    self.option=Multiple(Depend)
    self.package=Multiple()
    self.jar=Multiple(Jar)
    self.home=Single(Home)
    self.license=Single()
    self.nag=Multiple(Nag)
    self.javadoc=Single(Javadoc)
    self.junitreport=Single(JunitReport)
    self.work=Multiple(Work)
    self.mkdir=Multiple(Mkdir)
    self.redistributable=Single()

  # provide default elements when not defined in xml
  def complete(self,workspace):
    if self.isComplete: return

    # complete properties
    if self.ant: self.ant.complete(self)
    # compute home directory
    if self.home and isinstance(self.home,Single):
      if self.home.nested:
        srcdir=Module.list[self.module].srcdir
        self.home=os.path.normpath(os.path.join(srcdir,self.home.nested))
      elif self.home.parent:
        self.home=os.path.normpath(os.path.join(workspace.basedir,self.home.parent))
    elif not self.home: self.home=os.path.join(workspace.basedir,self.name)

    # resolve jars
    for jar in self.jar:
      if self.home and jar.name:
        jar.path=os.path.normpath(os.path.join(self.home,jar.name))

    # expand properties
    if self.ant: self.ant.expand(self)


    # ensure that every project that this depends on is complete
    self.isComplete=1
    for depend in self.depend+self.option:
      project=Project.list.get(depend.project,None)
      if project: project.complete(workspace)

    # complete properties
    if self.ant: self.ant.complete(self)

    # inherit dependencies:
    self.inheritDependencies()

  # Determine if this project has any unsatisfied dependencies left
  # on the todo list.
  def isReady(self,todo):
    for depend in self.depend+self.option:
      if Project.list.get(depend.project,None) in todo: return 0
    return 1

  # add this element and all of it's dependencies to a todo list 
  def addToTodoList(self,todo):
    todo.append(self)
    for depend in self.depend+self.option:
      project=Project.list[depend.project]
      if not project in todo: project.addToTodoList(todo)

  # determine if this project is a prereq of any project on the todo list
  def isPrereq(self,todo):
    for project in todo:
      for depend in project.depend+project.option:
	if depend.project==self.name: return 1

  # determine if this project is a prereq of any project on the todo list
  def hasFullDependencyOn(self,name):
    for depend in self.depend+self.option:
      if depend.project==name and not depend.noclasspath: return 1

  # process all inherited dependencies
  def inheritDependencies(self):

    for d1 in self.depend+self.option:
      project=Project.list.get(d1.project,None)
      if not project: continue
      inherit=d1.inherit
      for d2 in project.depend+project.option:
	if self.hasFullDependencyOn(d2.project): continue

	# include the dependency if:
	#   inherit="all"
	#   inherit="hard"
	#   inherit="runtime" and the matching dependency is listed as runtime
	#   if the dependency indicates that the jars are to be inherited
        include=0
	if inherit=="all" or inherit=="hard":
	  include=1
	elif inherit=="runtime" and d2.runtime:
	  include=1
	elif d2.inherit=="jars":
	  include=1

        # if the dependency is to be inherited, add it to the appropriate list
        if include:
	  if inherit=="hard" or d2 in project.depend:
	    self.depend.append(d2)
	  else:
	    self.option.append(d2)

# represents an <ant/> element
class Ant(GumpBase): 
  def init(self): 
    self.depend=Multiple(Depend)
    self.property=Multiple(Property)
    self.jvmarg=Multiple()

  # expand properties - in other words, do everything to complete the
  # entry that does NOT require referencing another project
  def expand(self,project):

    # convert property elements which reference a project into dependencies
    for property in self.property:
      if not property.project: continue
      if property.project==project.name: continue
      if property.reference=="srcdir": continue
      if project.hasFullDependencyOn(property.project): continue

      depend=Depend({'project':property.project})
      if not property.classpath: depend['noclasspath']=Single({})
      if property.runtime: depend['runtime']=property.runtime
      project.depend.append(depend)

    # convert all depend elements into property elements
    for depend in self.depend:
      property=Property(depend.__dict__)
      property['reference']='jarpath'
      property['name']=depend.project
      self.property.append(property)
      project.depend.append(depend)
    self.depend=None

  # complete the definition - it is safe to reference other projects
  # at this point
  def complete(self,project):

    for property in self.property: property.complete(project)

# represents a <nag/> element
class Nag(GumpBase): 
  def init(self): 
    self.regexp=Multiple()

# represents a <javadoc/> element
class Javadoc(GumpBase): 
  def init(self): 
    self.description=Multiple()

# represents a <property/> element
class Property(GumpBase): 
  # provide default elements when not defined in xml
  def complete(self,project):
    if self.reference=='home':
      self.value=Project.list[self.project].home

    elif self.reference=='srcdir':
      module=Project.list[self.project].module
      self.value=Module.list[module].srcdir

    elif self.reference=='jarpath':
      target=Project.list[self.project]
      if self.id:
	for jar in target.jar:
	  if jar.id==self.id:
	    self.value=jar.path
	    break
	else:
	  raise str(("jar with id %s was not found in project %s "
	     "referenced by %s") % (self.id, target.name, project.name))
      elif len(target.jar)==1:
	self.value=target.jar[0].path
      elif len(target.jar)>1:
	raise str(("Multiple jars defined by project %s referenced by %s; " +
	   "an id attribute is required to select the one you want") %
	   (target.name, project.name))
      else:
	raise str("Project %s referenced by %s defines no jars as output" %
	  (target.name, project.name))

      module=Project.list[self.project].module
      self.value=Module.list[module].srcdir


# TODO: set up the below elements with defaults using complete()

# represents a <depend/> element
class Depend(GumpBase): pass

# represents a <description/> element
class Description(GumpBase): pass

# represents a <home/> element
class Home(GumpBase): pass

# represents a <jar/> element
class Jar(GumpBase): pass

# represents a <junitreport/> element
class JunitReport(GumpBase): pass

# represents a <mkdir/> element
class Mkdir(GumpBase): pass

# represents a <work/> element
class Work(GumpBase): pass

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
