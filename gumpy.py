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
# $Header: $

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

def ignoreHangup(signum):
    pass
    
def runCommand(command,args='',dir=None,outputFile=None):
    """ Run a command, and check the result... """
    
    #    
    originalCWD=None
    if dir:     
        originalCWD=os.getcwd()
        cwdpath=os.path.abspath(dir)
        try:
            log.write('Executing with CWD: [' + dir + ']\n')    
            if not os.path.exists(cwdpath): os.makedirs(dir)
            os.chdir(cwdpath)
        except Exception, details :
            # Log the problem and re-raise
            log.write('Failed to create/change CWD [' + cwdpath + ']. Details: ' + str(details) + '\n')
            return 0
              
    try:
        
        #
        if not outputFile:
            outputFile='out.txt'
        
        fullCommand = command + ' ' + args + ' >' + outputFile + ' 2>&1'    
        log.write('Execute : ' + fullCommand + '\n')
       
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
        
        log.write('Exit Code : ' + `exit_code` + '\n')
    
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
        
def sendEmail(toaddr,fromaddr,subject,data,server,port=25):
    rawdata = "Date: %s\r\nFrom: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s"	\
           	% (	time.strftime('%d %b %y %H:%M:%S', time.gmtime()),
           	    fromaddr, toaddr,	subject,	data)
    try:
        #
        # Attach to the SMTP server to send....
        #
        server = smtplib.SMTP(server,port)
        #server.set_debuglevel(1)
        server.sendmail(fromaddr, toaddr, rawdata)
        server.quit()
        
    except Exception, details:
        print 'Failed to send mail: ' + str(details)
    
# Allow a lock
lockFile=os.path.abspath('gumpy.lock')
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
logFile=os.path.abspath('gumpy_log.txt')
log=open(logFile,'w',0) # Unbuffered...

result=0
        
mailserver=None
mailport=None
mailfrom=None
mailto=None
        
args=sys.argv
try:

    try:
        
        # Process Environment
        hostname = socket.gethostname()

        log.write('- GUMP run on host   : ' + hostname + '\n')
        log.write('- GUMP run @         : ' + time.strftime('%d %b %y %H:%M:%S', time.gmtime()) + '\n')
        log.write('- GUMP run by Python : ' + `sys.version` + '\n')
        log.write('- GUMP run on OS     : ' + `os.name` + '\n')
        log.write('- GUMP run in env    : \n')
        
        for envkey in os.environ.keys():
            envval=os.environ[envkey]
            log.write('      ' + envkey + ' -> [' + envval + ']\n')
        
        # Workspace is the hostname, unless overridden
        workspaceName = hostname + '.xml'
        if os.environ.has_key('GUMP_WORKSPACE'):        
            workspaceName = os.environ['GUMP_WORKSPACE'] + '.xml'   
        if len(args)>2 and args[1] in ['-w','--workspace']:
            workspaceName=args[2]
            del args[1:3]     
        workspacePath = os.path.abspath(workspaceName)
            
        projectsExpr='all'
        if os.environ.has_key('GUMP_PROJECTS'):        
            projectsExpr = os.environ['GUMP_PROJECTS']        
        if len(args)>1:
            projectsExpr=args[1]
            del args[1:2]      
            
        # Nope, can't find the workspace...
        if not os.path.exists(workspacePath):
            raise RuntimeError('No such workspace at ' + str(workspacePath))
        
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
        # Mail reporting
        mailserver=wsw.getAttribute('mailserver')
        mailport=wsw.getAttribute('mailport') or 25
        mailto=wsw.getAttribute('mailinglist')        
        mailfrom=wsw.getAttribute('email')  
        # Log (site) location(s)   
        logurl=wsw.getAttribute('logurl')   
        logdir=wsw.getAttribute('logdir') or os.path.join(basePath,'log')
        # Extract the mail server/address
        ws.unlink()
        
        log.write('- GUMP base directory : ' + baseDir + '\n')
        log.write('- GUMP base path      : ' + str(basePath) + '\n')
        if mailserver:
            log.write('- GUMP mail server    : ' + mailserver + '\n')
        if mailport:
            log.write('- GUMP mail port      : ' + str(mailport) + '\n')
        if mailfrom:
            log.write('- GUMP mail from      : ' + mailfrom + '\n')
        if mailto:
            log.write('- GUMP mail to        : ' + mailto + '\n')
        if logurl:
            log.write('- GUMP log is @       : ' + logurl + '\n')

        #
        # Add Gump to Python Path...
        #
        pythonPath=''
        if os.environ.has_key('PYTHONPATH'):
            pythonPath=os.environ['PYTHONPATH']
            pythonPath+=os.pathsep
        pythonPath+=str(os.path.abspath(os.path.join(os.getcwd(),'python')))
        log.write(' - GUMP PYTHONPATH  :  ' + pythonPath + '\n')
        os.environ['PYTHONPATH']=pythonPath

        #
        # Update Gump from CVS
        #    
        cvsExit = 0
        if not os.environ.has_key('GUMP_NO_CVS_UPDATE'):
            cvsroot=':pserver:anoncvs@cvs.apache.org:/home/cvspublic'
            os.environ['CVSROOT']=cvsroot
            # :TODO: ??? delete os.environ['CVS_RSH']
            cvsExit = runCommand('cvs -q update -dP')
        else:
            log.write('CVS update skipped per environment setting.\n')
        if cvsExit:
            result=1
            
        # :TODO: Need to remove all *.pyc (other than this one)
        # because a Gump refactor can leave old/stale compiled
        # classes around.
            
        # :TODO: Is this a CVS thing, or a Gump historical thing?
        if os.path.exists('.timestamp'): 
            os.remove('.timestamp')            
    
        if not result:
            #
            #
            # Process/build command line
            #        
            iargs = '-w ../' + workspaceName + ' ' + projectsExpr + ' ' + ' '.join(args[1:])
            
            # Allow a check not an integrate
            check=0
            if '--check' in args:
                check=0
            
            #
            # Run the main Gump...
            #    
            command='gump/integrate.py'
            if check:
                command='gump/check.py'
            integrationExit = runCommand('python '+command, iargs, 'python')
            if integrationExit:
                result=1

            # :TODO: Copy outputs (especially forrest) into log dir
            # for remote debuging.         

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
        published=0
        if logdir:
            publishedLogFile=os.path.abspath(os.path.join(logdir,'gumpy_log.txt'))
            try:
                publishedLog=open(publishedLogFile,'w',0) # Unbuffered...
                catFile(publishedLog, logFile, logTitle)    
                publishedLog.close()
                published=1
            except:
                published=0
                
        if not published:
            catFile(sys.stdout, logFile, logTitle)
        
        if mailserver and mailport and mailto and mailfrom and logurl:
            
            #:TODO:
            # We need to move the gumpy.log to the log
            # directory, so we can mail a URL to it.
        
            # :TODO: Sucky to read file into memory...
            # Need to figure out attachments, if that
            # helps & doesn't just do same...
            #tmpStream=StringIO.StringIO() 
            #catFile(tmpStream, logFile, logTitle)
            #tmpStream.seek(0)
            #logData=tmpStream.read()
            #tmpStream.close()
            #tmpStream=None
            logData='There is a problem with the run at : ' + logurl
            sendEmail(mailto,mailfrom,logTitle,logData,mailserver,mailport)

# bye!
sys.exit(result)
