#!/usr/bin/python
"""
        Resource updater for Gump
"""

import os, os.path, sys, urllib
from gumpconf import *

# output debug messages or not
debug = True #True
# Repository
class RuperRepository(object):
  def __init__(self,url,type):
    self.url=url
    self.type=type

  def resolve(self, resource):
    # FIXME (nicolaken)
    # delegate the getting of a resource to an outside file
    # named after the repository type
    if self.type == 'maven':
      # not necessarily Maven uses our resource.standardName()
      if resource.type == 'jar':
        resolvedUrl = '%s/%s/jars/%s-%s.jar' % (self.url,resource.name,resource.name,resource.version)
      else:
        raise Error, 'Unknown Resource Type; type: '+type
    else:
      raise Error, 'Unknown Repository; type: '+type

    return resolvedUrl

  def download(self, resource, destinationDir):
    if not os.path.isdir(destinationDir):
      raise IOError, 'This method needs a directory, instead it got:'+destinationDir

    remoteurl = self.resolve(resource)
    urllib.urlretrieve(remoteurl, '%s/%s' % (destinationDir,resource.standardName()))

  def update(self, resource, destinationDir):
   #download the file if not present
   if os.path.exists('%s/%s' % (destinationDir,resource.standardName())):
     if default.debug: print 'using cached file'
   else:
     if default.debug: print 'caching file...'
     download((self, resource, destinationDir))
     if default.debug: print '...done'

# Resource
class RuperResource(object):
  def __init__(self,name,version,type):
    self.name=name
    self.version=version
    self.type=type

  def standardName(self):
    if self.type == 'jar':
      return '%s-%s.jar' % (self.name,self.version)
    else:
      raise Error, 'Unknown Resource Type; type: '+type



if __name__=='__main__':
  os.chdir(dir.base)
  resource = RuperResource('log4j','1.3.4','jar')
  print resource.standardName()
  repository = RuperRepository('http://www.ibiblio.org/maven','maven')
  print repository.resolve(resource)
  repository.update(resource,dir.cache)



