#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/proposals/aj_python/gump/Attic/launcher.py,v 1.1 2003/08/21 19:38:14 nickchalko Exp $
# $Revision: 1.1 $
# $Date: 2003/08/21 19:38:14 $
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

from gump import log, gumpSafeName
from gump.conf import *
from gump.utils import *

CMD_STATUS_NOT_YET_RUN=0
CMD_STATUS_SUCCESS=1
CMD_STATUS_FAILED=2
CMD_STATUS_TIMED_OUT=3

states = { CMD_STATUS_NOT_YET_RUN : "Not Run",
           CMD_STATUS_SUCCESS : "Success",
           CMD_STATUS_FAILED : "Failed",
           CMD_STATUS_TIMED_OUT : "Timed Out" }

class Parameter:
    """Name/Value"""
    def __init__(self,name,value=None,separator=' ',prefix=None):
      self.name=name
      self.value=value
      self.separator=separator
      self.prefix=prefix
    
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
 
    def addParameter(self,name,value=None,separator=' ',prefix=None):
      param=Parameter(name,value,separator,prefix)
      self.list.append(param)
      self.dict[name]=param
      
    def removeParameter(self,name):
      for param in self.list:
        if param.name==name: 
          self.list.remove(param)
          del self.dict[name]
    
    def formatCommandLine(self):
      line = ''
      for param in self.list:
        if param.prefix: 
          line += param.prefix
        line += param.name
        val = param.value
        if val:
            line += param.separator
            line += val
        line += " "  
      return line
      
    def items(self):
      return self.list
      
    def dump(self,indent=''):
      for param in self.list:
        print indent+'  '+param.name+' '+str(param.value)+' ('+str(param.prefix)+')'
      
class Cmd:
    """Command Line (executable plus parameters)"""
    def __init__(self,command,name,cwd=None,env={}):
        self.cmdpath=command
        self.name=name
        self.params=Parameters()
        self.env=env
        self.cwd=cwd

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
        
class CmdResult:
    """Result of execution -- status/outputs"""
    def __init__(self,cmd):
        self.cmd=cmd
        self.status=CMD_STATUS_NOT_YET_RUN
        self.output=None
        self.elapsed=0
        
    def overview(self,indent):
        overview + indent+"Status: " + states[self.status]
        overview += self.cmd.overview(indent)
        if self.output:
          overview += indent+"Output: " + self.output
        if self.elapsed:
          overview += indent+"Elapsed: " + str(self.elapsed)
        if self.exit_code:
          overview += indent+"ExitCode: " + str(self.exit_code)
        return overview
          
    def dump(self,indent):
        print self.overview(indent)

def execute(cmd):
    res=CmdResult(cmd)
    return executeIntoResult(cmd,res)
	
def executeIntoResult(cmd,result):
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
    
    start_time=time.time()
    try:
      try:
        # Output
        outputFile=os.path.abspath(os.path.join(dir.tmp,gumpSafeName(cmd.name)+'.txt'))
        if os.path.exists(outputFile): os.remove(outputFile)
    
        #############################################################
        # Possibly temporary, pos perm, for testing...
        # Environment
        envFile=os.path.abspath(os.path.join(dir.tmp,gumpSafeName(cmd.name)+'.env.txt'))
        if os.path.exists(envFile): os.remove(envFile)
    
        try:            
            f=open( envFile, 'w')
            for envKey in os.environ.iterkeys():
                f.write('%s = %s\n' % (envKey, os.environ[envKey]))
        finally:
            # Since we may exit via an exception, close fp explicitly.
            if f: f.close()    
        #############################################################3
        
        if cmd.cwd: 
          cwdpath=os.path.abspath(cmd.cwd)
          if not os.path.exists(cwdpath): os.mkdir(cwdpath)
          os.chdir(cwdpath)
        
        execString=cmd.formatCommandLine()
        
        log.info('Executing: ' + execString + ' (Output to ' + str(outputFile) + ')')
    
        # Execute Command & Wait
        result.exit_code=os.system(execString + ' >' + str(outputFile) + ' 2>&1')
        #result.exit_code=0
    
        # Process Outputs (exit_code and stderr/stdout)
        if result.exit_code < 0:
          result.status=CMD_STATUS_TIMED_OUT
        elif result.exit_code > 0:    
          result.status=CMD_STATUS_FAILED
        else:
          result.status=CMD_STATUS_SUCCESS        
    
      except Exception, details :
        log.error('Failed to launch' + str(details))
        
        result.exit_code=-1
        result.status=CMD_STATUS_FAILED
        
    finally:
      if os.path.exists(outputFile):
          result.output=outputFile
        
        # Keep time information
      end_time=time.time()
      result.elapsed=round(end_time-start_time,2)
        
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
   
  cmd=Cmd('test','testoutput')
  cmd.addParameter("A","a")
  cmd.addPrefixedParameter("-D","B","b")
  cmd.addParameter("C")
  cmd.addParameter("A","aa") # Override for earlier
  
  params=Parameters()
  params.addParameter("D")
  cmd.addParameters(params)
  
  result = execute(cmd)  
  dump(result);
  
  cmd=Cmd('ls','ls-test')
  result = execute(cmd)  
  dump(result);
  
