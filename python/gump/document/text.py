#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/document/Attic/text.py,v 1.5 2004/01/09 19:57:20 ajack Exp $
# $Revision: 1.5 $
# $Date: 2004/01/09 19:57:20 $
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
    xdoc generation, for forrest
"""

import socket
import time
import os
import sys
import logging

from gump import log

from gump.utils.work import *

from gump.model.state import *

from gump.document.documenter import Documenter
from gump.document.resolver import *

class TextDocumenter(Documenter):
    
    def __init__(self,output=sys.stdout, dirBase='.', urlBase='.'):
        Documenter.__init__(self)
        self.output=output
        
        # Hack, ought return a non-hierarchical one
        self.resolver=Resolver(dirBase,urlBase)
        
    def getResolverForRun(self,run):
        return self.resolver
    
    def documentRun(self, run):    
        indent=' '
        
        workspace = run.getWorkspace()
        gumpSet = run.getGumpSet()
        output=self.output
            
        output.write(indent + "Workspace State : " + workspace.getStateDescription() + "\n")
        output.write(indent + "Workspace Secs : " + str(workspace.getElapsedSecs()) + "\n")
    
        output.write(indent + "Modules: " + str(len(workspace.getModules())) + "\n")
    
        self.documentAnnotations(indent,workspace)
        
        indent += ' '
        for module in workspace.getModules():
            if not gumpSet.inModules(module): continue        
            output.write(indent + "Module [" + module.getName() + "] State: " + module.getStateDescription() + "\n")
            output.write(indent + "Projects: " + str(len(module.getProjects())) + "\n")

            self.documentAnnotations(indent,module)
            
            for project in module.getProjects():
                if not gumpSet.inSequence(project): continue
            
                output.write(indent + "Project [" + project.getName() 	\
                    + "] State: " + project.getStateDescription() + "\n")
                self.documentAnnotations(indent,project)
                self.documentWork(indent,project)

    def documentWork(self, indent, workable):
        output=self.output    
        output.write(indent+"Work [" + str(len(workable.worklist)) \
                + "] [" + str(workable.getElapsedSecs()) + "] secs."  + "\n")
    
        for work in workable.worklist:
            output.write(indent+"Work : " + stateName(work.state) + "\n")
            if isinstance(work,CommandWorkItem):
                output.write(indent+"Work Name : " + work.command.name + "\n")
                output.write(indent+"Work Cmd  : " + work.command.formatCommandLine() + "\n")
                if work.command.cwd:
                    output.write(indent+"Work Cwd  : " + work.command.cwd + "\n")
                if work.result.signal:
                    output.write(indent+"Work Signal  : " + `work.result.signal` + "\n")
                output.write(indent+"Work Exit : " + str(work.result.exit_code) + "\n")
        

    def documentAnnotations(self, indent, annotatable): 
        output=self.output       
        for note in annotatable.getAnnotations():
            output.write(indent+" - " + str(note) + "\n")
        