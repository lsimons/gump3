#!/usr/bin/python

# $Header: /home/stefano/cvs/gump/python/gump/check.py,v 1.24 2003/10/06 14:04:15 ajack Exp $
# $Revision: 1.24 $
# $Date: 2003/10/06 14:04:15 $
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

from gump import log, load
from gump.logic import getBuildSequenceForProjects, getProjectsForProjectExpression
from gump.conf import dir, default, handleArgv, banner
from gump.model import Workspace, Module, Project
from gump.context import GumpContext, CommandWorkItem, WORK_TYPE_CHECK

from gump.launcher import getCmdFromString, execute, CMD_STATUS_SUCCESS

###############################################################################
# Initialize
###############################################################################


###############################################################################
# Functions
###############################################################################
def checkEnvironment(workspace, context=GumpContext(), exitOnError=1):
    """ Check Things That are Required """
    
    #
    # :TODO: Complete this, it ought be an important early warning...
    #
    
    
    #:TODO: Take more from runAnt.py on:
    # - ANT_OPTS?
    # - How to ensure lib/tools.jar is in classpath
    # - Others?
    
    #
    #	Directories...
    
    
    #
    # JAVACMD can be set (perhaps for JRE verse JDK)
    #
    if os.environ.has_key('JAVACMD'):        
        context.javaCommand  = os.environ['JAVACMD']
        context.addInfo('JAVACMD environmental variable setting java command to ' \
            + context.javaCommand )
    
    
    #	Envs:
    #	JAVA_HOME for bootstrap ant?
    #	CLASSPATH
    #	FORREST_HOME?
    
    if not checkEnvVariable(workspace, context, 'JAVA_HOME',0):    
        context.noJavaHome=1    
        context.addWarning('JAVA_HOME environmental variable not found. Might not be needed.')
                
    if not checkEnvVariable(workspace, context, 'CLASSPATH',0):    
        context.noClasspath=1    
        context.addWarning('CLASSPATH environmental variable not found. Might not be needed.')
                
    if not checkEnvVariable(workspace, context, 'FORREST_HOME',0): 
        context.noForrest=1
        context.addWarning('FORREST_HOME environmental variable not found, no xdoc output')
        
    #
    # Check for executables:
    #
    #	java
    #	javac (for bootstrap ant & beyond)
    #	cvs
    #
    #	These ought set a switch..
    #
    #	rsync or cp
    #	forrest (for documentation)
    #
    checkExecutable(workspace, context, 'env','',0)
    checkExecutable(workspace, context, context.javaCommand,'-version',exitOnError)
    checkExecutable(workspace, context, 'javac','-help',exitOnError)
    checkExecutable(workspace, context, 'java com.sun.tools.javac.Main','-help',exitOnError,'check_java_compiler')    
    checkExecutable(workspace, context, 'cvs','--version',exitOnError)
    if not context.noForrest and not checkExecutable(workspace, context, 'forrest','-projecthelp',0): 
        context.noForrest=1
        context.addWarning('"forrest" command not found, no xdoc output')
        
    if not checkExecutable(workspace, context, 'rsync','-help',0): 
        context.noRSync=1
        context.addWarning('"rsync" command not found, so attempting recursive copy "cp -R"')
        
    if not checkExecutable(workspace, context, 'pkill','-help',0): 
        context.noPKill=1
        context.addWarning('"pkill" command not found, no process clean-ups can occur')        
    
    # :TODO:
    # Need to check javac classes are on CLASSPATH
    #
    
def checkExecutable(workspace,context,command,options,mandatory,name=None):
    ok=0
    try:
        if not name: name='check_'+command
        cmd=getCmdFromString(command+" "+options,name)
        result=execute(cmd)
        ok=result.status==CMD_STATUS_SUCCESS 
        if not ok:
            log.error('Failed to detect [' + command + ']')     
    except Exception, details:
        ok=0
        log.error('Failed to detect [' + command + '] : ' + str(details))
        result=None
       
    # Update Context
    context.performedWork(CommandWorkItem(WORK_TYPE_CHECK,cmd,result))
        
    if not ok and mandatory:
        banner()
        print
        print " Unable to detect/test mandatory [" + command+ "] in path (see next)."
        for p in sys.path:
            print "  " + str(os.path.normpath(p))
        sys.exit(2)
    
    return ok
    
def checkEnvVariable(workspace, context,env,mandatory=1):
    ok=0
    try:
        ok=os.environ.has_key(env)
        if not ok:
            log.error('Failed to find environment variable [' + env + ']')
        
    except Exception, details:
        ok=0
        log.error('Failed to find environment variable [' + env + '] : ' + str(details))
    
    if not ok and mandatory:
        banner()
        print
        print " Unable to find mandatory [" + env + "] in environment (see next)."
        for e in os.environ.keys():
            try:
                v=os.environ[e]
                print "  " + e + " = " + v
            except:
                print "  " + e 
        sys.exit(3)
    
    return ok
    
def check(workspace, expr='*', context=GumpContext()):
  """dump all dependencies to build a project to the output"""

  projects=getProjectsForProjectExpression(expr)
  
  missing=[]
  optionalMissing=[]
  optionalOnlyMissing=[]
  
  # for each project
  for project in projects:
    printed_header=0;    
    projectmissing = 0
    if not printed_header: 
      printHeader(project)
      printed_header=1
    
    # for each dependency in current project
    for depend in project.depend:
      # if the dependency is not present in the projects, it's missing
      if depend.project not in Project.list:
        if not printed_header: 
          printHeader(project)
          printed_header=1    
        projectmissing+=1
        print "  missing: "+depend.project
        if depend.project not in missing:
          missing.append(depend.project)  
            
    for depend in project.option:
      # if the dependency is not present in the projects, it's missing
      if depend.project not in Project.list:
        if not printed_header: 
          printHeader(project)
          printed_header=1    
        projectmissing+=1
        print "  optional missing: "+depend.project
        if depend.project not in optionalMissing:
          optionalMissing.append(depend.project)
            
    if projectmissing>0:
      print "  total errors: " , projectmissing

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

  try:
    peekInGlobalProfile(missing);
  except:
    print
    print " ***** In Global Profile... ***** "  
    print
    print "  Cannot load the global Gump profile, you have to install %\n  the jars by hand."  
    print 
    traceback.print_exc()    
    print
      
  print
  print " ***** RESULT ***** "  
  print
  if len(missing)>0:
    print
    print "  - ERROR - Some projects that were referenced are missing in the workspace. "  
    print "    See the above messages for more detailed info."
  else:
    print "  -  OK - All projects that are referenced are present in the workspace."  

  if len(optionalOnlyMissing)>0:
    print  
    print "  - WARNING - Some projects that were referenced as optional only are "
    print "    missing in the workspace. "  
    print "    See the above messages for more detailed info."
  else:
    print "  -  OK - All OPTIONAL projects that are referenced are present in the workspace."  
    print " ***** RESULT ***** "
    
  return 0
  
def printHeader(project):
    print " *****************************************************"       
    print " Project: " + project.name
    
def peekInGlobalProfile(missing):
   
  print  
  print "  *****************************************************"     
  print "  **** Loading global Gump workspace to find info"
  print "       about missing projects.   Please wait...   *****"
  print "  *****************************************************"    
  print

  workspace=load(default.globalws)
  
  for missed in missing:
    print  
    print      
    print "  **** Project: " + missed
    print
    if missed in Project.list:
      currentproject = Project.list[missed]
      currentmodule = Module.list[currentproject.module]
      print "  ",currentmodule.description
      print
      if not currentproject.url.href == currentmodule.url.href:
            print "   project url: " , currentproject.url.href
      print "   module  url: " , currentmodule.url.href
      print "   module  cvs: " , currentmodule.cvsroot()
      if currentmodule.redistributable:
        print  
        print "   NOTE: You can also get it in the Gump jar repository." 
        print "         See http://jakarta.apache,org/gump/ for details."
        
    else:
      print "   Gump doesn't know about it. Or it's wrong, or you have to "
      print "   install the artifacts of " + missed +" manually."
            

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
  result = check(workspace, ps)

  # bye!
  sys.exit(result)
