#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/proposals/aj_python/gump/Attic/context.py,v 1.1 2003/08/21 19:38:14 nickchalko Exp $
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
    This module contains information on
"""
from gump import log
from gump.model import *
from gump.conf import *
from gump.launcher import *
from gump.utils import *

STATUS_UNSET=0
STATUS_SUCCESS=1
STATUS_FAILED=2
STATUS_PREREQ_FAILURE=3
STATUS_COMPLETE=4

stateDescriptions = { STATUS_UNSET : "Unset",
           STATUS_SUCCESS : "Success",
           STATUS_FAILED : "Failed",
           STATUS_PREREQ_FAILURE : "Prerequisite Failed",
           STATUS_COMPLETE : "Complete. Perform No Action" }

def stateName(state):
    return stateDescriptions[state]

stateMap = {   CMD_STATUS_NOT_YET_RUN : STATUS_UNSET,
               CMD_STATUS_SUCCESS : STATUS_SUCCESS,
               CMD_STATUS_FAILED : STATUS_FAILED,
               CMD_STATUS_TIMED_OUT : STATUS_FAILED }
               
def commandStatusToWorkStatus(state):
    return stateMap[state]
           
WORK_TYPE_CONFIG=1
WORK_TYPE_UPDATE=2
WORK_TYPE_SYNC=3
WORK_TYPE_BUILD=4
WORK_TYPE_DOCUMENT=5

workTypeDescriptions = { 	WORK_TYPE_CONFIG : "Config",
                WORK_TYPE_UPDATE : "Update",
                WORK_TYPE_SYNC : "Synchronize",
                WORK_TYPE_BUILD : "Build",
                WORK_TYPE_DOCUMENT : "Document" }    
    
def workTypeName(type):
    return workTypeDescriptions[type]
                   
class WorkItem:
    """ Unit of Work"""
    def __init__(self,type,status,message=''):
        self.type=type
        self.status=status
        self.message=message
            
    def overview(self):
        overview='Work Type: ' + workTypeName(self.type)+'\n'
        overview+='Status: ' + stateName(self.status)+'\n'
        if self.message:
            overview+=message+'\n'
        return overview

class TimedWorkItem(WorkItem):
    """ Unit of Work w/ times """
    def __init__(self,type,status,secs,message=''):
        WorkItem.__init__(self,type,status,message)
        self.secs=secs
                 
    def elapsedTime(self):   
        secs 	= self.secs or 0;
        if secs > 3600:
            hours	=	int(secs % 3600)
            secs	-=	(hours * 3600)
        else:
            hours	=	0
            
        if secs > 60:
            mins	=	secs % 60
            secs	-=	(mins * 60)
        else:
            mins 	= 	0
            
        return (hours, mins, secs)
         
    def overview(self):
        overview=WorkItem.overview(self)
        (hours,mins,secs)=self.elapsedTime()
        overview+='Elapsed: '
        overview+=str(hours) + ' hours, ' 
        overview+=str(mins) + ' minutes, ' 
        overview+=str(secs) + " seconds\n"
        return overview
        
class CommandWorkItem(TimedWorkItem):
    """ Unit of Work"""
    def __init__(self,type,command,result,message=''):
        TimedWorkItem.__init__(self,type,commandStatusToWorkStatus(result.status),result.elapsed,message)
        self.command=command
        self.result=result
        
    def overview(self):
        overview=TimedWorkItem.overview(self)
        overview += self.command.overview()
        return overview
            
class WorkList(list):
    """List of work (in order)"""
    def __init__(self):
        self.index={}
        
    def add(self,item):
        self.index[item.type]=item
        self.append(item)
    
    def elapsedSecs(self):
        elapsedSecs=0
        for item in self:
            if isinstance(item,TimedWorkItem): elapsedSecs += item.secs
        return elapsedSecs
    
    def elapsedTime(self):   
        secs 	= self.elapsedSecs();
        if secs > 3600:
            hours	=	int(secs % 3600)
            secs	-=	(hours * 3600)
        else:
            hours	=	0
            
        if secs > 60:
            mins	=	secs % 60
            secs	-=	(mins * 60)
        else:
            mins 	= 	0
            
        return (hours, mins, secs)
        
    
REASON_UNSET=0
REASON_PACKAGE=1
REASON_CIRCULAR=2
REASON_CONFIG_FAILED=3
REASON_UPDATE_FAILED=4
REASON_SYNC_FAILED=5
REASON_BUILD_FAILED=6

reasonCodeDescriptions = { 	REASON_UNSET : "Not Set",
                    REASON_PACKAGE : "Package Install",
                    REASON_CIRCULAR : "Circular Dependency",
                    REASON_CONFIG_FAILED : "Configuration Failed",
                    REASON_UPDATE_FAILED : "Update Failed",
                    REASON_SYNC_FAILED : "Synchronize Failed",
                    REASON_BUILD_FAILED : "Build Failed" }    
    
def reasonString(reasonCode):
    return reasonCodeDescriptions[reasonCode]
        
class Context:
    """Context for a single entity"""
    def __init__(self,name):
        self.status=STATUS_UNSET
        self.reason=REASON_UNSET
    	self.name=name
        self.worklist=WorkList()
        self.subcontexts=dict()
        self.messages=[]
        
    def __eq__(self,other):
        return self.name == other.name
        
    def __cmp__(self,other):
        return self.name < other.name
        
    def __repr__(self):
        return str(self.__class__)+':'+self.name
        
    def __str__(self):
        return str(self.__class__)+':'+self.name
        
    def performedWork(self,item):
    	self.worklist.add(item)   
    	
    def tree(self,indent='',done=None):       
        if not done: done=[]
        for (cname,ctxt) in self.subcontexts.iteritems():
            if not ctxt in done:
                done.append(ctxt)
                ctxt.tree(indent+' ',done)
            else:
                print indent + ' ' + 'Tree Done...'
            
    def propagateState(self,state,reason=REASON_UNSET):        
        if self.stateUnset():
            self.status=state
            self.reason=reason
            for (cname,ctxt) in self.subcontexts.iteritems():
                ctxt.propagateState(state,reason)
        
    def elapsedSecs(self):
        elapsedSecs=self.worklist.elapsedSecs()
        if self.subcontexts:
            for (cname,ctxt) in self.subcontexts.iteritems():
                elapsedSecs += ctxt.elapsedSecs()
        return round(elapsedSecs,2)
        
    def addMessage(self,message):
        self.messages.append(message)
        
    #
    # Return a triple of hours/minutes/seconds for total
    # elapsed time for this context and sub-contexts.
    #
    def elapsedTime(self):   
        secs 	= self.elapsedSecs();
        if secs > 3600:
            hours	=	int(secs % 3600)
            secs	-=	(hours * 3600)
        else:
            hours	=	0
            
        if secs > 60:
            mins	=	secs % 60
            secs	-=	(mins * 60)
        else:
            mins 	= 	0
            
        return (hours, mins, secs)
        
    def okToPerformWork(self):
        return self.stateUnset()
        
    def stateUnset(self):
        return self.status==STATUS_UNSET or self.status==STATUS_SUCCESS
            	
class ProjectContext(Context):
    """Context for a single project"""
    def __init__(self,name):
    	Context.__init__(self,name)
    	self.project=Project.list[name]
    	self.modulecontext=None
    	
    	#
    	# Dependency Trees
    	#
    	self.depends=[]
    	self.options=[]
    	self.dependees=[]
    	self.optionees=[]
    	
    	self.totalDepends=[]
    	self.totalDependees=[]
        
    def tree(self,indent='',done=None):       
        if not done: done=[]  
        if self in done: return
        print indent + ' ' + str(len(indent)) + ') ' + self.name   
        Context.tree(self,indent)
        for dependeeContext in self.dependees:
            if not dependeeContext in done:
                done.append(dependeeContext)    
                dependeeContext.tree(indent+' ',done)     
        for optioneeContext in self.optionees:
            if not optioneeContext in done:
                done.append(optioneeContext)        
                optioneeContext.tree(indent+' ',done)               
        
    def getDepends(self):   
        if self.totalDepends: return self.totalDepends
        
        for ctxt in self.depends+self.options:
            if not ctxt == self:
                if not ctxt in self.totalDepends: 
                    self.totalDepends.append(ctxt)
                    for subctxt in ctxt.getDepends():
                        if not subctxt in self.totalDepends:
                            self.totalDepends.append(subctxt)
        self.totalDepends.sort()
        return self.totalDepends
            
    def directDependencyCount(self):   
        return len(self.depends+self.options)
        
    def dependencyCount(self):         
        return len(self.getDepends())                      
    
    def getDependees(self):   
        if self.totalDependees: return self.totalDependees
        
        for ctxt in self.dependees+self.optionees:
            if not ctxt == self:
                if not ctxt in self.totalDependees: 
                    self.totalDependees.append(ctxt)
                    for subctxt in ctxt.getDependees():
                        if not subctxt in self.totalDependees:
                            self.totalDependees.append(subctxt)
        self.totalDependees.sort()
        return self.totalDependees
            
    def directDependeeCount(self):   
        return len(self.dependees+self.optionees)
        
    def dependeeCount(self):         
        return len(self.getDependees())   
             
    def propagateState(self,state,reason=REASON_UNSET):
        if self.stateUnset():
            Context.propagateState(self,state,reason)
               
            for dependeeContext in self.dependees:
                dependeeContext.propagateState(STATUS_PREREQ_FAILURE,reason)
            
class ModuleContext(Context):
    """Set of Modules (which contain projects)"""
    def __init__(self,name):
    	Context.__init__(self,name)
        	
    	self.totalDepends=[]
    	self.totalDependees=[]
        
    #
    # Get a project context, by name
    #
    def getProjectContextForProject(self,project):
        pctxt=self.getProjectContext(project.name)
        if not pctxt.modulecontext: pctxt.modulecontext=self
        return pctxt
        
    def getProjectContext(self,projectname):
        if not self.subcontexts.has_key(projectname): self.subcontexts[projectname] = ProjectContext(projectname)
        return self.subcontexts[projectname]
        
    def getDependees(self):   
        if self.totalDependees: return self.totalDependees
                
        for pctxt in self.subcontexts.values():
            if not pctxt in self.totalDependees:
                self.totalDependees.append(pctxt)
                for ppctxt in pctxt.getDependees():
                    if not ppctxt in self.totalDependees:
                        self.totalDependees.append(ppctxt)                        
        self.totalDependees.sort()
        return self.totalDependees
            
    def dependeeCount(self):         
        return len(self.getDependees())   
            
    def getDepends(self):   
        if self.totalDepends: return self.totalDepends
                
        for pctxt in self.subcontexts.values():
            if not pctxt in self.totalDepends:
                self.totalDepends.append(pctxt)
                for ppctxt in pctxt.getDepends():
                    if not ppctxt in self.totalDepends:
                        self.totalDepends.append(ppctxt)                        
        self.totalDepends.sort()
        return self.totalDepends
            
    def dependencyCount(self):         
        return len(self.getDepends())   
        
class GumpContext(Context):
    """Gump Run Context"""
    def __init__(self,name="Gump"):
    	Context.__init__(self,name)
    	self.projectexpression=''
        
    def performedWorkOnProject(self,project,item):
        (mctxt,pctxt)=self.getContextsForProject(project)
        pctxt.performedWork(item)
        
    def performedWorkOnModule(self,module,item):
        mctxt=self.getModuleContextForModule(module)
        mctxt.performedWork(item)
        
    def getModuleContextForModule(self,module):
        return self.getModuleContext(module.name)
        
    def getModuleContext(self,modulename):
        if not self.subcontexts.has_key(modulename): self.subcontexts[modulename] = ModuleContext(modulename)
        ctxt = self.subcontexts[modulename]
        return ctxt
        
    def getProjectContextForProject(self,project):
        (mctxt,pctxt)=self.getContextsForProject(project)
        return pctxt
        
    def getContextsForProject(self,project):
        return self.getContexts(project.module, project.name)
        
    def getProjectContext(self,modulename,projectname):
        mctxt=self.getModuleContext(modulename)
        pctxt=mctxt.getProjectContext(projectname)
        return pctxt
        
    def getContexts(self,modulename,projectname):
        mctxt=self.getModuleContext(modulename)
        pctxt=mctxt.getProjectContext(projectname)        
        return (mctxt,pctxt)
        
    def buildMap(self):
        """ Build a tree of dependencies, mark X depends upon Y, and also mark
            Y has a dependee of X (i.e. both directions)
            Do same for optional. """
        for project in Project.list.values():
            if not project.module: continue    
            projectContext=self.getProjectContext(project.module,project.name)
            for depend in project.depend:
                try:
                    dependProject=Project.list[depend.project]
                    if not dependProject.module: continue
                    dependContext=self.getProjectContext(dependProject.module,depend.project)
                    if not projectContext in dependContext.dependees:
                        dependContext.dependees.append(projectContext)
                    if not dependContext in projectContext.depends:
                        projectContext.depends.append(dependContext)
                except KeyError: # :TODO: Hack, do this sooner...
                    print "Unknown Project : " + depend.project                        
                        
            for option in project.option:                    
                try:
                    optionProject=Project.list[option.project]
                    if not optionProject.module: continue
                    optionContext=self.getProjectContext(optionProject.module,option.project)
                    if not projectContext in optionContext.optionees:
                        optionContext.optionees.append(projectContext)
                    if not optionContext in projectContext.options:
                        projectContext.options.append(optionContext)      
                except KeyError:
                    print "Unknown Project : " + option.project
                        
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)
   
  project1=Project({'name':'TestProject1'})
  project1.module=Module({'name':"M"})
  project2=Project({'name':'TestProject2'})
  project2.module=Module({'name':"M"})
  
  cmd=Cmd("test",'test_out')
  #set classpath/environment
  cmd.addParameter("A","a")
  cmd.addParameter("B")

  item=WorkItem(TYPE_TEST,cmd,CmdResult(cmd))
  
  context=GumpContext()
  context.performedWorkOnProject(project1, item);
  context.performedWorkOnProject(project2, item);
  context.performedWorkOnProject(project1, item);
  
  dump(context)
  
  gumpContext=GumpContext();
  moduleContext=gumpContext.getModuleContext("M")
  projectContext=gumpContext.getProjectContextForProject(project1)
  
