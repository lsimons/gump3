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

	State information    

"""

STATE_UNSET=0
STATE_NONE=1
STATE_SUCCESS=2
STATE_FAILED=3
STATE_STALE_SUCCESS=4
STATE_STALE_FAILED=5
STATE_FUZZY_SUCCESS=5
STATE_FUZZY_FAILED=4
STATE_PREREQ_FAILED=5
STATE_COMPLETE=6

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
                    
namedReasonCode = { "NotSet" : REASON_UNSET,
                    "CompletePackageInstall" : REASON_PACKAGE,
                    "BadPackageInstallation" : REASON_PACKAGE_BAD,
                    "CircularDependency" : REASON_CIRCULAR,
                    "ConfigurationFailed" : REASON_CONFIG_FAILED,
                    "UpdateFailed" : REASON_UPDATE_FAILED,
                    "SynchronizeFailed" : REASON_SYNC_FAILED,
                    "Pre-BuildFailed" : REASON_PREBUILD_FAILED,
                    "BuildFailed" : REASON_BUILD_FAILED,
                    "Post-BuildFailed" : REASON_POSTBUILD_FAILED,
                    "BuildTimedOut" : REASON_BUILD_TIMEDOUT,
                    "MissingBuildOutputs" : REASON_MISSING_OUTPUTS }    
                    
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
    
def reasonForName(name):
    return namedReasonCode.get(name,STATE_UNSET)    
    
def getStatePairFromNames(stateName,reasonName):
    state=stateForName(stateName)
    reason=reasonForName(reasonName)    
    return StatePair(state,reason)
          
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
        # These are 'enum'-like, so self hash,
        # but separate the two
        return (self.state << 8)+self.reason
             
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
        
    # Simple Tests
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
        return self.isFailed() 

    def okToPerformWork(self):
        return self.isUnsetOrOk()
        
class Stateful:
    def __init__(self):  
        """
        	
        	An entity that holds state
        	      
        """
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
        return not self.statePair.isReasonUnset()
        
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
        
    def okToPerformWork(self):
        return self.statePair.okToPerformWork() 
        
               
