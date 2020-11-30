#!/usr/bin/python

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

#
# $Header: /home/stefano/cvs/gump/python/gump.tool.shared/comparator.py,v 1.5 2004/07/08 20:33:11 ajack Exp $
# 
       
def compareObjects(o1,o2):     
    """
    Compare two objects, but be ware of Nones...   
    """
     
    if o1:
        if o2:
            if o1 > o2:
                return 1
            elif o1 == o2:
                return 0
            else:
                return -1
        else:
            return 1 # 02 none
    else:
        if o2:  return -1 # o1 none
    
    return 0 # Both none
    
#
# Module Comparisons
#            
def comparison(a,b):
    return int(a > b) - int(a < b)
        
def compareModulesByElapsed(module1,module2):
    elapsed1=module1.getElapsedSecs()
    elapsed2=module2.getElapsedSecs()
    c = 0
    if elapsed1 > elapsed2: c = -1
    if elapsed1 < elapsed2: c = 1       
    if not c: c=comparison(module1,module2)
    return c

def compareModulesByProjectCount(module1,module2):
    count1=len(module1.getProjects())
    count2=len(module2.getProjects())
    c = count2 - count1                  
    if not c: c=comparison(module1,module2)
    return c

def compareModulesByDependencyCount(module1,module2):
    count1=module1.getFullDependencyCount()
    count2=module2.getFullDependencyCount()
    c= count2 - count1                 
    if not c: c=comparison(module1,module2)
    return c        
        
def compareModulesByDependeeCount(module1,module2):
    count1=module1.getFullDependeeCount()
    count2=module2.getFullDependeeCount()
    c= count2 - count1                  
    if not c: c=comparison(module1,module2)
    return c       
    
def compareModulesByFOGFactor(module1,module2):
    fog1=module1.getFOGFactor()
    fog2=module2.getFOGFactor()
    # Allow comparison to 2 decimal places, by *100
    c= int(round((fog2 - fog1)*100,0))                  
    if not c: c=comparison(module1,module2)
    return c             
            
def compareModulesByLastModified(module1,module2):
    lm1=module1.getLastModified()
    lm2=module2.getLastModified()
    return compareObjects(lm1,lm2)
            
#
# Project Comparisons
#            
    
def compareProjectsByElapsed(project1,project2):
    elapsed1=project1.getElapsedSecs()
    elapsed2=project2.getElapsedSecs()
    c = 0
    if elapsed1 > elapsed2: c = -1
    if elapsed1 < elapsed2: c = 1       
    if not c: c=comparison(project1,project2)
    return c

def compareProjectsByDependencyCount(project1,project2):
    count1=project1.getDependencyCount()
    count2=project2.getDependencyCount()
    c= count2 - count1                 
    if not c: c=comparison(project1,project2)
    return c        
        
def compareProjectsByDependeeCount(project1,project2):
    count1=project1.getDependeeCount()
    count2=project2.getDependeeCount()
    c= count2 - count1                  
    if not c: c=comparison(project1,project2)
    return c       
    
def compareProjectsByFullDependeeCount(project1,project2):
    count1=project1.getFullDependeeCount()
    count2=project2.getFullDependeeCount()
    c= count2 - count1                  
    if not c: c=comparison(project1,project2)
    return c       
    
def compareProjectsByFullDependencyCount(project1,project2):
    count1=project1.getFullDependencyCount()
    count2=project2.getFullDependencyCount()
    c= count2 - count1                 
    if not c: c=comparison(project1,project2)
    return c        
        
def compareProjectsByFOGFactor(project1,project2):
    fog1=project1.getFOGFactor()
    fog2=project2.getFOGFactor()
    # Allow comparison to 2 decimal places, by *100
    c= int(round((fog2 - fog1)*100,0))                  
    if not c: c=comparison(project1,project2)
    return c             
            
def compareProjectsByLastModified(project1,project2):
    lm1=project1.getLastModified()
    lm2=project2.getLastModified()
    return compareObjects(lm1,lm2)
            
def compareProjectsBySequenceInState(project1,project2):
    seq1=project1.getStats().sequenceInState
    seq2=project2.getStats().sequenceInState
    c= int(round(seq2 - seq1,0))                  
    if not c: c=comparison(project1,project2)
    return c                         
                        
def compareProjectsByDependencyDepth(project1,project2):
    dep1=project1.getDependencyDepth()
    dep2=project2.getDependencyDepth()
    c= int(round(dep2 - dep1,0))                  
    if not c: c=comparison(project1,project2)
    return c                         
                            
def compareProjectsByTotalDependencyDepth(project1,project2):
    tot1=project1.getTotalDependencyDepth()
    tot2=project2.getTotalDependencyDepth()
    c= int(round(tot2 - tot1,0))                  
    if not c: c=comparison(project1,project2)
    return c                         
                            
def compareProjectsByAffected(project1,project2):
    aff1=project1.countAffectedProjects()
    aff2=project2.countAffectedProjects()
    c= int(round(aff2 - aff1,0))                  
    if not c: c=comparison(project1,project2)
    return c                         
            
