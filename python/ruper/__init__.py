#!/usr/bin/python

## ====================================================================
##
## The Apache Software License, Version 1.1
##
## Copyright (c) 1999-2003 The Apache Software Foundation.  All rights
## reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions
## are met:
##
## 1. Redistributions of source code must retain the above copyright
##    notice, this list of conditions and the following disclaimer.
##
## 2. Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in
##    the documentation and/or other materials provided with the
##    distribution.
##
## 3. The end-user documentation included with the redistribution, if
##    any, must include the following acknowlegement:
##       "This product includes software developed by the
##        Apache Software Foundation (http://www.apache.org/)."
##    Alternately, this acknowlegement may appear in the software itself,
##    if and wherever such third-party acknowlegements normally appear.
##
## 4. The names "The Jakarta Project", "Alexandria", and "Apache Software
##    Foundation" must not be used to endorse or promote products derived
##    from this software without prior written permission. For written
##    permission, please contact apache@apache.org.
##
## 5. Products derived from this software may not be called "Apache"
##    nor may "Apache" appear in their names without prior written
##    permission of the Apache Group.
##
## THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
## WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
## OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
## ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
## USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
## OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
## OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
## SUCH DAMAGE.
## ====================================================================
##
## This software consists of voluntary contributions made by many
## individuals on behalf of the Apache Software Foundation.  For more
## information on the Apache Software Foundation, please see
## <http://www.apache.org/>.

"""

Ruper package in Python
Ruper == Resource UPdatER

"""

__author__  = "Apache Software Foundation"
__status__  = "$Header: /home/stefano/cvs/gump/python/ruper/Attic/__init__.py,v 1.2 2003/04/28 07:30:26 nicolaken Exp $"
__version__ = "$Revision: 1.2 $"
__date__    = "$Date: 2003/04/28 07:30:26 $"

import os, os.path, sys, urllib, logging

# init logging
logging.basicConfig()
log = logging.getLogger("Ruper")
log.setLevel(logging.DEBUG) #set verbosity to show all messages of severity >= DEBUG
 
# Repository
class Repository(object):
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
     log.debug('using cached file')
   else:
     log.debug('caching file...')
     download((self, resource, destinationDir))
     log.debug('...done')

# Resource
class Resource(object):
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
  resource = Resource('log4j','1.3.4','jar')
  print resource.standardName()
  repository = Repository('http://www.ibiblio.org/maven','maven')
  print repository.resolve(resource)
  repository.update(resource,dir.cache)



