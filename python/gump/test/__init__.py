#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/test/__init__.py,v 1.9 2004/03/18 23:24:56 ajack Exp $
# $Revision: 1.9 $
# $Date: 2004/03/18 23:24:56 $
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


# tell Python what modules make up the gump.test package
#__all__ = ["",""]

from gump.model.loader import WorkspaceLoader

import gump
import gump.config

from gump.model.state import *
from gump.model.rawmodel import XMLWorkspace
from gump.model.workspace import Workspace

from gump.output.statsdb import StatisticsDB
from gump.utils.tools import listDirectoryToFileHolder

def getTestWorkspace(xml=None):
    if not xml: xml='gump/test/resources/full1/workspace.xml'    
    #print "Workspace File: " + str(xml)    
    workspace = WorkspaceLoader().load(xml)
    return workspace
    
def getWorkedTestWorkspace(xml=None):
    workspace=getTestWorkspace(xml)
       
    # Load statistics for this workspace
    db=StatisticsDB(gump.dir.test,'test.db')  
    db.loadStatistics(workspace)

    # Some work items...
    listDirectoryToFileHolder(workspace,workspace.getBaseDirectory())        
    for module in workspace.getModules():        
        listDirectoryToFileHolder(module,module.getSourceDirectory())
        for project in module.getProjects():
            listDirectoryToFileHolder(project,project.getHomeDirectory())     
     
    #       
    # Try to set some statii
    #
    m=0
    for module in workspace.getModules():   
        #
        # Set one in three modules as failed.
        #
        m+=1 
        if m % 3 == 0:
            module.changeState(STATE_FAILED)
        else:
            if m % 2 == 0:
                module.setUpdated(1)
            module.changeState(STATE_SUCCESS)
        p=0
        for project in module.getProjects(): 
            #
            # Set one in three projects as failed.
            #
            p+=1
            if p % 3 == 0:
                project.changeState(STATE_FAILED)
            else:
                project.changeState(STATE_SUCCESS)

    return workspace
    

    
def createTestWorkspace():
    xmlworkspace=XMLWorkspace({})
    workspace=Workspace(xmlworkspace)
    return workspace
  
    