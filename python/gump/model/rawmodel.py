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

import os,types

from gump import log
from gump.core.config import default

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
        if value and isinstance(value,types.StringTypes):
            if not name == '@basedir' and not name == 'annotations':
                self.__dict__[name]=value.replace('@@DATE@@',default.date)
      
class XMLWorkspace(Named,GumpXMLModelObject):
  """Represents a <workspace/> element."""

  map={}
  
  def init(self):
    self.property=Multiple(XMLProperty)
    self.sysproperty=Multiple(XMLProperty)
    self.project=Multiple(XMLProject)
    self.module=Multiple(XMLModule)
    self.repository=Multiple(XMLRepository)
    self.server=Multiple(XMLServer)
    self.tracker=Multiple(XMLTracker)
    self.profile=Multiple(XMLProfile)
    self.nag=Single(XMLWorkspaceNag)
    self.version=Single(GumpXMLModelObject)

    
# represents a <profile/> element
class XMLProfile(Named,GumpXMLModelObject):
  map={}
  def init(self):
    self.project=Multiple(XMLProject)
    self.module=Multiple(XMLModule)
    self.repository=Multiple(XMLRepository)
    self.server=Multiple(XMLServer)
    self.tracker=Multiple(XMLTracker)

# represents a <module/> element
class XMLModule(Named):
  map={}
  def init(self):
    self.cvs=Single(GumpXMLModelObject)
    self.svn=Single(GumpXMLModelObject)
    self.artefacts=Single(GumpXMLModelObject)
    self.url=Single(GumpXMLModelObject)
    self.description=Single(GumpXMLModelObject)
    self.redistributable=Single(GumpXMLModelObject)
    self.nag=Multiple(XMLNag)
    self.project=Multiple(XMLProject)

# represents a <server/> element
class XMLServer(Named):
  map={}
  def init(self):
    self.attribution=Single(GumpXMLModelObject)
    self.title=Single(GumpXMLModelObject)
    self.url=Single(GumpXMLModelObject)
    self.site=Single(GumpXMLModelObject)
    self.note=Single(GumpXMLModelObject)
    
# represents a <tracker/> element
class XMLTracker(Named):
  map={}
  def init(self):
    self.attribution=Single(GumpXMLModelObject)
    self.title=Single(GumpXMLModelObject)
    self.url=Single(GumpXMLModelObject)
    self.site=Single(GumpXMLModelObject)

# represents a <repository/> element
class XMLRepository(Named):
  map={}
  def init(self):
    self['home-page']=Single(GumpXMLModelObject)
    self.title=Single(GumpXMLModelObject)
    self.cvsweb=Single(GumpXMLModelObject)
    self.web=Single(GumpXMLModelObject)
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
  map={}
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
    self.sysproperty=Multiple(XMLProperty)
  
# represents an <ant/> element
class XMLAnt(GumpXMLModelObject):
  def init(self):  
    self.depend=Multiple(XMLDepend)
    self.property=Multiple(XMLProperty)
    self.sysproperty=Multiple(XMLProperty)
    self.jvmarg=Multiple(GumpXMLModelObject)

# represents a <maven/> element
class XMLMaven(GumpXMLModelObject):
  def init(self):  
    self.depend=Multiple(XMLDepend)
    self.property=Multiple(XMLProperty)
    self.sysproperty=Multiple(XMLProperty)
    self.jvmarg=Multiple(GumpXMLModelObject)

# represents a <nag/> element in the workspace
class XMLWorkspaceNag(GumpXMLModelObject):
  def init(self):
    self.toaddr=Single()
    self.fromaddr=Single()
    
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

# represents a <property/> or <sysproperty/> element
class XMLProperty(GumpXMLModelObject):
    
  def getName(self):
    return self.name    
        
# TODO: set up the below elements with defaults using complete()

#
# 	Represents a <depend/> element
#
#	Two depends are equal
#
class XMLDepend(GumpXMLModelObject):
  def init(self):
    self.noclasspath=Single(GumpXMLModelObject)
    
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
