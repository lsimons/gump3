#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/Attic/model.py,v 1.9 2003/05/04 21:02:57 nicolaken Exp $
# $Revision: 1.9 $
# $Date: 2003/05/04 21:02:57 $
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

import os,types,traceback,logging

from gump import GumpBase, Named, Single, Multiple
from gump.conf import dir, default

    
###############################################################################
# Initialize
###############################################################################

# use own logging

# init logging
logging.basicConfig()

# base gump logger
log = logging.getLogger(__name__)

#set verbosity to show all messages of severity >= default.logLevel
log.setLevel(default.logLevel)


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

  def cvsroot(self):
    if not self.cvs: return
    repository=Repository.list[self.cvs.repository]

    root=':' + str(repository.root.method) + ':'
    if repository.root.user: root+=str(repository.root.user)
    if repository.root.hostname:
      root+='@'
      if self.cvs['host-prefix']: root+=self.cvs['host-prefix']+'.'
      root+=str(repository.root.hostname) + ':'
    root+=str(repository.root.path)
    if self.cvs.dir: root+='/'+str(self.cvs.dir)

    return root

  # provide default elements when not defined in xml
  def complete(self,workspace):
    if self.tag and self.cvs: self.cvs.tag=self.tag
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
  def complete(self,workspace):
    if self.root:
      if self.user: self.root.user=self.user
      if self.path: self.root.path=self.path
      if self.method: self.root.method=self.method
      if self['host-name']: self.root['host-name']=self['host-name']

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
    elif not self.home: 
      if type(self.package) in types.StringTypes:
        self.home=os.path.join(workspace.pkgdir,self.package)
      elif self.module:
        self.home=Module.list[self.module].srcdir
      else:
        self.home=os.path.join(workspace.basedir,self.name)

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

  def classpath(self):
    result=[]

    # start with the work directories
    srcdir=Module.list[self.module].srcdir
    for work in self.work:
      result.append(os.path.normpath(os.path.join(srcdir,work.nested)))

    # add in depends and options
    for depend in self.depend+self.option:
      result+=[jar.path for jar in depend.jars()]

    return result

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
      try:
        self.value=Project.list[self.project].home
      except:
        log.debug( traceback.format_stack() )
        log.warn( "Cannot resolve homedir of " + self.project + " for " + project.name)

    elif self.reference=='srcdir':
      try:
        module=Project.list[self.project].module
        self.value=Module.list[module].srcdir
      except:
        log.debug( traceback.format_stack() )
        log.warn( "Cannot resolve srcdir of " + self.project + " for " + project.name)
        
    elif self.reference=='jarpath':
      try:
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
        
      except:
        log.debug( traceback.format_stack() )
        log.warn( "Cannot resolve jarpath of " + self.project + " for " + project.name)

# TODO: set up the below elements with defaults using complete()

# represents a <depend/> element
class Depend(GumpBase): 
  def jars(self):
    result=[]
    ids=(self.ids or '').split(' ')
    for jar in Project.list[self.project].jar:
      if (not self.ids) or (jar.id in ids): result.append(jar)
    return result

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
