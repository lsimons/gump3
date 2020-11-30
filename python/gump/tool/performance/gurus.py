#!/usr/bin/python

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

"""    
    Does lots of guru stuff (for performance tuning) 
"""

import os.path
import sys

from gump import log
from gump.core.gumpinit import gumpinit
from gump.test import getWorkedTestRun
from gump.tool.guru.stats import StatisticsGuru
from gump.tool.guru.xref import XRefGuru
from gump.core.commandLine import handleArgv
from gump.core.run.gumprun import GumpRun
from gump.core.loader.loader import WorkspaceLoader

def gurus(run,runs=1):
    
    for r in range(runs):   
        print('Perform run # ' + repr(r))
        log.info('Generate Statistic Guru')
        stats=StatisticsGuru(run.getWorkspace())
        log.info('Generate XRef Guru')
        xref=XRefGuru(run.getWorkspace())    
        
def xrun():
    gumpinit()
   
    if len(sys.argv) > 1:
        # Process command line
        (args,options) = handleArgv(sys.argv)
        ws=args[0]
        ps=args[1]    
        
        # get parsed workspace definition
        workspace=WorkspaceLoader(options.isCache()).load(ws)    
        
        
        # Load statistics for this workspace
        from gump.actor.stats.statsdb import StatisticsDB
        db=StatisticsDB('test','test.db')  
        db.loadStatistics(workspace)
        
        from gump.actor.document.xdocs.resolver import XDocResolver
        options.setResolver(XDocResolver('./test/bogus','http://bogus.org/'))
        
        # The Run Details...
        run=GumpRun(workspace,ps,options)
    else:
        run=getWorkedTestRun()    
        
    gurus(run,100) 
    
    # bye!
    sys.exit(0)
    
# static void main()
if __name__=='__main__':

    #print 'Profiling....'
    #import profile
    #profile.run('xrun()', 'iprof')
    xrun()
     
