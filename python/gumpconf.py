#!/usr/bin/python
"""
    Global configuration settings for gump, done as Python classes
"""

import socket, time, os.path, sys

class dir:
    cmdpath   = os.path.abspath(sys.argv[0])
    base      = os.path.normpath('%s/%s' % (os.path.dirname(cmdpath),'..'))
    cache     = os.path.normpath('%s/%s' % (base,'cache'))
    work      = os.path.normpath('%s/%s' % (base,'work'))

    if not os.path.exists(cache): os.path.mkdir(cache)
    if not os.path.exists(work): os.path.mkdir(work)
    
    if base not in sys.path: sys.path.insert(0, base)
    
class default:
    workspace  = socket.gethostname().split('.')[0] + ".xml"
    project    = "krysalis-ruper-test"
    merge      = "merge.xml"
    date       = time.strftime('%Y%m%d')
    debug      = True
    antCommand = 'java org.apache.tools.ant.Main -Dbuild.sysclasspath=only'
    syncCommand= 'cp -Rf'

