#!/usr/bin/python
"""
  Display the Gump definitions
"""

import os.path
import os
import sys
import traceback
import logging

from gump import log, load
from gump.logic import getBuildSequenceForProjects, getProjectsForProjectExpression
from gump.conf import dir, default, handleArgv
from gump.model import Workspace, Module, Project
from gump.context import GumpContext
from gump.utils import *

###############################################################################
# Initialize
###############################################################################


###############################################################################
# Functions
###############################################################################

def display(workspace, expr='*', context=GumpContext()):
  """dump all dependencies to build a project to the output"""

  projects=getProjectsForProjectExpression(expr)
  
  missing=[]
  optionalMissing=[]
  optionalOnlyMissing=[]
  
  # for each project
  for project in projects:
    displayStack(project)
    
    pctxt=context.getProjectContextForProject(project)    
    
    pctxt.tree()
    dump(project)
    print "Dependencies : " + str(pctxt.dependencyCount())
    print "Direct Dependencies : " + str(pctxt.depends)
    print "Dependencies : " + str(pctxt.getDepends())
    print "Dependees    : " + str(pctxt.dependeeCount())
    print "Direct Dependees    : " + str(pctxt.dependees)
    print "Dependees    : " + str(pctxt.getDependees())
    
    
def displayStack(project,indent="",recurse=None):
    print " Dependency Stack For: " + project.name
    for dependency in getBuildSequenceForProjects([project]):
        if not dependency.name==project.name:
            print indent + " - " + dependency.name
            if recurse:
                displayStack(dependency,indent+'  ',recurse)
                

# static void main()
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)
  
  args = handleArgv(sys.argv,0)
  ws=args[0]
  ps=args[1]


  context=GumpContext()
  
  # get parsed workspace definition
  workspace=load(ws, context)

  # check
  result = display(workspace, ps, context);

  # bye!
  sys.exit(result)
