#!/usr/bin/python
"""
	Configuration for Gump, done as Python classes
"""

import socket

class dir:
   base      = ".."
   cache     = "cache"
   work      = "work"

class default:
  workspace  = socket.gethostname().split('.')[0] + ".xml"
  project    = "krysalis-ruper-test"
  merge      = "merge.xml"

