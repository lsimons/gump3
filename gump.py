#!/usr/bin/env python

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
__revision__  = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

"""

  This is the commandline entrypoint into Python Gump,
  used *primarily* by nightly cron jobs.
  
  It updates Gump (from CVS) to ensure it (itself) is 
  latest, does some environment twiddling, and runs the
  main gump/integration.py. Bit more twiddling with 
  outputs afterwards...

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

LINE=' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - GUMP'

GUMP_VERSION='2.0.2-alpha-0003'

def runCommand(command,args='',dir=None,outputFile=None):
    """ Run a command, and check the result... """
    
    #    
    originalCWD=None
    if dir:     
        originalCWD=os.getcwd()
        cwdpath=os.path.abspath(dir)
        try:
            sys.stdout.write('Executing with CWD: [' + dir + ']\n')    
            if not os.path.exists(cwdpath): os.makedirs(dir)
            os.chdir(cwdpath)
        except Exception, details :
            # Log the problem and re-raise
            sys.stdout.write('Failed to create/change CWD [' + cwdpath + ']. Details: ' + str(details) + '\n')
            return 0
              
    try:              
        fullCommand = command + ' ' + args  
        sys.stdout.write('Execute : ' + fullCommand + '\n')
       
        # Execute Command & Calculate Exit Code
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
    
        if exit_code:
            sys.stdout.write('Process Exit Code : ' + `exit_code` + '\n')
    
    finally:
        if originalCWD: os.chdir(originalCWD)
      
    return exit_code

def catFile(output,file,title=None):
    """ Cat a file to a stream... """
    if title:
        output.write(LINE + '\n')    
        output.write(title + '\n\n')
        
    input=open(file,'r')
    line = input.readline()
    while line:
        output.write(line)
        # Next...
        line = input.readline()
        
def establishLock(lockFile):

    failed=0
    info=''
    if 'posix'==os.name:
        import fcntl
                
        try:            
            lock=open(lockFile,'a+')
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except:            
            failed=1
            info=', and is locked.'
        
    else:
        if os.path.exists(lockFile):
            failed=1
        
        # Write this PID into a lock file
        lock=open(lockFile,'w')
            
    if failed:
        print """The lock file [%s] exists%s. 
Either Gump is still running, or it terminated very abnormally.    
Please resolve this (waiting or removing the lock file) before retrying.
        """ % (lockFile, info)
        sys.exit(1)
    
    # Leave a mark...
    lock.write(`os.getpid()`)
    lock.flush()
        
    return lock
        
def releaseLock(lock,lockFile):
      
    if 'posix'==os.name:
        import fcntl            
        try:
            fcntl.flock(lockFile.fileno(), fcntl.LOCK_UN)
        except:
            pass
    
    # Close it, so we can dispose of it
    lock.close()    
    
    # Others might be blocked on this
    try:
        os.remove(lockFile)
    except:
        # Somehow another could delete this, even if locked...
        pass
             
# Ensure we start in the correct directory, setting GUMP_HOME
gumpHome=os.path.abspath(os.getcwd())
os.environ['GUMP_HOME']=gumpHome     
os.chdir(gumpHome)

# Allow a lock    
lockFile=os.path.abspath('gump.lock')
lock=establishLock(lockFile)        
    
hostname='Unknown'
workspaceName='Unknown'
        
args=sys.argv
result=0
svnExit = -1
cvsExit = -1
integrationExit = -1
        
try:

    try:
        
        # Process Environment
        hostname = socket.gethostname()

        sys.stdout.write('- ************************************\n')
        sys.stdout.write('-            Apache Gump \n')
        sys.stdout.write('- ************************************\n')
        sys.stdout.write('- GUMP run on host   : ' + hostname + '\n')
        sys.stdout.write('- GUMP run @         : ' + time.strftime('%d %b %y %H:%M:%S', time.localtime()) + '\n')
        sys.stdout.write('- GUMP run @  UTC    : ' + time.strftime('%d %b %y %H:%M:%S', time.gmtime()) + '\n')
        sys.stdout.write('- GUMP run by Python : ' + `sys.version` + '\n')
        sys.stdout.write('- GUMP run by Python : ' + `sys.executable` + '\n')
        sys.stdout.write('- GUMP run by Gump   : ' + GUMP_VERSION + '\n')
        sys.stdout.write('- GUMP run on OS     : ' + `os.name` + '\n')
        
        #sys.stdout.write('- GUMP run in env    : \n')        
        #for envkey in os.environ.keys():
        #    envval=os.environ[envkey]
        #    sys.stdout.write('      ' + envkey + ' -> [' + envval + ']\n')
        
        # Workspace is the hostname, unless overridden
        workspaceName = 'metadata/' + hostname + '.xml'
        if len(args)>2 and args[1] in ['-w','--workspace']:
            workspaceName=args[2]
            del args[1:3]     
        workspacePath = os.path.abspath(workspaceName)
            
        projectsExpr='all'
        if len(args)>1:
            projectsExpr=args[1]
            del args[1:2]      
            
        # Check version information
        (major, minor, micro, releaselevel, serial) = sys.version_info
        if not major >=2 and minor >= 3:
            raise RuntimeError('Gump requires Python 2.3 or above. [' + sys.version() + ']')
            
        # Nope, can't find the workspace...
        if not os.path.exists(workspacePath):
            raise RuntimeError('No such workspace at ' + str(workspacePath))
   
        # Add Gump to Python Path...
        pythonPath=''
        if os.environ.has_key('PYTHONPATH'):
            pythonPath=os.environ['PYTHONPATH']
            pythonPath+=os.pathsep
        pythonDir=str(os.path.abspath(os.path.join(os.getcwd(),'python')))
        pythonPath+=pythonDir
        sys.stdout.write('- GUMP PYTHONPATH  :  ' + pythonPath + '\n')
        os.environ['PYTHONPATH']=pythonPath
        
        # Wipe all *.pyc from the pythonPath (so we don't
        # have old code lying around as compiled zombies)
        for root, dirs, files in os.walk(pythonDir):
            for name in files:
                if name.endswith('.pyc'):
                    fullname=os.path.join(root, name)
                    # sys.stdout.write('- Remove PYC : ' + fullname + '\n')    
                    os.remove(fullname)       
        
        # Update Gump code from SVN
        if not os.environ.has_key('GUMP_NO_SVN_UPDATE') and \
            not os.environ.has_key('GUMP_NO_SCM_UPDATE'):
            svnExit = runCommand('svn','update --non-interactive')
        else:
            sys.stdout.write('SVN update skipped per environment setting.\n')
            svnExit=0
        if svnExit:
            result=1     
        
        if not result:
            # Update Gump metadata from CVS
            if not os.environ.has_key('GUMP_NO_CVS_UPDATE') and \
                not os.environ.has_key('GUMP_NO_SCM_UPDATE'):
                cvsroot=':pserver:anoncvs@cvs.apache.org:/home/cvspublic'
                os.environ['CVSROOT']=cvsroot
                # :TODO: ??? delete os.environ['CVS_RSH']
                cvsExit = runCommand('cvs','-q update -dP','metadata')
            else:
                sys.stdout.write('CVS update skipped per environment setting.\n')
                cvsExit=0
            if cvsExit:
                result=1
            
        # :TODO: Need to remove all *.pyc (other than this one)
        # because a Gump refactor can leave old/stale compiled
        # classes around.
            
        # :TODO: Is this a CVS thing, or a Gump historical thing?
        if os.path.exists('.timestamp'): 
            os.remove('.timestamp')            
    
        if not result:
            # Process/build command line
            iargs = '-w ' + workspaceName + ' ' + projectsExpr + ' ' + ' '.join(args[1:])
            
            # Allow a check not an integrate
            check=0
            if '--check' in args:
                check=0
            
            #
            # Run the main Gump...
            #    
            command='bin/integrate.py'
            if check:
                command='bin/check.py'
            integrationExit = runCommand(sys.executable+ ' '+command, iargs)
            if integrationExit:
                result=1

    except KeyboardInterrupt:    
        sys.stdout.write('Terminated by user interrupt...\n')
        result = 1
        raise
        
    except:    
        sys.stdout.write('Terminated unintentionally...\n')
        result = 1
        raise
    
finally:
 
    releaseLock(lock,lockFile) 
       
# bye!
sys.exit(result)
