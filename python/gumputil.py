#!/usr/bin/python
"""
	Utility functions for Gump
"""

import os, os.path, sys, urllib, urlparse
from gumpconf import *

# output debug messages or not
debug = False #True
  
#########################################################################
#                     Utility functions                                 #
#########################################################################

 
# returns the path of the file in the href, cached if remote
def gumpCache(href):
    
  #if it's a local file get it locally
  if not href.startswith('http://'):
    newHref=href;  
  else:
    if debug: print 'url: ' + href
    if not os.path.exists(dir.cache):  mkdir(dir.cache)

    #the name of the cached descriptor
    quotedHref = urllib.quote_plus(href)
    #the path of the cached descriptor
    newHref = dir.cache+'/'+quotedHref
    
    #download the file if not present in the cache
    if os.path.exists(newHref): 
      if debug: print 'using cached descriptor'
    else:  
      if debug: print 'caching...'
      urllib.urlretrieve(href, newHref)
      if debug: print '...done' 

  return newHref
