#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/state.py,v 1.4 2003/11/19 15:42:16 ajack Exp $
# $Revision: 1.4 $
# $Date: 2003/11/19 15:42:16 $
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
    This module contains information on
"""

from time import localtime, strftime, tzname

from gump.utils.launcher import *

STATE_UNSET=0
STATE_NONE=1
STATE_SUCCESS=2
STATE_FAILED=3
STATE_PREREQ_FAILED=4
STATE_COMPLETE=5

stateDescriptions = { STATE_UNSET : "Unset",
           STATE_NONE : "No Work Performed",
           STATE_SUCCESS : "Success",
           STATE_FAILED : "Failed",
           STATE_PREREQ_FAILED : "Prerequisite Failed",
           STATE_COMPLETE : "Complete" }

def stateName(state):
    return stateDescriptions.get(state,'Unknown State:' + str(state))
    

describedState = { "Unset" : STATE_UNSET,
           "No Work Performed" : STATE_NONE,
            "Success" : STATE_SUCCESS,
            "Failed" : STATE_FAILED,
            "Prerequisite Failed" : STATE_PREREQ_FAILED,
            "Complete"  : STATE_COMPLETE}
           
def stateForName(name):
    return describedState.get(name,STATE_UNSET)

stateMap = {   CMD_STATE_NOT_YET_RUN : STATE_UNSET,
               CMD_STATE_SUCCESS : STATE_SUCCESS,
               CMD_STATE_FAILED : STATE_FAILED,
               CMD_STATE_TIMED_OUT : STATE_FAILED }
               
def commandStateToWorkState(state):
    return stateMap[state]
           
def stateUnset(state):
    return state==STATE_NONE or state==STATE_UNSET 
        
def stateOk(state):
    return state==STATE_SUCCESS
        
def stateUnsetOrOk(state):
    return stateUnset(state) or stateOk(state)           
    
REASON_UNSET=0
REASON_PACKAGE=1
REASON_PACKAGE_BAD=2
REASON_CIRCULAR=3
REASON_CONFIG_FAILED=4
REASON_UPDATE_FAILED=5
REASON_SYNC_FAILED=6
REASON_PREBUILD_FAILED=7
REASON_BUILD_FAILED=8
REASON_BUILD_TIMEDOUT=9
REASON_MISSING_OUTPUTS=10

reasonCodeDescriptions = { 	REASON_UNSET : "Not Set",
                    REASON_PACKAGE : "Complete Package Install",
                    REASON_PACKAGE_BAD : "Bad Package Installation",
                    REASON_CIRCULAR : "Circular Dependency",
                    REASON_CONFIG_FAILED : "Configuration Failed",
                    REASON_UPDATE_FAILED : "Update Failed",
                    REASON_SYNC_FAILED : "Synchronize Failed",
                    REASON_BUILD_FAILED : "Pre-Build Failed",
                    REASON_BUILD_TIMEDOUT : "Build Timed Out",
                    REASON_BUILD_FAILED : "Build Failed",
                    REASON_MISSING_OUTPUTS : "Missing Build Outputs" }    
    
def reasonString(reasonCode):
    return reasonCodeDescriptions.get(reasonCode,'Unknown Reason:' + str(reasonCode))
          
class StatePair:
    """Contains a State Plus Reason"""
    def __init__(self,state=STATE_UNSET,reason=REASON_UNSET):
        self.state=state
        self.reason=reason
        
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        result=stateName(self.state)
        if not self.reason == REASON_UNSET:
            result += ":" + reasonString(self.reason)
        return result
        
    def __eq__(self,other):
        return self.state == other.state and self.reason == other.reason
                
    def __cmp__(self,other):
        c = cmp(self.state,other.state)
        if not c: c = cmp(self.reason,other.reason)
        return c
         
    def __hash__(self):
        return hash(self.state)+has(self.reason)
             
    def getState(self):
        return self.state
        
    def getStateDescription(self):
        return stateName(self.getState())
        
    def getReason(self):
        return self.reason
        
    def getReasonDescription(self):
        return reasonString(self.getState())
           
class Stateful:
    def __init__(self):        
        self.statePair=StatePair()
        
    def setStatePair(self,statePair):  
        self.statePair=statePair
            
    def getStatePair(self):  
        return self.statePair
        
    def getState(self):
        return self.statePair.state
        
    def getStateDescription(self):
        return self.statePair.getStateDescription()
        
    def getReason(self):
        return self.statePair.reason
        
    def getReasonDescription(self):
        return self.statePair.getReasonDescription()
        
    def stateUnsetOrOk(self):
        return stateUnsetOrOk(self.statePair.state)
        
    def isSuccess(self):
        return STATE_SUCCESS == self.statePair.state
                
    def isFailed(self):
        return STATE_FAILED == self.statePair.state
        
    def isPrereqFailure(self):
        return STATE_PREREQ_FAILED == self.statePair.state
        
