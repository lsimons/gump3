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
  
  if not projects:
      log.error("No projects matching expression: " + expr)
      sys.exit(1)
  
  missing=[]
  optionalMissing=[]
  optionalOnlyMissing=[]
  
  # for each project
  for project in projects:
    displayStack(project,1)
    
    # pctxt=context.getProjectContextForProject(project)    
    #
    #printSeparator()
    #pctxt.tree()
    #printSeparator()
    #dump(project)
    #printSeparator()
    #print "Dependencies : " + str(pctxt.dependencyCount())
    #print "Direct Dependencies : " + str(pctxt.depends)
    #print "Dependencies : " + str(pctxt.getDepends())
    #print "Dependees    : " + str(pctxt.dependeeCount())
    #print "Direct Dependees    : " + str(pctxt.dependees)
    #print "Dependees    : " + str(pctxt.getDependees())
    
  printSeparator()
  
  todo=getBuildSequenceForProjects(projects)
  for project in todo:
    print "Project: " + project.name
    
  
    
def displayStack(project,recurse=None,indent=""):
    printSeparator()    
    print indent+"Dependency Stack For: " + project.name
    shown=[]
    displayFullStack(project,recurse,indent,shown)
    printSeparator()    
    print indent+"Build Sequence For: " + project.name
    for dependency in getBuildSequenceForProjects([project]):
        print indent + "- " + dependency.name    
    printSeparator()
    
def displayFullStack(project,recurse=None,indent="",shown=[]):
    for dependency in getBuildSequenceForProjects([project]):
        if not dependency.name==project.name:
            if not dependency in shown :
                print indent + "- " + dependency.name
                shown.append(dependency)
                if recurse:
                    displayFullStack(dependency,recurse,indent+'  ')
            else:
                print indent + "+ " + dependency.name + " ..."
                

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
