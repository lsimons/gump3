#!/usr/bin/python

# $Header: /home/stefano/cvs/gump/python/gump/build.py,v 1.11 2003/09/23 15:13:08 ajack Exp $
# $Revision: 1.11 $
# $Date: 2003/09/23 15:13:08 $
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
from gump.logic import getBuildSequenceForProjects, getBuildCommand, getProjectsForProjectExpression, getModulesForProjectList
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
  """ Build a expression of projects """

  projects=getProjectsForProjectExpression(expr)
  
  # if the project is not there, exit with error
  if not projects:
    print
    print "The project expresion '"+expr+"' does not match the workspace's projects."
    print "Available projects:"
    for p in Project.list:
        print "  - " + p
    return 1

  return buildProjectList(workspace,projects,context)
  
def buildProjectList(workspace, projects, context=GumpContext()):
  """ Build a expression of projects """
        
  log.info('Requests Projects')
  for p in projects:
    log.info('  Requested : ' + p.name)
    
  sequence=getBuildSequenceForProjects(projects)

  return buildProjectSequence(workspace,sequence,context)
  
def buildProjectSequence(workspace,sequence,context=GumpContext()):
    
  log.info('Total Project Sequence (i.e. build order):');
  for p in sequence:
    log.info('  Sequence : ' + p.name)

  # synchronize @ module level
  syncWorkDir( workspace, sequence, context )

  # build
  buildProjects( workspace, sequence, context )
  
  return context.status


def syncWorkDir( workspace, sequence, context=GumpContext() ):
  """copy the raw module (project) materials from source to work dir (hopefully using rsync, cp is fallback)"""

  log.info('--- Synchronizing work directories with sources')

  modules=getModulesForProjectList(sequence)
  
  log.info('Total Module Sequence:');
  for m in modules:
    log.info('  Modules : ' + m.name)    

  for module in modules:
      
    (mctxt) = context.getModuleContextForModule(module)
      
    if mctxt.okToPerformWork() and Module.list.has_key(module.name):
        module=Module.list[module.name];
        sourcedir = os.path.abspath(os.path.join(workspace.cvsdir,module.name)) # todo allow override
        destdir = os.path.abspath(workspace.basedir)
        
        # :TODO: Make this configurable (once again)
        #if not workspace.sync:
        #  workspace.sync = default.syncCommand
    
        if context.noRSync:
            cmd=Cmd('cp','sync_'+module.name,dir.work)
            cmd.addParameter('-Rf')
            cmd.addParameter(sourcedir)
            cmd.addParameter(destdir)
        else:
            cmd=Cmd('rsync','rsync_'+module.name,dir.work)            
            cmd.addParameter('-r')
            cmd.addParameter('-a')
            cmd.addParameter('--delete')
            cmd.addParameter(sourcedir)
            cmd.addParameter(destdir)

        log.debug(' ------ Sync\'ing : '+ module.name)
    
        # Perform the Sync
        cmdResult=execute(cmd,workspace.tmpdir)

        work=CommandWorkItem(WORK_TYPE_SYNC,cmd,cmdResult)
        mctxt.performedWork(work)

        # Update Context w/ Results  
        if not cmdResult.status==CMD_STATUS_SUCCESS:
            mctxt.propagateErrorState(STATUS_FAILED,REASON_SYNC_FAILED)
        else:
            mctxt.status=STATUS_SUCCESS
    else:
        # :TODO: Is the redundanct, ought it not have already be published?
        # Does this account for the confusion?
        mctxt.propagateErrorState(mctxt.status,mctxt.reason)

def buildProjects( workspace, sequence, context=GumpContext() ):
  """actually perform the build of the specified project and its deps"""

  log.info('--- Building work directories with sources')

  # build all projects this project depends upon, then the project itself
  for project in sequence:

    (mctxt,pctxt) = context.getContextsForProject(project)
    
    if pctxt.okToPerformWork():
        
        #:TODO:Consider looking for outputs and deleting if found
        
        # get the module object given the module name,
        # which is gotten from the project
        module=Module.list[project.module]

        log.debug(' ------ Building: '+ module.name + ':' + project.name)

        cmd=getBuildCommand(workspace,module,project,context)

        if cmd:
            # Execute the command ....
            cmdResult=execute(cmd,workspace.tmpdir)
    
            # Update Context    
            work=CommandWorkItem(WORK_TYPE_BUILD,cmd,cmdResult)
            pctxt.performedWork(work)
            
            # Update Context w/ Results  
            if not cmdResult.status==CMD_STATUS_SUCCESS:
                pctxt.propagateErrorState(STATUS_FAILED,REASON_BUILD_FAILED)
            else:
                outputsOk=1
                for i in range(0,len(project.jar)):
                    jar=os.path.normpath(project.jar[i].path)
                    if jar:
                        if not os.path.exists(jar):
                            pctxt.propagateErrorState(STATUS_FAILED,REASON_MISSING_OUTPUTS)
                            outputsOk=0
                            pctxt.addError("Missing Output: " + str(jar))

                if outputsOk: pctxt.status=STATUS_SUCCESS  
    else:
        # :TODO: Redundant? 
        #
        pctxt.propagateErrorState(pctxt.status,pctxt.reason)

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
