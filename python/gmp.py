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
# $Header: /home/stefano/cvs/gump/python/gmp.py,v 1.2 2004/04/10 11:16:50 nicolaken Exp $

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

def ignoreHangup(signum):
    pass

def glog(descr, what):
    log.write('- GUMP ' + descr + ' :['+ what + ']\n')
    
def runCommand(command,args='',dir=None,outputFile=None):
    """ Run a command, and check the result... """
    
    #    
    originalCWD=None
    if dir:     
        originalCWD=os.getcwd()
        cwdpath=os.path.abspath(dir)
        try:
            glog('Executing with CWD', dir )    
            if not os.path.exists(cwdpath): os.makedirs(dir)
            os.chdir(cwdpath)
        except Exception, details :
            # Log the problem and re-raise
            glog('Failed to create/change CWD', cwdpath)
            glog('Details', str(details) )
            return 0
              
    try:
        
        #
        if not outputFile:
            outputFile='out.tmp'
        
        fullCommand = command + ' ' + args + ' >' + outputFile + ' 2>&1'    
        glog('Execute', fullCommand)
       
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
    
        if os.path.exists(outputFile):
            if os.path.getsize(outputFile) > 0:
                catFile(log,outputFile)            
            os.remove(outputFile)
        
        glog('Exit Code', `exit_code`)
    
    finally:
        if originalCWD: os.chdir(originalCWD)
      
    return exit_code

def catFile(output,file,title=None):
    """ Cat a file to a stream... """
    if title:
        output.write('---------------------------------------------------------------- GUMP\n')    
        output.write(title + '\n\n')
        
    input=open(file,'r')
    line = input.readline()
    while line:
        output.write(line)
        # Next...
        line = input.readline()

def callGmpCommand(ws,command,projects,iargs):

    glog('ws',ws)
    glog('command',command)
    glog('projects',projects)
    glog('args',iargs)
    
    #
    # Actually run the Gump command
    #    
    command=os.path.join(os.environ['GUMP_HOME'],'python/gump/'+command+'.py')

    exitValue = runCommand('python '+command+' -w '+ws+' '+projects, iargs, 'python')
    if exitValue:
        result=1


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
    
# Set the signal handler to ignore hangups
try:
    # Not supported by all OSs
    # :TODO: Does the variable signal.SIG_HUP even exist? Test
    # this code on Linux w/o the try/except.
    signal.signal(signal.SIG_HUP, ignoreHangup)
except:
    pass
    
# Write this PID into a lock file
lock=open(lockFile,'w')
lock.write(`os.getpid()`)
lock.close()

# Enable a log
logFile=os.path.abspath('gmp.log')
log=open(logFile,'w',0) # Unbuffered...

result=0
        
args=sys.argv
try:

    try:
        # Process Environment
        hostname = socket.gethostname()

        glog('run on host  ',hostname)
        glog('run @        ',time.strftime('%d %b %y %H:%M:%S', time.gmtime()))
        glog('run by Python',`sys.version`)
        glog('run on OS    ',`os.name`)
        glog('run in env   ','see below')
        
        for envkey in os.environ.keys():
            envval=os.environ[envkey]
            glog('  ' + envkey, envval)

        # The path of this command
        gmpPath = os.path.abspath(args[0])
        del args[0]     

        # Workspace is 'workspace.xml', unless overridden
        workspaceName = 'workspace.xml'
        if len(args)>1 and args[0] in ['-w','--workspace']:
            workspaceName=args[1]
            del args[0:1]     
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
        
        glog('base directory', baseDir)
        glog('base path     ',str(basePath))
        if logurl:
            glog('log is @  ',logurl)

        #
        # Add Gump to Python Path...
        #
        pythonPath=''
        if os.environ.has_key('PYTHONPATH'):
            pythonPath=os.environ['PYTHONPATH']
            pythonPath+=os.pathsep
        pythonPath+=str(os.path.abspath(os.path.join(os.environ['GUMP_HOME'],'python')))
        glog('PYTHONPATH', pythonPath)
        os.environ['PYTHONPATH']=pythonPath

        callGmpCommand(workspacePath,command,projectsExpr,iargs)

    except KeyboardInterrupt:    
        log.write('Terminated by user interrupt...\n')
        result = 1
        raise
        
    except:    
        log.write('Terminated unintentionally...\n')
        result = 1
        raise
    
finally:
    # Close the log
    log.close()
    
    # :TODO: We have issues when python is killed, we get a lock
    # left around despite this finally.
    os.remove(lockFile)
    
    if 1 or result:
        logTitle='The Apache Gump log...'
        
        # :TODO: Need to check if stdout is a plain terminal? Not sure, see next.
        # :TODO: On some cron set-ups this will mail the log, on
        # others it won't.
        #
        # Cat log if failed...
        catFile(sys.stdout, logFile, logTitle)

# bye!
sys.exit(result)
