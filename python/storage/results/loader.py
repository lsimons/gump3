#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/storage/results/Attic/loader.py,v 1.2 2004/03/15 16:12:23 ajack Exp $
# $Revision: 1.2 $
# $Date: 2004/03/15 16:12:23 $
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
import xml.dom.minidom

from gump import log
from gump.results.model import WorkspaceResult
from gump.utils.xmlutils import SAXDispatcher
from gump.utils.note import transferAnnotations, Annotatable
from gump.utils import dump
from gump.config import gumpPath

class WorkspaceResultLoader:
    def __init__(self):
        self.annotations=[]
        
    def loadFromUrl(self,url):
        """Builds in memory from the xml file. Return the generated objects."""
      
        # Download (relative to base)
        if not url.startswith('http://'):
            newurl=gumpPath(url,'.');
        else:
            newurl=cacheHTTP(url)
            
        return self.load(newurl)
        
    def load(self,file):
        """Builds in memory from the xml file. Return the generated objects."""

        if not os.path.exists(file):
            log.error('WorkspaceResult metadata file ['+file+'] not found')
            raise IOError, """WorkspaceResult %s not found!""" % file 
    
        input=open(file,'r')
    
        dom=minidom.parse(input)
    
        # Construct object around DOM.
        workspaceResult=WorkspaceResult()
  
        #
        # Cook the raw model...
        #
        workspaceResult.complete(dom)

        return workspaceResult      