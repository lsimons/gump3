#!/usr/bin/python
"""
        Global configuration settings for gump, done as Python classes
"""

import socket, time

class dir:
   base      = ".."
   cache     = "cache"
   work      = "work"

class default:
  workspace  = socket.gethostname().split('.')[0] + ".xml"
  project    = "krysalis-ruper-test"
  merge      = "merge.xml"
  date       = time.strftime('%Y%m%d')
  debug      = 1
  antCommand = 'java org.apache.tools.ant.Main -Dbuild.sysclasspath=only'
  syncCommand= 'cp -Rf'
  
