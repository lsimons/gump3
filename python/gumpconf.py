#!/usr/bin/python
"""
    Global configuration settings for gump, done as Python classes
"""

import socket, time, os, os.path,sys

class dir:
    cmdpath   = os.path.abspath(sys.argv[0])
    base      = os.path.normpath('%s/%s' % (os.path.dirname(cmdpath),'..'))
    cache     = os.path.normpath('%s/%s' % (base,'cache'))
    work      = os.path.normpath('%s/%s' % (base,'work'))

    if not os.path.exists(cache): os.mkdir(cache)
    if not os.path.exists(work): os.mkdir(work)
    
    if base not in sys.path: sys.path.insert(0, base)
    
class default:
    workspace  = os.path.normpath('%s/%s.xml' % (dir.base, socket.gethostname().split('.')[0]))
    project    = "krysalis-ruper-test"
    merge      = os.path.normpath('%s/%s' % (dir.work, 'merge.xml'))
    date       = time.strftime('%Y%m%d')
    antCommand = 'java org.apache.tools.ant.Main -Dbuild.sysclasspath=only'
    syncCommand= 'cp -Rf'

