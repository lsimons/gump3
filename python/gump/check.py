#!/usr/bin/python

# $Header: /home/stefano/cvs/gump/python/gump/check.py,v 1.34 2003/11/18 00:29:49 ajack Exp $
# $Revision: 1.34 $
# $Date: 2003/11/18 00:29:49 $
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
  Checks that the Gump definitions are ok.
"""

import os.path
import os
import sys
import traceback
import logging

from gump import log
from gump.logic import getBuildSequenceForProjects, getProjectsForProjectExpression
from gump.config import dir, default, handleArgv,
from gump.model import Workspace, Module, Project
from gump.context import Workspace, CommandWorkItem, WORK_TYPE_CHECK, STATE_SUCCESS
from gump.tools import tailFileToString

from gump.launcher import getCmdFromString, execute

###############################################################################
# Initialize
###############################################################################


###############################################################################
# Functions
###############################################################################

def check(workspace, expr='*', context=GumpContext(),display=1):
  """dump all dependencies to build a project to the output"""

  projects=getProjectsForProjectExpression(expr)
  
  missing=[]
  optionalMissing=[]
  optionalOnlyMissing=[]
  
  # for each project
  for project in projects:
    printed_header=0;    
    projectmissing = 0
   
    # for each dependency in current project
    for depend in project.depend:
      # if the dependency is not present in the projects, it's missing
      if depend.project not in Project.list:
        projectmissing+=1
        message="  Missing dependency: " + depend.project + " on project " + project.name
        
        if display:
            if not printed_header: 
              printHeader(project)
              printed_header=1            
            print message
        
        # Store message into context...
        context.addWarning(message)
        if depend.project not in missing:
          missing.append(depend.project)  
            
    for depend in project.option:
      # if the dependency is not present in the projects, it's missing
      if depend.project not in Project.list:
        projectmissing+=1
        message="  Missing optional dependency: " + depend.project + " on project " + project.name

        if display:
            if not printed_header: 
              printHeader(project)
              printed_header=1    
            print message
        context.addWarning(message)
        if depend.project not in optionalMissing:
          optionalMissing.append(depend.project)
            
    if display and projectmissing>0:
        print "  total errors: " , projectmissing

  if display:
      if len(optionalMissing)>0:     
        print
        print " ***** MISSING OPTIONAL *ONLY* PROJECTS THAT ARE REFERENCED ***** "
        print
        for missed in optionalMissing:
          if missed not in missing:
            optionalOnlyMissing.append(missed)
            print "  " + missed
              
      if len(missing)>0:
        print
        print " ***** MISSING PROJECTS THAT ARE REFERENCED ***** "
        print
        for missed in missing:
          print "  " + missed

  # Comment out for now ...
  # 'cos loading a new workspace overwrites
  # the loaded one..
  
  #try:
  #  peekInGlobalProfile(missing);
  #except:
  #  print
  #  print " ***** In Global Profile... ***** "  
  #  print
  #  print "  Cannot load the global Gump profile, you have to install %\n  the jars by hand."  
  #  print 
  #  traceback.print_exc()    
  #  print
    
  if display:  
      print
      print " ***** WORKSPACE RESULT ***** "  
      print
      
  if len(missing)>0:
    context.addError("Some projects that were referenced are missing in the workspace.")    
    if display:
      print
      print "  - ERROR - Some projects that were referenced are missing in the workspace. "  
      print "    See the above messages for more detailed info."
  elif display:
    print "  -  OK - All projects that are referenced are present in the workspace."  

  if len(optionalOnlyMissing)>0:
    context.addWarning("Some projects that were referenced as optional are missing in the workspace.");
    if display:
        print  
        print "  - WARNING - Some projects that were referenced as optional only are "
        print "    missing in the workspace. "  
        print "    See the above messages for more detailed info."
  elif display:
    print "  -  OK - All OPTIONAL projects that are referenced are present in the workspace."  
    print " ***** RESULT ***** "
    
  return 0
  
def printHeader(project):
    print " *****************************************************"       
    print " Project: " + project.name
    
    
# Comment out for now ...
# 'cos loading a new workspace overwrites
# the loaded one..
#def peekInGlobalProfile(missing):
#   
#  print  
#  print "  *****************************************************"     
#  print "  **** Loading global Gump workspace to find info"
#  print "       about missing projects.   Please wait...   *****"
#  print "  *****************************************************"    
#  print
#
#  workspace=load(default.globalws)
#  
#  for missed in missing:
#    print  
#    print      
#    print "  **** Project: " + missed
#    print
#    if missed in Project.list:
#      currentproject = Project.list[missed]
#      currentmodule = Module.list[currentproject.module]
#      print "  ",currentmodule.description
#      print
#      if not currentproject.url.href == currentmodule.url.href:
#            print "   project url: " , currentproject.url.href
#      print "   module  url: " , currentmodule.url.href
#      print "   module  cvs: " , currentmodule.cvsroot()
#      if currentmodule.redistributable:
#        print  
#        print "   NOTE: You can also get it in the Gump jar repository." 
#        print "         See http://jakarta.apache,org/gump/ for details."
#        
#    else:
#      print "   Gump doesn't know about it. Or it's wrong, or you have to "
#      print "   install the artifacts of " + missed +" manually."
#            

# static void main()
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)
  
  args = handleArgv(sys.argv,0)
  ws=args[0]
  ps=args[1]

  # get parsed workspace definition
  workspace=load(ws)
 
  context=GumpContext()
 
  #
  checkEnvironment(workspace,context,0)

  # check
  result = check(workspace, ps, context, 1)

  # bye!
  sys.exit(result)
