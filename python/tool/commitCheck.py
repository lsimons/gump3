#!/usr/bin/env python
#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# $Header: /home/stefano/cvs/gump/python/tool/commitCheck.py,v 1.2 2004/07/08 20:33:10 ajack Exp $

"""
  Used to do Python testing prior to commiting a code change.
"""

import os.path
import os
import sys
import socket
import time
import signal
import smtplib
import io
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
        except Exception as details :
            # Log the problem and re-raise
            log.write('Failed to create/change CWD [' + cwdpath + ']. Details: ' + str(details) + '\n')
            return 0
              
    try:
        
        #
        if not outputFile:
            outputFile=os.tmpnam()
        
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
        
        log.write('Exit Code : ' + repr(exit_code) + '\n')
    
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
        
# Allow a lock
lockFile=os.path.abspath('gump_check.lock')
if os.path.exists(lockFile):
    # :TODO: Ought we look at the contents, get the PID of the
    # supposed other Gump, and determine if it is still alive
    # or not?
    print("""The lock file [%s] exists. 
Either Gump is still running, or it terminated very abnormally.    
Please resolve this (waiting or removing the lock file) before retrying.
    """ % lockFile)
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
lock.write(repr(os.getpid()))
lock.close()

# Enable a log
logFile=os.path.abspath('gump_check_log.txt')
log=open(logFile,'w',0) # Unbuffered...

result=0
        
args=sys.argv
try:

    try:
        
        # Process Environment
        hostname = socket.gethostname()

        log.write('- GUMP run on host   : ' + hostname + '\n')
        log.write('- GUMP run @         : ' + time.strftime('%d %b %Y %H:%M:%S', time.gmtime()) + '\n')
        log.write('- GUMP run by Python : ' + repr(sys.version) + '\n')
        log.write('- GUMP run on OS     : ' + repr(os.name) + '\n')
        log.write('- GUMP run in env    : \n')
        
        #
        # Add Gump to Python Path...
        #
        pythonPath=''
        if 'PYTHONPATH' in os.environ:
            pythonPath=os.environ['PYTHONPATH']
            pythonPath+=os.pathsep
        absGumpPython=os.path.abspath(os.path.join(os.getcwd(),'python'))
        if not str(absGumpPython) in pythonPath:
            pythonPath+=str(absGumpPython)
        log.write('- GUMP PYTHONPATH    :  ' + pythonPath + '\n')
        os.environ['PYTHONPATH']=pythonPath

        #
        # Do NOT Update Gump from CVS
        # :TODO: Debatable...
        #    
        os.environ['GUMP_NO_CVS_UPDATE']='DO NOT UPDATE'
            
        # :TODO: Need to remove all *.pyc (other than this one)
        # because a Gump refactor can leave old/stale compiled
        # classes around.
        
        #try:
        #    # :TODO: PyChecker
        #    check=''
        #    for m in ['gump','gump.actor.document','gump.core.model']:
        #        if check: check += ' '
        #        mPath=os.path.join(absGumpPython,m)
        #        check += str(mPath)
        #    print "Python Checker : [" + check + "]"
        #    os.environ['PYCHECKER'] =  check
        #    import pychecker.checker   
        #except:
        #    print 'Failed to PyChecker code...'
        #    pass
        possiblePackages=[]     
        for dirpath, dirs, files in os.walk(os.path.abspath(os.path.join(absGumpPython,'gump'))):
            possiblePackages.append(dirpath)
        
        # :TODO: Make dynamic (use os.walk or something)
        for p in possiblePackages:
            if not result:
                check=''
                for file in os.listdir(p):
                    if file.endswith('.py'):
                        if check: check += ' '
                        check += str(os.path.join(p,file))
                if check:
                    # print "Python Checker : [" + check + "]"        
                    checkerExit=runCommand('pychecker',check,str(absGumpPython))
                    #if checkerExit:
                    #    result=1
        
        if not result:
            # PyUnit            
            unitExit = runCommand('python gump/test/pyunit.py','*',str(absGumpPython))
            if unitExit: 
                log.write('***************** Unit Tests Failed ***************\n')
                result=1
            
        if not result:
            # A test run...
            integrationExit = runCommand('gump')
            if integrationExit:                 
                log.write('**************** Test Run Failed ***************\n')
                result=1           

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
    
    if result:
        logTitle='The Apache Gump log...'
        catFile(sys.stdout, logFile, logTitle)
        print("Something failed...")
        
# bye!
sys.exit(result)
