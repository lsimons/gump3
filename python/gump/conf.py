#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/Attic/conf.py,v 1.5 2003/05/08 06:35:41 nicolaken Exp $
# $Revision: 1.5 $
# $Date: 2003/05/08 06:35:41 $
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

class dir:
    """Configuration of paths"""

    cmdpath   = os.path.abspath(sys.argv[0])
    base      = os.path.normpath('%s/%s' % (os.path.dirname(cmdpath),'../..'))
    cache     = os.path.normpath('%s/%s' % (base,'cache'))
    work      = os.path.normpath('%s/%s' % (base,'work'))

class default:
    """Configuration of default settings"""
    
    workspace  = os.path.normpath('%s/%s.xml' % (dir.base, socket.gethostname().split('.')[0]))
    globalws   = os.path.normpath('%s/%s' % (dir.base, 'global-workspace.xml'))
    project    = "krysalis-ruper-test"
    merge      = os.path.normpath('%s/%s' % (dir.work, 'merge.xml'))
    date       = time.strftime('%Y%m%d')
    antCommand = 'java org.apache.tools.ant.Main -Dbuild.sysclasspath=only'
    syncCommand= 'cp -Rf'
    logLevel   = logging.INFO

def basicConfig():
    if not os.path.exists(dir.cache): os.mkdir(dir.cache)
    if not os.path.exists(dir.work): os.mkdir(dir.work)

    if dir.base not in sys.path: sys.path.insert(0, dir.base)
        
def handleArgv(argv):
  args = []  
  # the workspace
  if len(argv)>2 and argv[1] in ['-w','--workspace']:
    args.append(argv[2])
    del argv[1:3]
  else:
    args.append(default.workspace)
    print
    print " No workspace defined, using default:"
    print "  " , default.workspace
    print
    
  # determine which modules the user desires (wildcards are permitted)
  if len(argv)>2:
   args.append(argv[1] or '*')
   if args[1]=='all': args[1]='*'
  else:
   args.append(default.project)  
      
  return args
    
