#!/usr/bin/env python

# Copyright 2003-2004 The Apache Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# $Header: /home/stefano/cvs/gump/python/gump/update.py,v 1.31 2004/07/19 16:07:53 ajack Exp $
# 

"""
  This is one commandline entrypoint into Gump.

  It loads the workspace, then updates the specified modules.
  
"""

import os.path
import os
import sys
import logging

from gump import log
from gump.core.gumpinit import gumpinit
from gump.runner.runner import getRunner
import gump.run.options
from gump.run.gumprun import *
from gump.core.commandLine import handleArgv
from gump.loader.loader import WorkspaceLoader


###############################################################################
# Initialize
###############################################################################


###############################################################################
# Functions
###############################################################################

# static void main()
if __name__=='__main__':

    gumpinit()    
    
    # Process command line
    (args,options) = handleArgv(sys.argv)
    ws=args[0]
    ps=args[1]
    
    # get parsed workspace definition
    workspace=WorkspaceLoader(options.isCache()).load(ws) 
    
    # Ensure we use text, not xdocs...
    options.setText(True)
    
    # 
    options.setObjectives(gump.run.options.OBJECTIVE_UPDATE)    
    
    # The Run Details...
    run=GumpRun(workspace,ps,options)
    
    #
    #    Perform this integration run...
    #
    result = getRunner(run).perform()

    #
    log.info('Gump Update complete. Exit code:' + str(result))
          
    # bye!
    sys.exit(result)