#!/usr/bin/python

# $Header: /home/stefano/cvs/gump/python/gump/utils/http.py,v 1.4 2004/02/23 23:11:22 ajack Exp $
# $Revision: 1.4 $
# $Date: 2004/02/23 23:11:22 $
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

from gump import log
from gump.config import dir, switch, setting

###############################################################################
# Initialize
###############################################################################
  
#
# Set the User Agent to be Gump...
#
class GumpURLopener(urllib.FancyURLopener):
    def __init__(self, *args):
        self.version = "Apache-Gump/"+setting.version
        urllib.FancyURLopener.__init__(self, *args)

urllib._urlopener = GumpURLopener()

###############################################################################
# Functions
###############################################################################

  
def cacheHTTP(href,cacheDir=dir.cache):
    """returns the path of the file in the href, cached if remote"""

    #if it's a local file get it locally
 
    log.debug('Cache URL : ' + href)
    if not os.path.exists(cacheDir):  os.mkdir(cacheDir)

    #the name of the cached descriptor
    quotedHref = urllib.quote_plus(href)
    #the path of the cached descriptor
    cachedHrefFile = cacheDir+'/'+quotedHref

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
        log.error('Failed to download ['+href+']. Details: ' + str(detail))
        try:
          os.remove(cachedHrefFile)
        except:
          log.debug('No faulty cached file to remove, or failed to remove.')
      else: 
         log.debug('...done')

    return cachedHrefFile
