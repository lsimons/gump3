#!/usr/bin/python

# $Header: /home/stefano/cvs/gump/python/gump/Attic/config.py,v 1.11 2003/12/15 19:36:51 ajack Exp $
# $Revision: 1.11 $
# $Date: 2003/12/15 19:36:51 $
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
    base      = os.path.abspath('%s/%s' % (os.path.dirname(cmdpath),'../..'))
    
    cache     = os.path.abspath('%s/%s' % (base,'cache'))
    work      = os.path.abspath('%s/%s' % (base,'work'))
    tmp       = os.path.abspath('%s/%s' % (base,'tmp'))
    template  = os.path.abspath('%s/%s' % (base,'template'))
        
    test      = os.path.abspath('%s/%s' % (base,'test'))

def gumpPath(path,basedir=None):
  """returns the path absolutized relative to the base gump dir"""

  return os.path.abspath(os.path.join(basedir or dir.base,path))

class default:
    """Configuration of default settings"""
    
    gumpfullhost   = socket.gethostname()   
    gumphost   = socket.gethostname().split('.')[0]
    gumpid	   = os.getpid()    
    workspace  = os.path.abspath('%s/%s.xml' % (dir.base, gumphost))
    globalws   = os.path.abspath('%s/%s' % (dir.base, 'global-workspace.xml'))
    merge      = os.path.abspath('%s/%s' % (dir.work, 'merge.xml'))
    date       = time.strftime('%Y%m%d')
    logLevel   = logging.INFO # logging.DEBUG
    classpath = (os.getenv('CLASSPATH') or '').split(os.pathsep)  
    
    logurl		=	'http://cvs.apache.org/builds/gump/nightly/'
    bannerimage = 'http://jakarta.apache.org/images/jakarta-logo.gif'
    
    email = 'gump@' + gumpfullhost
    mailinglist = 'gump@jakarta.apache.org'
    mailserver = 'mail.apache.org'
    mailport = 25
    prefix = '[GUMP@' + gumphost + ']'
    signature="\r\n--\r\nGump http://jakarta.apache.org/gump\n" \
        + '[' + gumpfullhost + "]\n"
        
    if not os.name == 'dos' and not os.name == 'nt':
        classpathSeparator=':'
        shellQuote='\''
        shellEscape='\\'
    else:
        classpathSeparator=';'
        shellQuote='"'
        shellEscape='\\'
    
class setting:    
    """Configuration of hardcoded settings"""
    
    version="2.0.2-alpha-0002"
    
    # :TODO: Add "minimum version" checks...
    ws_version="0.4"
    
    datetimeformat='%a, %d %b %Y %H:%M:%S (%Z)'
    timeformat='%H:%M:%S (%Z)'
    
    timeout=60*60 # 60 minutes (in seconds)
    
class switch:
    """Configuration of switches """   
    optimize=0 # Optimize (at risk to exact correctness) anywhere one can
    optimizenetwork=1 # Do least network traffic 
    debugging=0 # Not debugging..
    
def basicConfig():
    if not os.path.exists(dir.cache): os.mkdir(dir.cache)
    if not os.path.exists(dir.work): os.mkdir(dir.work)
    if not os.path.exists(dir.tmp): os.mkdir(dir.tmp)
    if not os.path.exists(dir.test): os.mkdir(dir.test)

    if dir.base not in sys.path: sys.path.insert(0, dir.base)

