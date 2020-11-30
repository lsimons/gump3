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
# $Header: /home/stefano/cvs/gump/python/gump/preview.py,v 1.9 2004/07/28 15:50:29 ajack Exp $
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
from gump.core.run.gumprun import GumpRun
from gump.core.run.gumpset import GumpSet
from gump.core.run.options import GumpRunOptions
from gump.core.commandLine import handleArgv
from gump.core.loader.loader import WorkspaceLoader

from gump.util.note import Annotatable

from gump.core.runner.runner import getRunner

###############################################################################
# Initialize
###############################################################################

SEPARATOR='-------------------------------------------------------------'

###############################################################################
# Functions
###############################################################################
    
def prun():
    gumpinit()    
    
    # Process command line
    (args,options) = handleArgv(sys.argv)
    ws=args[0]
    ps=args[1]
    
    result=0
    
    # get parsed workspace definition
    workspace=WorkspaceLoader(options.isCache()).load(ws) 
    
    # The Run Details...
    run=GumpRun(workspace,ps,options)    
    run.dump()
    
    debug=run.getOptions().isDebug()
    verbose=run.getOptions().isVerbose()
     
    # :TODO: Show the environment
     
    if verbose:  
        # Show the workings
        runner=getRunner(run)
        
        #
        updater=runner.getUpdater()
        builder=runner.getBuilder()
        languageHelper=runner.getJavaHelper()
            
        for module in run.getGumpSet().getModules():
            print(SEPARATOR)
            print(repr(module))
            if debug:
                print(module.getXml())
            module.dump()
            if module.isUpdatable():
                updater.preview(module)
                       
        for project in run.getGumpSet().getProjects():
            print(SEPARATOR)
            print(repr(project))
            if debug:
                print(project.getXml())
            project.dump()
            if project.hasBuilder():
                builder.preview(project, languageHelper)
    
    # Show any nasties...
    if workspace.containsNasties():
        print(SEPARATOR)    
        print(repr(workspace))    
        Annotatable.dump(workspace)
    for module in run.getGumpSet().getModules():
        if module.containsNasties():
            print(SEPARATOR)    
            print(repr(module))    
            Annotatable.dump(module)
    for project in run.getGumpSet().getProjects():
        if project.containsNasties():
            print(SEPARATOR)    
            print(repr(project))    
            Annotatable.dump(project)
            
    # bye!
    sys.exit(result)
    
    
# static void main()
if __name__=='__main__':

    #print 'Profiling....'
    #import profile
    #profile.run('prun()', 'iprof')
    prun()
    
