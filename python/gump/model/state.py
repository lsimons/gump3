#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/state.py,v 1.11 2004/02/17 21:54:20 ajack Exp $
# $Revision: 1.11 $
# $Date: 2004/02/17 21:54:20 $
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

stateNames = { STATE_UNSET : "Unset",
           STATE_NONE : "NoWork",
           STATE_SUCCESS : "Success",
           STATE_FAILED : "Failed",
           STATE_PREREQ_FAILED : "PrereqFailed",
           STATE_COMPLETE : "Complete" }

stateDescriptions = { STATE_UNSET : "Unset",
           STATE_NONE : "No Work Performed",
           STATE_SUCCESS : "Success",
           STATE_FAILED : "Failed",
           STATE_PREREQ_FAILED : "Prerequisite Failed",
           STATE_COMPLETE : "Complete" }

def stateName(state):
    return stateNames.get(state,'Unknown:' + str(state)) 
       
def stateDescription(state):
    return stateDescriptions.get(state,'Unknown State:' + str(state))    

namedState = { "Unset" : STATE_UNSET,
           "NoWork" : STATE_NONE,
            "Success" : STATE_SUCCESS,
            "Failed" : STATE_FAILED,
            "PrereqFailed" : STATE_PREREQ_FAILED,
            "Complete"  : STATE_COMPLETE}
            
describedState = { "Unset" : STATE_UNSET,
           "No Work Performed" : STATE_NONE,
            "Success" : STATE_SUCCESS,
            "Failed" : STATE_FAILED,
            "Prerequisite Failed" : STATE_PREREQ_FAILED,
            "Complete"  : STATE_COMPLETE}
           
def stateForName(name):
    return namedState.get(name,STATE_UNSET)
    
def stateForDescription(name):
    return describedState.get(name,STATE_UNSET)

stateMap = {   CMD_STATE_NOT_YET_RUN : STATE_UNSET,
               CMD_STATE_SUCCESS : STATE_SUCCESS,
               CMD_STATE_FAILED : STATE_FAILED,
               CMD_STATE_TIMED_OUT : STATE_FAILED }
               
def commandStateToWorkState(state):
    return stateMap[state]
           

REASON_UNSET=0
REASON_PACKAGE=1
REASON_PACKAGE_BAD=2
REASON_CIRCULAR=3
REASON_CONFIG_FAILED=4
REASON_UPDATE_FAILED=5
REASON_SYNC_FAILED=6
REASON_PREBUILD_FAILED=7
REASON_BUILD_FAILED=8
REASON_POSTBUILD_FAILED=9
REASON_BUILD_TIMEDOUT=10
REASON_MISSING_OUTPUTS=11

reasonCodeNames = { 	REASON_UNSET : "NotSet",
                    REASON_PACKAGE : "CompletePackageInstall",
                    REASON_PACKAGE_BAD : "BadPackageInstallation",
                    REASON_CIRCULAR : "CircularDependency",
                    REASON_CONFIG_FAILED : "ConfigurationFailed",
                    REASON_UPDATE_FAILED : "UpdateFailed",
                    REASON_SYNC_FAILED : "SynchronizeFailed",
                    REASON_PREBUILD_FAILED : "Pre-BuildFailed",
                    REASON_BUILD_FAILED : "BuildFailed",
                    REASON_POSTBUILD_FAILED : "Post-BuildFailed",
                    REASON_BUILD_TIMEDOUT : "BuildTimedOut",
                    REASON_MISSING_OUTPUTS : "MissingBuildOutputs" }    
                    
reasonCodeDescriptions = { 	REASON_UNSET : "Not Set",
                    REASON_PACKAGE : "Complete Package Install",
                    REASON_PACKAGE_BAD : "Bad Package Installation",
                    REASON_CIRCULAR : "Circular Dependency",
                    REASON_CONFIG_FAILED : "Configuration Failed",
                    REASON_UPDATE_FAILED : "Update Failed",
                    REASON_SYNC_FAILED : "Synchronize Failed",
                    REASON_PREBUILD_FAILED : "Pre-Build Failed",
                    REASON_BUILD_FAILED : "Build Failed",
                    REASON_POSTBUILD_FAILED : "Post-Build Failed",
                    REASON_BUILD_TIMEDOUT : "Build Timed Out",
                    REASON_MISSING_OUTPUTS : "Missing Build Outputs" }    
    
def reasonName(reasonCode):
    return reasonCodeNames.get(reasonCode,'Unknown:' + str(reasonCode))
    
def reasonDescription(reasonCode):
    return reasonCodeDescriptions.get(reasonCode,'Unknown Reason:' + str(reasonCode))
          
class StatePair:
    """Contains a State Plus Reason"""
    def __init__(self,state=STATE_UNSET,reason=REASON_UNSET):
        self.state=state
        self.reason=reason
        
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        result=stateDescription(self.state)
        if not self.reason == REASON_UNSET:
            result += ":" + reasonDescription(self.reason)
        return result
        
    def __eq__(self,other):
        return self.state == other.state and self.reason == other.reason
                
    def __cmp__(self,other):
        c = cmp(self.state,other.state)
        if not c: c = cmp(self.reason,other.reason)
        return c
         
    def __hash__(self):
        return hash(self.state)+hash(self.reason)
             
    def getState(self):
        return self.state
        
    def getStateDescription(self):
        return stateDescription(self.getState())
        
    def getStateName(self):
        return stateName(self.getState())
        
    def getReason(self):
        return self.reason
        
    def getReasonName(self):
        return reasonName(self.getReason())
        
    def getReasonDescription(self):
        if self.isReasonUnset(): return ''
        return reasonDescription(self.getReason())
        
    #
    #
    #
    def isSuccess(self):
        return STATE_SUCCESS == self.state
                
    def isComplete(self):
        return STATE_COMPLETE == self.state
                
    def isFailed(self):
        return STATE_FAILED == self.state
        
    def isPrereqFailed(self):
        return STATE_PREREQ_FAILED == self.state
                
    def isUnset(self):
        return STATE_NONE==self.state \
                or STATE_UNSET==self.state
                
    def isReasonUnset(self):
        return REASON_UNSET==self.reason
        
    def isUnsetOrOk(self):
        return self.isUnset() or self.isOk()           

    def isOk(self):
        return self.isSuccess() or self.isComplete()   

    def isNotOk(self):
        return self.isFailed() or self.isPrereqFailed()
               
class Stateful:
    def __init__(self):        
        self.statePair=StatePair()
        
    def setStatePair(self,statePair):  
        self.statePair=statePair
            
    def getStatePair(self):  
        return self.statePair
        
    def getState(self):
        return self.statePair.state
        
    def getStateName(self):
        return self.statePair.getStateName()
        
    def getStateDescription(self):
        return self.statePair.getStateDescription()
        
    def hasReason(self):
        if self.statePair.isReasonUnset(): return 0
        return 1
        
    def getReason(self):
        return self.statePair.reason
        
    def getReasonDescription(self):
        return self.statePair.getReasonDescription()
        
    def getReasonName(self):
        return self.statePair.getReasonName()
        
    def isSuccess(self):
        return self.statePair.isSuccess()
        
    def isComplete(self):
        return self.statePair.isComplete()
                
    def isFailed(self):
        return self.statePair.isFailed()
        
    def isPrereqFailed(self):
        return self.statePair.isPrereqFailed()
                
    def isUnset(self):
        return self.statePair.isUnset()
        
    def isUnsetOrOk(self):
        return self.statePair.isUnsetOrOk()          

    def isOk(self):
        return self.statePair.isOk()    

    def isNotOk(self):
        return self.statePair.isNotOk() 
               