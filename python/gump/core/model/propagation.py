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
    This module contains information on
"""

from time import localtime, strftime, tzname
from string import lower, capitalize

from gump.core.model.state import *
from gump.util.work import *

class Propogatable(Stateful):
    
    def __init__(self):     
        Stateful.__init__(self)
        
        # Problems        
        self.cause=None	# Primary Cause
        self.causes=[]
            
    def resetState(self):
        """ Used by Unit Tests only """
        Stateful.setStatePair(self, StatePair())        

    def changeState(self,state,reason=REASON_UNSET,cause=None,message=None):  
          
        #
        # Do NOT over-write a pre-determined condition
        #            
        if self.isUnsetOrOk():

            # Store it...        
            newState=StatePair(state,reason)
            Stateful.setStatePair(self,newState)        
                
            # If we are having something bad going on...
            if not newState.isOk(): 
                #
                # If no-one else to point the finger at ...
                # ... step up.
                #
                if not cause: cause = self
                
                # List of things that caused issues...
                self.addCause(cause)
                                   
                # Describe the problem
                if not message:
                    message = lower(stateDescription(state))
                    if not REASON_UNSET == reason:
                        message += " with reason " + lower(reasonDescription(reason))   
                if isinstance(self,Workable):
                    self.addInfo(capitalize(message))
        
                # Send on the changes...
                self.propagateErrorStateChange(state,reason,cause,message)
    
    def propagateErrorStateChange(self,state,reason,cause,message):
               
        # .. then push this error down
        if hasattr(self,'getChildren'):
            for object in self.getChildren():
                object.changeState(state,reason,cause,message)        
                            
    def hasCause(self):
        return self.cause
        
    def getCause(self):
        return self.cause
        
    def addCause(self,cause):
        if not self.cause: 
            self.cause=cause
            from gump.core.model.project import Project
            if isinstance(cause,Project):
                cause.addAffected(self)
        self.causes.append(cause)
        
    def getCauses(self):
        return self.causes
