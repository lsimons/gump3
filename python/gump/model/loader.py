#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/Attic/loader.py,v 1.6 2004/02/15 17:32:05 ajack Exp $
# $Revision: 1.6 $
# $Date: 2004/02/15 17:32:05 $
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
    This module contains information on
"""
import os, os.path

from gump import log
from gump.model.rawmodel import XMLWorkspace,XMLProfile,	\
            XMLModule, XMLProject, XMLRepository, \
            XMLServer,	XMLTracker
from gump.model.workspace import Workspace
from gump.model.module import Module
from gump.utils.xmlutils import SAXDispatcher
from gump.utils.note import transferAnnotations, Annotatable
from gump.utils import dump

class WorkspaceLoader:
    def __init__(self):
        self.annotations=[]
        
    def load(self,file):
      """Builds a GOM in memory from the xml file. Return the generated GOM."""

      if not os.path.exists(file):
        log.error('Workspace metadata file ['+file+'] not found')
        raise IOError, """Workspace %s not found!

      You need to specify a valid workspace for Gump to run
      If you are new to Gump, simply copy minimal-workspace.xml
      to a file with the name of your computer (`hostname`.xml)
      and rerun this program.""" % file 
    
      #
      # Clear out the maps
      #
      XMLProfile.map={}
      XMLRepository.map={}
      XMLModule.map={}
      XMLProject.map={}
      XMLServer.map={}
      XMLTracker.map={}
    
      log.debug("Launch SAX Dispatcher onto : " + file);
              
      parser=SAXDispatcher(file,'workspace',XMLWorkspace)
    
      # Extract the root XML
      xmlworkspace=parser.docElement
    
      if not xmlworkspace:
        raise IOError, "Failed to load workspace" + file
    
      # Construct object around XML.
      workspace=Workspace(xmlworkspace)
      
      # Copy over any XML errors/warnings
      transferAnnotations(parser, workspace)
  
      #
      # Cook the raw model...
      #
      workspace.complete(XMLProfile.map,XMLRepository.map,	\
                          XMLModule.map,XMLProject.map,	\
                          XMLServer.map, XMLTracker.map)

      #
      # Clear out the maps [so don't continue to use them]
      #
      XMLModule.map={}
      XMLProject.map={}
      XMLProfile.map={}
      XMLRepository.map={}
      XMLTracker.map={}
      XMLServer.map={}
  
      return workspace      
      
    def loadModule(self,url,workspace):
        
        log.debug("Launch SAX Dispatcher onto : " + url);
        
        XMLModule.map={}
        XMLProject.map={}
      
        xmlmodule=SAXDispatcher(url,'module',XMLModule).docElement
    
        if not xmlmodule:
            raise IOError, "Failed to load module: " + url

        #
        #for xmlproject in xmlmodule.project:
        #    print "XMLProject: " + str(xmlproject)
                       
        #
        module=Module(xmlmodule,None)        
        module.complete(workspace)

        #
        # Clear out the maps [so don't continue to use them]
        #
        XMLModule.map={}
        XMLProject.map={}
      
        return module