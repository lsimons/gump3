#!/usr/bin/python

# $Header: /home/stefano/cvs/gump/python/gump/__init__.py,v 1.16 2003/10/13 18:51:20 ajack Exp $
# $Revision: 1.16 $
# $Date: 2003/10/13 18:51:20 $
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

  The idea is that a subclass of GumpModelObject is used for each of the various
  xml tags which can appear in a gump profile, with a saxdispatcher
  generating a tree of GumpModelObject objects from the profile, dynamically
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

# base gump logger
log = logging.getLogger(__name__)

from gump.xmlutils import SAXDispatcher
from gump.conf import dir, default, setting, switch
from gump.utils import *

###############################################################################
# Initialize
###############################################################################

# tell python what modules make up the gump package
__all__ = ["conf", "launcher", "view", "build", "gen", "check", "update", 
			"model", "xmlutils", "rss", "login", "xdoc", "statistics",
			"document","tools"]


# ensure dirs exists
conf.basicConfig()


timestamp=os.path.join(dir.base,'.timestamp')
if os.path.exists(timestamp):
  mtime=time.localtime(os.path.getmtime(timestamp))
  default.date = time.strftime('%Y%m%d',mtime)
  
#
# Set the User Agent to be Gump...
#
class GumpURLopener(urllib.FancyURLopener):
    def __init__(self, *args):
        self.version = "Jakarta-Gump/"+setting.version
        urllib.FancyURLopener.__init__(self, *args)

urllib._urlopener = GumpURLopener()

###############################################################################
# Functions
###############################################################################
def gumpSafeName(name):
  """returns a file system safe name"""
  return urllib.quote_plus(name)
  
def gumpPath(path):
  """returns the path absolutized relative to the base gump dir"""

  return os.path.abspath(os.path.join(dir.base,path))

def gumpCache(href):
  """returns the path of the file in the href, cached if remote"""

  #if it's a local file get it locally
  if not href.startswith('http://'):
    cachedHrefFile=gumpPath(href);
  else:
    log.debug('Cache url: ' + href)
    if not os.path.exists(dir.cache):  os.mkdir(dir.cache)

    #the name of the cached descriptor
    quotedHref = urllib.quote_plus(href)
    #the path of the cached descriptor
    cachedHrefFile = dir.cache+'/'+quotedHref

    #download the file if not present in the cache
    usecached=0
    if switch.optimize and switch.optimizenetwork:
        if os.path.exists(cachedHrefFile):
          log.info('Using cached descriptor for ' + href)
          usecached=1
          
    if not usecached:
      log.debug('Downloading (if date/timestamp changes) : '+href)      
      try:
        #
        # urllib ought do some (timestamp oriented) caching also...
        #
        urllib.urlretrieve(href, cachedHrefFile)
      except IOError, detail:
        log.error('Failed to download ['+href+']. Details: ' + detail)
        try:
          os.remove(cachedHrefFile)
        except:
          log.debug('No faulty cached file to remove, or failed to remove.')
      else: 
         log.debug('...done')

  return cachedHrefFile

from gump.context import GumpContext

def load(file, context=GumpContext()):
  try:
    return loadWorkspace(file, context)
  except IOError, detail:
    log.critical(detail)  
    sys.exit(1)
    
def loadWorkspace(file, context=GumpContext()):
  """Run a file through a saxdispatcher.

    This builds a GOM in memory from the xml file. Return the generated GOM."""

  if not os.path.exists(file):
    log.error('workspace '+file+' not found')

    raise IOError, """workspace %s not found!

  You need to specify a valid workspace for Gump to run
  If you are new to Gump, simply copy minimal-workspace.xml
  to a file with the name of your computer (mycomputer.xml)
  and rerun this program.""" % file 

  from gump.model import Workspace, Repository, Module, Project, Profile
  
  Module.list={}
  Project.list={}
  Profile.list={}
  Repository.list={}
  
  log.debug("SAXDispatcher on : " + file);
    
  workspace=SAXDispatcher(file,'workspace',Workspace).docElement
 
  if not workspace:
    raise IOError, "Failed to load workspace" + file
  
  #
  # Complete all entries
  #
  workspace.complete()
  for repository in Repository.list.values(): repository.complete(workspace)
  for module in Module.list.values(): module.complete(workspace)
  for project in Project.list.values(): project.complete(workspace)
  
  
    	# :TODO: Bad place for this, move?
  context.buildMap()
    
  #context.tree()
  #sys.exit(0)
  
  return workspace


###############################################################################
# Demonstration code
###############################################################################

if __name__=='__main__':
  from gump.core import *

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)

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
