#!/usr/bin/env python

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"


#
# $Header: /home/stefano/cvs/gump/python/gump/integrate.py,v 1.31 2004/07/19 16:07:53 ajack Exp $
# 

"""
    This is the main commandline entrypoint into gump.

    It updates modules/projects, builds, and publishes results
        
"""

import os.path
import os
import sys

from gump import log
from gump.core.gumpinit import gumpinit
from gump.core.runner.runner import getRunner
import gump.core.run.options
import gump.core.run.gumprun
from gump.core.commandLine import handleArgv
from gump.util import logResourceUtilization
from gump.core.loader.loader import WorkspaceLoader


###############################################################################
# Initialize
###############################################################################

###############################################################################
# Functions
###############################################################################

def ignoreHangup(signum):
    pass
    
def irun():
    
    gumpinit()  
    
    # Process command line
    (args,options) = handleArgv(sys.argv)
    ws=args[0]
    ps=args[1]    
                
    logResourceUtilization('Before load workspace')
        
    # get parsed workspace definition
    workspace=WorkspaceLoader(False).load(ws)

    logResourceUtilization('Before create run')
    
    # Has to be absolute latest descriptors, not quick/cached...
    options.setQuick(False)
    options.setCache(False)
    
    if 'GUMP_WORK_OFFLINE' not in os.environ:
      options.setObjectives(gump.core.run.options.OBJECTIVE_INTEGRATE)
    else:
      options.setCache(True)
      options.setObjectives(gump.core.run.options.OBJECTIVE_OFFLINE)
    
    
    # The Run Details...
    run=gump.core.run.gumprun.GumpRun(workspace,ps,options)
    
    #    Perform this integration run...
    result = getRunner(run).perform()

    logResourceUtilization('Before exit')
    
    #
    log.info('Gump Integration complete. Exit code [0=SUCCESS] : ' + str(result))                  
          
    # bye!
    sys.exit(result)
    
# static void main()
if __name__=='__main__':
    
    # Set the signal handler to ignore hangups
    try:
        # Not supported by all OSs
        signal.signal(signal.SIG_HUP, ignoreHangup)
    except:
        pass

    #print 'Profiling....'
    #import profile
    #profile.run('irun()', 'iprof')
    irun()
