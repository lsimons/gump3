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
    Checks that the Gump definitions are ok.
    
    The workspace is loaded into memory, rudimentary
    checks occur, and the output tree is documented
    (e.g. via forrest).
    
"""

import os.path
import sys

from gump import log
from gump.core.gumpinit import gumpinit
from gump.runner.runner import getRunner
import gump.run.options
import gump.run.gumprun
from gump.core.commandLine import handleArgv
from gump.loader.loader import WorkspaceLoader

def crun():
    gumpinit()
    
    # Process command line
    (args,options) = handleArgv(sys.argv)
    ws=args[0]
    ps=args[1]
    
    # get parsed workspace definition
    workspace=WorkspaceLoader(options.isQuick()).load(ws)
    
    # 
    options.setObjectives(gump.run.options.OBJECTIVE_CHECK)    
    
    # The Run Details...
    run=gump.run.gumprun.GumpRun(workspace,ps,options)
    
    #
    #    Perform this check run...
    #
    result = getRunner(run).perform()

    #
    log.info('Gump Check complete. Exit code:' + str(result))
          
    # bye!
    sys.exit(result)
    
    
# static void main()
if __name__=='__main__':

    #print 'Profiling....'
    #import profile
    #profile.run('crun()', 'iprof')
    crun()
    