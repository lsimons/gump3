#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/update.py,v 1.13 2003/09/26 19:25:35 ajack Exp $
# $Revision: 1.13 $
# $Date: 2003/09/26 19:25:35 $
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
Execute the appropriate cvs checkout or update commands
"""
import os

from gump import log, load
from gump.conf import *
from gump.model import Module,Repository
from gump.context import *
from gump.launcher import Cmd,CmdResult,execute
from gump.logic import *
from gump.utils import dump
 
# password encryption table used by cvs
shifts = [
    0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
   16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
  114,120, 53, 79, 96,109, 72,108, 70, 64, 76, 67,116, 74, 68, 87,
  111, 52, 75,119, 49, 34, 82, 81, 95, 65,112, 86,118,110,122,105,
   41, 57, 83, 43, 46,102, 40, 89, 38,103, 45, 50, 42,123, 91, 35,
  125, 55, 54, 66,124,126, 59, 47, 92, 71,115, 78, 88,107,106, 56,
   36,121,117,104,101,100, 69, 73, 99, 63, 94, 93, 39, 37, 61, 48,
   58,113, 32, 90, 44, 98, 60, 51, 33, 97, 62, 77, 84, 80, 85,223,
  225,216,187,166,229,189,222,188,141,249,148,200,184,136,248,190,
  199,170,181,204,138,232,218,183,255,234,220,247,213,203,226,193,
  174,172,228,252,217,201,131,230,197,211,145,238,161,179,160,212,
  207,221,254,173,202,146,224,151,140,196,205,130,135,133,143,246,
  192,159,244,239,185,168,215,144,139,165,180,157,147,186,214,176,
  227,231,219,169,175,156,206,198,129,164,150,210,154,177,134,127,
  182,128,158,208,162,132,167,209,149,241,153,251,237,236,171,195,
  243,233,253,240,194,250,191,155,142,137,245,235,163,242,178,152 ]

# encode a password in the same way that cvs does
def mangle(passwd):
  return 'A' +''.join(map(chr,[shifts[ord(c)] for c in str(passwd or '')]))

def update(workspace, expr='*', context=GumpContext()):
        
  log.info('--- Updating work directories from (CVS) Repositories ')

  modules = getModulesForProjectList(getBuildSequenceForProjects(getProjectsForProjectExpression(expr)))
      
  return updateModules(workspace,modules,context)

def readLogins():
  # read the list of cvs repositories that the user is already logged into
  logins={}
  cvspassfile=os.path.expanduser(os.path.join('~','.cvspass'))
  try:
    cvspass=open(cvspassfile)
    for line in cvspass.readlines():
        clean=line.strip()
        parts=clean.split(' ')
        root=parts[0]
        mangle=parts[1]
        # Cope with new format .cvspass 
        if len(parts) > 2:
            root=parts[1]
            mangle=parts[2] 
        # Stash this mangle for this root               
        logins[root]=mangle
    cvspass.close()
  
  except Exception, detail:
    log.error('Failed to read ~/.cvspass. Details: ' + str(detail))
    
  return logins
 
def loginToRepositoryOnDemand(repository,root,logins):
    # log into the cvs repository
    if repository.root.method=='pserver':
        newpass=mangle(repository.root.password)
        if not root in logins or logins[root]<>newpass:
            log.info('Provide login for CVS repository: ' + repository.name + ' @ ' + root)            
            # Open with append...
            try:
                cvspassfile=os.path.expanduser(os.path.join('~','.cvspass'),'a')
                cvspassfile.write('/1 '+root+' '+newpass+'\n')
                cvspassfile.close()
            except Exception, detail:
                log.error('Failed to append to ~/.cvspass. Details: ' + str(detail))
                
def updateModules(workspace, modules, context=GumpContext()):
 
  os.chdir(workspace.cvsdir)
  log.debug("Workspace CVS Directory: " + workspace.cvsdir)

  logins=readLogins()

  log.info('Modules to update:') 
    
  # Update all the modules that have CVS repositories
  for module in modules:          
    if not module.cvs: continue
    log.info('  - ' + module.name)
    
    name=module.name

    mctxt = context.getModuleContextForModule(module)
    
    if mctxt.okToPerformWork() \
        and not switch.failtesting:
        try:
          log.info("CVS Update Module " + name + ", Repository Name: " + str(module.cvs.repository))

          repository=Repository.list[module.cvs.repository]
          root=module.cvsroot()
      
          log.info("CVS Root " + module.cvsroot() + " Repository: " + str(repository))
      
          #
          # Provide logins, if not already there
          #
          loginToRepositoryOnDemand(repository,root,logins)

          #
          # Prepare CVS checkout/update command...
          # 
          cmd=Cmd('cvs','update_'+name,workspace.cvsdir)
          cmd.addParameter('-z3')
          cmd.addParameter('-d', root)
    
          if os.path.exists(name):

            # do a cvs update
            cmd.addParameter('update')
            cmd.addParameter('-P')
            cmd.addParameter('-d')
            if module.cvs.tag:
              cmd.addParameter('-r',module.cvs.tag,' ')
            else:
              cmd.addParameter('-A')
            cmd.addParameter(name)

          else:

            # do a cvs checkout
            cmd.addParameter('checkout')
            cmd.addParameter('-P')
            if module.cvs.tag: cmd.addParameter('-r',module.cvs.tag,' ')

            if module.cvs.module<>name: cmd.addParameter('-d',name,' ')
            cmd.addParameter(module.cvs.module)

          # Execute the command and capture results
          
          # Testing...
          cmdResult=execute(cmd,workspace.tmpdir)
      
          work=CommandWorkItem(WORK_TYPE_UPDATE,cmd,cmdResult)
    
          # Update Context
          mctxt.performedWork(work)
      
            # Update Context w/ Results  
          if not cmdResult.status==CMD_STATUS_SUCCESS:              
              log.error('Failed to update module: ' + module.name)        
              mctxt.propagateErrorState(STATUS_FAILED,REASON_UPDATE_FAILED)
          else:
              mctxt.status=STATUS_SUCCESS
                
        except Exception, detail:
        
          log.error('Failed to update module: ' + module.name + ' : ' + str(detail))
        
          mctxt.propagateErrorState(STATUS_FAILED,REASON_UPDATE_FAILED)  
    else:
        # :TODO: Redundant?
        mctxt.propagateErrorState(mctxt.status,mctxt.reason)
        
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)

  args = handleArgv(sys.argv)
  ws=args[0]
  ps=args[1]
  
  # load the workspace
  workspace=load(ws)
  
  context=GumpContext()
  
  logins=readLogins()
  
  dump(logins)
  
  # update(workspace, ps, context)
  
  # dump(context)
