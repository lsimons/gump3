#!/usr/bin/python
"""
  This is the commandline entrypoint into gump.

  It at the moment basically
  calls gump.load() to get the workspace, then dumps
  information about what it should be doing to stdout.

  The main thing to do here is to clone dumpDeps to create a
  build() method which executes the appropriate script
  (probably only ant at the moment; would be nice to have
  support for maven) for each of the dependencies.
"""

import os.path
import os
import sys
import logging

from gump import log, load
from gump.conf import dir, default, handleArgv
from gump.model import Workspace, Module, Project
from gump.context import *
from gump.update import update
from gump.build import build
from gump.document import document
from gump.nag import nag
from gump.utils import dump, display
from gump.statistics import *
from gump.logic import *

###############################################################################
# Initialize
###############################################################################


###############################################################################
# Functions
###############################################################################
def preprocess(workspace,expr='*',context=GumpContext()):

    #
    # Store for later
    #
    context.projectexpression=expr
    
    
    
  #modules = getModulesForProjectList(getBuildSequenceForProjects(getProjectsForProjectExpression(expr)))
  #for module in modules:      
    
    # Mark all packages as not needing building... 
    projects=getProjectsForProjectExpression(expr)
    for p in projects:
        if p.package:
            pctxt = context.getProjectContextForProject(p)
            pctxt.state=STATUS_COMPLETE
            pctxt.reason=REASON_PACKAGE
      
    
def integrate(workspace,expr='*',context=GumpContext()):
  
  preprocess(workspace,expr,context)
  update(workspace,expr,context)
  build(workspace,expr,context)
  
  # Update Statistics
  statistics(workspace,context)
  
  # Build HTML Result (via Forrest)
  document(workspace,context,1)
  
  # Nag about failures
  nag(workspace,context)
  
  #display(context)
  
  result = context.status

# static void main()
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)

  args = handleArgv(sys.argv)
  ws=args[0]
  ps=args[1]
  
  context=GumpContext()
  
  # get parsed workspace definition
  workspace=load(ws,context)
   
  #
  result = integrate(workspace, ps, context)

  # bye!
  sys.exit(result)
