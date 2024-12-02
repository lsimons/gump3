#!/usr/bin/env python

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

"""
    Executing processes (CVS, ant, etc.) and capturing results
"""

import os
import sys
import logging
import signal
import re

from gump import log
from gump.core.config import dir
from gump.util import *
from gump.util.timing import *
from gump.util.process import command
    
# A separate launcher script/process is used on Windows, on Unix we fork/exec.
LAUNCHER = os.path.join('python','gump','util','process','launcher.py')

def execute(cmd,tmp=dir.tmp):
    res = command.CmdResult(cmd)
    return executeIntoResult(cmd,res,tmp)
	
def executeIntoResult(cmd,result,tmp=dir.tmp):
    """
    	Execute a command and capture the result
   	"""
    outputFile = None
    start = getLocalNow()
    try:
      try:          
 
        # The command line
        execString = cmd.formatCommandLine()        
        
        # Output
        outputFile = os.path.abspath(os.path.join(tmp,gumpSafeName(cmd.name)+'.txt'))
        if os.path.exists(outputFile): os.remove(outputFile)

        # Exec File
        execFile = os.path.abspath(os.path.join(tmp,gumpSafeName(cmd.name)+'.exec'))
        if os.path.exists(execFile): os.remove(execFile)
            
        try:            
            f = open(execFile, 'w')
            # The CMD
            f.write( 'CMD: %s\n' % (execString))
            # The OUTPUT
            f.write( 'OUTPUT: %s\n' % (outputFile))
            # Dump the TMP
            if tmp: f.write( 'TMP: %s\n' % (tmp))
            # Dump the cwd (if specified)
            if cmd.cwd: f.write( 'CWD: %s\n' % (cmd.cwd))
            
            if 'posix' != os.name :
                # Write the TIMEOUT
                if cmd.timeout: f.write( 'TIMEOUT: %s\n' % (cmd.timeout))    
                
            # Write ENV over-writes...
            for envKey in cmd.env.keys(): f.write('%s: %s\n' % (envKey, cmd.env[envKey]))    
        finally:
            # Since we may exit via an exception, close explicitly.
            if f: f.close()    
        
        # make sure that the python path includes the gump modules
        os.environ['PYTHONPATH'] = os.path.abspath(os.path.join(os.getcwd(),'./python'))
        
        if 'posix' == os.name :
            
            # Fork to get a child 'cos we are going to crap into
            # it's ENV, and we don't want to mess in our own.
            forkPID = os.fork();
            
            # Child gets PID = 0
            if 0 == forkPID:
                # Become a process group leader
                os.setpgrp()
                
                # Run the information within this file...
                os._exit(runProcess(execFile,0))
            
            # Parent gets real PID
            else:
                # Timeout support
                timer = None
                if cmd.timeout:
                    import threading
                    timer = threading.Timer(cmd.timeout, \
		    		    shutdownProcessAndProcessGroup, [forkPID])
                    timer.start()
            
                # Run the command
                (childPID, waitcode) = os.waitpid(forkPID,0)
                
                # Stop timer (if still running)
                if timer and timer.is_alive(): 
                    timer.cancel()      
                
                # The return code (from system = from wait) is (on Unix):
                #    a 16 bit number
                #    top byte    =    exit status
                #    low byte    =    signal that killed it
                result.signal = (waitcode & 0xFF)
                result.exit_code = (((waitcode & 0xFF00) >> 8) & 0xFF)
            
                #log.debug('Command returned [' + str(systemReturn)+ '] [Sig:' + str(result.signal) + ' / Exit:' + str(result.exit_code) + '].')
        
                # Assume timed out if signal terminated
                if result.signal > 0:
                    result.state = command.CMD_STATE_TIMED_OUT
                    #log.warn('Command timed out. [' + execString + '] [' + str(timeout) + '] seconds.')
                
                    # Process Outputs (exit_code and stderr/stdout)
                elif result.exit_code > 0:    
                    result.state = command.CMD_STATE_FAILED
                    #log.warn('Command failed. [' + execString + ']. ExitCode: ' + str(result.exit_code))
                else:
                    result.state = command.CMD_STATE_SUCCESS         
                  
        else:
            
            # Run another python process (to crap into it's ENV not the main, multi-threaded, one.)
            fullExec = sys.executable + ' ' + LAUNCHER + ' ' + execFile
                                    
            #log.debug('Executing: ' + execString)
            #log.debug('     Exec: ' + str(execFile))
            #log.debug('   Output: ' + str(outputFile))
            #log.debug('Full Exec: ' + fullExec)
        
            # Execute Command & Wait
            systemReturn = os.system(fullExec)
        
            if not os.name == 'dos' and not os.name == 'nt':
                waitcode = systemReturn
                # The return code (from system = from wait) is (on Unix):
                #	a 16 bit number
                #	top byte	=	exit status
                #	low byte	=	signal that killed it
                result.signal = (waitcode & 0xFF)
                result.exit_code = (((waitcode & 0xFF00) >> 8) & 0xFF)
            else:
                result.signal = 0
                result.exit_code = systemReturn
            
            #log.debug('Command returned [' + str(systemReturn)+ '] [Sig:' + str(result.signal) + ' / Exit:' + str(result.exit_code) + '].')
        
            # Assume timed out if signal terminated
            if result.signal > 0:
                result.state = command.CMD_STATE_TIMED_OUT
                #log.warn('Command timed out. [' + execString + '] [' + str(timeout) + '] seconds.')
                
                # Process Outputs (exit_code and stderr/stdout)
            elif result.exit_code > 0:    
                result.state = command.CMD_STATE_FAILED
                #log.warn('Command failed. [' + execString + ']. ExitCode: ' + str(result.exit_code))
            else:
                result.state = command.CMD_STATE_SUCCESS                
     
      except Exception as details :
          log.error('Failed to launch command. Details: ' + str(details), exc_info=1) 
          result.exit_code = -1
          result.state = command.CMD_STATE_FAILED
        
    finally:
      # Clean Up Empty Output Files
      if outputFile and os.path.exists(outputFile):
          if os.path.getsize(outputFile) > 0:
              result.output = outputFile
          else:
              os.remove(outputFile)
        
      # Keep time information
      end = getLocalNow()
      result.start = start
      result.end = end 
	  
    return result
    
def shutdownProcessAndProcessGroup(pid):
    """
    Kill this (and all child processes).
    """
    log.warn('Kill process group (anything launched by PID %s)' % (pid))    
    try:
        pgrpID=os.getpgid(pid)
        log.warn('Kill process group %s (i.e. anything launched by PID %s) [from %s, for %s]' \
                    % (pgrpID, pid, os.getpid(), default.gumpid))  
        if -1 != pgrpID:
            # Give cores time to be produced, then just get serious...
            os.killpg(pgrpID,signal.SIGABRT)
            time.sleep(10)
            os.killpg(pgrpID,signal.SIGKILL)
        else:
            log.warn('No such PID' + str(pid) + '.')    
    except Exception as details:
        log.error('Failed to dispatch signal ' + str(details), exc_info=1)
        
        
def shutdownProcesses():
    """
    Kill this (and all child processes).
    """
    pid=os.getpid()
    log.warn('Kill all child processed (anything launched by PID %s)' % (pid))    
    try:
        os.kill(pid,signal.SIGKILL)
    except Exception as details:
        log.error('Failed to dispatch signal ' + str(details), exc_info=1)
         
def runProcess(execFilename,standaloneProcess=1):
    """
    Read an 'exec file' (formatted by Gump) to detect what to run,
    and how to run it.
    """
    execFile = None
    try:
        execFile = open(execFilename,'r')
    
        # Split into a dict of NAME: VALUE (from file)
        execInfo = dict(re.findall('(.*?): (.*)', execFile.read()))
        
        #print execInfo
        #for key in execInfo.iterkeys():
        #    print 'KEY : ' + key  + ' -> ' + execInfo[key]
        
        cmd = execInfo['CMD']
        outputFile = execInfo['OUTPUT']
        cwd = None
        if 'CWD' in execInfo: cwd = execInfo['CWD']
        tmp = execInfo['TMP']
        timeout = 0
        if 'TIMEOUT' in execInfo: timeout = int(execInfo['TIMEOUT'])
       
        # Make the TMP if needed
        if not os.path.exists(tmp): os.makedirs(tmp)
       
        # Make the CWD if needed
        if cwd: 
          cwdpath = os.path.abspath(cwd)
          if not os.path.exists(cwdpath): os.makedirs(cwdpath)
          os.chdir(cwdpath)
       
        # Write ENV over-writes...
        for envKey in execInfo.keys():
            if not envKey in ['CMD','TMP','CWD']:
                os.environ[envKey] = execInfo[envKey]
               
        # Timeout support
        timer = None
        if timeout and standaloneProcess:
            import threading
            timer = threading.Timer(timeout, shutdownProcesses)
            timer.setDaemon(1)
            timer.start()
            
        # Allow redirect
        cmd += ' >>' + str(outputFile) + ' 2>&1'
        
        # Run the command
        systemReturn = os.system(cmd)
                  
        # Stop timer (if still running)
        if timer: timer.cancel() 
        
        if not os.name in ['dos','nt']:
            waitcode = systemReturn
            # The return code (from system = from wait) is (on Unix):
            #    a 16 bit number
            #    top byte    =    exit status
            #    low byte    =    signal that killed it
            signal = (waitcode & 0xFF)
            exit_code = (((waitcode & 0xFF00) >> 8) & 0xFF)
        else:
            signal = 0
            exit_code = systemReturn
            
    finally:
        if execFile: execFile.close()
        
    return exit_code

if __name__=='__main__':
    
    exit_code = 0
    execFilename = sys.argv[1]
    
    # Run the information within this file...
    exit_code = runProcess(execFilename,1)
        
    # print 'Exit: ' + `exit_code`
    sys.exit(exit_code)
