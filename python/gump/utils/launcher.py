#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/utils/Attic/launcher.py,v 1.4 2003/12/11 18:56:26 ajack Exp $
# $Revision: 1.4 $
# $Date: 2003/12/11 18:56:26 $
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
    Executing process (CVS, ant, etc.) and capturing results
"""

import os
import sys
import logging
import signal

from threading import Timer
    
from string import split

from gump import log
from gump.config import *
from gump.utils import *

CMD_STATE_NOT_YET_RUN=0
CMD_STATE_SUCCESS=1
CMD_STATE_FAILED=2
CMD_STATE_TIMED_OUT=3

states = { CMD_STATE_NOT_YET_RUN : "Not Run",
           CMD_STATE_SUCCESS : "Success",
           CMD_STATE_FAILED : "Failed",
           CMD_STATE_TIMED_OUT : "Timed Out" }

class Parameter:
    """Name/Value"""
    def __init__(self,name,value=None,separator=' ',prefix=None):        
      #if not name:
      #    raise 'Unnamed Parameter'
      if not name: log.error('Unnamed Parameter')
      self.name=name
      self.value=value
      self.separator=separator
      self.prefix=prefix
    
        
    def isRequiresQuoting(self):
        if self.name:
            if ' ' in self.name: return 1
            if default.shellQuote in self.name: return 1
            if default.shellEscape in self.name: return 1
                        
        if self.value:
            if ' ' in self.value: return 1
            if default.shellQuote in self.value: return 1
            if default.shellEscape in self.value: return 1
            
        return 0
                
    
def getParameterFromString(strp):
    """Extract a Parameter Object from a String"""
    parts=split(strp,'=')
    partCount=len(parts)
    if partCount==1:
        pname=parts[0]
        pvalue=None
        psep=''
    elif partCount > 1:
        pname=parts[0]
        pvalue=parts[1]
        psep='='
    else:
        return None
        
    return Parameter(pname,pvalue,psep)
    
class Parameters:
    """An ordered set of command line parameters w/ last overriding first"""
    def __init__(self):
      self.list=[]
      self.dict={}
      
    def addPrefixedParameter(self,prefix,name,value=None,separator=' '):
      self.addParameter(name,value,separator,prefix)
      
    def addPrefixedNamedParameter(self,prefix,name,value=None,separator=' '):
      self.addNamedParameter(name,value,separator,prefix)
      
    def addNamedParameter(self,name,value=None,separator=' ',prefix=None):
      if self.dict.has_key(name):
        self.removeParameter(name)
      self.addParameter(name,value,separator,prefix)
 
    def addNamedParameterObject(self,param):
      if self.dict.has_key(param.name):
        self.removeParameter(param.name)
      self.addParameterObject(param)
 
    def addParameter(self,name,value=None,separator=' ',prefix=None):
      param=Parameter(name,value,separator,prefix)
      self.addParameterObject(param)
      
    def addParameterObject(self,param):
      self.list.append(param)
      self.dict[param.name]=param
        
    def removeParameter(self,name):
      for param in self.list:
        if param.name==name: 
          self.list.remove(param)
          del self.dict[name]
    
    def formatCommandLine(self):
      line = ''
      for param in self.list:
        requiresQuoting=param.isRequiresQuoting()
        
        if requiresQuoting:
            line+=default.shellQuote
        
        if param.prefix: 
          line += param.prefix
          
        #
        # Deal w/ escaping quotes
        #
        line += self.getEscapedEntry(param.name)
        val = param.value
        if val:
            line += param.separator
            line += self.getEscapedEntry(val)        
            
        if requiresQuoting:
            line+=default.shellQuote            
        line += ' '
        
      return line
        
    def getEscapedEntry(self,entry):
        if not entry: return
        escapedEntry=entry.replace(default.shellEscape,default.shellEscape+default.shellEscape)        
        escapedEntry=escapedEntry.replace(default.shellQuote,default.shellEscape+default.shellQuote)
        return escapedEntry
        
    def items(self):
      return self.list
      
    def dump(self,indent=''):
      for param in self.list:
        print indent+'  '+param.name+' '+str(param.value)+' ('+str(param.prefix)+')'
      
class Cmd:
    """Command Line (executable plus parameters)"""
    def __init__(self,command,name,cwd=None,env=None,timeout=None):
        self.cmdpath=command
        self.name=name
        self.params=Parameters()
        self.env=env
        if not env: self.env={}
        self.cwd=cwd
        self.timeout=timeout

    def addParameter(self,name,val=None,separator=' '):
        self.params.addParameter(name,val,separator)
        
    def addPrefixedParameter(self,prefix,name,val=None,separator=' '):
        self.params.addPrefixedParameter(prefix,name,val,separator)
        
    def addPrefixedParameters(self,prefix,params):
        for p in params.items():
          self.params.addPrefixedParameter(prefix,p.name,p.value,p.separator)
          
    def addPrefixedNamedParameters(self,prefix,params):
        for p in params.items():
          self.params.addPrefixedNamedParameter(prefix,p.name,p.value,p.separator)

    def addParameterObject(self,param):
        self.params.addParameterObject(param)
        
    def addParameters(self,params):
        for p in params.items():
          self.params.addParameter(p.name,p.value,p.separator,p.prefix)
        
    def addNamedParameters(self,params):
        for p in params.items():
          self.params.addNamedParameter(p.name,p.value,p.separator,p.prefix)
        
    def addEnvirionment(self,name,val=None):
        self.env[name]=val
        
    def formatCommandLine(self):
        line = str(self.cmdpath)
        line += " "
        line += self.params.formatCommandLine()
        return line
            
    def overview(self,indent=''):
        overview=indent+'Command Line: ' + self.formatCommandLine()+'\n'
        if self.cwd:
            overview += indent+'CWD: ' + self.cwd + '\n'
        return overview
        
    def dump(self,indent=''):
        print self.overview(indent)
        
def getCmdFromString(strcmd,name=None):
    """Extract a Cmd Object from a String"""
    parts=split(strcmd,' ')
    cmdcmd=parts[0]
    if not name: name=cmdcmd
    cmd=Cmd(cmdcmd,name)
    for i in range(1,len(parts)):
        if parts[i]:
            cmd.addParameterObject(getParameterFromString(parts[i]))
    return cmd
                
class CmdResult:
    """Result of execution -- state/outputs"""
    def __init__(self,cmd):
        self.cmd=cmd
        self.state=CMD_STATE_NOT_YET_RUN
        self.output=None
        self.signal=0
        self.exit_code=-1
        
        # To calculate elapsed
        self.start_time=None
        self.end_time=None
        
    def overview(self,indent):
        overview + indent+"State: " + states[self.state]
        overview += self.cmd.overview(indent)
        if self.output:
          overview += indent+"Output: " + self.output
        if self.hasTimes():
          overview += indent+"Elapsed: " + str(self.getElapsedTime())
        if self.signal:
          overview += indent+"Termination Signal: " + str(self.signal)
        if self.exit_code:
          overview += indent+"ExitCode: " + str(self.exit_code)
        
        return overview
        
    def tail(self,lines):                
        if self.output:
            from gump.utils.tools import tailFileToString            
            tail = tailFileToString(self.output,lines)
        else:
            tail = "No output\n"
            
        return tail
    
    def hasOutput(self):
        if self.output: return 1
        return 0
        
    def getOutput(self):
        return self.output
        
    def hasTimes(self):
        if self.start_time and self.end_time: return 1
        return 0
        
    def getStartTimeSecs(self):
        return self.start_time
        
    def getEndTimeSecs(self):
        return self.end_time
        
    def getElapsedSecs(self):
        return int(round(self.end_time-self.start_time,0))        
        
    def dump(self,indent):
        print self.overview(indent)

def killChildProcesses():
    gumpid=default.gumpid
    log.warn('Kill all child processed (anything launched by Gumpy) [PID' + str(gumpid) + ']')    
    pidsFile = dir.tmp + '/childPIDs.txt'
    command='pgrep -P ' + str(gumpid) + ' -l > ' + pidsFile
    os.system(command)
    
    ids=None
    try:     
        ids=open(pidsFile,'r')
    
        line=ids.readline()
        while line:            
            parts=line.split()
            childPID=int(parts[0])
            process=parts[1]
            if not process=='python':
                log.warn('Terminate PID [' + str(childPID) + '] Process: [' + process + ']')            
                os.kill(childPID,signal.SIGKILL)
            
            # Get next PID/process combination
            line=ids.readline()
    finally:
        if ids: ids.close()
    
    if os.path.exists(pidsFile):
        os.remove(pidsFile)    
    
    log.warn('Terminated All.')   
    sys.exit(0)                         
    
def execute(cmd,tmp=dir.tmp):
    res=CmdResult(cmd)
    return executeIntoResult(cmd,res,tmp)
	
def executeIntoResult(cmd,result,tmp=dir.tmp):
    """Execute a command and capture the result"""	
    
    # Store the current settings
    originalCWD=os.getcwd()
    # Note: We only override what is given, not everything
    originalENV={}
    for envKey in cmd.env.iterkeys():
      try:
        originalENV[envKey]=os.environ[envKey]
      except:
        originalENV[envKey]=''
      os.environ[envKey]=cmd.env[envKey]
    outputFile=None
    start_time=time.time()
    try:
      try:          
        # Make the TMP if needed
        try:
            if not os.path.exists(tmp): os.mkdir(tmp)
        except Exception, details :
            # Log the problem and re-raise
            log.error('Failed to create TMP [' + tmp + ']. Details: ' + str(details))
            raise
              
        # Make the CWD if needed
        if cmd.cwd: 
          try:
              log.debug('Executing with CWD: [' + cmd.cwd + ']')
    
              cwdpath=os.path.abspath(cmd.cwd)
              if not os.path.exists(cwdpath): os.mkdir(cwdpath)
              os.chdir(cwdpath)
          except Exception, details :
              # Log the problem and re-raise
              log.error('Failed to create CWD [' + cwdpath + ']. Details: ' + str(details))
              raise
        
        # The command line
        execString=cmd.formatCommandLine()        
        
        # Output
        outputFile=os.path.abspath(os.path.join(tmp,gumpSafeName(cmd.name)+'.txt'))
        if os.path.exists(outputFile): os.remove(outputFile)
    
        if switch.debugging:
            #############################################################
            # This debug might become permenant ...
            #############################################################
            try:            
                f=open(outputFile, 'w')
                # Dump the command line
                printSeparatorToFile(f)    
                f.write( 'Command Line: %s\n' % (execString))
                # Dump the cwd (if specified)
                if cmd.cwd:
                    printSeparatorToFile(f)            
                    f.write( 'Working Directory: %s\n' % (cmd.cwd))
                # Dump the environment
                printSeparatorToFile(f)
                f.write( 'Environment:\n')
                for envKey in os.environ.iterkeys():
                    f.write('%s = %s\n' % (envKey, os.environ[envKey]))
                # Gap before the real stuff...
                printSeparatorToFile(f)
                f.write('\n\n')
            finally:
                # Since we may exit via an exception, close explicitly.
                if f: f.close()    
            
        #############################################################                
        log.debug('Executing: ' + execString + ' (Output to ' + str(outputFile) + ')')
    
        # Set the signal handler and an N-second alarm
        timeout=cmd.timeout or setting.timeout
        timer = Timer(timeout, killChildProcesses)
        timer.setDaemon(1)
        timer.start()

        #
        # Execute Command & Wait
        #
        waitcode=os.system(execString + ' >>' + str(outputFile) + ' 2>&1')
        
        #
        # The return code (from system = from wait) is (on Unix):
        #
        #	a 16 bit number
        #	top byte	=	exit status
        #	low byte	=	signal that killed it
        #
        result.signal=(waitcode & 0xFF)
        result.exit_code=(((waitcode & 0xFF00) >> 8) & 0xFF)
        
        log.debug('Command . [' + str(waitcode)+ '] [Sig:' + str(result.signal) + ' / Exit:' + str(result.exit_code) + '].')
            
        #
        # Assume timed out if signal terminated
        #
        if result.signal > 0:
            result.state=CMD_STATE_TIMED_OUT
            log.error('Command timed out. [' + execString + '] [' + str(timeout) + '] seconds.')
        # Process Outputs (exit_code and stderr/stdout)
        elif result.exit_code > 0:    
            result.state=CMD_STATE_FAILED
            log.error('Command failed. [' + execString + ']. ExitCode: ' + str(result.exit_code))
        else:
            result.state=CMD_STATE_SUCCESS
    
        #
        # Stop it (if still running)
        #
        timer.cancel()            
                    
      except Exception, details :
        log.error('Failed to launch command. Details: ' + str(details))
        
        result.exit_code=-1
        result.state=CMD_STATE_FAILED
        
    finally:
      #
      # Clean Up Empty Output Files
      #
      if outputFile and os.path.exists(outputFile):
          if os.path.getsize(outputFile) > 0:
              result.output=outputFile
          else:
              os.remove(outputFile)
        
      # Keep time information
      end_time=time.time()
      result.start_time=start_time
      result.end_time=end_time
      
      # Restore environment.
      if cmd.cwd: os.chdir(originalCWD)
      for envKey in originalENV.iterkeys():
	    value=originalENV[envKey]
	    os.environ[envKey]=value
	  
    return result
    
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)
   

#  cmd=Cmd('test','testoutput')
#  cmd.addParameter("A","a")
#  cmd.addPrefixedParameter("-D","B","b")
#  cmd.addParameter("C")
#  cmd.addParameter("A","aa") # Override for earlier
  
#  params=Parameters()
#  params.addParameter("D")
#  cmd.addParameters(params)
  
#  result = execute(cmd)  
#  dump(result);
  
#  cmd=Cmd('ls','ls-test')
#  result = execute(cmd)  
#  dump(result);
  
  cmd=Cmd('sleep','sleep-test')
  cmd.addParameter("300")
  cmd.timeout=10
  result = execute(cmd)  
#  dump(result);
  
  sys.exit(0)
  
  
