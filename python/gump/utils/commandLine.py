#!/usr/bin/python

# $Header: /home/stefano/cvs/gump/python/gump/utils/Attic/commandLine.py,v 1.3 2003/12/05 00:51:49 ajack Exp $
# $Revision: 1.3 $
# $Date: 2003/12/05 00:51:49 $
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
    Global configuration defaults for gump. All these should really be
    set in the Workspace; this file is here to provide sensible defaults.
"""

import socket
import time
import os
import sys
import logging

from gump import log
from gump.config import default
from gump.utils import banner

#
# Process the command line, returning:
#
#	args[0]	=	workspace filename
#	args[1] =	project specifier (expression)
#	
#
class CommandLine:
    def __init__(self,argv,requireProject=1):
        self.args = []  
        
        # Extract the workspace
        if len(argv)==2: 
            if argv[1] in ['-V','--version']:
                banner()
                sys.exit(0)      
            elif argv[1] in ['-h','--help']:
                banner()
      
                print "command: " , __name__    
                print "Usage: python "+__name__+".py [OPTION]... [PROJECT]... [OTHER]..."
                print 
                print "Mandatory arguments to long options are mandatory for short options too."
                print 
                print "Startup:"
                print "  -V,  --version           display the version of Gump and exit."
                print "  -h,  --help              print this help."
                print "  -w,  --workspace         use this workspace for Gump."
                print 
                print "General:"
                print "  -v,  --verbose           verbose logging."
                print "  -d,  --debug             debug logging."
                print
                print "For bug reports use Bugzilla: http://bugzilla.apache.org/."
                print "For suggestions: <gump@jakarta.apache.org/>."
                sys.exit(0)
      
        if len(argv)>2 and argv[1] in ['-w','--workspace']:
            self.args.append(argv[2])
            del argv[1:3]
        else:
            self.args.append(default.workspace)
            log.info("No workspace defined with -w or -workspace.")
            log.info("Using default workspace: " + default.workspace)
    
        # determine which modules the user desires (wildcards are permitted)
        if requireProject:
            if len(argv)>1:
                self.args.append(argv[1] or '*')
                if self.args[1]=='all': self.args[1]='*'
                del argv[1:1]
            else:
                banner()
                print
                print " No project specified, please supply a project expressions or 'all'."
                print " Project wildcards are accepted, e.g. \"jakarta-*\"."
                sys.exit(1)
    
        # Allow extras...
        self.args += argv
  
        # 
        # Process global arguments
        #
        for arg in self.args:
            if arg in ['-d','--debug']: 
                log.info('Setting log level to DEBUG')
                log.setLevel(logging.DEBUG ) 
            elif arg in ['-v','--verbose']: 
                log.info('Setting log level to VERBOSE')
                # :TODO:
                log.setLevel(logging.DEBUG )  
    
    def getArguments(self):
        return self.args

def handleArgv(argv, requireProject=1):
    cl=CommandLine(argv,requireProject)
    return cl.getArguments()
    