#!/usr/bin/python

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__revision__  = "$Rev: 36667 $"
__date__      = "$Date: 2004-08-20 08:55:45 -0600 (Fri, 20 Aug 2004) $"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"


"""

    Commandline Handling.
    
    Note: All gump scripts currently have the same command line
    
    
"""
import sys
import logging

from gump import log
from gump.core.config import default
from gump.util import banner

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
        
        # For storing options
        import gump.core.run.options
        self.options=gump.core.run.options.GumpRunOptions()
        
        # Print the banner
        banner()

        # Extract the workspace
        if len(argv)==2: 
            if argv[1] in ['-V','--version']:
                sys.exit(0)      
            elif argv[1] in ['-h','--help']:
                print "command: " , __name__    
                print "Usage: python "+__name__+".py -w {workspaceFile} [OPTION] [PROJECT]"
                print 
                print "Mandatory arguments to long options are mandatory for short options too."
                print 
                print "Startup:"
                print "  -V,  --version           display the version of Apache Gump(TM) and exit."
                print "  -h,  --help              print this help."
                print "  -w,  --workspace         use this workspace for Gump."
                print 
                print "General:"
                print "  -v,  --verbose           verbose logging."
                print "  -d,  --debug             debug logging."
                print
                print " Not relevent to all scripts:"
                print "  -O,  --official          Full run, publishing notifications, etc."
                print "  -D,  --dated             Dated log files."
                print "  -c,  --cache             Use local cache (do not download over HTTP)."
                print "  -t,  --text              Use text not xdocs."
                print "  -X,  --xdocs             Output xdocs, not XHTML."
                print
                print "For bug reports use JIRA: http://issues.apache.org/."
                print "For suggestions: <general@gump.apache.org/>."
                sys.exit(0)
      
        # 
        # Process global arguments
        #
        removers=[]
        for arg in argv:
            if arg in ['-d','--debug']:
                removers.append(arg) 
                log.info('Setting log level to DEBUG')
                self.options.setVerbose(True) # Sub-set of debug
                self.options.setDebug(True)
                log.setLevel(logging.DEBUG) 
            elif arg in ['-v','--verbose']: 
                removers.append(arg) 
                log.info('Setting log level to VERBOSE')
                self.options.setVerbose(True)
                # :TODO: VERBOSE doesn't exist within logging...
                log.setLevel(logging.DEBUG)  
            elif arg in ['-l','--latest']:
                removers.append(arg)
                self.options.setCache(False)
                self.options.setQuick(False)
                log.info('Absolute Latest [no use of cache, don\'t skip stack]')
            elif arg in ['-D','--dated']:
                removers.append(arg)    
                #
                # Dated means add the date to the log dir...
                #
                self.options.setDated(True)                    
                log.info('Dated Operation (add date to log dir)')
            elif arg in ['-H','--historical']:
                removers.append(arg)    
                self.options.setHistorical(True)                    
                log.info('Historical Database Operation')
            elif arg in ['-O','--official']:
                removers.append(arg)    
                self.options.setOfficial(True)                    
                log.info('Official run (publish notifications, etc.)')
            elif arg in ['-c','--cache']:
                removers.append(arg)        
                self.options.setCache(True)
                log.info('Use cache (do not download latest over HTTP).')
            elif arg in ['-t','--text']:
                removers.append(arg)        
                self.options.setText(True)
                log.info('Use text (not xdocs).')
            elif arg in ['-x','--xdocs']:
                removers.append(arg)        
                self.options.setXDocs(True)
                log.info('Output xdocs (not XHTML).')
                
        # Remove 
        for arg in removers:
            argv.remove(arg)

        removers=[]
        if len(argv)>2 and argv[1] in ['-w','--workspace']:
            self.args.append(argv[2])
            del argv[1:3]
        else:
            self.args.append(default.workspace)
            log.info("No workspace defined with -w or -workspace.")
            log.info("Using default workspace: " + default.workspace)
    
        # Remove the XXXXXX.py
        del argv[0] 
          
        # determine which modules the user desires (wildcards are permitted)
        if requireProject:
            if len(argv)>0:
                for arg in argv:
                    if arg=='all':
                        self.args.append('*')
                    else: 
                        self.args.append(arg)
                    removers.append(arg)        
            else:
                print
                print " No project specified, please supply a comma separated list of project expressions or 'all'."
                print " Project wildcards are accepted, e.g. \"jakarta-*\"."
                sys.exit(1)
             
        # Remove those used
        for arg in removers: argv.remove(arg)
            
        for arg in argv:
            log.debug("Unused command line argument : " + arg)
            
        for arg in self.args:
            log.debug("Produced Argument : " + arg)

    def getArguments(self):
        """
        Get the primary arguments (workspace and project expression)
        """
        return self.args
        
    def getOptions(self):
        """
        Get configured options (e.g. --debug).
        """
        return self.options

def handleArgv(argv, requireProject=1):
    cl=CommandLine(argv,requireProject)
    return (cl.getArguments(), cl.getOptions())
    
