#!/usr/bin/env python

# $Header: /home/cvspublic/jakarta-gump/python/gump/conf.py,v 1.7 2003/05/10 18:20:36 nicolaken Exp $
# $Revision: 1.7 $
# $Date: 2003/05/10 18:20:36 $
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

from gump import log
from gump.model import *
from gump.conf import *
from gump.launcher import *
from gump.utils import *

STATUS_UNSET=0
STATUS_NONE=1
STATUS_SUCCESS=2
STATUS_FAILED=3
STATUS_PREREQ_FAILURE=4
STATUS_COMPLETE=5

stateDescriptions = { STATUS_UNSET : "Unset",
           STATUS_NONE : "No Work Performed",
           STATUS_SUCCESS : "Success",
           STATUS_FAILED : "Failed",
           STATUS_PREREQ_FAILURE : "Prerequisite Failed",
           STATUS_COMPLETE : "Complete" }

def stateName(state):
    return stateDescriptions.get(state,'Unknown State:' + str(state))
    

describedState = { "Unset" : STATUS_UNSET,
           "No Work Performed" : STATUS_NONE,
            "Success" : STATUS_SUCCESS,
            "Failed" : STATUS_FAILED,
            "Prerequisite Failed" : STATUS_PREREQ_FAILURE,
            "Complete"  : STATUS_COMPLETE}
           
def stateForName(name):
    return describedState.get(name,STATUS_UNSET)

stateMap = {   CMD_STATUS_NOT_YET_RUN : STATUS_UNSET,
               CMD_STATUS_SUCCESS : STATUS_SUCCESS,
               CMD_STATUS_FAILED : STATUS_FAILED,
               CMD_STATUS_TIMED_OUT : STATUS_FAILED }
               
def commandStatusToWorkStatus(state):
    return stateMap[state]
           
def stateUnset(state):
    return state==STATUS_NONE or state==STATUS_UNSET 
        
def stateOk(state):
    return state==STATUS_SUCCESS
        
def stateUnsetOrOk(state):
    return stateUnset(state) or stateOk(state)           
    
LEVEL_UNSET=0
LEVEL_INFO=1
LEVEL_WARNING=2
LEVEL_ERROR=3
LEVEL_FATAL=4

levelDescriptions = { 	LEVEL_UNSET : "Not Set",
                    LEVEL_INFO : "Info",
                    LEVEL_WARNING : "Warning",
                    LEVEL_ERROR : "Error",
                    LEVEL_FATAL : "Fatal" }               

def levelName(level):
    return levelDescriptions.get(level,'Unknown Level:' + str(level))
    
class Annotation:
    """ An annotation ... a log entry on the object ..."""
    def __init__(self,level,text):
        self.level=level
        self.text=text
        
    def __str__(self):
        return levelName(self.level) + ":" + self.text
               
WORK_TYPE_CHECK=1
WORK_TYPE_CONFIG=2
WORK_TYPE_UPDATE=3
WORK_TYPE_SYNC=4
WORK_TYPE_BUILD=5
WORK_TYPE_DOCUMENT=6

workTypeDescriptions = { 	WORK_TYPE_CHECK : "CheckEnvironment",
                WORK_TYPE_CONFIG : "Config",
                WORK_TYPE_UPDATE : "Update",
                WORK_TYPE_SYNC : "Synchronize",
                WORK_TYPE_BUILD : "Build",
                WORK_TYPE_DOCUMENT : "Document" }    
    
def workTypeName(type):
    return workTypeDescriptions.get(type,'Unknown Work Type:' + str(type))
                   
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
        return secsToElapsedTime(self.secs or 0)
         
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
    def __init__(self,type,command,result=None,message=''):
        if not result: result=CmdResult(command)
        TimedWorkItem.__init__(self,type,commandStatusToWorkStatus(result.status),result.elapsed,message)
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
        
    
REASON_UNSET=0
REASON_PACKAGE=1
REASON_PACKAGE_BAD=2
REASON_CIRCULAR=3
REASON_CONFIG_FAILED=4
REASON_UPDATE_FAILED=5
REASON_SYNC_FAILED=6
REASON_BUILD_FAILED=7
REASON_MISSING_OUTPUTS=8

reasonCodeDescriptions = { 	REASON_UNSET : "Not Set",
                    REASON_PACKAGE : "Complete Package Install",
                    REASON_PACKAGE_BAD : "Bad Package Installation",
                    REASON_CIRCULAR : "Circular Dependency",
                    REASON_CONFIG_FAILED : "Configuration Failed",
                    REASON_UPDATE_FAILED : "Update Failed",
                    REASON_SYNC_FAILED : "Synchronize Failed",
                    REASON_BUILD_FAILED : "Build Failed",
                    REASON_MISSING_OUTPUTS : "Missing Build Outputs" }    
    
def reasonString(reasonCode):
    return reasonCodeDescriptions.get(reasonCode,'Unknown Reason:' + str(reasonCode))
          
class StatePair:
    """Contains a State Plus Reason"""
    def __init__(self,status=STATUS_UNSET,reason=REASON_UNSET):
        self.status=status
        self.reason=reason
        
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        result=stateName(self.status)
        if not self.reason == REASON_UNSET:
            result += ":" + reasonString(self.reason)
        return result
        
    def __eq__(self,other):
        return self.status == other.status and self.reason == other.reason
                
    def __cmp__(self,other):
        cmp = self.status < other.status
        if not cmp: cmp = self.reason < other.reason
        return cmp

class Summary:
    """ Contains an overview """
    def __init__(self,projects=0,successes=0,failures=0,prereqs=0,noworks=0,packages=0,others=0,statepairs=None):
        self.projects=projects
        self.successes=successes
        self.failures=failures
        self.prereqs=prereqs
        self.noworks=noworks
        self.packages=packages
        self.others=others
        self.statepairs=statepairs
        
        if not self.statepairs: self.statepairs=[]
        
    def addState(self,pair):            
        status=pair.status
        # Stand up and be counted
        if not stateUnset(status):
            if stateOk(status):
                self.successes+=1
            elif STATUS_PREREQ_FAILURE == status:
                self.prereqs+=1
            elif STATUS_FAILED == status:
                self.failures+=1
            elif STATUS_NONE == status:
                self.noworks+=1
            elif STATUS_COMPLETE == status:
                # :TODO: Accurate?
                self.packages+=1
            else:
                self.others+=1
                
        # One more project...
        self.projects += 1
                
        # Add state, if not already there
        if not stateUnset(pair.status) and not pair in self.statepairs: \
            self.statepairs.append(pair)
        
    def addSummary(self,summary):
                 
        self.projects += summary.projects
        
        self.successes += summary.successes
        self.failures += summary.failures
        self.prereqs += summary.prereqs
        self.noworks += summary.noworks
        self.packages += summary.packages
        self.others += summary.others
        
        # Add state pair, if not already there
        for pair in summary.statepairs:
            if not stateUnset(pair.status) and not pair in self.statepairs: \
                self.statepairs.append(pair)
        
class Context:
    """Context for a single entity"""
    def __init__(self,name,parent=None):
        
        self.status=STATUS_NONE
        self.reason=REASON_UNSET        
        self.cause=None
        
    	self.name=name
        self.subcontexts=dict()
        self.parent=parent
        self.annotations=[]
        self.worklist=WorkList()
        
    # Same if same type, and same name
    # i.e project context X is not equals to module context X
    def __eq__(self,other):
        return self.__class__ == other.__class__ and self.name == other.name
        
    def __cmp__(self,other):
        return self.name < other.name
        
    def __repr__(self):
        return str(self.__class__)+':'+self.name
        
    def __str__(self):
        return str(self.__class__)+':'+self.name
        
    def __iter__(self):
        return AlphabeticDictionaryIterator(self.subcontexts)
        
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
            
    def setState(self,status,reason=REASON_UNSET,cause=None):  
        self.status=status
        self.reason=reason
        self.cause=cause
            
    def getStatePair(self):  
        return StatePair(self.status, self.reason)
        
    def aggregateStates(self, states=None):
        if not states: states=[]
        
        pair=self.getStatePair()
        # Add state, if not already there
        if not stateUnset(pair.status) and not pair in states: \
            states.append(pair)
        
        return self.getSubbordinateStates(states);
        
    def getSubbordinateStates(self, states=None):
        if not states: states=[]
        
        # Subbordinates
        for ctxt in self:
            ctxt.aggregateStates(states)
            
        return states;
    
            
    def propagateErrorState(self,status,reason=REASON_UNSET,cause=None):
        #
        # If no-one else to point the finger at ...
        # ... step up.
        #
        if not cause: cause = self
            
        #
        # Do NOT over-write a pre-determined condition
        #
        if stateUnsetOrOk(self.status):
            # Modify self
            self.setState(status,reason,cause)
            # .. then push this error down
            for ctxt in self:
                ctxt.propagateErrorState(status,reason,cause)        
        
    def elapsedSecs(self):
        elapsedSecs=self.worklist.elapsedSecs()
        if self.subcontexts:
            for (cname,ctxt) in self.subcontexts.iteritems():
                elapsedSecs += ctxt.elapsedSecs()
        return int(round(elapsedSecs,0))
        
    def addInfo(self,text):
        self.addAnnotation(LEVEL_INFO, text)
        
    def addWarning(self,text):
        self.addAnnotation(LEVEL_WARNING, text)
        
    def addError(self,text):
        self.addAnnotation(LEVEL_ERROR, text)
        
    def addFatal(self,text):
        self.addAnnotation(LEVEL_FATAL, text)
        
    def addAnnotation(self,level,text):
        self.addAnnotationObject(Annotation(level,text))
        
    def addAnnotationObject(self,message):
        self.annotations.append(message)
        
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
        
    def okToPerformWork(self):
        return stateUnsetOrOk(self.status)
        
            	
class ProjectContext(Context):
    """Context for a single project"""
    def __init__(self,name,parent=None):
    	Context.__init__(self,name,parent)
    	self.project=Project.list[name]
    	
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
             
    def getFOGFactor(self):
        fogFactor=0
        if hasattr(self,'stats'):
             fogFactor = self.stats.getFOGFactor()
        return fogFactor
            
        return round(fogFactor/fogFactors,2)
        
    def propagateErrorState(self,status,reason=REASON_UNSET,cause=None): 
        #
        # If no-one else to point the finger at ...
        # ... step up.
        #
        if not cause: cause = self
                        
        # Do NOT over-write a preexisting condition
        if stateUnsetOrOk(self.status):
            # Call the superclass behaviour
            Context.propagateErrorState(self,status,reason,cause)
            
            #
            #
            #
            message = lower(stateName(status))
            if not REASON_UNSET == reason:
                message += " with reason " + lower(reasonString(reason))            
            self.addError(capitalize(message))
            
            #
            # Mark depend*ee*s as failed for this cause...
            #
            for dependeeContext in self.dependees:
                dependeeContext.addError("Dependency " + self.name + " " + message)
                dependeeContext.propagateErrorState(STATUS_PREREQ_FAILURE,reason,cause)
                
            #
            # At least notify these folks
            #
            for optioneeContext in self.optionees:
                optioneeContext.addWarning("Optional dependency " + self.name + " " + message)

UNNAMED_MODULE='Unnamed Module'
            
class ModuleContext(Context):
    """Set of Modules (which contain projects)"""
    def __init__(self,name=UNNAMED_MODULE,parent=None):
    	Context.__init__(self,name,parent)
        	
    	if Module.list.has_key(name):
    	    self.module=Module.list[name]
        else:
            self.module=None # :TODO: Cleanup this...
    	
    	self.totalDepends=[]
    	self.totalDependees=[]
        
    #
    # Get a project context, by name
    #
    def getProjectContextForProject(self,project):
        return self.getProjectContext(project.name)
        
             
    def getProjectContext(self,projectname):
        if not self.subcontexts.has_key(projectname): 
            self.subcontexts[projectname] =  ProjectContext(projectname,self)
        return self.subcontexts[projectname]
        
    def getDependees(self):   
        if self.totalDependees: return self.totalDependees
                
        for pctxt in self:
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
        
    def getFOGFactor(self):
        fogFactor=0
        fogFactors=0
        for ctxt in self:
                projectFOGFactor = ctxt.getFOGFactor()
                fogFactor += projectFOGFactor
                fogFactors += 1
                
        if not fogFactors:
            fogFactors=1 # 0/1 is better than 0/0
            
        return round(fogFactor/fogFactors,2)
         
    # Get a summary of states for each project
    def getProjectSummary(self,summary=None):            
        if not summary: 
            summary=Summary()
        
        #
        # Subordinates are projects, so get their summary
        #
        for ctxt in self:
            summary.addState(ctxt.getStatePair())
            
        return summary
           
class GumpContext(Context):
    """Gump Run Context"""
    def __init__(self,name="Gump",parent=None):
    	Context.__init__(self,name,parent)
    	
        #
    	# Set to true if not found, see checkEnvironment
    	#
    	self.noRSync=0
    	self.noForrest=0
    	
    	#
    	# JAVACMD can override this, see checkEnvironment
    	#
        self.javaCommand = 'java'
        
        #
        # Turns on ant '-debug'
        #
        self.debug=0	
        
        #
        # Turns on ant '-verbose'
        #
        self.verbose=0	
        
        #    
        self.startdatetime=time.strftime(setting.datetimeformat, \
                                time.localtime())
        self.timezone=str(time.tzname)
        
    def performedWorkOnProject(self,project,item):
        (mctxt,pctxt)=self.getContextsForProject(project)
        pctxt.performedWork(item)
        
    def performedWorkOnModule(self,module,item):
        mctxt=self.getModuleContextForModule(module)
        mctxt.performedWork(item)
        
    def getModuleContextForModule(self,module):
        return self.getModuleContext(module.name)
        
    def getModuleContext(self,modulename=UNNAMED_MODULE):
        if not self.subcontexts.has_key(modulename): self.subcontexts[modulename] = \
          ModuleContext(modulename,self)
        ctxt = self.subcontexts[modulename]
        return ctxt
        
    def getProjectContextForProject(self,project):
        (mctxt,pctxt)=self.getContextsForProject(project)
        return pctxt
        
    def getContextsForProject(self,project):
        return self.getContexts(project.module, project.name)
        
    def getProjectContext(self,modulename,projectname):
        mctxt=self.getModuleContext(modulename or UNNAMED_MODULE)
        pctxt=mctxt.getProjectContext(projectname)
        return pctxt
        
    def getContexts(self,modulename,projectname):
        mctxt=self.getModuleContext(modulename or UNNAMED_MODULE)
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
                    # Hack -- need to figure these w/ no module out...
                    if not dependProject.module: continue
                    dependContext=self.getProjectContext(dependProject.module,depend.project)
                    # Add a dependee
                    if not projectContext in dependContext.dependees:
                        dependContext.dependees.append(projectContext)
                    # Add a dependency
                    if not dependContext in projectContext.depends:
                        projectContext.depends.append(dependContext)
                except KeyError: # :TODO: Hack, do this sooner...
                    print "Unknown Project : " + depend.project                        
                        
            for option in project.option:                    
                try:
                    optionProject=Project.list[option.project]
                    # Hack -- need to figure these w/ no module out...
                    if not optionProject.module: continue
                    optionContext=self.getProjectContext(optionProject.module,option.project)
                    # Add an optional dependee
                    if not projectContext in optionContext.optionees:
                        optionContext.optionees.append(projectContext)
                    # Add an optional dependency
                    if not optionContext in projectContext.options:
                        projectContext.options.append(optionContext)      
                except KeyError:
                    print "Unknown Project : " + option.project
        
    # Get a summary of states for each project
    def getProjectSummary(self,summary=None):            
        if not summary: 
            summary=Summary()
        
        # Subordinates are modules, get their simmary
        # information into this summary
        for ctxt in self:
            ctxt.getProjectSummary(summary)
            
        return summary
                    
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

  item=WorkItem(WORK_TYPE_CHECK,cmd,CmdResult(cmd))
  
  context=GumpContext()
  context.performedWorkOnProject(project1, item);
  context.performedWorkOnProject(project2, item);
  context.performedWorkOnProject(project1, item);
  
  dump(context)
  
  gumpContext=GumpContext();
  moduleContext=gumpContext.getModuleContext("M")
  projectContext=gumpContext.getProjectContextForProject(project1)
  

  summary=gumpContext.getProjectSummary()
  dump(summary)