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
# $Header: /home/stefano/cvs/gump/python/gump/preview.py,v 1.3 2004/04/30 18:55:07 ajack Exp $
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
from gump.core.gumprun import GumpRun, GumpRunOptions, GumpSet
from gump.core.commandLine import handleArgv
from gump.model.loader import WorkspaceLoader


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
    
    result=0
    
    # get parsed workspace definition
    workspace=WorkspaceLoader().load(ws, options.isCache()) 
    
    # The Run Details...
    run=GumpRun(workspace,ps,options)    
    run.dump()
    
    # Display some interesting things...
    # E.g. command lines, env
    # :TODO:
        
    for module in run.getGumpSet().getModules():
        print "-------------------------------------------------------------"
        print "Module : " + `module` + "\n"
        if module.isUpdatable():
            (repository, root, command ) = module.getUpdateCommand(0)
            command.dump()
            
            (repository, root, command ) = module.getUpdateCommand(1)
            command.dump()                                  
        
    for project in run.getGumpSet().getProjects():
        print "-------------------------------------------------------------"
        print "Project : " + `project` + "\n"
        if project.hasBuildCommand():
            command=project.getBuildCommand() 
            command.dump()
            
    # bye!
    sys.exit(result)