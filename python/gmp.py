#!/bin/bash
#
#   Copyright 2003-2004 The Apache Software Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# $Header: /home/stefano/cvs/gump/python/gmp.py,v 1.7 2004/04/24 15:25:18 ajack Exp $

"""
  This is the commandline entrypoint into Python Gump as a
  build system (as opposed to a cronned CI tool).
  
  It works similarly to "cvs", as it needs to be given the action
  to do, and it needs to be run in the correct directory
  (workspace or project).
"""

import os.path
import os
import sys
import socket
import time
import signal
import smtplib
import StringIO
from xml.dom import minidom

def runCommand(command,args='',dir=None,outputFile=None):
    """ Run a command, and check the result... """
    
    #    
    originalCWD=None
    if dir:     
        originalCWD=os.getcwd()
        cwdpath=os.path.abspath(dir)
        try:
            if not os.path.exists(cwdpath): os.makedirs(dir)
            os.chdir(cwdpath)
        except Exception, details :
            # Log the problem and re-raise
            return 0
              
    try:
    
        fullCommand = command + ' ' + args    
        
        #
        # Execute Command & Calculate Exit Code
        #
        systemReturn=os.system(fullCommand)
        
        if not os.name == 'dos' and not os.name == 'nt':
            waitcode=systemReturn
        
            #
            # The return code (from system = from wait) is (on Unix):
            #
            #    a 16 bit number
            #    top byte    =    exit status
            #    low byte    =    signal that killed it
            #
            exit_code=(((waitcode & 0xFF00) >> 8) & 0xFF)
        
        else:
            exit_code=systemReturn
    
    finally:
        if originalCWD: os.chdir(originalCWD)
      
    return exit_code

def callGmpCommand(ws,command,projects,iargs):
    
    iargs+=' --text'
    
    #
    # Actually run the Gump command
    #    
    command=os.path.join(os.environ['GUMP_HOME'],'python/gump/'+command+'.py')

    exitValue = runCommand('python '+command+' -w '+ws+' '+projects, iargs, 'python')
    
    return exitValue
    

if not os.environ.has_key('GUMP_HOME'):
    print 'Please set GUMP_HOME to where Gump is installed.'
    sys.exit(1)
        
# Allow a lock
lockFile=os.path.abspath('gmp.lock')
if os.path.exists(lockFile):
    # :TODO: Ought we look at the contents, get the PID of the
    # supposed other Gump, and determine if it is still alive
    # or not?
    print """The lock file [%s] exists. 
Either Gump is still running, or it terminated very abnormally.    
Please resolve this (waiting or removing the lock file) before retrying.
    """ % lockFile
    sys.exit(1)
    
# Write this PID into a lock file
lock=open(lockFile,'w')
lock.write(`os.getpid()`)
lock.close()

result=0
        
args=sys.argv
try:
    print 'Apache Gump (A multi-project builder)'
    
    try:
        # Process Environment
        hostname = socket.gethostname()

        # The path of this command
        gmpPath = os.path.abspath(args[0])
        del args[0]     
       
        # Workspace is the `hostname`.xml or workspace.xml, 
        # unless overridden
        workspaceName = hostname + '.xml'
        if not os.path.exists(os.path.abspath(workspaceName)):
            workspaceName='workspace.xml'
            
        if os.environ.has_key('GUMP_WORKSPACE'):        
            workspaceName = os.environ['GUMP_WORKSPACE'] + '.xml'   
        if len(args)>2 and args[1] in ['-w','--workspace']:
            workspaceName=args[2]
            del args[1:3]     
        workspacePath = os.path.abspath(workspaceName)

        # Nope, can't find the workspace...
        if not os.path.exists(workspacePath):
            raise RuntimeError('No such workspace at ' + str(workspacePath))
        
        # Command has to be given
        if len(args)>0:
            command=args[0]
            del args[0]     
        else:
            raise RuntimeError('Must supply a Gump command')

        # Projects to be built are 'all', unless overridden
        projectsExpr='all'
        if len(args)>0:
            projectsExpr=args[0]
            del args[0]      

        #flatten the remaining args
        iargs=''
        for i in args:
            iargs+=(i+' ')
      
        #
        # Process the workspace...
        #     
        ws = minidom.parse(workspacePath)
        workspaceElementList=ws.getElementsByTagName('workspace')
        if not workspaceElementList.length == 1:
            raise RuntimeError('Need one (only) <workspace> tag. Found ' + \
                       ` workspaceElementList.length` + '.')    
        wsw=workspaceElementList.item(0)
        wsName=wsw.getAttribute('name')
        # Extract the base directory
        baseDir=wsw.getAttribute('basedir')      
        basePath=os.path.abspath(baseDir)
        # Log (site) location(s)   
        logurl=wsw.getAttribute('logurl')   
        logdir=wsw.getAttribute('logdir') or os.path.join(basePath,'log')
        # Finish parsing
        ws.unlink()

        #
        # Add Gump to Python Path...
        #
        pythonPath=''
        if os.environ.has_key('PYTHONPATH'):
            pythonPath=os.environ['PYTHONPATH']
            pythonPath+=os.pathsep
        pythonPath+=str(os.path.abspath(os.path.join(os.environ['GUMP_HOME'],'python')))
        os.environ['PYTHONPATH']=pythonPath

        result=callGmpCommand(workspacePath,command,projectsExpr,iargs)       

    except KeyboardInterrupt:    
        print 'Terminated by user interrupt...'
        result = 1
        raise
        
    except:    
        print 'Terminated unintentionally...'
        result = 1
        raise
    
finally:
    # :TODO: We have issues when python is killed, we get a lock
    # left around despite this finally.
    os.remove(lockFile)

# bye!
sys.exit(result)
