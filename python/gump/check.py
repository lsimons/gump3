#!/usr/bin/python
"""
  Checks that the Gump definitions are ok.
"""

import os.path
import os
import sys
import logging

from gump import load, buildSequence
from gump.conf import dir, default
from gump.model import Workspace, Module, Project

###############################################################################
# Initialize
###############################################################################

# base gump logger
log = logging.getLogger(__name__)

###############################################################################
# Functions
###############################################################################

def check(workspace, projectname):

  missing=[]
  optionalMissing=[]
  optionalOnlyMissing=[]
  
  # for each project
  for projectname in Project.list:
    projectmissing = 0
    print    
    print " TESTING " + projectname + " ************* "
    project = Project.list[projectname]
    
    # for each dependency in current project
    for depend in project.depend:
      # if the dependency is not present in the projects, it's missing
      if depend.project not in Project.list:
        projectmissing+=1
        print "  missing: "+depend.project
        if depend.project not in missing:
          missing.append(depend.project)  
            
    for depend in project.option:
      # if the dependency is not present in the projects, it's missing
      if depend.project not in Project.list:
        projectmissing+=1
        print "  optional missing: "+depend.project
        if depend.project not in optionalMissing:
          optionalMissing.append(depend.project)
            
    if projectmissing>0:
      print "  total errors: " , projectmissing

  if len(optionalMissing)>0:
    print
    print " ***** MISSING OPTIONAL *ONLY* PROJECTS THAT ARE REFRENCED ***** "
    print
    for missed in optionalMissing:
      if missed not in missing:
        optionalOnlyMissing.append(missed)
        print "  " + missed
      
  if len(missing)>0:
    print
    print " ***** MISSING PROJECTS THAT ARE REFRENCED ***** "
    print
    for missed in missing:
      print "  " + missed

  #peekInGlobalProfile(missing);
  
  print
  print " ***** RESULT ***** "  
  print
  if len(missing)>0:
    print
    print "  - ERROR - Some projects that were referenced are missing in the workspace. "  
    print "    See the above messages for more detailed info."
  else:
    print "  -  OK - All projects that are referenced are present in the workspace."  

  if len(optionalOnlyMissing)>0:
    print  
    print "  - WARNING - Some projects that were referenced as optional only are "
    print "    missing in the workspace. "  
    print "    See the above messages for more detailed info."
  else:
    print "  -  OK - All OPTIONAL projects that are referenced are present in the workspace."  
    print " ***** RESULT ***** "

    
  return 0
  
def peekInGlobalProfile(missing):

  workspace=load(default.globalws)
  
  for missed in missing:
    print "  " + missed
    if(missed in Project.list):
      print "found: " , missed
  

# static void main()
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)
  
  # load commandline args or use default values
  if len(sys.argv)>1 :
    ws=sys.argv[1]
  else:
    ws=default.workspace

  if len(sys.argv)>2 :
    ps=sys.argv[2]
  else:
    ps=default.project

  # get parsed workspace definition
  workspace=load(ws)

  # check
  result = check(workspace, ps);

  # bye!
  sys.exit(result)
