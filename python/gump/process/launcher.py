#!/usr/bin/env python

# Copyright 2003-2004 The Apache Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
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

from string import split

from gump import log
from gump.core.config import dir
from gump.utils import *
from gump.utils.timing import *

import gump.process.command

LAUNCHER=os.path.join(os.path.join('gump','process'),'launcher.py')

def execute(cmd,tmp=dir.tmp):
    res=gump.process.command.CmdResult(cmd)
    return executeIntoResult(cmd,res,tmp)
	
def executeIntoResult(cmd,result,tmp=dir.tmp):
    """
    
    	Execute a command and capture the result
   
   	"""	
    
    outputFile=None
    start_time=time.time()
    try:
      try:          
 
        # The command line
        execString=cmd.formatCommandLine()        
        
        # Exec File
        execFile=os.path.abspath(os.path.join(tmp,gumpSafeName(cmd.name)+'.exec'))
        if os.path.exists(execFile): os.remove(execFile)
        
        # Output
        outputFile=os.path.abspath(os.path.join(tmp,gumpSafeName(cmd.name)+'.txt'))
        if os.path.exists(outputFile): os.remove(outputFile)
    
        try:            
            f=open(execFile, 'w')
            
            # The CMD
            f.write( 'CMD: %s\n' % (execString))
                
            # Dump the TMP
            if tmp:
                f.write( 'TMP: %s\n' % (tmp))
                
            # Dump the cwd (if specified)
            if cmd.cwd:
                f.write( 'CWD: %s\n' % (cmd.cwd))
                     
            # Write ENV over-writes...
            for envKey in cmd.env.iterkeys():
                f.write('%s: %s\n' % (envKey, cmd.env[envKey]))    
 
        finally:
            # Since we may exit via an exception, close explicitly.
            if f: f.close()    
            
        #############################################################          
           
        fullExec = sys.executable + ' ' + LAUNCHER + ' ' + execFile + \
                                    ' >>' + str(outputFile) + ' 2>&1'
                                    
        log.debug('Executing: ' + execString)
        log.debug('     Exec: ' + str(execFile))
        log.debug('   Output: ' + str(outputFile))
        log.debug('Full Exec: ' + fullExec)
        
        # Execute Command & Wait
        systemReturn=os.system(fullExec)
        
        if not os.name == 'dos' and not os.name == 'nt':
            waitcode=systemReturn
        
            #
            # The return code (from system = from wait) is (on Unix):
            #
            #	a 16 bit number
            #	top byte	=	exit status
            #	low byte	=	signal that killed it
            #
            result.signal=(waitcode & 0xFF)
            result.exit_code=(((waitcode & 0xFF00) >> 8) & 0xFF)
        
        else:
            
            result.signal=0
            result.exit_code=systemReturn
            
        log.debug('Command returned [' + str(systemReturn)+ '] [Sig:' + str(result.signal) + ' / Exit:' + str(result.exit_code) + '].')
        
        #
        # Assume timed out if signal terminated
        #
        if result.signal > 0:
            result.state=gump.process.command.CMD_STATE_TIMED_OUT
            log.warn('Command timed out. [' + execString + '] [' + str(timeout) + '] seconds.')
        # Process Outputs (exit_code and stderr/stdout)
        elif result.exit_code > 0:    
            result.state=gump.process.command.CMD_STATE_FAILED
            log.warn('Command failed. [' + execString + ']. ExitCode: ' + str(result.exit_code))
        else:
            result.state=gump.process.command.CMD_STATE_SUCCESS                
     
      except Exception, details :
        log.error('Failed to launch command. Details: ' + str(details))
        
        result.exit_code=-1
        result.state=gump.process.command.CMD_STATE_FAILED
        
    finally:
      # Clean Up Empty Output Files
      if outputFile and os.path.exists(outputFile):
          if os.path.getsize(outputFile) > 0:
              result.output=outputFile
          else:
              os.remove(outputFile)
        
      # Keep time information
      end_time=time.time()
      result.start_time=start_time
      result.end_time=end_time 
	  
    return result
        
    
if __name__=='__main__':
    import re
    
    exit_code=0
    execFilename=sys.argv[1]
    execFile=None
    try:
        execFile=file(execFilename,'r')
    
        # Split into a dict of NAME: VALUE (from file)
        execInfo=dict(re.findall('(.*?): (.*)', execFile.read()))
        
        #print execInfo
        #for key in execInfo.iterkeys():
        #    print 'KEY : ' + key  + ' -> ' + execInfo[key]
        
        cmd=execInfo['CMD']
        cwd=None
        if execInfo.has_key('CWD'):cwd=execInfo['CWD']
        tmp=execInfo['TMP']
       
        # Make the TMP if needed
        if not os.path.exists(tmp): os.makedirs(tmp)
       
        # Make the CWD if needed
        if cwd: 
          cwdpath=os.path.abspath(cwd)
          if not os.path.exists(cwdpath): os.makedirs(cwdpath)
          os.chdir(cwdpath)
       
        # Write ENV over-writes...
        for envKey in execInfo.iterkeys():
            if not envKey in ['CMD','TMP','CWD']:
                os.environ[envKey]=execInfo[envKey]
                
        systemReturn=os.system(cmd)
        
        if not os.name == 'dos' and not os.name == 'nt':
            waitcode=systemReturn
        
            #
            # The return code (from system = from wait) is (on Unix):
            #
            #    a 16 bit number
            #    top byte    =    exit status
            #    low byte    =    signal that killed it
            #
            signal=(waitcode & 0xFF)
            exit_code=(((waitcode & 0xFF00) >> 8) & 0xFF)
        
        else:
            signal=0
            exit_code=systemReturn
            
    finally:
        if execFile: execFile.close()
        
    # print 'Exit: ' + `exit_code`
    sys.exit(exit_code)
        
  
  
