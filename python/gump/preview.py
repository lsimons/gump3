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
# $Header: /home/stefano/cvs/gump/python/gump/preview.py,v 1.8 2004/07/19 16:07:53 ajack Exp $
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
from gump.run.gumprun import GumpRun
from gump.run.gumpset import GumpSet
from gump.run.options import GumpRunOptions
from gump.core.commandLine import handleArgv
from gump.loader.loader import WorkspaceLoader

from gump.utils.note import Annotatable

from gump.runner.runner import getRunner

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
        updater=runner.getUpdater()
        builder=runner.getBuilder()
            
        for module in run.getGumpSet().getModules():
            print SEPARATOR
            print `module`
            if debug:
                print module.getXml()
            module.dump()
            if module.isUpdatable():
                updater.preview(module)
                       
        for project in run.getGumpSet().getProjects():
            print SEPARATOR
            print `project`
            if debug:
                print project.getXml()
            project.dump()
            if project.hasBuilder():
                builder.preview(project)
    
    # Show any nasties...
    if workspace.containsNasties():
        print SEPARATOR    
        print `workspace`    
        Annotatable.dump(workspace)
    for module in run.getGumpSet().getModules():
        if module.containsNasties():
            print SEPARATOR    
            print `module`    
            Annotatable.dump(module)
    for project in run.getGumpSet().getProjects():
        if project.containsNasties():
            print SEPARATOR    
            print `project`    
            Annotatable.dump(project)
            
    # bye!
    sys.exit(result)
    
    
# static void main()
if __name__=='__main__':

    #print 'Profiling....'
    #import profile
    #profile.run('prun()', 'iprof')
    prun()
    