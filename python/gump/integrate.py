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
from gump.check import checkEnvironment
from gump.context import *
from gump.update import updateModules
from gump.build import buildProjectSequence
from gump.document import document
from gump.nag import nag
from gump.utils import dump, display
from gump.statistics import *
from gump.logic import *
from gump.rss import rss

###############################################################################
# Initialize
###############################################################################


###############################################################################
# Functions
###############################################################################
def preprocess(workspace,expr='*',context=GumpContext()):

    #
    # Perform start-up logic 
    #
    preprocessContext(workspace,context)
    
    #
    # Store for later
    #
    context.gumpset=getGumpSetForProjectExpression(expr)
    
    
def integrate(workspace,expr='*',context=GumpContext()):
        
    projects=getProjectsForProjectExpression(expr)
    sequence=getBuildSequenceForProjects(projects)
    modules=getModulesForProjectList(sequence)  
  
    #
    # Prepare the context tree
    #
    preprocess(workspace,expr,context)
  
    #
    # Checkout from source code repositories
    #
    updateModules(workspace,modules,context)
  
    #
    # Run the build commands
    #
    buildProjectSequence(workspace,sequence,context)
  
    #
    # Only an 'all' is an official build...
    #
    if '*' == expr or 1:	# Testing
        # Update Statistics
        statistics(workspace,context)
  
        # Build HTML Result (via Forrest)
        if not context.noForrest:
            document(workspace,context,1,modules,sequence)
            #document(workspace,context,1)
  
        # Nag about failures
        # nag(workspace,context)
  
        # Provide a news feed
        rss(workspace,context)

    # Return an exit code based off success
    if stateOk(context.status):
        result = 0 
    else: 
        result = 1

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
    # Check Environment (eventually not do this each time)
    #
    checkEnvironment(workspace,context)
    
    #
    result = integrate(workspace, ps, context)

    # bye!
    sys.exit(result)