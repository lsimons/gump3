#!/usr/bin/python

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


"""
    This is one commandline entrypoint into gump.

    The workspace is metadata loaded then various
    projects are built. No source control updates
    are performed. 

"""

import os.path
import sys

from gump import log
from gump.core.gumpinit import gumpinit
from gump.core.gumprun import *
from gump.core.commandLine import handleArgv
from gump.runner.runner import getRunner
from gump.loader.loader import WorkspaceLoader


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
        
    # Ensure we use text, not forrest...
    options.setText(1)
    
    # 
    options.setObjectives(OBJECTIVE_BUILD)
    
    # The Run Details...
    run=GumpRun(workspace,ps,options)
        
    #
    #    Perform this integration run...
    #
    result = getRunner(run).perform()
    
    #
    log.info('Gump Build complete. Exit code:' + str(result))
          
    # bye!
    sys.exit(result)