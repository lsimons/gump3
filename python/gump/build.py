#!/usr/bin/python

# $Header: /home/stefano/cvs/gump/python/gump/build.py,v 1.30 2003/11/03 19:56:31 ajack Exp $
# $Revision: 1.30 $
# $Date: 2003/11/03 19:56:31 $
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
from gump.logic import getBuildSequenceForProjects, getBuildCommand, \
        getMkDirCommand, getDeleteCommand, \
        getProjectsForProjectExpression, getModulesForProjectList, \
        hasOutputs
from gump.repository import JarRepository
from gump.conf import dir, default, handleArgv
from gump.model import Workspace, Module, Project
from gump.launcher import Cmd, CmdResult, execute
from gump.utils import dump
from gump.tools import listDirectoryAsWork, syncDirectories

###############################################################################
# Initialize
###############################################################################


###############################################################################
# Functions
###############################################################################

def build(workspace, expr='*', context=GumpContext(), nosync=None):
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

  return buildProjectList(workspace,projects,context,nosync)
  
def buildProjectList(workspace, projects, context, nosync=None):
  """ Build a expression of projects """
        
  log.debug('Requests Projects')
  for p in projects:
    log.debug('  Requested : ' + p.name)
    
  sequence=getBuildSequenceForProjects(projects)

  return buildProjectSequence(workspace,sequence,context,nosync)
  
def buildProjectSequence(workspace,sequence,context,nosync=None):
    
  log.debug('Total Project Sequence (i.e. build order):');
  for p in sequence:
    log.debug('  Sequence : ' + p.name)

  # synchronize @ module level
  if not nosync:  syncWorkDir( workspace, sequence, context )

  # build
  buildProjects( workspace, sequence, context )
  
  return context.status


def syncWorkDir( workspace, sequence, context ):
  """copy the raw module (project) materials from source to work dir (hopefully using rsync, cp is fallback)"""

  log.debug('--- Synchronizing work directories with sources')

  modules=getModulesForProjectList(sequence)
  
  log.debug('Total Module Sequence:');
  for m in modules:
    log.debug('  Modules : ' + m.name)    

  for module in modules:
      
    (mctxt) = context.getModuleContextForModule(module)
      
    if mctxt.okToPerformWork() \
        and Module.list.has_key(module.name) \
        and not switch.failtesting:
            
        module=Module.list[module.name];
        sourcedir = os.path.abspath(os.path.join(workspace.cvsdir,module.name)) # todo allow override
        destdir = os.path.abspath(workspace.basedir)
        
        work=syncDirectories(context,workspace,WORK_TYPE_SYNC,dir.work,sourcedir,destdir,module.name)
        
        mctxt.performedWork(work)

        # Update Context w/ Results  
        if not work.result.status==CMD_STATUS_SUCCESS:
            mctxt.propagateErrorState(STATUS_FAILED,REASON_SYNC_FAILED)
        else:
            mctxt.status=STATUS_SUCCESS

def buildProjects( workspace, sequence, context ):
  """actually perform the build of the specified project and its deps"""

  log.debug('--- Building work directories with sources')

  # Place repository in jardir (to be renamed to repodir)
  repository=JarRepository(workspace.jardir)

  # build all projects this project depends upon, then the project itself
  for project in sequence:

    (mctxt,pctxt) = context.getContextsForProject(project)
    
    if pctxt.okToPerformWork():
        
        # Get the module object given the module name,
        # which is gotten from the project
        module=Module.list[project.module]

        log.debug(' ------ Performing pre-Build Actions (mkdir/delete) for : '+ module.name + ':' + project.name)

        performPreBuild( workspace, context, mctxt, module, pctxt, project )

        if pctxt.okToPerformWork():
        
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
                    reason=REASON_BUILD_FAILED
                    if cmdResult.status==CMD_STATUS_TIMED_OUT:
                        reason=REASON_BUILD_TIMEDOUT
                    pctxt.propagateErrorState(STATUS_FAILED,reason)
                else:
                    if hasOutputs(project,pctxt):
                        outputsOk=1
                        for i in range(0,len(project.jar)):
                            jar=os.path.normpath(project.jar[i].path)
                            if jar:
                                if not os.path.exists(jar):
                                    pctxt.propagateErrorState(STATUS_FAILED,REASON_MISSING_OUTPUTS)
                                    outputsOk=0
                                    pctxt.addError("Missing Output: " + str(jar))
                            
                        if outputsOk: 
                            for i in range(0,len(project.jar)):
                                jar=os.path.normpath(project.jar[i].path)
                                # Copy to repository
                                repository.publish( module.name, jar )
            
                            pctxt.status=STATUS_SUCCESS  
                    
                            # For 'fun' list repository
                            listDirectoryAsWork(pctxt,repository.getGroupDir(module.name), \
                                                'list_repo_'+project.name) 
                    
                        else:
                            #
                            # List all directories that should've contained
                            # outputs, to see what is there.
                            #
                            dirs=[]
                            dircnt=0
                            for i in range(0,len(project.jar)):
                                jar=os.path.normpath(project.jar[i].path)
                                if jar:
                                    dir=os.path.dirname(jar)
                                    if not dir in dirs and os.path.exists(dir):
                                        dircnt += 1
                                        listDirectoryAsWork(pctxt,dir,\
                                            'list_'+project.name+'_dir'+str(dircnt)+'_'+os.path.basename(dir))
                                        dirs.append(dir)
                                    else:
                                        pctxt.addWarning("No such directory (where output is expect) : " + dir)
                    else:
                        pctxt.status=STATUS_SUCCESS  
    
            if not pctxt.status == STATUS_SUCCESS:
                log.warn('Failed to build project [' + pctxt.name + ']')
            

def performPreBuild( workspace, context, mctxt, module, pctxt, project ):
    """ Perform pre-build Actions """
    
    # Deletes...
    dels=0
    for delete in project.delete:
        cmd=getDeleteCommand(workspace,context,module,project,delete,dels)

        # Execute the command ....
        cmdResult=execute(cmd,workspace.tmpdir)
    
        # Update Context    
        work=CommandWorkItem(WORK_TYPE_PREBUILD,cmd,cmdResult)
        pctxt.performedWork(work)
            
        # Update Context w/ Results  
        if not cmdResult.status==CMD_STATUS_SUCCESS:
            pctxt.propagateErrorState(STATUS_FAILED,REASON_PREBUILD_FAILED)
        else:
            dels+=1
            pctxt.status=STATUS_SUCCESS  
                
    # MkDirs...
    mkdirs=0
    for mkdir in project.mkdir:   
        cmd=getMkDirCommand(workspace,context,module,project,mkdir,mkdirs)

        # Execute the command ....
        cmdResult=execute(cmd,workspace.tmpdir)
    
        # Update Context    
        work=CommandWorkItem(WORK_TYPE_PREBUILD,cmd,cmdResult)
        pctxt.performedWork(work)
            
        # Update Context w/ Results  
        if not cmdResult.status==CMD_STATUS_SUCCESS:
            pctxt.propagateErrorState(STATUS_FAILED,REASON_PREBUILD_FAILED)
        else:
            mkdirs+=1
            pctxt.status=STATUS_SUCCESS  
                
    if not pctxt.okToPerformWork():
        log.warn('Failed to perform prebuild on project [' + pctxt.name + ']')
        
# static void main()
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)

  args = handleArgv(sys.argv)
  ws=args[0]
  ps=args[1]
  
  # Allow a nosync option
  nosync=None
  if len(args) > 2: nosync=args[2]
  
  # A context to work into...
  context=GumpContext()
  
  # get parsed workspace definition
  workspace=load(ws,context)
  
  #
  # Perform build tasks
  #
  result = build(workspace, ps, context, nosync)

  # bye!
  sys.exit(result)
