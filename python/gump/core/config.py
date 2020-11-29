#!/usr/bin/python

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
    Global configuration defaults for gump. All these should really be
    set in the Workspace; this file is here to provide sensible defaults.
"""

import socket
import time
import datetime
import os
import sys
import logging
import string

from gump import log

EXIT_CODE_SUCCESS=0
EXIT_CODE_FAILED=1
EXIT_CODE_MISSING_UTILITY=2
EXIT_CODE_BAD_ENVIRONMENT=3

class dir:
    """Configuration of paths"""

    base      = os.path.abspath(os.getcwd())  
    
    cache     = os.path.abspath(os.path.join(base,'cache'))
    work      = os.path.abspath(os.path.join(base,'work'))
    tmp       = os.path.abspath(os.path.join(base,'tmp'))
    template  = os.path.abspath(os.path.join(base,'template'))
        
    test      = os.path.abspath(os.path.join(base,'test'))

def gumpPath(path,basedir=None):
  """returns the path absolutized relative to the base gump dir"""

  return os.path.abspath(os.path.join(basedir or dir.base,path))
    
class setting:    
    """Configuration of hardcoded settings"""
    
    VERSION='2.3'
    
    WS_VERSION="0.4"
    WS_MINIMUM_VERSION="0.3"
    
    DATETIME_FORMAT='%Y%m%d%H%M%S'
    DATE_FORMAT='%Y%m%d'
    
    DATE_PRESENTATION_FORMAT='%a, %d %b %Y'
    
    DATETIME_PRESENTATION_FORMAT='%a, %d %b %Y %H:%M:%S (%Z)'
    TIME_PRESENTATION_FORMAT='%H:%M:%S (%Z)'
    
    UTC_DATETIME_PRESENTATION_FORMAT='%a, %d %b %Y %H:%M:%S (UTC)'
    UTC_TIME_PRESENTATION_FORMAT='%H:%M:%S (UTC)'
    
    TIMEOUT=60*60 # 60 minutes (in seconds)
    if 'GUMP_TIMEOUT' in os.environ:
            TIMEOUT = string.atoi(os.environ['GUMP_TIMEOUT'])
    
class default:
    """Configuration of default settings"""
    
    gumpfullhost = socket.gethostname()   
    gumphost     = socket.gethostname().split('.')[0]
    gumpid       = os.getpid()    
    workspace    = os.path.abspath('%s/%s.xml' % (dir.base, gumphost))
    globalws     = os.path.abspath('%s/%s' % (dir.base, 'global-workspace.xml'))
    merge        = os.path.abspath('%s/%s' % (dir.work, 'merge.xml'))
    
    # Note, these can be updated by gumpinit
    timestamp    = time.time()
    datetime     = datetime.datetime.fromtimestamp(timestamp)
    datetime_str = datetime.strftime(setting.DATETIME_FORMAT)
    date_str     = datetime.strftime(setting.DATE_FORMAT)
    
    logLevel     = logging.INFO # logging.DEBUG
    classpath    = (os.getenv('CLASSPATH') or '').split(os.pathsep)  
    
    bannerimage  = 'http://gump.apache.org/images/gump-logo.png'
    
    email = 'gump@' + gumpfullhost
    administrator = 'general@gump.apache.org'
    mailserver = 'mail.apache.org'
    mailport = 25
    prefix = '[GUMP@' + gumphost + ']'
    signature="\r\n--\r\nApache Gump\nhttp://gump.apache.org/ " \
        + '[Instance: ' + gumpfullhost + "]\n"

    mvnRepoProxyPort = '8192'
        
    # Information for portability
    if not os.name == 'dos' and not os.name == 'nt':
        classpathSeparator=':'
        shellQuote='\''
        shellEscape='\\'
    else:
        classpathSeparator=';'
        shellQuote='"'
        shellEscape='\\'

class switch:
    """Configuration of switches """   
    optimize        = False # Optimize (at risk to exact correctness) anywhere one can
    optimizenetwork = False # Do least network traffic 
    debugging       = False # Not debugging..
    
def basicConfig():
    if not os.path.exists(dir.cache): os.mkdir(dir.cache)
    if not os.path.exists(dir.work): os.mkdir(dir.work)
    if not os.path.exists(dir.tmp): os.mkdir(dir.tmp)
    if not os.path.exists(dir.test): os.mkdir(dir.test)

    if dir.base not in sys.path: 
        sys.path.insert(0, dir.base)

if __name__ == '__main__':
  def dump(section):
    print()
    print(("---", str(section).split('.')[-1], "---"))
    for attr in __builtins__.dir(section):
      if attr == '__module__': continue
      print((" ", attr + ":\t" + getattr(section, attr).__repr__()))

  for section in sys.argv[1:] or ('dir','default','setting','switch'):
    dump(locals()[section])
