#!/usr/bin/python

# $Header: /home/stefano/cvs/gump/proposals/aj_python/gump/Attic/build.py,v 1.1 2003/08/21 19:38:14 nickchalko Exp $
# $Revision: 1.1 $
# $Date: 2003/08/21 19:38:14 $
#
# ====================================================================
#
# The Apache Software License, Version 1.1
#
# Copyright (c) 2003 The Apache Software Foundation.  All rights
# reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. The end-user documentation included with the redistribution, if
#    any, must include the following acknowlegement:
#       "This product includes software developed by the
#        Apache Software Foundation (http://www.apache.org/)."
#    Alternately, this acknowlegement may appear in the software itself,
#    if and wherever such third-party acknowlegements normally appear.
#
# 4. The names "The Jakarta Project", "Alexandria", and "Apache Software
#    Foundation" must not be used to endorse or promote products derived
#    from this software without prior written permission. For written
#    permission, please contact apache@apache.org.
#
# 5. Products derived from this software may not be called "Apache"
#    nor may "Apache" appear in their names without prior written
#    permission of the Apache Group.
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
# ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# ====================================================================
#
# This software consists of voluntary contributions made by many
# individuals on behalf of the Apache Software Foundation.  For more
# information on the Apache Software Foundation, please see
# <http://www.apache.org/>.

"""

  This is the commandline entrypoint into gump for 'building'.

  Note: CVS 'updating' is a pre-requisite.

"""

import os.path
import os
import sys
import logging

from gump import log, load
from gump.context import *
from gump.logic import getBuildSequenceForProjects, getBuildCommand, getProjectsForProjectExpression
from gump.conf import dir, default, handleArgv
from gump.model import Workspace, Module, Project
from gump.launcher import Cmd, CmdResult, execute
from gump.utils import dump

###############################################################################
# Initialize
###############################################################################


###############################################################################
# Functions
###############################################################################

def build(workspace, expr='*', context=GumpContext()):
  """dump all dependencies to build a project to the output"""

  projects=getProjectsForProjectExpression(expr)
  
  # if the project is not there, exit with error
  if not projects:
    print
    print "The project expresion '"+expr+"' does not match the workspace's projects."
    print "Available projects:"
    for p in Project.list:
        print "  - " + p
    return 1

  log.info('Requests Projects')
  for p in projects:
    log.info('  - ' + p.name)
    
  sequence=getBuildSequenceForProjects(projects)
  
  log.info('Total Sequence (i.e. build order):');
  for p in sequence:
    log.info('  - ' + p.name)

  # synchronize
  syncWorkDir( workspace, sequence, context )

  # build
  buildProjects( workspace, sequence, context )
  
  return context.status


def syncWorkDir( workspace, sequence, context=GumpContext() ):
  """copy the raw project materials from source to work dir (hopefully using rsync, cp is fallback)"""

  log.info('--- Synchronizing work directories with sources')

  for project in sequence:
      
    (mctxt,pctxt) = context.getContextsForProject(project)
      
    if pctxt.okToPerformWork():
        module=Module.list[project.module];
        sourcedir = os.path.normpath(os.path.join(workspace.cvsdir,module.name)) # todo allow override
        # destdir = os.path.normpath(os.path.join(workspace.basedir,module.name))
        destdir = os.path.normpath(workspace.basedir)

        # if not os.path.exists(destdir) : os.mkdir(destdir)

        # :TODO: Make this configurable (once again)
        #if not workspace.sync:
        #  workspace.sync = default.syncCommand
    
        cmd=Cmd('cp','sync_'+module.name,dir.work)
        cmd.addParameter('-Rf')
        cmd.addParameter(sourcedir)
        cmd.addParameter(destdir)

        log.debug(' ------ Sync\'ing : '+ module.name + ':' + project.name)
    
        # Perform the Sync
        cmdResult=execute(cmd)

        work=CommandWorkItem(WORK_TYPE_SYNC,cmd,cmdResult)
        pctxt.performedWork(work)

        # Update Context w/ Results  
        if not cmdResult.status==CMD_STATUS_SUCCESS:
            pctxt.propagateState(STATUS_FAILED,REASON_BUILD_FAILED)
        else:
            pctxt.status=STATUS_SUCCESS
    else:
        pctxt.propagateState(pctxt.status,pctxt.reason)

def buildProjects( workspace, sequence, context=GumpContext() ):
  """actually perform the build of the specified project and its deps"""

  log.info('--- Building work directories with sources')

  # build all projects this project depends upon, then the project itself
  for project in sequence:

    (mctxt,pctxt) = context.getContextsForProject(project)
    
    if pctxt.okToPerformWork():
        
        # get the module object given the module name,
        # which is gotten from the project
        module=Module.list[project.module]

        log.debug(' ------ Building: '+ module.name + ':' + project.name)

        cmd=getBuildCommand(workspace,module,project)

        if cmd:
            # Execute the command ....
            cmdResult=execute(cmd)
    
            # Update Context    
            work=CommandWorkItem(WORK_TYPE_BUILD,cmd,cmdResult)
            pctxt.performedWork(work)

            # Update Context w/ Results  
            if not cmdResult.status==CMD_STATUS_SUCCESS:
                pctxt.propagateState(STATUS_FAILED,REASON_BUILD_FAILED)
            else:
                outputsOk=1
                for i in range(0,len(project.jar)):
                    jar=project.jar[i].path
                    if jar:
                        if not os.path.exists(jar):
                            pctxt.propagateState(STATUS_FAILED,REASON_BUILD_FAILED)
                            outputsOk=0
                            pctxt.addMessage("Missing Output: " + str(jar.path))

                if outputsOk: pctxt.status=STATUS_SUCCESS                
    else:
        pctxt.propagateState(pctxt.status,pctxt.reason)

# static void main()
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)

  args = handleArgv(sys.argv)
  ws=args[0]
  ps=args[1]
  
  # get parsed workspace definition
  workspace=load(ws)
  
  # run gump
  result = build(workspace, ps);

  # bye!
  sys.exit(result)
