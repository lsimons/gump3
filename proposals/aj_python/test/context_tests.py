#!/usr/bin/env python
# $Header: /home/stefano/cvs/gump/proposals/aj_python/test/Attic/context_tests.py,v 1.1 2003/08/21 19:43:15 nickchalko Exp $
# $Revision: 1.1 $
# $Date: 2003/08/21 19:43:15 $
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
    Model Testing
"""

import os
import logging
import types, StringIO

from gump import log, loadWorkspace
from gump.xmlutils import *
from gump.model import *
from gump.utils import *
from gump.context import *
    

if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)
  
  module1=Module({'name':"M"})
  Module.list[module1.name]=module1
  
  project1=Project({'name':'TestProject1'})
  project1.module='name'
  Project.list[project1.name]=project1
  project1.depend.append(Depend({'project':'TestProject2'}))
  project2=Project({'name':'TestProject2'})
  project2.module='name'
  Project.list[project2.name]=project2
  
  cmd=Cmd("test",'test_out')
  #set classpath/environment
  cmd.addParameter("A","a")
  cmd.addParameter("B")

  item=WorkItem(WORK_TYPE_CONFIG,cmd,CmdResult(cmd))
  
  context=GumpContext()
  context.performedWorkOnProject(project1, item);
  context.performedWorkOnProject(project2, item);
  context.performedWorkOnProject(project1, item);
  
  # dump(context)
  
  gumpContext=GumpContext();
  moduleContext=gumpContext.getModuleContext("M")
  projectContext1=gumpContext.getProjectContextForProject(project1)
  projectContext2=gumpContext.getProjectContextForProject(project2)
  
  print projectContext1
  print projectContext2
  
  if not projectContext1==projectContext1: raise "Uh Oh!"
  if projectContext1==projectContext2: raise "Uh Oh!"
  
  list=[]
  list.append(projectContext1)
  
  print list
  
  if not projectContext1 in list: raise "Uh Oh!"
  if projectContext2 in list: raise "Uh Oh!"
  

