#!/usr/bin/python

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

"""
  Gump HTTP Client
"""

import os.path
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

  
def cacheHTTP(href,cacheDir=dir.cache,optimize=0):
    """returns the path of the file in the href, cached if remote"""

    #if its a local file get it locally
 
    log.debug('Cache URL : ' + href)
    if not os.path.exists(cacheDir):  os.mkdir(cacheDir)

    #the name of the cached descriptor
    quotedHref = urllib.quote_plus(href)
    #the path of the cached descriptor
    cachedHrefFile = cacheDir+'/'+quotedHref

    #download the file if not present in the cache
    usecached=0
    if optimize or (switch.optimize and switch.optimizenetwork):
        if os.path.exists(cachedHrefFile):
          log.debug('Using cached descriptor for ' + href)
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
