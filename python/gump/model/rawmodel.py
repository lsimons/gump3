#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/Attic/rawmodel.py,v 1.14 2004/02/15 17:32:05 ajack Exp $
# $Revision: 1.14 $
# $Date: 2004/02/15 17:32:05 $
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

import os,types

import logging

import gump.config
from gump.utils.xmlutils import SAXDispatcher, GumpXMLObject, Single, Multiple, Named

"""
  Gump XML metadata loading depends on this object model.

  An instance of this object model is imported from a set of XML files.
  
  Gump uses a SAX dispatcher tool, a dependency walker, and this 
  object model (GOM).

  The idea is that a subclass of GumpModelObject is used for each of the various
  xml tags which can appear in a gump profile, with a saxdispatcher
  generating a tree of GumpModelObject objects from the profile, dynamically
  merging as it finds href references.

  Then there's some basic procedures to work with the GOM, like load().

"""
from gump import log

###############################################################################
# Initialize
###############################################################################


###############################################################################
# Gump Object Model
#
# All intelligence and functionality is provided in the base classes
# above, allowing the actual model to be rather simple and compact.
###############################################################################

class GumpXMLModelObject(GumpXMLObject): 

  def __init__(self,attrs):
    GumpXMLObject.__init__(self,attrs)
    
    
    # :TODO: This is too low level, do later/higher (somehow)
    
    # parse out '@@DATE@@'
    for (name,value) in attrs.items():
      if not name == '@basedir' and not name == 'annotations':
          self.__dict__[name]=value.replace('@@DATE@@',gump.default.date)
      
class XMLWorkspace(GumpXMLModelObject):
  """Represents a <workspace/> element."""

  def init(self):
    self.property=Multiple(XMLProperty)
    self.project=Multiple(XMLProject)
    self.module=Multiple(XMLModule)
    self.repository=Multiple(XMLRepository)
    self.server=Multiple(XMLServer)
    self.tracker=Multiple(XMLTracker)
    self.profile=Multiple(XMLProfile)
    self.version=Single(GumpXMLModelObject)

    
# represents a <profile/> element
class XMLProfile(Named,GumpXMLModelObject):
  list={}
  def init(self):
    self.project=Multiple(XMLProject)
    self.module=Multiple(XMLModule)
    self.repository=Multiple(XMLRepository)
    self.server=Multiple(XMLServer)
    self.tracker=Multiple(XMLTracker)

# represents a <module/> element
class XMLModule(Named):
  list={}
  def init(self):
    self.cvs=Single(GumpXMLModelObject)
    self.svn=Single(GumpXMLModelObject)
    self.jars=Single(GumpXMLModelObject)
    self.url=Single(GumpXMLModelObject)
    self.description=Single(GumpXMLModelObject)
    self.redistributable=Single(GumpXMLModelObject)
    self.nag=Multiple(XMLNag)
    self.project=Multiple(XMLProject)

# represents a <server/> element
class XMLServer(Named):
  list={}
  def init(self):
    self.attribution=Single(GumpXMLModelObject)
    self.title=Single(GumpXMLModelObject)
    self.url=Single(GumpXMLModelObject)
    self.site=Single(GumpXMLModelObject)
    
# represents a <tracker/> element
class XMLTracker(Named):
  list={}
  def init(self):
    self.attribution=Single(GumpXMLModelObject)
    self.title=Single(GumpXMLModelObject)
    self.url=Single(GumpXMLModelObject)
    self.site=Single(GumpXMLModelObject)

# represents a <repository/> element
class XMLRepository(Named):
  list={}
  def init(self):
    self['home-page']=Single(GumpXMLModelObject)
    self.title=Single(GumpXMLModelObject)
    self.cvsweb=Single(GumpXMLModelObject)
    self.url=Single(GumpXMLModelObject)
    self.root=Single(XMLRepositoryRoot)
    self.redistributable=Single(GumpXMLModelObject)

# represents a <root/> element within a <repository/> element
class XMLRepositoryRoot(GumpXMLModelObject):
  def init(self):
    self.method=Single(GumpXMLModelObject)
    self.user=Single(GumpXMLModelObject)
    self.password=Single(GumpXMLModelObject)
    self.hostname=Single(GumpXMLModelObject)
    self.path=Single(GumpXMLModelObject)
    

# represents a <project/> element
class XMLProject(Named):
  list={}
  def init(self):
    self.ant=Single(XMLAnt)
    self.maven=Single(XMLAnt)
    self.script=Single(XMLScript)
    self.depend=Multiple(XMLDepend)
    self.description=Single(GumpXMLModelObject)
    self.url=Single(GumpXMLModelObject)
    self.option=Multiple(XMLDepend)
    self.package=Multiple(GumpXMLModelObject)
    self.jar=Multiple(XMLJar)
    self.home=Single(XMLHome)
    self.license=Single(GumpXMLModelObject)
    self.nag=Multiple(XMLNag)
    self.javadoc=Single(XMLJavadoc)
    self.junitreport=Single(XMLJunitReport)
    self.work=Multiple(XMLWork)
    self.mkdir=Multiple(XMLMkdir)
    self.delete=Multiple(XMLDelete)
    self.redistributable=Single(GumpXMLModelObject)

# represents a <script/> element
class XMLScript(GumpXMLModelObject):
  def init(self):
    self.arg=Multiple(GumpXMLModelObject)
    self.property=Multiple(XMLProperty)
  
# represents an <ant/> element
class XMLAnt(GumpXMLModelObject):
  def init(self):  
    self.depend=Multiple(XMLDepend)
    self.property=Multiple(XMLProperty)
    self.jvmarg=Multiple(GumpXMLModelObject)

# represents a <maven/> element
class XMLMaven(GumpXMLModelObject):
  def init(self):  
    self.depend=Multiple(XMLDepend)
    self.property=Multiple(XMLProperty)
    self.jvmarg=Multiple(GumpXMLModelObject)

# represents a <nag/> element
class XMLNag(GumpXMLModelObject):
  def init(self):
    self.regexp=Multiple(GumpXMLModelObject)
    self.toaddr=Single()
    self.fromaddr=Single()

# represents a <javadoc/> element
class XMLJavadoc(GumpXMLModelObject):
  def init(self):
    self.description=Multiple(GumpXMLModelObject)

# represents a <property/> element
class XMLProperty(GumpXMLModelObject):
    
  def getName(self):
    return self.name    
        
# TODO: set up the below elements with defaults using complete()

#
# 	Represents a <depend/> element
#
#	Two depends are equal
#
class XMLDepend(GumpXMLModelObject): pass
 
# represents a <description/> element
class XMLDescription(GumpXMLModelObject): pass

# represents a <home/> element
class XMLHome(GumpXMLModelObject): pass

# represents a <jar/> element
class XMLJar(GumpXMLModelObject): 
  def getName(self):
    return self.name    

# represents a <junitreport/> element
class XMLJunitReport(GumpXMLModelObject): pass

# represents a <mkdir/> element
class XMLMkdir(GumpXMLModelObject): pass

# represents a <delete/> element
class XMLDelete(GumpXMLModelObject): pass

# represents a <work/> element
class XMLWork(GumpXMLModelObject): pass
