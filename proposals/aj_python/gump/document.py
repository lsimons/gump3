#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/proposals/aj_python/gump/Attic/document.py,v 1.1 2003/08/21 19:38:14 nickchalko Exp $
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
    xdoc generation, for forrest
"""

import socket
import time
import os
import sys
import logging
from string import lower

from gump import log, gumpSafeName
from gump.conf import *
from gump.xdoc import *
from gump.xmlutils import xmlize
from gump.context import *
from gump.model import *
from gump.statistics import StatisticsDB,ProjectStatistics,StatisticsGuru

def documentText(workspace,context):
    print "Workspace Status : " + stateName(context.status)
    print "Workspace Secs : " + str(context.elapsedSecs())
    print "Modules: " + str(len(context.subcontexts))
    for (mname,mctxt) in context.subcontexts.iteritems():
        print " Module [" + mname + "] Status: " + stateName(mctxt.status)
        print " Projects: " + str(len(mctxt.subcontexts))
        for (pname,pctxt) in mctxt.subcontexts.iteritems():
            print "  Project [" + pname + "] Status: " + stateName(pctxt.status)
            print "   Work [" + str(len(pctxt.worklist)) + "] [" + str(pctxt.elapsedSecs()) + "] secs." 
            for work in pctxt.worklist:
                print "    Work : " + stateName(work.status)
                if isinstance(work,CommandWorkItem):
                    print "    Work Name : " + work.command.name
                    print "    Work Cmd  : " + work.command.formatCommandLine()
                    if work.command.cwd:
                        print "    Work Cwd  : " + work.command.cwd
                    print "    Work Exit : " + str(work.result.exit_code)

def document(workspace,context,full=None):
    
    log.info('--- Documenting Results')
  
    db=StatisticsDB()
  
    documentWorkspace(workspace,context,db)
    
    if full:
        documentStatistics(workspace,context,db)
        #documentXRef(workspace,context)
        
    forrest=Cmd('forrest','forrest',dir.docs)
    forrestResult=execute(forrest)

    # Update Context    
    work=CommandWorkItem(WORK_TYPE_DOCUMENT,forrest,forrestResult)
    context.performedWork(work)
    
    #documentText(workspace,context)

     
#####################################################################           
#
# Model Pieces
#      
def documentWorkspace(workspace,context,db):
    wdir=getWorkspaceDir()
    x=startXDoc(getWorkspaceDocument(wdir))
    headerXDoc(x,'Workspace')
    
    if workspace.description:
        startSectionXDoc(x,'Description')    
        paragraphXDoc(x,workspace.description)
        endSectionXDoc(x)
    
    startSectionXDoc(x,'Modules')
    startTableXDoc(x)
    for (mname,mctxt) in context.subcontexts.iteritems():
        (mhours, mmins, msecs) 	= mctxt.elapsedTime();
        x.write('     <tr><!-- %s -->' % (mname))        
        x.write('      <td><link href=\'%s\'>%s</link></td><td>%s</td>' % (getModuleRelativeUrl(mname),mname,stateName(mctxt.status)))    
        x.write('      <td>%s:%s:%s</td>' % (str(mhours),str(mmins),str(msecs)))    
        x.write('     </tr>')
    endTableXDoc(x)
    endSectionXDoc(x)
    
    startSectionXDoc(x,'Details')
    startListXDoc(x,'Details')
    addItemXDoc(x,"Status : ", stateName(context.status))
    
    (hours, mins, secs) 	= context.elapsedTime();
    addItemXDoc(x,"Elapsed Time : ", str(hours) + ':' + str(mins) + ':' + str(secs))
    endListXDoc(x)
    endSectionXDoc(x)
    
    documentWorkList(x,context.worklist,wdir)
    
    footerXDoc(x)
    endXDoc(x)
    
    #
    # Document 
    #
    for (mname,mctxt) in context.subcontexts.iteritems():
        documentModule(wdir,mname,mctxt,db)
        
def documentModule(wdir,modulename,modulecontext,db):
    mdir=getModuleDir(modulename,wdir)
    module=Module.list[modulename]
    x=startXDoc(getModuleDocument(modulename,mdir))
    headerXDoc(x,'Module : ' + modulename)
    
    if module.description:
        startSectionXDoc(x,'Description')     
        paragraphXDoc(x,module.description)
        endSectionXDoc(x)
    
    startSectionXDoc(x,'Projects')
    x.write('    <table>\n')
    for (pname,pctxt) in modulecontext.subcontexts.iteritems():
        (phours, pmins, psecs) 	= pctxt.elapsedTime();
        x.write('     <tr><!-- %s -->' % (pname))        
        x.write('      <td><link href=\'%s\'>%s</link></td><td>%s</td>' % (getProjectRelativeUrl(pname),pname,stateName(pctxt.status)))    
        x.write('      <td>%s:%s:%s</td>' % (str(phours),str(pmins),str(psecs)))    
        x.write('     </tr>')
    x.write('    </table>\n')
    endSectionXDoc(x)
    
    startSectionXDoc(x,'Module Details')
    paragraphXDoc(x,"Status: " + stateName(modulecontext.status))
    endSectionXDoc(x)
       
    documentWorkList(x,modulecontext.worklist,mdir)
    
    footerXDoc(x)
    endXDoc(x)
  
    # Document Projects
    for (pname,pctxt) in modulecontext.subcontexts.iteritems():
        documentProject(modulename,mdir,pname,pctxt,db)
   
def documentProject(modulename,mdir,projectname,projectcontext,db): 
    module=Module.list[modulename]
    project=Project.list[projectname]
    x=startXDoc(getProjectDocument(modulename,projectname,mdir))
    headerXDoc(x,'Project : ' + projectname)
   
    description=project.description or module.description
    if description:
        startSectionXDoc(x,'Description')     
        paragraphXDoc(x,description)
        endSectionXDoc(x)

    # Extract from project statistics DB
    stats=db.getProjectStats(projectname)
 
    startSectionXDoc(x,'Details')
    startListXDoc(x)
    addItemXDoc(x,"Status: ", stateName(projectcontext.status))  
    addItemXDoc(x,"Elapsed: ", str(projectcontext.elapsedSecs()))
    addItemXDoc(x,"FOG Factor: ", str(stats.getFOGFactor()))
    addItemXDoc(x,"Successes: ", str(stats.successes))
    addItemXDoc(x,"Failures: ", str(stats.failures))
    addItemXDoc(x,"Prerequisite Failures: ", str(stats.prereqs))
    if stats.first:
        addItemXDoc(x,"First Success: ", str(stats.first))
    if stats.last:
        addItemXDoc(x,"Last Success: ", str(stats.last))
    endListXDoc(x)
    endSectionXDoc(x)
         
    if project.depend and len(project.depend) > 0:
        startSectionXDoc(x,"Project Dependencies")
        startListXDoc(x)
        for depend in project.depend:
          addItemXDoc(x,depend.project)
        endListXDoc(x)
        endSectionXDoc(x)
            
    if project.option and len(project.option) > 0:
        startSectionXDoc(x,"Optional Project Dependencies")
        startListXDoc(x)
        for option in project.option:
          addItemXDoc(x,option.project)
        endListXDoc(x)
        endSectionXDoc(x)
                      
    documentWorkList(x,projectcontext.worklist,mdir)
    footerXDoc(x)
    endXDoc(x)

def documentWorkList(x,worklist,dir='.'):
    if not worklist: return
    startSectionXDoc(x,'Work')
    x.write('    <table>\n')
    for work in worklist:
        x.write('     <tr><!-- %s -->' % (workTypeName(work.type)))       
        x.write('      <td>%s</td>' % (workTypeName(work.type))) 
        x.write('      <td><link href=\'%s\'>%s</link></td>' % (getWorkRelativeUrl(work.type,work.command.name),work.command.name))    
        x.write('      <td>%s</td><td>%s</td>' % (stateName(work.status), str(work.secs)))    
        x.write('     </tr>')
    x.write('    </table>\n')
    endSectionXDoc(x)
    
    for work in worklist:
        documentWork(work,dir)
        
def documentWork(work,dir):
    if isinstance(work,CommandWorkItem):    
        x=startXDoc(getWorkDocument(dir,work.command.name,work.type))
        headerXDoc(x, workTypeName(work.type) + ' : ' + work.command.name)
        startSectionXDoc(x,'Details')
        paragraphXDoc(x,"Status: " + stateName(work.status))
        endSectionXDoc(x)
        
        startListXDoc(x)
        addItemXDoc(x,"Command: ", work.command.name)
        if work.command.cwd:
            addItemXDoc(x,"Working Directory: ", work.command.cwd)
        addItemXDoc(x,"Output: ", work.result.output)
        addItemXDoc(x,"Exit Code: ", str(work.result.exit_code))
        endListXDoc(x)
        
        if work.command.params:
            x.write('<table><tr><th>Parameters</th></tr><tr><th>Prefix</th><th>Name</th><th>Value</th></tr>')
            for param in work.command.params.items():
                x.write('<tr><td>')
                if param.prefix: 
                  x.write(param.prefix)
                x.write('</td><td>')
                x.write(param.name)
                x.write('</td><td>')
                val = param.value
                if val:
                    x.write(val)
                else:
                    x.write('N/A')
                x.write('</td></tr>\n')        
            x.write('</table>\n')
        
        if work.command.env:
            x.write('<table><tr><th>Environment</th></tr><tr><th>Name</th><th>Value</th></tr>')
            for (name, value) in work.command.env.iteritems():
                x.write('<tr><td>')
                x.write(name)
                x.write('</td><td>')
                if value:
                    x.write(value)
                else:
                    x.write('N/A')
                x.write('</td></tr>\n')        
            x.write('</table>\n')
        
        startSectionXDoc(x,'Command Line')
        noteXDoc(x,work.command.formatCommandLine())
        endSectionXDoc(x)
        
        startSectionXDoc(x,'Output')
        output=work.result.output
        if output:
            x.write('<source>')
            x.write(':TODO: Copy data from .... ')
            x.write(output)
            x.write('</source>\n')
      
        endSectionXDoc(x)
        footerXDoc(x)
        endXDoc(x)
        
#####################################################################           
#
# Statistics Pages
#           
def documentStatistics(workspace,context,db):
    
    stats=StatisticsGuru(workspace,context,db)
    
    sdir=getStatisticsDir()
    x=startXDoc(getStatisticsDocument(sdir))
    headerXDoc(x,'Statistics')
    
    startSectionXDoc(x,'Overview')
    startListXDoc(x)
    addItemXDoc(x,'Modules: ', stats.wguru.modulesInWorkspace)
    addItemXDoc(x,'Projects: ', stats.wguru.projectsInWorkspace)
    addItemXDoc(x,'Avg Projects Per Module: ', stats.wguru.averageProjectsPerModule)
    endListXDoc(x)
    endSectionXDoc(x)
    
    
    x.write('    <p>\n')
    addLinkXDoc(x, 'elapsed.html', 'Modules By Elapsed Time')
    addLinkXDoc(x, 'projects.html', 'Modules By Project Count')
    addLinkXDoc(x, 'dependencies.html', 'Modules By Dependency Count')
    addLinkXDoc(x, 'dependees.html', 'Modules By Dependee Count')    
    x.write('    </p>\n')
    
    footerXDoc(x) 
    endXDoc(x)
    
    documentModulesByElapsed(stats, sdir)
    documentModulesByProjects(stats, sdir)
    documentModulesByDependencies(stats, sdir)
    documentModulesByDependees(stats, sdir)
    

def documentModulesByElapsed(stats,sdir):
    x=startXDoc(os.path.join(sdir,'elapsed.xml'))
    headerXDoc(x, 'Modules By Elapsed Time')
    
    startTableXDoc(x,'Modules By Elapsed')
    for mctxt in stats.modulesByElapsed:
        startTableRowXDoc(x)
        insertTableHeaderXDoc(x,mctxt.name)
        insertTableDataXDoc(x, mctxt.elapsedSecs())
        endTableRowXDoc(x)
    endTableXDoc(x)
    
    footerXDoc(x)
    endXDoc(x)

def documentModulesByProjects(stats,sdir):
    x=startXDoc(os.path.join(sdir,'projects.xml'))
    headerXDoc(x, 'Modules By Project Count')
    
    startTableXDoc(x,'Modules By Project Count')
    for mctxt in stats.modulesByProjectCount:
        startTableRowXDoc(x)
        insertTableHeaderXDoc(x,mctxt.name)
        insertTableDataXDoc(x, len(mctxt.subcontexts))
        
        projectsString=''
        for pctxt in mctxt.subcontexts.values():
            projectsString+=pctxt.name
            projectsString+=' '            
        insertTableDataXDoc(x, projectsString)
        
        endTableRowXDoc(x)
    endTableXDoc(x)
    
    footerXDoc(x)
    endXDoc(x)
 
def documentModulesByDependencies(stats,sdir):
    x=startXDoc(os.path.join(sdir,'dependencies.xml'))
    headerXDoc(x, 'Modules By Dependency Count')
    
    startTableXDoc(x,'Modules By Dependency Count')
    for mctxt in stats.modulesByTotalDependencies:
        startTableRowXDoc(x)
        insertTableHeaderXDoc(x,mctxt.name)
        insertTableDataXDoc(x, mctxt.dependencyCount())
        
        projectsString=''
        for pctxt in mctxt.getDepends():
            projectsString+=pctxt.name
            projectsString+=' '            
        insertTableDataXDoc(x, projectsString)
       
        endTableRowXDoc(x)
    endTableXDoc(x)
    
    footerXDoc(x)
    endXDoc(x)
    
 
 
def documentModulesByDependees(stats,sdir):
    x=startXDoc(os.path.join(sdir,'dependees.xml'))
    headerXDoc(x, 'Modules By Dependee Count')
    
    startTableXDoc(x,'Modules By Dependee Count')
    for mctxt in stats.modulesByTotalDependees:
        startTableRowXDoc(x)
        insertTableHeaderXDoc(x,mctxt.name)
        insertTableDataXDoc(x, mctxt.dependeeCount())
        
        projectsString=''
        for pctxt in mctxt.getDependees():
            projectsString+=pctxt.name
            projectsString+=' '            
        insertTableDataXDoc(x, projectsString)
        
        endTableRowXDoc(x)
    endTableXDoc(x)
    
    footerXDoc(x)
    endXDoc(x)
    
 
#####################################################################           
#
# Helper Methods
#           
 
def getWorkspaceDir():
    ddir=os.path.normpath(os.path.join(dir.docs,'forrest'))
    if not os.path.exists(ddir): os.mkdir(ddir)
    cdir=os.path.normpath(os.path.join(ddir,'content'))
    if not os.path.exists(cdir): os.mkdir(cdir)
    xdir=os.path.normpath(os.path.join(cdir,'xdocs'))
    if not os.path.exists(xdir): os.mkdir(xdir)
    return xdir
    
    
def getStatisticsDir(workspacedir=None):
    wdir=workspacedir or getWorkspaceDir()
    sdir=os.path.normpath(os.path.join(wdir,'stats'))
    if not os.path.exists(sdir): os.mkdir(sdir)
    return sdir
    
def getXRefDir(workspacedir=None):
    wdir=workspacedir or getXRefDir()
    xdir=os.path.normpath(os.path.join(wdir,'xref'))
    if not os.path.exists(xdir): os.mkdir(xdir)
    return xdir
    
def getModuleDir(modulename,workspacedir=None):
    mdir=gumpSafeName(modulename)
    if not workspacedir: workspacedir = getWorkspaceDir()
    xdir=os.path.normpath(os.path.join(workspacedir,mdir))
    if not os.path.exists(xdir): os.mkdir(xdir)
    return xdir

def getWorkDir(rootdir,type):
    tdir=gumpSafeName(lower(workTypeName(type)))
    wdir=os.path.normpath(os.path.join(rootdir,tdir))
    if not os.path.exists(wdir): os.mkdir(wdir)
    return wdir    
 
def getWorkspaceDocument(workspacedir=None):
    if not workspacedir: workspacedir = getWorkspaceDir()    
    return os.path.join(workspacedir,'index.xml')
    
def getStatisticsDocument(statsdir=None):
    if not statsdir: statsdir = getStatisticsDir()    
    return os.path.join(statsdir,'index.xml')
    
def getXRefDocument(xrefdir=None):
    if not xrefdir: xrefdir = getXRefDir()    
    return os.path.join(xrefdir,'index.xml')
    
def getModuleDocument(modulename,moduledir=None):
    mdir=gumpSafeName(modulename)
    if not moduledir: moduledir=getModuleDir(modulename)
    return os.path.join(moduledir,'index.xml')

def getProjectDocument(modulename,projectname,moduledir=None):
    pname=gumpSafeName(projectname)
    if not moduledir: moduledir=getModuleDir(modulename)
    return os.path.join(moduledir,pname+'.xml')

def getWorkDocument(rootdir,name,type,wdir=None):
    wname=gumpSafeName(name)
    if not wdir: wdir=getWorkDir(rootdir,type)
    return os.path.join(wdir,wname+'.xml')
    
def getWorkspaceRelativeUrl(depth=0):
    return getUp(depth)+'index.html'
    
def getWorkspaceRelativeUrlFromModule():
    return getWorkspaceRelativeUrl(1)
    
def getWorkspaceRelativeUrlFromProject():
    return getWorkspaceRelativeUrl(1)
    
def getModuleRelativeUrl(name,depth=0):
    return getUp(depth)+gumpSafeName(name)+'/index.html'
    
def getModuleRelativeUrlFromModule(name):
    return getModuleRelativeUrl(name,1)
    
def getModuleRelativeUrlFromProject(name):
    return getModuleRelativeUrl(name,1)

def getProjectRelativeUrl(name,depth=0):
    return getUp(depth)+gumpSafeName(name)+'.html'
    
def getModuleProjectRelativeUrl(mname,pname,depth=0):
    return getUp(depth)+gumpSafeName(mname)+'/'+gumpSafeName(pname)+'/index.html'
    
def getModuleProjectRelativeUrlFromModule(mname,pname):
    return getProjectRelativeUrl(mname,pname,1)

def getModuleProjectRelativeUrlFromProject(mname,pname):
    return getProjectRelativeUrl(mname,pname,1)

def getWorkRelativeUrl(type,name):
    tdir=gumpSafeName(lower(workTypeName(type)))
    return tdir+'/'+gumpSafeName(name)+'.html'
    
def getUp(depth):
    url=''
    i = 0
    while i < depth:
        url+='../'
        i += 1
    return url
           
#####################################################################           
#
# XDoc Pieces
#           
def startXDoc(xfile):

    log.debug("Documenting to file : [" + xfile + "]")
    # f=StringIO.StringIO() # Testing
    f=open(xfile, 'w')
    return f

def headerXDoc(f,title):
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<!DOCTYPE document PUBLIC "-//APACHE//DTD Documentation V1.1//EN" "./dtd/document-v11.dtd">\n')
    f.write('<!-- Automatically Generated by Python Gump: http://jakarta.apache.org/gump -->\n\n')
    f.write('<document>\n')
    f.write('  <header>\n')
    f.write('   <title>%s</title>\n' % (title))
    f.write('   <authors>\n')
    f.write('    <person id="gump" name="Gump" email="gump@lists.apache.org"/>\n')
    f.write('   </authors>\n')
    f.write('   </header>\n')
    f.write('  <body>\n')    
    
def footerXDoc(f):
    f.write('  </body>\n')
    f.write('</document>\n')  
    
def endXDoc(f):
    if isinstance(f,StringIO.StringIO): # Testing
        f.seek(0)
        # print f.read()
    f.close()  

def startSectionXDoc(f, title):
    f.write('    <section><title>%s</title>\n' % (title))
    
def paragraphXDoc(f, content):
    f.write('    <p>%s</p>\n' % (content))
    
def endSectionXDoc(f):
    f.write('    </section>\n')
    
def startTableXDoc(f, title=None):
    f.write('    <table>\n');
    if title:
        f.write('<tr><th>%s</th></tr>\n' % (title))

def startTableRowXDoc(f):
    f.write('     <tr>\n');

def insertTableHeaderXDoc(f,d):
    f.write('      <th>%s</th>\n' % (d));
    
def insertTableDataXDoc(f,d):
    f.write('      <td>%s</td>\n' % (d));

def endTableRowXDoc(f):
    f.write('     </tr>\n')
    
def endTableXDoc(f):
    f.write('    </table>\n')
    
def startListXDoc(f, title=None):
    if title:
        paragraphXDoc(f,title)
    f.write('    <ul>\n');
    
def addItemXDoc(f,t,i=''):
    f.write('      <li><strong>%s</strong>%s</li>\n' % (t,i))
    
def addLinkXDoc(f,url,title):
    f.write('       <link href=\'%s\'>%s</link>' % (url,title))    
  
def endListXDoc(f ):
    f.write('    </ul>\n')
    
def insertXmlXDoc(f,nodename,nodexml):
    xmlize(nodename,nodexml,f)

def noteXDoc(f,text):
    f.write('<note>\n')
    f.write(text)
    f.write('</note>\n')                
    
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
    cmd.addParameter("A","a")
    cmd.addParameter("B")

    item=CommandWorkItem(TYPE_BUILD,cmd,CmdResult(cmd))
    
    context=GumpContext()
    context.performedWorkOnProject(project1, item)
    context.performedWorkOnProject(project2, item)
    context.performedWorkOnProject(project1, item)
  
    dump(context)
    
    document(context)
  