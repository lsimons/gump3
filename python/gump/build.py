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

from gump import log
from gump.engine import GumpEngine
from gump.gumprun import GumpRun, GumpRunOptions, GumpSet
from gump.utils.commandLine import handleArgv
from gump.model.loader import WorkspaceLoader


###############################################################################
# Initialize
###############################################################################


###############################################################################
# Functions
###############################################################################

# static void main()
if __name__=='__main__':

    # Process command line
    (args,options) = handleArgv(sys.argv)
    ws=args[0]
    ps=args[1]

    # get parsed workspace definition
    workspace=WorkspaceLoader().load(ws, options.isQuick())
      
    #
    # Check Environment (eventually not do this each time)
    # Exit if problems...
    #
    #checkEnvironment(workspace,context,1)
        
    #
    # Check projects (and such) in workspace...
    # Store results in context, do not display
    # to screen.
    #
    #check(workspace, ps, context, 0)    
    
    # The Run Details...
    run=GumpRun(workspace,ps,options)
    
    engine=GumpEngine()
    
    #
    #    Perform this integration run...
    #
    if '*' in args:
        result = engine.buildAll(run)
    else:
        result = engine.buildProjects(run)

    #
    log.info('Gump Build complete. Exit code:' + str(result))
          
    # bye!
    sys.exit(result)