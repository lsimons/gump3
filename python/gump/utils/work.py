#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/utils/work.py,v 1.2 2003/12/02 17:36:40 ajack Exp $
# $Revision: 1.2 $
# $Date: 2003/12/02 17:36:40 $
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
from string import lower, capitalize

from gump.model.state import *
from gump.utils.owner import *
from gump.utils.launcher import *

               
WORK_TYPE_CHECK=1
WORK_TYPE_CONFIG=2
WORK_TYPE_UPDATE=3
WORK_TYPE_SYNC=4
WORK_TYPE_PREBUILD=5
WORK_TYPE_BUILD=6
WORK_TYPE_POSTBUILD=7
WORK_TYPE_DOCUMENT=8

workTypeDescriptions = { 	WORK_TYPE_CHECK : "CheckEnvironment",
                WORK_TYPE_CONFIG : "Config",
                WORK_TYPE_UPDATE : "Update",
                WORK_TYPE_SYNC : "Synchronize",
                WORK_TYPE_PREBUILD : "PreBuild",
                WORK_TYPE_BUILD : "Build",
                WORK_TYPE_POSTBUILD : "PostBuild",
                WORK_TYPE_DOCUMENT : "Document" }    
    
def workTypeName(type):
    return workTypeDescriptions.get(type,'Unknown Work Type:' + str(type))
                   
class WorkItem(Ownable):
    """ Unit of Work"""
    def __init__(self,name,type,state,message=''):
        Ownable.__init__(self)
        
        self.name=name
        self.type=type
        self.state=state
        self.message=message
            
    def overview(self):
        overview='Work Name: ' + self.name +'\n'
        overview='Work Type: ' + workTypeName(self.type)+'\n'
        overview+='State: ' + stateName(self.state)+'\n'
        if self.message:
            overview+=message+'\n'
        return overview
        
    def getType(self):
        return self.type

    def getTypeName(self):
        return workTypeName(self.type)
        
    def getName(self):
        return self.name
        
    def setName(self,name):
        self.name=name
        
    def clone(self):
        return WorkItem(self.name,self.type,self.state,self.message)
        

class TimedWorkItem(WorkItem):
    """ Unit of Work w/ times """
    def __init__(self,name,type,state,secs,message=''):
        WorkItem.__init__(self,name,type,state,message)
        self.secs=secs
                 
    def elapsedTime(self):   
        return secsToElapsedTime(self.secs or 0)
         
    def overview(self):
        overview=WorkItem.overview(self)
        (hours,mins,secs)=self.elapsedTime()
        overview+='Elapsed: '
        overview+=str(hours) + ' hours, ' 
        overview+=str(mins) + ' minutes, ' 
        overview+=str(secs) + " seconds\n"
        return overview
        
    def clone(self):
        return TimedWorkItem(self.name,self.type,self.state,self.secs,self.message)
        
class CommandWorkItem(TimedWorkItem):
    """ Unit of Work"""
    def __init__(self,type,command,result=None,message=''):
        if not result: result=CmdResult(command)
        TimedWorkItem.__init__(self,command.name,type,\
                commandStateToWorkState(result.state),result.elapsed,message)
        self.command=command
        self.result=result
        
    def overview(self,lines=50):
        overview=TimedWorkItem.overview(self)
        overview += self.command.overview()        
        if self.result:
            overview += "---------------------------------------------\n"                
            overview+=self.result.tail(lines)            
            overview += "---------------------------------------------\n"
        return overview
        
    def tail(self,lines=50):
        return self.result.tail(lines)
        
    def clone(self):
        return CommandWorkItem(self,type,self.command,self.result,self.message)
            
class WorkList(list,Ownable):
    
    """List of work (in order)"""
    def __init__(self,owner=None):
        Ownable.__init__(self,owner)            
        
        # Organize by name
        self.nameIndex={}
        
    def add(self,item):
        
        if item.hasOwner():
            raise RuntimeError, 'WorkItem already owned, can\'t add to list'
        
        # Keep unique within the scope of this list
        name=item.getName()
        uniquifier=1
        while self.nameIndex.has_key(name):
            name=item.getName()+str(uniquifier)
            uniquifier+=1
        item.setName(name)
        
        # Store by name
        self.nameIndex[name]=item
        
        # Store in the list
        self.append(item)
        
        # Let this item know it's owner
        item.setOwner(self.getOwner())
    
    def elapsedSecs(self):
        elapsedSecs=0
        for item in self:
            if isinstance(item,TimedWorkItem): elapsedSecs += item.secs
        return elapsedSecs
    
    def elapsedTime(self):   
        secs 	= self.elapsedSecs();
        if secs > 3600:
            hours	=	int(secs / 3600)
            secs	%=	3600
        else:
            hours	=	0
            
        if secs > 60:
            mins	=	int(secs / 60)
            secs	%=	60
        else:
            mins 	= 	0
                    
        secs 	=	int(round(secs,0))        
    
        return (hours, mins, secs)
        
class Workable(Stateful):       
    def __init__(self):
        Stateful.__init__(self)
        self.worklist=WorkList(self)
        
    def getWorkList(self):
        return self.worklist
        
    def performedWork(self,item):
    	self.worklist.add(item)   
        	
    def okToPerformWork(self):
        return self.isUnset() or self.isSuccess()        
               
    #
    # Return a triple of hours/minutes/seconds for total
    # elapsed time for this context and sub-contexts.
    #
    def elapsedTime(self):   
        secs 	= self.elapsedSecs();
        if secs > 3600:
            hours	=	int(secs / 3600)
            secs	%=	3600
        else:
            hours	=	0
            
        if secs > 60:
            mins	=	int(secs / 60)
            secs	%=	60
        else:
            mins 	= 	0
            
        secs 	=	int(round(secs,0))
        
        return (hours, mins, secs)