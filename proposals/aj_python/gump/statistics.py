#!/usr/bin/python

# $Header: /home/stefano/cvs/gump/proposals/aj_python/gump/Attic/statistics.py,v 1.1 2003/08/21 19:38:14 nickchalko Exp $
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
    Statistics gathering/manipulation
"""

import time
import os
import sys
import logging

from anydbm import open

from gump import log
from gump.conf import *
from gump.utils import *
from gump.context import *

class ProjectStatistics:
    """Statistics Holder"""
    def __init__(self,projectname):
        self.projectname=projectname
        self.successes=0
        self.failures=0
        self.prereqs=0
        self.first=''
        self.last=''
        
    def getFOGFactor(self):
        return (self.successes - self.failures - self.prereqs)
        
    def nameKey(self):
        return self.projectname + '-pname'
        
    def successesKey(self):
        return self.projectname + '-successes'
        
    def failuresKey(self):
        return self.projectname + '-failures'
        
    def prereqsKey(self):
        return self.projectname + '-prereqs'
        
    def firstKey(self):
        return self.projectname + '-first'
        
    def lastKey(self):
        return self.projectname + '-last'
        
class StatisticsDB:
    """Statistics Interface"""

    def __init__(self):
        self.dbpath    = os.path.normpath('%s/%s' % (dir.work,'stats.db'))
        self.db		=	open(self.dbpath,'cw')
 
    def dumpProjects(self):
        for key in self.db.keys():
            if not -1 == key.find('-pname'):
                pname=key[0:len(key)-6]
                print "Project " + pname + " Key " + key
                s=self.getProjectStats(pname)
                dump(s)
            
    def getProjectStats(self,projectname):
        s=ProjectStatistics(projectname)
        s.successes=self.getInt(s.successesKey())
        s.failures=self.getInt(s.failuresKey())
        s.prereqs=self.getInt(s.prereqsKey())
        s.first=self.getDate(s.firstKey())
        s.last=self.getDate(s.lastKey())
        return s
    
    def putProjectStats(self,s):
        self.put(s.nameKey(), s.projectname)
        self.putInt(s.successesKey(), s.successes)
        self.putInt(s.failuresKey(), s.failures)
        self.putInt(s.prereqsKey(), s.prereqs)
        self.putDate(s.firstKey(), s.first)
        self.putDate(s.lastKey(), s.last)
        
    def delProjectStats(self,s):
        try:
            del self.db[s.nameKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[s.successesKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[s.failuresKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[s.prereqsKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[s.firstKey()]
        except:
            """ Hopefully means it wasn't there... """
        try:
            del self.db[s.lastKey()]
        except:
            """ Hopefully means it wasn't there... """
        
    def getInt(self,key):
        val=0
        if self.db.has_key(key): val=self.db[key]
        return int(val)
        
    def getFloat(self,key):
        val=0
        if self.db.has_key(key): val=self.db[key]
        return float(val)
        
    def getDate(self,key):
        return self.getFloat(key)
        
    def put(self,key,val=''):
        self.db[key]=val
        
    def putInt(self,key,val=0):
        self.db[key]=str(val)
        
    def putDate(self,key,val=0):
        self.putInt(key,val)


def statistics(workspace,context):
    
    log.info('--- Updating Project Statistics')
    
    db=StatisticsDB()       
    for (mname,mctxt) in context.subcontexts.iteritems():
        for (pname,pctxt) in mctxt.subcontexts.iteritems():
            s=db.getProjectStats(pname)
            
            #
            # Update based off current run
            #
            if pctxt.status==STATUS_SUCCESS:
                s.successes += 1
                s.last = time.time()
                
                if not s.first:
                    s.first=s.last
            elif pctxt.status==STATUS_PREREQ_FAILURE:
                s.prereqs  += 1
            else:
                s.failures += 1
            
            #
            # Write out the updates
            #
            db.putProjectStats(s)
            
class WorkspaceStatisticsGuru:                        
    """ Know it all for a workspace... """
    def __init__(self, workspace):
        self.workspace=workspace
        self.calculate()
        
    def calculate(self):
        # I hate to use these globals, but best for now...
        self.modulesInWorkspace=len(Module.list)
        self.projectsInWorkspace=len(Project.list)
        
        self.maxProjectsForAModule=1
        self.moduleWithMaxProjects=''
        for module in Module.list.values():
            
            #
            # Calculate
            #
            projectCount=len(module.project)
            if projectCount > self.maxProjectsForAModule:
                self.maxProjectsForAModule=projectCount
                self.moduleWithMaxProjects=module.name
                
        #
        # Average Projects Per Module
        #
        self.averageProjectsPerModule=round(self.projectsInWorkspace/self.modulesInWorkspace,2)
        
def sortByElapsed(mctxt1,mctxt2):
    elapsed1=mctxt1.elapsedSecs()
    elapsed2=mctxt2.elapsedSecs()
    cmp = 0
    if elapsed1 > elapsed2: cmp = 1
    if elapsed1 < elapsed2: cmp = -1
    return cmp

def sortByProjectCount(mctxt1,mctxt2):
    count1=len(mctxt1.subcontexts.values())
    count2=len(mctxt2.subcontexts.values())
    return count2 - count1              

def sortByDependencyCount(mctxt1,mctxt2):
    count1=mctxt1.dependencyCount()
    count2=mctxt2.dependencyCount()
    return count2 - count1          
        
def sortByDependeeCount(mctxt1,mctxt2):
    count1=mctxt1.dependeeCount()
    count2=mctxt2.dependeeCount()
    return count2 - count1              
            
class StatisticsGuru:
    """ Know it all ... """
    
    def __init__(self, workspace, context, db):
        self.workspace=workspace
        self.context=context
        self.db=db
        
        self.wguru=WorkspaceStatisticsGuru(workspace)
                
        self.modulesByElapsed=orderedList(context.subcontexts.values(),sortByElapsed)
        self.modulesByProjectCount=orderedList(context.subcontexts.values(),sortByProjectCount)
        self.modulesByTotalDependencies=orderedList(context.subcontexts.values(),sortByDependencyCount)
        self.modulesByTotalDependees=orderedList(context.subcontexts.values(),sortByDependeeCount)
   
        
#        calculate()
 #       
  #  def calculate(self):
   #     """ Calculate Stuff """
        
            
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)

  db=StatisticsDB()
  s=db.getProjectStats('test')
  s.successes += 1
  db.putProjectStats(s)
  db.dumpProjects()
  s.failures += 1
  db.putProjectStats(s)
  db.dumpProjects()
  db.delProjectStats(s)
