#!/usr/bin/python

# $Header: /home/stefano/cvs/gump/python/gump/Attic/conf.py,v 1.20 2003/10/13 22:37:12 ajack Exp $
# $Revision: 1.20 $
# $Date: 2003/10/13 22:37:12 $
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
    Global configuration defaults for gump. All these should really be
    set in the Workspace; this file is here to provide sensible defaults.
"""

import socket
import time
import os
import sys
import logging

from gump import log

class dir:
    """Configuration of paths"""

    cmdpath   = os.path.abspath(sys.argv[0])
    if 1: # 0 was for unit testing, lazy...
      base      = os.path.normpath('%s/%s' % (os.path.dirname(cmdpath),'../..'))
    else:
      base		= os.path.normpath('.')
    cache     = os.path.normpath('%s/%s' % (base,'cache'))
    work      = os.path.normpath('%s/%s' % (base,'work'))
    tmp       = os.path.normpath('%s/%s' % (base,'tmp'))
    template  = os.path.normpath('%s/%s' % (base,'template'))

class default:
    """Configuration of default settings"""
    
    gumpfullhost   = socket.gethostname()   
    gumphost   = socket.gethostname().split('.')[0]
    workspace  = os.path.normpath('%s/%s.xml' % (dir.base, gumphost))
    globalws   = os.path.normpath('%s/%s' % (dir.base, 'global-workspace.xml'))
    project    = "jakarta-gump"
    merge      = os.path.normpath('%s/%s' % (dir.work, 'merge.xml'))
    date       = time.strftime('%Y%m%d')
    logLevel   = logging.INFO
    classpath = (os.getenv('CLASSPATH') or '').split(os.pathsep)  
    
    logurl		=	'http://cvs.apache.org/builds/gump/nightly/'
    bannerimage = 'http://jakarta.apache.org/images/jakarta-logo.gif'
    
    email = 'gump@lists.apache.org'
    mailserver = 'mail.apache.org'
    prefix = '[GUMPY@' + gumphost + ']'
    signature="\r\n--\r\nGump http://jakarta.apache.org/gump\n" \
        + '[' + gumpfullhost + "]\n"
    
class setting:    
    """Configuration of hardcoded settings"""
    
    version="2.0.1-alpha-0005"
    
    # :TODO: Add "minimum checks later..."
    ws_version="0.4"
    
    datetimeformat="%a, %d %b %Y %H:%M:%S (%Z)"
    
    timeout=60*30 # 30 minutes (in seconds)
    
class switch:
    """Configuration of switches """   
    optimize=0 # Optimize (at risk to exact correctness) anywhere one can
    optimizenetwork=1 # Do least network traffic 
    failtesting=0 # Not testing.. 
    debugging=0 # Not debugging..
    
def basicConfig():
    if not os.path.exists(dir.cache): os.mkdir(dir.cache)
    if not os.path.exists(dir.work): os.mkdir(dir.work)
    if not os.path.exists(dir.tmp): os.mkdir(dir.tmp)

    if dir.base not in sys.path: sys.path.insert(0, dir.base)

def banner():
  print
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  print "Apache Python Gump (" + setting.version + "), a multi-project builder."
  print  
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  print
  print "Copyright (C) 2003 Apache Software Foundation. All rights reserved."
  print "See the Apache Software License 1.1 for more details."
  print "http://www.apache.org/"
  print
        
def handleArgv(argv, requireProject=1):
  args = []  
  # the workspace
  if len(argv)==2: 
    if argv[1] in ['-V','--version']:
      banner()
      sys.exit(0)
      
    elif argv[1] in ['-h','--help']:
      banner()
      print "command: " , __name__    
      print "Usage: python "+__name__+".py [OPTION]... [PROJECT]... [OTHER]..."
      print 
      print "Mandatory arguments to long options are mandatory for short options too."
      print 
      print "Startup:"
      print "  -V,  --version           display the version of Gump and exit."
      print "  -h,  --help              print this help."
      print "  -w,  --workspace         use this workspace for Gump."
      print
      print "For bug reports use Bugzilla: http://bugzilla.apache.org/."
      print "For suggestions: <gump@jakarta.apache.org/>."
      sys.exit(0)
      
  if len(argv)>2 and argv[1] in ['-w','--workspace']:
    args.append(argv[2])
    del argv[1:3]
  else:
    args.append(default.workspace)
    log.info("No workspace defined with -w or -workspace.")
    log.info("Using default workspace: " + default.workspace)
    
  # determine which modules the user desires (wildcards are permitted)
  if len(argv)>1:
   args.append(argv[1] or '*')
   if args[1]=='all': args[1]='*'
  else:
    if requireProject:
      banner()
      print
      print " No project specified, please supply a project expressions or 'all'."
      print " Project wildcards are accepted, e.g. \"jakarta-*\"."
      print "  " , default.workspace
      sys.exit(1)
    else:
     args.append(default.project)
     
  return args
    
