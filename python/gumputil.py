#!/usr/bin/python
"""
   Utility functions for Gump
"""

import os, os.path, sys, urllib, urlparse, logging
from gumpconf import *

# init logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG) #set verbosity to show all messages of severity >= DEBUG

#########################################################################
#                     Utility functions                                 #
#########################################################################

# returns the path absolutized relative to the base gump dir
def gumpPath(path):
  return os.path.normpath('%s/%s' % (dir.base,path))
                 

# returns the path of the file in the href, cached if remote
def gumpCache(href):

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

# display an error message in standard formatting
def gumpMessage(type, error, description):
  print
  print
  print ' ****************************************************************'
  print '     ',type
  print ' ****************************************************************'
  print ' **                                                            **'
  print '   ',error
  print
  print description
  print
  print ' **                                                            **'
  print ' ****************************************************************'
  print
  print

