#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/Attic/logic.py,v 1.47 2003/11/17 22:10:51 ajack Exp $
# $Revision: 1.47 $
# $Date: 2003/11/17 22:10:51 $
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
  This is the logic gump applies to the model in order to perform tasks.
"""

import os.path
import os
import sys
import logging
import types
from string import split
from fnmatch import fnmatch

from gump import log, load
from gump.launcher import Cmd, Parameters
from gump.conf import dir, default, handleArgv
from gump.model import Workspace, Module, Project
from gump.context import *
from gump.tools import listDirectoryAsWork

###############################################################################
# Initialize
###############################################################################


###############################################################################
# Classes
###############################################################################

###############################################################################
# Functions
###############################################################################

# static void main()
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)

  args = handleArgv(sys.argv)
  ws=args[0]
  ps=args[1]
  
  context=GumpContext()
  
  # get parsed workspace definition
  workspace=load(ws, context)
  
  #projects=getPackagedProjects(context)
  #print "Packaged Projects : " + str(len(projects))
  #for p in projects: print "Packaged Project " + str(p.name)
    
  printSeparator()
  print "Project Expression : " + ps
  
  projects=getProjectsForProjectExpression(ps)
  #print "Resolved Projects : " + str(len(projects))
  #for p in projects: print "Project " + str(p.name)
  #modules=getModulesForProjectExpression(ps)
  #print "Resolved Modules : " + str(len(modules))
  #for m in modules: print "Module " + str(m.name) + " : " + str(m.cvs.repository)
  
  #projects=getBuildSequenceForProjects(getProjectsForProjectExpression(ps))
  #print "Resolved Project Tree : " + str(len(projects))
  #for p in projects: print "Project " + str(p.name)
  #modules=getModulesForProjectList(projects)
  #print "Resolved Module Tree : " + str(len(modules))
  #for m in modules: print "Module " + str(m.name) + " : " + str(m.cvs.repository)
  
  printSeparator()
  
  # preprocessContext(workspace, context)
  
  # from gump.document import documentText
  # documentText(workspace, context, ps)
  
  for project in projects:
      (cp,bcp)=getClasspathLists(project,workspace,context,1)
      print "Project : " + project.name 
      for p in cp:
          if isinstance(p,AnnotatedPath):
              pp='Unnamed'
              ppp='Unnamed'
              if p.context: pp=p.context.name
              if p.pcontext: ppp=p.pcontext.name
              print " - " + str(p) + " : " + pp + " : " + ppp + " : " + str(p.note)
          else:
              print " + " + str(p)
              
      for p in bcp:
          if isinstance(p,AnnotatedPath):
              pp='Unnamed'
              ppp='Unnamed'
              if p.context: pp=p.context.name
              if p.pcontext: ppp=p.pcontext.name
              print " - " + str(p) + " : " + pp + " : " + ppp + " : " + str(p.note) + " --- BOOT"
          else:
              print " + " + str(p) + " --- BOOT"
              
      cmd=getBuildCommand(workspace,Module.list[project.module],project,context)
      if cmd:
          cmd.dump()