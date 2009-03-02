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

from types import NoneType
from threading import Timer
    
from string import split

from gump import log
from gump.core.config import *
from gump.util import *
from gump.util.timing import *

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
            if ' ' in self.name: return True
            if default.shellQuote in self.name: return True
            if default.shellEscape in self.name: return True
                        
        if self.value:
            if ' ' in self.value: return True
            if default.shellQuote in self.value: return True
            if default.shellEscape in self.value: return True
            
        return False
                
    
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
            line += default.shellQuote
        
        if param.prefix: 
          line += param.prefix
          
        # Deal w/ escaping quotes
        line += self.getEscapedEntry(param.name)
        val = param.value
        
        if not isinstance(val,NoneType):
            line += param.separator
            line += self.getEscapedEntry(val)        
            
        if requiresQuoting:
            line += default.shellQuote
        line += ' '
        
      return line
        
    def getEscapedEntry(self,entry):
        if not entry: return ""
        # Try without escape escape for now...
        #escapedEntry=entry.replace(default.shellEscape,default.shellEscape+default.shellEscape)        
        escapedEntry=entry.replace(default.shellQuote,default.shellEscape+default.shellQuote)
        return escapedEntry
        
    def items(self):
      return self.list
      
    def dump(self,indent=''):
      for param in self.list:
        print indent + '  ' + param.name + ' ' + str(param.value) + ' (' + str(param.prefix) + ')'
      
class Cmd:
    """Command Line (executable plus parameters)"""
    def __init__(self,command,name=None,cwd=None,env=None,timeout=setting.TIMEOUT):
        self.cmdpath = command
        self.name = name
        if not self.name:
            self.name = command
        self.params = Parameters()
        self.env = env
        if not env: self.env = {}
        self.cwd = cwd
        self.timeout = timeout

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
        overview = indent + 'Command Line: ' + self.formatCommandLine() + '\n'
        if self.cwd:
            overview += indent + '[Working Directory: ' + self.cwd + ']\n'
        if self.env:
            for envKey in self.env.keys():
                overview += indent + envKey + ': ' + self.env[envKey] + '\n'
        return overview
        
    def dump(self,indent=''):
        print self.overview(indent)
        
def getCmdFromString(strcmd, name = None, cwd = None):
    """Extract a Cmd Object from a String"""
    parts = split(strcmd,' ')
    cmdcmd = parts[0]
    if not name: name = cmdcmd
    cmd = Cmd(cmdcmd, name, cwd)
    for i in range(1,len(parts)):
        if parts[i]:
            cmd.addParameterObject(getParameterFromString(parts[i]))
    return cmd
                
class CmdResult:
    """Result of execution -- state/outputs"""
    def __init__(self,cmd):
        self.cmd = cmd
        self.state = CMD_STATE_NOT_YET_RUN
        self.output = None
        self.signal = 0
        self.exit_code = -1
        
        # To calculate elapsed
        self.start = None
        self.end = None
        
    def overview(self,indent=''):
        overview = indent + "State: " + states[self.state] + "\n"
        overview += self.cmd.overview(indent)
        if self.output:
          overview += indent + "Output: " + self.output + "\n"
        if self.hasTimes():
          overview += indent + "Elapsed: " + secsToElapsedTimeString(self.getElapsedSecs()) + "\n"
        if self.signal:
          overview += indent + "Termination Signal: " + str(self.signal) + "\n"
        if self.exit_code:
          overview += indent + "ExitCode: " + str(self.exit_code) + "\n"
        
        return overview
        
    def tail(self,lines,wrapLen=0,eol=None,marker=None):                
        if self.output:
            from gump.util.tools import tailFileToString            
            tail = tailFileToString(self.output,lines,wrapLen,eol,marker)
        else:
            tail = "No output\n"
            
        return tail
        
    def isOk(self):
        return (self.state == CMD_STATE_SUCCESS)
    
    def hasOutput(self):
        if self.output: return 1
        return 0
        
    def getOutput(self):
        return self.output
        
    def hasTimes(self):
        if self.start and self.end: return 1
        return 0
        
    def getStart(self):
        return self.start
        
    def getEnd(self):
        return self.end
        
    def getElapsedSecs(self):
        return deltaToSecs(self.end-self.start)        
        
    def dump(self,indent):
        print self.overview(indent)

  
