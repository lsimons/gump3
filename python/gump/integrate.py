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


"""
    This is the main commandline entrypoint into gump.

    It updates modules/projects, builds, and publishes results
        
"""

import os.path
import os
import sys
import logging

from gump import log
from gump.engine import GumpEngine
from gump.gumprun import GumpRun, GumpRunOptions, GumpSet
from gump.utils.commandLine import handleArgv
from gump.utils import logResourceUtilization
from gump.model.loader import WorkspaceLoader


###############################################################################
# Initialize
###############################################################################

###############################################################################
# Functions
###############################################################################

def irun():
    
    # Process command line
    (args,options) = handleArgv(sys.argv)
    ws=args[0]
    ps=args[1]    
                
    logResourceUtilization('Before load workspace')
        
    # get parsed workspace definition
    workspace=WorkspaceLoader().load(ws, 0)

    logResourceUtilization('Before create run')
    
    # Has to be absolute latest descriptors, not cached...
    options.setQuick(0)
    
    # The Run Details...
    run=GumpRun(workspace,ps,options)
    
    #
    #    Perform this integration run...
    #
    result = GumpEngine().integrate(run)

    logResourceUtilization('Before exit')
    
    #
    log.info('Gump Integration complete. Exit code:' + str(result))                  
          
    # bye!
    sys.exit(result)
    
# static void main()
if __name__=='__main__':
    #print 'Profiling....'
    #import profile
    #profile.run('irun()', 'iprof')
    irun()
