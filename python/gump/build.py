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
import os
import sys
import logging

from gump import log
from gump.engine import GumpEngine
from gump.gumprun import GumpRun, GumpRunOptions, GumpSet
from gump.utils.commandLine import handleArgv
from gump.model.loader import WorkspaceLoader


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
    
    
    # The Run Details...
    run=GumpRun(workspace,ps,options)
        
    #
    #    Perform this integration run...
    #
    result = GumpEngine().build(run, '*' in args)
    
    #
    log.info('Gump Build complete. Exit code:' + str(result))
          
    # bye!
    sys.exit(result)