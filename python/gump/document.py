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
    xdoc generation, for forrest
"""

import socket
import time
import os
import sys
import logging
from string import lower,replace
from xml.sax.saxutils import escape

from gump import log, gumpSafeName
from gump.conf import *
from gump.utils import *
from gump.xmlutils import xmlize
from gump.context import *
from gump.model import *
from gump.statistics import StatisticsDB,ProjectStatistics,StatisticsGuru
from gump.logic import getPackagedProjectContexts, getBuildSequenceForProjects,\
     getProjectsForProjectExpression, getModuleNamesForProjectList, \
    getClasspathLists, AnnotatedPath, hasBuildCommand

def documentText(workspace,context):    
    documentTextToFile(sys.stdout,workspace,context)
    
def documentTextToFile(f,workspace,context):    
    
    moduleList=context.gumpset.getModules()
    projectList=context.gumpset.getSequence()
    
    f.write("Workspace Status : " + stateName(context.status) + "\n")
    f.write("Workspace Secs : " + str(context.elapsedSecs()) + "\n")
    f.write("Modules: " + str(len(context.subcontexts)) + "\n")
    for note in context.annotations:
        f.write(" - " + str(note) + "\n")
    for mctxt in context:
        mname=mctxt.name
        if moduleList and not mctxt.module in moduleList: continue        
        mname=mctxt.name
        f.write(" Module [" + mname + "] Status: " + stateName(mctxt.status) + "\n")
        f.write(" Projects: " + str(len(mctxt.subcontexts)) + "\n")
        for note in mctxt.annotations:
            f.write("  - " + str(note) + "\n")
        for work in mctxt.worklist:
            f.write("    Work : " + stateName(work.status) + "\n")
            if isinstance(work,CommandWorkItem):
                f.write("    Work Name : " + work.command.name + "\n")
                f.write("    Work Cmd  : " + work.command.formatCommandLine() + "\n")
                if work.command.cwd:
                    f.write("    Work Cwd  : " + work.command.cwd + "\n")
                f.write("    Work Exit : " + str(work.result.exit_code) + "\n")
        
        for pctxt in mctxt:
            pname=pctxt.name
            if projectList and not pctxt.project in projectList: continue
            
            f.write("  Project [" + pname + "] Status: " + stateName(pctxt.status) + "\n")
            f.write("   Work [" + str(len(pctxt.worklist)) + "] [" + str(pctxt.elapsedSecs()) + "] secs."  + "\n")
            for note in pctxt.annotations:
                f.write("   - " + str(note) + "\n")
            for work in pctxt.worklist:
                f.write("    Work : " + stateName(work.status) + "\n")
                if isinstance(work,CommandWorkItem):
                    f.write("    Work Name : " + work.command.name + "\n")
                    f.write("    Work Cmd  : " + work.command.formatCommandLine() + "\n")
                    if work.command.cwd:
                        f.write("    Work Cwd  : " + work.command.cwd + "\n")
                    f.write("    Work Exit : " + str(work.result.exit_code) + "\n")

def document(workspace,context):
    
    log.debug('--- Documenting Results')

    moduleList=context.gumpset.getModules()
    projectList=context.gumpset.getSequence()
    
    seedForrest(workspace,context)
    
    db=StatisticsDB()
  
    documentWorkspace(workspace,context,db,moduleList,projectList)
    
    if context.gumpset.isFull():
        documentStatistics(workspace,context,db,moduleList,projectList)
        documentXRef(workspace,context,moduleList,projectList)

    executeForrest(workspace,context)

#####################################################################
#
# Forresting...
def seedForrest(workspace,context):
    forrestTemplate=getForrestTemplateDir()    
    forrestSiteTemplate=getForrestSiteTemplateDir()    
    forrest=getForrestDir(workspace)    
    
    # :TODO: This gave an ugly tree (src/doc/cont../xdocs..)
    # with sub-directories. It is a nice idea, but not
    # quite there for us now, do a plain old template
    # copy instead.
    
    # First .. seed the project    
    #forrestSeed=Cmd('forrest','forrest_seed',forrest)
    #forrestSeed.addPrefixedParameter('-D','java.awt.headless','true','=')
    #forrestSeed.addParameter('seed')    
    #forrestSeedResult=execute(forrestSeed)
    # Consider adding, but a second seed might fail, need to ignore that...
    #work=CommandWorkItem(WORK_TYPE_DOCUMENT,forrest,forrestSeedResult)
    #context.performedWork(work)
    
    # Consider syncDirectories (to start with)
    # cp -Rf doesn't seem to be doing a nice job of overwritting :(
    # rsynch would disallow default/site though :(
    
    # Copy in the defaults
    forrestSeed=Cmd('cp','forrest_seed',forrest)
    forrestSeed.addParameter('-Rufv')
    forrestSeed.addParameter(forrestTemplate)    
    forrestSeed.addParameter(os.path.abspath(workspace.basedir))    
    forrestSeedResult=execute(forrestSeed)
    work=CommandWorkItem(WORK_TYPE_DOCUMENT,forrestSeed,forrestSeedResult)
    context.performedWork(work)
    
    # Copy over the local site defaults (if any)
    if os.path.exists(forrestSiteTemplate):
        forrestSiteSeed=Cmd('cp','forrest_site_seed',forrest)
        forrestSiteSeed.addParameter('-Rufv')
        forrestSiteSeed.addParameter(forrestSiteTemplate)    
        forrestSiteSeed.addParameter(workspace.basedir)  
        forrestSiteSeedResult=execute(forrestSiteSeed)
        work=CommandWorkItem(WORK_TYPE_DOCUMENT,forrestSiteSeed,forrestSiteSeedResult)
        context.performedWork(work)
   
     
def executeForrest(workspace,context):
    # The project tree
    forrest=getForrestDir(workspace)
    content=getContentDir(workspace,forrest)
    xdocs=getWorkspaceDir(workspace,content)        
    
    # Then generate...        
    forrest=Cmd('forrest','forrest',forrest)
  
    forrest.addPrefixedParameter('-D','java.awt.headless','true','=')
    #forrest.addPrefixedParameter('-D','project.content-dir',  \
    #    content, '=')    
    #forrest.addPrefixedParameter('-D','project.xdocs-dir',  \
    #    xdocs, '=')
        
    forrest.addPrefixedParameter('-D','project.site-dir',  \
        workspace.logdir, '=')
     
    #   
    # Do we just tweak forrest.properties?
    #
    #forrest.addPrefixedParameter('-D','project.sitemap-dir',  \
    #    docroot, '=')    
    #forrest.addPrefixedParameter('-D','project.stylesheets-dir',  \
    #    docroot, '=')    
    #forrest.addPrefixedParameter('-D','project.images-dir',  \
    #    docroot, '=')    

    #forrest.addPrefixedParameter('-D','project.skinconf', \
    #    getWorkspaceSiteDir(workspace), '=' )
      
    # Temporary
    # Too verbose ... forrest.addParameter('-debug')
    #forrest.addParameter('-verbose')
    
    # A sneak preview ... 
    work=CommandWorkItem(WORK_TYPE_DOCUMENT,forrest)
    context.performedWork(work)
    
    #
    # Do the actual work...
    #
    forrestResult=execute(forrest)

    # Update Context    
    work=CommandWorkItem(WORK_TYPE_DOCUMENT,forrest,forrestResult)
    context.performedWork(work)    
     
#####################################################################           
#
# Model Pieces
#      
def documentWorkspace(workspace,context,db,moduleList,projectList):
    
    sortedModuleList=OrderedList(moduleList)
    sortedProjectList=OrderedList(projectList)
    
    wdir=getWorkspaceDir(workspace)
    
    #
    # ----------------------------------------------------------------------
    #
    # Index.xml
    #
    
    x=startXDoc(getWorkspaceDocument(workspace,wdir))
    headerXDoc(x,'Workspace')    
        
    
    startSectionXDoc(x,'Workspace Definition')    
    startTableXDoc(x)       
    titledDataInTableXDoc(x,'Gump Version', setting.version)
    if workspace.description:
            titledDataInTableXDoc(x,'Description', workspace.description)
    if workspace.version: 
        titledDataInTableXDoc(x,'Workspace Version', workspace.version)
    if not workspace.version or not workspace.version == setting.ws_version:
        titledDataInTableXDoc(x,'Gump Preferred Workspace Version', setting.ws_version)
    titledDataInTableXDoc(x,'Java Command', context.javaCommand)
    titledDataInTableXDoc(x,'Python', str(sys.version))
    titledDataInTableXDoc(x,'@@DATE@@', str(default.date))
    titledDataInTableXDoc(x,'Start Date/Time', context.startdatetime)
    titledDataInTableXDoc(x,'Timezone', context.timezone)
    
    endTableXDoc(x)
    endSectionXDoc(x)                
    
    if not context.gumpset.isFull():
        note="""This output does not represent the a complete workspace,
        but a partial one.         
        Only projects, and their dependents, matching this regular expression """ + \
            "<strong>[" + context.gumpset.projectexpression + "]</strong>."
        
        note+="\n\nRequested Projects:\n"
        for project in context.gumpset.projects:
            note += project.name + " "
                        
        noteXDoc(x,note)
    
    documentSummary(x,context.getProjectSummary())
    
    documentAnnotations(x,context.annotations)
    
    startSectionXDoc(x,'Details')
    startTableXDoc(x,'Details')
    titledDataInTableXDoc(x,"Status : ", stateName(context.status))    
    (hours, mins, secs) 	= context.elapsedTime();
    titledDataInTableXDoc(x,"Elapsed Time : ", str(hours) + ':' + str(mins) + ':' + str(secs))
    titledDataInTableXDoc(x,"Base Directory : ", str(workspace.basedir))
    titledDataInTableXDoc(x,"Temporary Directory : ", str(workspace.tmpdir))
    if workspace.scratchdir:
        titledDataInTableXDoc(x,"Scratch Directory : ", str(workspace.scratchdir))    
    # :TODO: We have duplicate dirs? tmp = scratch?
    titledDataInTableXDoc(x,"Log Directory : ", str(workspace.logdir))
    titledDataInTableXDoc(x,"Jars Repository : ", str(workspace.jardir))
    titledDataInTableXDoc(x,"CVS Directory : ", str(workspace.cvsdir))
    titledDataInTableXDoc(x,"Package Directory : ", str(workspace.pkgdir))
    titledDataInTableXDoc(x,"List Address: ", str(workspace.mailinglist))
    titledDataInTableXDoc(x,"E-mail Address: ", str(workspace.email))
    titledDataInTableXDoc(x,"E-mail Server: ", str(workspace.mailserver))
    titledDataInTableXDoc(x,"Prefix: ", str(workspace.prefix))
    titledDataInTableXDoc(x,"Signature: ", str(workspace.signature))
    
    # Does this workspace send nag mails?
    if workspace.nag:
        nag='true'
    else:
        nag='false'
    titledDataInTableXDoc(x,"Send Nag E-mails: ", nag)
    endTableXDoc(x)
    endSectionXDoc(x)       
    
    x.write('<p><strong>Context Tree:</strong> <link href=\'context.html\'>context</link></p>')
    # x.write('<p><strong>Workspace Config:</strong> <link href=\'xml.txt\'>XML</link></p>')
    # x.write('<p><strong>RSS :</strong> <link href=\'index.rss\'>News Feed</link></p>')
    
    documentWorkList(x,workspace,context,context.worklist,'Workspace-level Work',wdir)
        
    footerXDoc(x)
    endXDoc(x)
 
    #
    # ----------------------------------------------------------------------
    #
    # buildLog.xml -- Projects in build order
    #
    x=startXDoc(getWorkspaceDocument(workspace,wdir,'buildLog'))      
    headerXDoc(x,'Project Build Log')
    
    documentSummary(x,context.getProjectSummary())
    
    startSectionXDoc(x,'Project in Build Order')
    startTableXDoc(x)
    x.write('     <tr>')        
    x.write('      <th>Name</th><th>Project State</th><th>Elapsed Time</th>')
    x.write('     </tr>')
    pcount=0
    for project in projectList:
        pctxt=context.getProjectContextForProject(project)
        pname=pctxt.name
        pcount+=1

        x.write('     <tr><!-- %s -->\n' % (pname))        
        x.write('      <td><link href=\'%s\'>%s</link></td><td>%s</td>\n' % \
                      (	getModuleProjectRelativeUrl(pctxt.parent.name, pname),	\
                        pname,	\
                        getStateIcon(pctxt)))    
        x.write('      <td>%s</td>\n' % elapsedTimeToString(pctxt.elapsedTime()))    
        x.write('     </tr>\n\n')
            
    if not pcount: x.write('	<tr><td>None</td></tr>')
    endTableXDoc(x)
    endSectionXDoc(x)    

    footerXDoc(x)
    endXDoc(x)
       
    #
    # ----------------------------------------------------------------------
    #
    # projects.xml -- Projects in build order
    #
    x=startXDoc(getWorkspaceDocument(workspace,wdir,'projects'))      
    headerXDoc(x,'All Projects')
    
    documentSummary(x,context.getProjectSummary())
    
    startSectionXDoc(x,'Project in Build Order')
    startTableXDoc(x)
    x.write('     <tr>')        
    x.write('      <th>Name</th><th>Project State</th><th>Elapsed Time</th>')
    x.write('     </tr>')
    pcount=0
    for project in sortedProjectList:
        pctxt=context.getProjectContextForProject(project)
        pname=pctxt.name
        pcount+=1

        x.write('     <tr><!-- %s -->\n' % (pname))        
        x.write('      <td><link href=\'%s\'>%s</link></td><td>%s</td>\n' % \
                      (	getModuleProjectRelativeUrl(pctxt.parent.name, pname),	\
                        pname,	\
                        getStateIcon(pctxt)))    
        x.write('      <td>%s</td>\n' % elapsedTimeToString(pctxt.elapsedTime()))    
        x.write('     </tr>\n\n')
            
    if not pcount: x.write('	<tr><td>None</td></tr>')
    endTableXDoc(x)
    endSectionXDoc(x)    

    footerXDoc(x)
    endXDoc(x)
       
    #
    # ----------------------------------------------------------------------
    #
    # project_todoss.xml -- Projects w/ issues in build order
    #
    x=startXDoc(getWorkspaceDocument(workspace,wdir,'project_todos'))      
    headerXDoc(x,'All Projects')
    
    documentSummary(x,context.getProjectSummary())
    
    startSectionXDoc(x,'Project in Build Order')
    startTableXDoc(x)
    x.write('     <tr>')        
    x.write('      <th>Name</th><th>Project State</th><th>Elapsed Time</th>')
    x.write('     </tr>')
    pcount=0
    for project in sortedProjectList:
        pctxt=context.getProjectContextForProject(project)
        pname=pctxt.name
        
        if not pctxt.status==STATUS_FAILED:
            continue
            
        pcount+=1

        x.write('     <tr><!-- %s -->\n' % (pname))        
        x.write('      <td><link href=\'%s\'>%s</link></td><td>%s</td>\n' % \
                      (	getModuleProjectRelativeUrl(pctxt.parent.name, pname),	\
                        pname,	\
                        getStateIcon(pctxt)))    
        x.write('      <td>%s</td>\n' % elapsedTimeToString(pctxt.elapsedTime()))    
        x.write('     </tr>\n\n')
            
    if not pcount: x.write('	<tr><td>None</td></tr>')
    endTableXDoc(x)
    endSectionXDoc(x)    

    footerXDoc(x)
    endXDoc(x)
       
    #
    # ----------------------------------------------------------------------
    #
    # module_todos.xml
    #
    x=startXDoc(getWorkspaceDocument(workspace,wdir,'module_todos'))    
    headerXDoc(x,'Modules with TODOs')    
    
    documentSummary(x,context.getProjectSummary())
    
    startSectionXDoc(x,'Modules with TODOs')
    startTableXDoc(x)
    x.write('     <tr>')        
    x.write('      <th>Name</th><th>Affects</th><th>Duration</th><th>Module State</th><th>Project State(s)</th><th>Elapsed Time</th>')
    x.write('     </tr>')
    mcount=0
    for mctxt in context:
        mname=mctxt.name
        if not Module.list.has_key(mname): continue        
        if moduleList and not mctxt.module in moduleList: continue
        
        #
        # Determine if there are todos, otherwise continue
        #
        todos=0
        for pair in mctxt.aggregateStates():
            if pair.status==STATUS_FAILED:
                todos=1
                
        if not todos: continue

        # Shown something...
        mcount+=1
        
        # Determine longest sequence in this (failed) state...
        # for any of the projects
        seq=0
        for pctxt in mctxt:
            if pctxt.status==STATUS_FAILED:
                # Note: Leverages previous extraction from project statistics DB
                if not hasattr(pctxt,'stats'):
                    # Extract from project statistics DB
                    stats=db.getProjectStats(pctxt.name)
                    pctxt.stats=stats
                stats=pctxt.stats
    
                if stats.sequenceInState > seq: seq = stats.sequenceInState

        #
        # Determine the number of projects this module (or it's projects)
        # cause not to be run.
        #
        affected=mctxt.determineAffected()
        
        # Display
        x.write('     <tr><!-- %s -->\n' % (mname))        
        x.write('      <td><link href=\'%s\'>%s</link></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>\n' % \
          (getModuleRelativeUrl(mname),mname,	\
              affected, \
              seq, \
              getStateIcon(mctxt),	\
              getStateIcons(mctxt)))    
        x.write('      <td>%s</td>\n' % elapsedTimeToString(mctxt.elapsedTime()))    
        x.write('     </tr>\n\n')
    if not mcount: x.write('	<tr><td>None</td></tr>')
    endTableXDoc(x)
    endSectionXDoc(x)
    
    footerXDoc(x)
    endXDoc(x)
    
    #
    # ----------------------------------------------------------------------
    #
    # Modules.xml
    #
    x=startXDoc(getWorkspaceDocument(workspace,wdir,'modules'))      
    headerXDoc(x,'All Modules')
    
    documentSummary(x,context.getProjectSummary())
    
    startSectionXDoc(x,'All Modules')
    startTableXDoc(x)
    x.write('     <tr>')        
    x.write('      <th>Name</th><th>Module State</th><th>Project State(s)</th><th>Elapsed Time</th>')
    x.write('     </tr>')
    mcount=0
    for mctxt in context:
        mname=mctxt.name
        if not Module.list.has_key(mname): 
            log.warn("Unknown module : " + mname)
            continue        
        if moduleList and not mctxt.module in moduleList: 
            log.info("Module filtered out: " + mname)
            continue
        mcount+=1

        x.write('     <tr><!-- %s -->\n' % (mname))        
        x.write('      <td><link href=\'%s\'>%s</link></td><td>%s</td><td>%s</td>\n' % \
          (getModuleRelativeUrl(mname),mname,\
              getStateIcon(mctxt),	\
              getStateIcons(mctxt)))    
        x.write('      <td>%s</td>\n' % elapsedTimeToString(mctxt.elapsedTime()))    
        x.write('     </tr>\n\n')
    if not mcount: x.write('	<tr><td>None</td></tr>')
    endTableXDoc(x)
    endSectionXDoc(x)
    
    footerXDoc(x)
    endXDoc(x)
   
    #
    # ----------------------------------------------------------------------
    #
    # Packages.xml
    #
    x=startXDoc(getWorkspaceDocument(workspace,wdir,'packages'))     
    headerXDoc(x,'Packages')
    
    startSectionXDoc(x,'Packaged Modules')
    startTableXDoc(x)
    x.write('     <tr>')        
    x.write('      <th>Name</th><th>Project State(s)</th><th>Elapsed Time</th>')
    x.write('     </tr>')
    mcount=0
    for mctxt in context:
        mname=mctxt.name
        if not Module.list.has_key(mname): continue        
        if moduleList and not mctxt.module in moduleList: continue
        
        packaged=0
        #
        # Determine if there are todos, otherwise continue
        #
        if mctxt.status==STATUS_COMPLETE and mctxt.reason==REASON_PACKAGE:
            packaged=1
                
        if not packaged: continue
    
        mcount+=1

        x.write('     <tr><!-- %s -->\n' % (mname))        
        x.write('      <td><link href=\'%s\'>%s</link></td><td>%s</td>\n' % \
          (getModuleRelativeUrl(mname),mname,getStateIcons(mctxt)))    
        x.write('      <td>%s</td>\n' % elapsedTimeToString(mctxt.elapsedTime()))    
        x.write('     </tr>\n\n')
    if not mcount: x.write('	<tr><td>None</td></tr>')
    endTableXDoc(x)
    endSectionXDoc(x)
    
    startSectionXDoc(x,'Packaged Projects')
    packages=getPackagedProjectContexts(context)
    if packages:
        startTableXDoc(x)
        x.write('      <tr><th>Name</th><th>State</th><th>State</th><th>Location</th></tr>')
        for pctxt in packages:
            x.write('     <tr><!-- %s -->' % (pctxt.name))        
            x.write('      <td>%s</td>' % getContextLink(pctxt,0))   
            x.write('      <td>%s</td>' % getContextStateDescription(pctxt))
            x.write('      <td>%s</td>' % getStatePairIcon(pctxt.getStatePair()))            
            x.write('      <td>%s</td>' % pctxt.project.home)    
            x.write('     </tr>')
        endTableXDoc(x)
    else:
        x.write('<p><strong>No packaged projects installed.</strong></p>')   
    endSectionXDoc(x)
      
    footerXDoc(x)
    endXDoc(x)
    
    #
    # Document modules
    #
    for mctxt in context:
        mname=mctxt.name    
        if not Module.list.has_key(mname): continue        
        if moduleList and not mctxt.module in moduleList: continue    
        documentModule(workspace,context,wdir,mctxt.name,mctxt,db,projectList)
        
    # Document context
    x=startXDoc(getWorkspaceContextDocument(workspace,wdir))
    headerXDoc(x,'Context')    
    x.write('<source>\n')
    documentTextToFile(x,workspace,context)    
    x.write('</source>\n')   
    footerXDoc(x)
    endXDoc(x)
        
    # Document the workspace XML    
    f=open(getWorkspaceXMLAsTextDocument(workspace), 'w')
    xml = xmlize('workspace',workspace,f)
    f.close()  
    
def getStateIcons(modulecontext):
    icons=''
    for projectcontext in modulecontext:
        # :TODO: Dig in and get the first 'failed' 
        # launched task to use as link
        href=getStateIcon(projectcontext)
        icons+=href+' '
    return icons
    
def getStateIcon(context):
    icon=getStatePairIcon(context.getStatePair())
    href=getContextStateLink(context,0,icon)
    return href
    
def documentModule(workspace,context,wdir,modulename,modulecontext,db,projectList):
    mdir=getModuleDir(workspace,modulename,wdir)
    
    if not Module.list.has_key(modulename): return
    
    module=Module.list[modulename]
    x=startXDoc(getModuleDocument(workspace,modulename,mdir))
    headerXDoc(x,'Module : ' + modulename)
        
    
    # Provide a description/link back to the module site.
    startSectionXDoc(x,'Description') 
    description=escape(str(module.description))
    if not description.strip().endswith('.'):
        description+='. '    
    if not description:
        description='No description provided.'        
    if module.url:
        description+=' For more information, see: ' + getFork(module.url.href)
    else:
        description+=' (No module URL provided).'
            
    xparagraphXDoc(x,description)
    endSectionXDoc(x)
    
    documentSummary(x,modulecontext.getProjectSummary())
        
    documentAnnotations(x,modulecontext.annotations)
    
      
    startSectionXDoc(x,'Projects with TODOs')
    x.write('    <table>\n')
    x.write('     <tr>')        
    x.write('      <th>Name</th><th>State</th><th>Elapsed Time</th>')
    x.write('     </tr>')
    pcount=0
    for pctxt in modulecontext:     
        if projectList and not pctxt.project in projectList: continue  
        pname=pctxt.name   
        
        #
        # Determine if there are todos, otherwise continue
        #
        todos=0
        for pair in pctxt.aggregateStates():
            if pair.status==STATUS_FAILED:
                todos=1
                
        if not todos: continue
         
        pcount+=1
        
        x.write('     <tr><!-- %s -->' % (pname))        
        x.write('      <td><link href=\'%s\'>%s</link></td><td>%s</td>' % \
          (getProjectRelativeUrl(pname),pname,getStatePairIcon(pctxt.getStatePair(),1)))    
        x.write('      <td>%s</td>' % elapsedTimeToString(pctxt.elapsedTime()))    
        x.write('     </tr>')
        
    if not pcount: x.write('	<tr><td>None</td></tr>')
    x.write('    </table>\n')
    endSectionXDoc(x)        
    
    startSectionXDoc(x,'All Projects')
    x.write('    <table>\n')
    x.write('     <tr>')        
    x.write('      <th>Name</th><th>State</th><th>Elapsed Time</th>')
    x.write('     </tr>')
    pcount=0
    for pctxt in modulecontext:     
        if projectList and not pctxt.project in projectList: continue  
        pname=pctxt.name    
        pcount+=1
        
        x.write('     <tr><!-- %s -->' % (pname))        
        x.write('      <td><link href=\'%s\'>%s</link></td><td>%s</td>' % \
          (getProjectRelativeUrl(pname),pname,getStatePairIcon(pctxt.getStatePair(),1)))    
        x.write('      <td>%s</td>' % elapsedTimeToString(pctxt.elapsedTime()))    
        x.write('     </tr>')
        
    if not pcount: x.write('	<tr><td>None</td></tr>')
    x.write('    </table>\n')
    endSectionXDoc(x)
    
    startSectionXDoc(x,'Module Details')
    startListXDoc(x)
    addItemXDoc(x,"Status: " + stateName(modulecontext.status))
    if not modulecontext.reason == REASON_UNSET:
        addItemXDoc(x,"Reason: " + reasonString(modulecontext.reason))
    if modulecontext.cause and not modulecontext==modulecontext.cause:
         addXItemXDoc(x, "Root Cause: ", getTypedContextLink(modulecontext.cause)) 
    if module.cvs.repository:
         addItemXDoc(x, "CVS Repository: ", module.cvs.repository) 
    if module.cvs.module:
         addItemXDoc(x, "CVS Module: ", module.cvs.module) 
    endListXDoc(x)
    endSectionXDoc(x)
       
#   x.write('<p><strong>Module Config :</strong> <link href=\'xml.html\'>XML</link></p>')
    
    documentWorkList(x,workspace,modulecontext,modulecontext.worklist,'Module-level Work',mdir)
    
    footerXDoc(x)
    endXDoc(x)
  
    # Document Projects
    for pctxt in modulecontext:
        if projectList and not pctxt.project in projectList: continue      
        documentProject(workspace,context,modulename,mdir,pctxt.name,pctxt,db)
   
    # Document the module XML
#    x=startXDoc(getModuleXMLDocument(workspace,modulename,mdir))
#    headerXDoc(x,'Module XML')    
#    x.write('<source>\n')
#    xf=StringIO.StringIO()
#    xml = xmlize('module',module,xf)
#    x.write(escape(xml))    
#    x.write('</source>\n')   
#    footerXDoc(x)
#    endXDoc(x)
    
def documentProject(workspace,context,modulename,mdir,projectname,projectcontext,db): 
    module=Module.list[modulename]
    project=Project.list[projectname]
    x=startXDoc(getProjectDocument(workspace,modulename,projectname,mdir))
    headerXDoc(x,'Project : ' + projectname)
   
     
    # Provide a description/link back to the module site.
    startSectionXDoc(x,'Description') 
    description=escape(str(project.description) or str(module.description))
    if not description.strip().endswith('.'):
        description+='. '
    if not description:
        description='No description provided.'        
    if project.url:
        description+=' For more information, see: ' + getFork(project.url.href)
    else:        
        description=' (No project URL provided.)'   
            
    xparagraphXDoc(x,description)
    endSectionXDoc(x)

    documentAnnotations(x,projectcontext.annotations)
    
    # Note: Leverages previous extraction from project statistics DB
    if not hasattr(projectcontext,'stats'):
        # Extract from project statistics DB
        stats=db.getProjectStats(projectname)
        projectcontext.stats=stats
    stats=projectcontext.stats
    
    startSectionXDoc(x,'Details')
    startListXDoc(x)
    addItemXDoc(x,"Status: ", stateName(projectcontext.status))  
    if not projectcontext.reason == REASON_UNSET:
        addItemXDoc(x,"Reason: " + reasonString(projectcontext.reason))
    addXItemXDoc(x,"Module: ", getContextLink(projectcontext.parent))
    if projectcontext.cause and not projectcontext==projectcontext.cause:
        addXItemXDoc(x,"Root Cause: ", getTypedContextLink(projectcontext.cause))
    addItemXDoc(x,"Elapsed: ", str(projectcontext.elapsedSecs()))
    addItemXDoc(x,"FOG Factor: ", str(round(stats.getFOGFactor(),2)))
    addItemXDoc(x,"Successes: ", str(stats.successes))
    addItemXDoc(x,"Failures: ", str(stats.failures))
    addItemXDoc(x,"Prerequisite Failures: ", str(stats.prereqs))
    addItemXDoc(x,"Previous Status: ", stateName(stats.previousState))
    
    if stats.first:
        addItemXDoc(x,"First Success: ", secsToDate(stats.first))
    if stats.last:
        addItemXDoc(x,"Last Success: ", secsToDate(stats.last))
        
    # Display nag information
    for nagEntry in project.nag:
        toaddr=getattr(nagEntry,'to') or workspace.mailinglist
        fromaddr=getStringFromUnicode(getattr(nagEntry,'from') or workspace.email)
        addItemXDoc(x,"Nag To: ", toaddr)
        addItemXDoc(x,"Nag From: ", fromaddr)     
        
    endListXDoc(x)
        
    endSectionXDoc(x)
    
    documentProjectContextList(x,"Project Dependencies",projectcontext.depends)    
    documentProjectContextList(x,"Optional Project Dependencies",projectcontext.options)                      
    documentProjectContextList(x,"Project Dependees",projectcontext.dependees)            
    documentProjectContextList(x,"Optional Project Dependees",projectcontext.optionees)                  

    if hasBuildCommand(project):
        (classpath,bootclasspath)=getClasspathLists(project,workspace,context)            
        displayClasspath(x,classpath,'Classpath',context)        
        displayClasspath(x,bootclasspath,'Boot Classpath',context)    
       
#    x.write('<p><strong>Project Config :</strong> <link href=\'%s\'>XML</link></p>' \
#                % (getModuleProjectRelativeUrl(modulename,projectcontext.name)) )
        
    documentWorkList(x,workspace,projectcontext,projectcontext.worklist,'Project-level Work',mdir)
    footerXDoc(x)
    endXDoc(x)    
    
    # Document the project XML
#    x=startXDoc(getProjectXMLDocument(workspace,modulename,projectcontext.name))
#    headerXDoc(x,'Project XML')    
#    x.write('<source>\n')
#    xf=StringIO.StringIO()
#    xml = xmlize('project',project,xf)
#    x.write(escape(xml))    
#    x.write('</source>\n')   
#    footerXDoc(x)
#    endXDoc(x)

def displayClasspath(x,classpath,title,context):
     
    startSectionXDoc(x,title)
    startTableXDoc(x)
    
    x.write('      <tr><th>Path Entry</th><th>Contributor</th><th>Instigator</th><th>Annotation</th></tr>')       
    paths=0
    for path in classpath: 
        if isinstance(path,AnnotatedPath):
            pcontext=path.context
            ppcontext=path.pcontext
            note=path.note
        else:
            pcontext=context
            ppcontext=None
            note=''
        
        startTableRowXDoc(x)
        insertTableDataXDoc(x, path)
        
        # Contributor
        insertTableDataXDoc(x, getContextLink(pcontext))
        
        # Instigator (if not Gump)
        link=''
        if ppcontext: link=getContextLink(ppcontext)
        insertTableDataXDoc(x, link)
        
        # Additional Notes...
        insertTableDataXDoc(x, note)
        endTableRowXDoc(x)
        paths+=1

    if not paths:        
        startTableRowXDoc(x)    
        insertTableDataXDoc(x,'No ' + title + ' entries')
        endTableRowXDoc(x)
   
    endTableXDoc(x)
    endSectionXDoc(x)
                 
def documentProjectContextList(x,title,projects):
  if projects:
        startSectionXDoc(x,title)
        startTableXDoc(x)
        x.write('      <tr><th>Name</th><th>Status</th></tr>')
        for pctxt in projects:
            startTableRowXDoc(x)    
            insertTableDataXDoc(x,getContextLink(pctxt))
            insertTableDataXDoc(x,getContextStateDescription(pctxt))
            endTableRowXDoc(x)
        endTableXDoc(x)
        endSectionXDoc(x)
            
def documentAnnotations(x,annotations):
    if not annotations: return
    startSectionXDoc(x,'Annotations')
    x.write('    <table>\n')
    for note in annotations:      
        x.write('      <tr><td>%s</td><td>%s</td></tr>' % \
          (levelName(note.level), note.text)) 
    x.write('    </table>\n')
    endSectionXDoc(x)
        
def documentSummary(x,summary,description='Project Summary'):
    if not summary or not summary.projects: return
    startSectionXDoc(x,description)
    startTableXDoc(x)
    
    startTableRowXDoc(x)        
    insertTableHeaderXDoc(x, 'Projects')
    insertTableHeaderXDoc(x, 'Successes')
    insertTableHeaderXDoc(x, 'Failures')
    insertTableHeaderXDoc(x, 'Prereqs')
    insertTableHeaderXDoc(x, 'No Works')
    insertTableHeaderXDoc(x, 'Packages')
    if summary.others:
        insertTableHeaderXDoc(x, 'Others')
    endTableRowXDoc(x)
    
    startTableRowXDoc(x)        
    insertTableDataXDoc(x, summary.projects)
    insertTableDataXDoc(x, summary.successes)
    insertTableDataXDoc(x, summary.failures)
    insertTableDataXDoc(x, summary.prereqs)
    insertTableDataXDoc(x, summary.noworks)
    insertTableDataXDoc(x, summary.packages)
    if summary.others:
        insertTableDataXDoc(x, summary.others)
    endTableRowXDoc(x)
       
    endTableXDoc(x) 
    endSectionXDoc(x)
  
def documentWorkList(x,workspace,workcontext,worklist,description='Work',dir='.'):
    if not worklist: return
    startSectionXDoc(x,description)
    
    x.write('    <table>\n')
    x.write('      <tr><th>Name</th><th>Type</th><th>State</th><th>Start Time</th><th>Elapsed Time</th></tr>')
    for work in worklist:
        x.write('     <tr><!-- %s -->' % (workTypeName(work.type)))       
        x.write('      <td><link href=\'%s\'>%s</link></td>' % \
            (getWorkRelativeUrl(work.type,work.command.name),work.command.name))    
        x.write('      <td>%s</td>' % (workTypeName(work.type))) 
        x.write('      <td>%s</td><td>%s</td><td>%s</td>' \
            % ( stateName(work.status), \
                secsToDate(work.result.start_time), \
                secsToString(work.secs)))    
        x.write('     </tr>')
    x.write('    </table>\n')
    
    #
    # Do a tail on all work that failed...
    #
    for work in worklist:
        if isinstance(work,CommandWorkItem):      
            if not STATUS_SUCCESS == work.status:
                tail=work.tail()
                if tail:
                    #
                    # Write out the 'tail'
                    #
                    startSectionXDoc(x,workTypeName(work.type))
                    sourceXDoc(x,tail)
                    endSectionXDoc(x)
            
    endSectionXDoc(x)
    
    for work in worklist:
        documentWork(workspace,workcontext,work,dir)
        
def documentWork(workspace,workcontext,work,dir,depth=2):
    if isinstance(work,CommandWorkItem):    
        x=startXDoc(getWorkDocument(dir,work.command.name,work.type))
        headerXDoc(x, workTypeName(work.type) + ' : ' + work.command.name)
        startSectionXDoc(x,'Details')
        
        startListXDoc(x) 
        addItemXDoc(x,"Status: ", stateName(work.status))
        addXItemXDoc(x,"For: ", getTypedContextLink(workcontext,depth))
        # addItemXDoc(x,"Command: ", work.command.name)
        if work.command.cwd:
            addItemXDoc(x,"Working Directory: ", work.command.cwd)
        if work.result.output:
            addItemXDoc(x,"Output: ", work.result.output)
        else:
            addItemXDoc(x,"Output: None")
            
        if work.result.signal:
            addItemXDoc(x,"Termination Signal: ", str(work.result.signal))
        addItemXDoc(x,"Exit Code: ", str(work.result.exit_code))
                
        
        addItemXDoc(x,"Start Time: ", secsToDate(work.result.start_time))
        addItemXDoc(x,"End Time: ", secsToDate(work.result.end_time))
        addItemXDoc(x,"Elapsed Time: ", secsToString(work.secs))
        
        endListXDoc(x)
        endSectionXDoc(x)
       
        #
        # Show parameters
        #
        if work.command.params:
            title='Parameter'
            if len(work.command.params.items()) > 1:
                title += 's'
            startSectionXDoc(x,title)    
            x.write('<table><tr><th>Prefix</th><th>Name</th><th>Value</th></tr>')
            for param in work.command.params.items():
                x.write('<tr><td>')
                if param.prefix: 
                    x.write(param.prefix)
                x.write('</td><td>')
                x.write(param.name)
                x.write('</td><td>')
                val = param.value
                # :TODO: Hack for BOOTCLASSPATH
                if param.name.startswith('bootclasspath'):
                   val=':\n'.join(val.split(':'))
                if val:
                    x.write(val)
                else:
                    x.write('N/A')
                x.write('</td></tr>\n')  
                    
            x.write('</table>\n')
            endSectionXDoc(x)
                
        #
        # Show ENV overrides
        #
        if work.command.env:
            startSectionXDoc(x,'Environment Overrides')    
            x.write('<table><tr><th>Name</th><th>Value</th></tr>')
            for (name, value) in work.command.env.iteritems():
                x.write('<tr><td>')
                x.write(name)
                x.write('</td><td>')
                if value:
                    # :TODO: Hack for CLASSPATH
                    if name == "CLASSPATH":
                        value=':\n'.join(value.split(':'))
                    x.write(escape(value))
                else:
                    x.write('N/A')
                x.write('</td></tr>\n')        
            x.write('</table>\n')
            endSectionXDoc(x)
        
        #
        # Wrap the command line..
        #
        parts=work.command.formatCommandLine().split(' ')
        line=''
        commandLine=''
        for part in parts:
            if (len(line) + len(part)) > 80:
                commandLine += line
                commandLine += '\n        '
                line=part
            else:
                if line: line+=' '
                line+=part
        if line:
            commandLine += line
        
        #
        # Show the wrapped command line
        #
        startSectionXDoc(x,'Command Line')
        sourceXDoc(x,commandLine)
        endSectionXDoc(x)
        
        #
        # Show the content...
        #
        startSectionXDoc(x,'Output')
        output=work.result.output
        x.write('<source>')
        if output:
            try:
                try:
                    # Keep a length count to not exceed 32K
                    size=0
                    o=open(output, 'r')
                    line=o.readline()
                    while line:
                        length = len(line)
                        size += length
                        # Crude to 'ensure' that escaped
                        # it doesn't exceed 32K.
                        if size > 20000:
                            x.write('</source>')
                            x.write('<p>Continuation...</p>')
                            x.write('<source>')
                            size = length
                        x.write(escape(line))                
                        line=o.readline()
                finally:
                    if o: o.close()
            except:
                x.write('Failed to copy contents from :' + output)
        else:
            x.write('No output to stdout/stderr from this command.')
        x.write('</source>\n')
        
      
        endSectionXDoc(x)
        footerXDoc(x)
        endXDoc(x)
        
#####################################################################           
#
# Statistics Pages
#           
def documentStatistics(workspace,context,db,moduleList,projectList):
    
    stats=StatisticsGuru(workspace,context,db)
    
    sdir=getStatisticsDir(workspace)
    x=startXDoc(getStatisticsDocument(workspace,sdir))
    headerXDoc(x,'Statistics')
    
    startSectionXDoc(x,'Overview')
    startListXDoc(x)
    addItemXDoc(x,'Modules: ', stats.wguru.modulesInWorkspace)
    addItemXDoc(x,'Projects: ', stats.wguru.projectsInWorkspace)
    addItemXDoc(x,'Avg Projects Per Module: ', stats.wguru.averageProjectsPerModule)
    endListXDoc(x)
    endSectionXDoc(x)    
    
    footerXDoc(x) 
    endXDoc(x)
    
    documentModulesByElapsed(stats, sdir, moduleList)
    documentModulesByProjects(stats, sdir, moduleList)
    documentModulesByDependencies(stats, sdir, moduleList)
    documentModulesByDependees(stats, sdir, moduleList)
    documentModulesByFOGFactor(stats, sdir, moduleList)
    

def documentModulesByElapsed(stats,sdir,moduleList):
    x=startXDoc(os.path.join(sdir,'elapsed.xml'))
    headerXDoc(x, 'Modules By Elapsed Time')
    
    startTableXDoc(x,'Modules By Elapsed')
    for mctxt in stats.modulesByElapsed:        
        if moduleList and not mctxt.module in moduleList: continue
        titledXDataInTableXDoc(x,getContextLink(mctxt), elapsedTimeToString(mctxt.elapsedTime()))

    endTableXDoc(x)
    
    footerXDoc(x)
    endXDoc(x)

def documentModulesByProjects(stats,sdir,moduleList):
    x=startXDoc(os.path.join(sdir,'projects.xml'))
    headerXDoc(x, 'Modules By Project Count')
    
    startTableXDoc(x,'Modules By Project Count')
    for mctxt in stats.modulesByProjectCount:        
        if moduleList and not mctxt.module in moduleList: continue    
        startTableRowXDoc(x)
        
        insertTableDataXDoc(x, getContextLink(mctxt))
        insertTableDataXDoc(x,len(mctxt.subcontexts))
        
        projectsString=''
        for pctxt in mctxt.subcontexts.values():
            projectsString+=getContextLink(pctxt)
            projectsString+=' '            
        insertTableDataXDoc(x, projectsString)
        
        endTableRowXDoc(x)
    endTableXDoc(x)
    
    footerXDoc(x)
    endXDoc(x)
 
def documentModulesByDependencies(stats,sdir,moduleList):
    x=startXDoc(os.path.join(sdir,'dependencies.xml'))
    headerXDoc(x, 'Modules By Dependency Count')
    
    startTableXDoc(x,'Modules By Dependency Count')
    for mctxt in stats.modulesByTotalDependencies:        
        if moduleList and not mctxt.module in moduleList: continue    
        startTableRowXDoc(x)
        insertTableDataXDoc(x, getContextLink(mctxt))
        insertTableDataXDoc(x, mctxt.dependencyCount())
        
        projectsString=''
        for pctxt in mctxt.getDepends():
            projectsString+=getContextLink(pctxt)
            projectsString+=' '            
        insertTableDataXDoc(x, projectsString)
       
        endTableRowXDoc(x)
    endTableXDoc(x)
    
    footerXDoc(x)
    endXDoc(x)
    
 
 
def documentModulesByDependees(stats,sdir,moduleList):
    x=startXDoc(os.path.join(sdir,'dependees.xml'))
    headerXDoc(x, 'Modules By Dependee Count')
    
    startTableXDoc(x,'Modules By Dependee Count')
    for mctxt in stats.modulesByTotalDependees:        
        if moduleList and not mctxt.module in moduleList: continue    
        startTableRowXDoc(x)
        insertTableDataXDoc(x, getContextLink(mctxt))
        insertTableDataXDoc(x, mctxt.dependeeCount())
        
        projectsString=''
        for pctxt in mctxt.getDependees():
            projectsString+=getContextLink(pctxt)
            projectsString+=' '            
        insertTableDataXDoc(x, projectsString)
        
        endTableRowXDoc(x)
    endTableXDoc(x)
    
    footerXDoc(x)
    endXDoc(x)
    
def documentModulesByFOGFactor(stats,sdir,moduleList):
    x=startXDoc(os.path.join(sdir,'fogfactor.xml'))
    headerXDoc(x, 'Modules By FOG Factor')
    
    startTableXDoc(x,'Modules By FOG Factor')
    for mctxt in stats.modulesByFOGFactor:        
        if moduleList and not mctxt.module in moduleList: continue    
        startTableRowXDoc(x)
        insertTableDataXDoc(x,getContextLink(mctxt))
        insertTableDataXDoc(x, str(round(mctxt.getFOGFactor(),2)))
        
        projectsString=''
        for pctxt in mctxt:
            projectsString+=getContextLink(pctxt)
            projectsString+='='            
            projectsString+=str(round(pctxt.getFOGFactor(),2))
            projectsString+='  '            
        insertTableDataXDoc(x, projectsString)
        
        endTableRowXDoc(x)
    endTableXDoc(x)
    
    footerXDoc(x)
    endXDoc(x)
    
#####################################################################           
#
# XRef Pages
#           
def documentXRef(workspace,context,moduleList,projectList):
    
    xdir=getXRefDir(workspace)
    x=startXDoc(getXRefDocument(workspace,xdir))
    headerXDoc(x,'Cross Reference')

    # :TODO: Packages and such...
    x.write('<p>To be completed...</p>')
   
    footerXDoc(x) 
    endXDoc(x)
    
 
#####################################################################           
#
# Helper Methods
#           
 
#def getWorkspaceSiteDir(workspace):
#    sdir=os.path.normpath(os.path.join(workspace.logdir,'site'))
#    if not os.path.exists(sdir): os.mkdir(sdir)
#    return sdir    
    
def getForrestTemplateDir():
    fdir=os.path.abspath(os.path.join(dir.template,'forrest'))
    return fdir  
    
def getForrestSiteTemplateDir():
    fdir=os.path.abspath(os.path.join(dir.template,'site-forrest'))
    return fdir  
      
def getForrestDir(workspace):
    fdir=os.path.abspath(os.path.join(workspace.basedir,'forrest'))
    if not os.path.exists(fdir): os.mkdir(fdir)
    return fdir  
    
def getContentDir(workspace,forrestdir=None):
    fdir=forrestdir or getForrestDir(workspace)
    sdir=os.path.abspath(os.path.join(fdir,'src'))
    if not os.path.exists(sdir): os.mkdir(sdir)
    ddir=os.path.abspath(os.path.join(sdir,'documentation'))
    if not os.path.exists(ddir): os.mkdir(ddir)
    cdir=os.path.abspath(os.path.join(ddir,'content'))
    if not os.path.exists(cdir): os.mkdir(cdir)
    return cdir  
    
def getWorkspaceDir(workspace,contentdir=None):
    cdir = contentdir or getContentDir(workspace)
    xdir=os.path.abspath(os.path.join(getContentDir(workspace),'xdocs'))
    if not os.path.exists(xdir): os.mkdir(xdir)
    return xdir  
    
def getStatisticsDir(workspace,workspacedir=None):
    wdir=workspacedir or getWorkspaceDir(workspace)
    sdir=os.path.abspath(os.path.join(wdir,'gump_stats'))
    if not os.path.exists(sdir): os.mkdir(sdir)
    return sdir
    
def getXRefDir(workspace,workspacedir=None):
    wdir=workspacedir or getWorkspaceDir(workspace)
    xdir=os.path.abspath(os.path.join(wdir,'xref'))
    if not os.path.exists(xdir): os.mkdir(xdir)
    return xdir
    
def getModuleDir(workspace,modulename,workspacedir=None):
    mdir=gumpSafeName(modulename)
    if not workspacedir: workspacedir = getWorkspaceDir(workspace)
    xdir=os.path.abspath(os.path.join(workspacedir,mdir))
    if not os.path.exists(xdir): os.mkdir(xdir)
    return xdir

def getWorkDir(rootdir,type):
    tdir=gumpSafeName(lower(workTypeName(type)))
    wdir=os.path.abspath(os.path.join(rootdir,tdir))
    if not os.path.exists(wdir): os.mkdir(wdir)
    return wdir    
 
def getWorkspaceDocument(workspace,workspacedir=None,document=None):
    if not document: document='index.xml'
    if not document.endswith('.xml'): document += '.xml'
    if not workspacedir: workspacedir = getWorkspaceDir(workspace)    
    return os.path.join(workspacedir,document)
    
def getWorkspaceContextDocument(workspace,workspacedir=None):
    if not workspacedir: workspacedir = getWorkspaceDir(workspace)    
    return os.path.join(workspacedir,'context.xml')
    
    
# Couldn't cope w/ log4j nagger's name characterset, so bailed
# and went to text...
def getWorkspaceXMLAsTextDocument(workspace,contentdir=None):
    if not contentdir: contentdir = getContentDir(workspace)    
    return os.path.join(contentdir,'xml.txt')
    
def getStatisticsDocument(workspace,statsdir=None):
    if not statsdir: statsdir = getStatisticsDir(workspace)    
    return os.path.join(statsdir,'index.xml')
    
def getXRefDocument(workspace,xrefdir=None):
    if not xrefdir: xrefdir = getXRefDir(workspace)    
    return os.path.join(xrefdir,'index.xml')
    
def getModuleDocument(workspace, modulename,moduledir=None):
    mdir=gumpSafeName(modulename)
    if not moduledir: moduledir=getModuleDir(workspace, modulename)
    return os.path.join(moduledir,'index.xml')

def getModuleXMLDocument(workspace, modulename,moduledir=None):
    mdir=gumpSafeName(modulename)
    if not moduledir: moduledir=getModuleDir(workspace, modulename)
    return os.path.join(moduledir,'xml.xml')

def getProjectDocument(workspace,modulename,projectname,moduledir=None):
    pname=gumpSafeName(projectname)
    if not moduledir: moduledir=getModuleDir(workspace, modulename)
    return os.path.join(moduledir,pname+'.xml')
    
def getProjectXMLDocument(workspace,modulename,projectname,moduledir=None):
    pname=gumpSafeName(projectname)
    if not moduledir: moduledir=getModuleDir(workspace, modulename)
    return os.path.join(moduledir,pname+'_xml.xml')

def getWorkDocument(rootdir,name,type,wdir=None):
    wname=gumpSafeName(name)
    if not wdir: wdir=getWorkDir(rootdir,type)
    return os.path.join(wdir,wname+'.xml')
    
def getContextAbsoluteUrl(root,context):
    url=root
    if not url.endswith('/'): url += '/'
    url += getContextUrl(context,0)
    return url
        
def getContextDirRelativeUrl(context,depth=1):
    if isinstance(context,GumpContext):
        url=getWorkspaceDirRelativeUrl(depth)
    elif isinstance(context,ModuleContext):
        url=getModuleDirRelativeUrl(context.name,depth)
    else:        
        url=getModuleDirRelativeUrl(context.parent.name,depth)
    return url
        
def getContextUrl(context,depth=1,state=0):
    url=None
    #
    # If we are looking for what set the state, look at
    # work first. Pick the first...
    #
    if state:
        for work in context.worklist:
            if not url:
                if not work.status==STATUS_SUCCESS:
                    url=getContextDirRelativeUrl(context,depth) 
                    url+=getWorkRelativeUrl(work.type,work.command.name)
        
    #
    # Otherwise return link to context...
    #     
    if not url:
        if isinstance(context,GumpContext):
            url=getWorkspaceRelativeUrl(depth)
        elif isinstance(context,ModuleContext):
            url=getModuleRelativeUrl(context.name,depth)
        else:        
            url=getModuleProjectRelativeUrl(context.parent.name,context.name,depth)
            
    return url

def getTypedContextLink(context,depth=1):
    return getContextLink(context,depth,None,1)

def getContextStateLink(context,depth=1,xdata=None,typed=0):
    return getContextLink(context,depth,xdata,typed,1)
    
def getContextLink(context,depth=1,xdata=None,typed=0,state=0):
    if not xdata:
        description=""
        if typed:
            if isinstance(context,GumpContext):
                description="Gump: "
            elif isinstance(context,ModuleContext):
                description="Module: "
            else:        
                description="Project: "
        description+=context.name
    
        return getLink(getContextUrl(context,depth,state),description)
    else:
        return getXLink(getContextUrl(context,depth,state),xdata)
    
def getContextStateDescription(context):
    xdoc=stateName(context.status)
    if not context.reason==REASON_UNSET: xdoc+=' with reason '+reasonString(context.reason)
    if context.cause and not context.cause == context:
        xdoc+=", caused by "
        xdoc+=getContextStateLink(context.cause)
    return xdoc

def getWorkspaceRelativeUrl(depth=0):
    return getWorkspaceDirRelativeUrl(depth)+'index.html'
    
def getWorkspaceDirRelativeUrl(depth=0):
    return getUp(depth)+'/'
    
def getWorkspaceRelativeUrlFromModule():
    return getWorkspaceRelativeUrl(1)
    
def getWorkspaceRelativeUrlFromProject():
    return getWorkspaceRelativeUrl(1)
    
def getModuleRelativeUrl(name,depth=0):
    return getModuleDirRelativeUrl(name,depth)+'index.html'
    
def getModuleDirRelativeUrl(name,depth=0):
    return getUp(depth)+gumpSafeName(name)+'/'
    
def getModuleRelativeUrlFromModule(name,depth=1):
    return getModuleRelativeUrl(name,depth)
    
def getModuleRelativeUrlFromProject(name,depth=1):
    return getModuleRelativeUrl(name,depth)

def getProjectRelativeUrl(name,depth=0):
    return getUp(depth)+gumpSafeName(name)+'.html'
    
def getModuleProjectRelativeUrl(mname,pname,depth=0):
    return getUp(depth)+gumpSafeName(mname)+'/'+gumpSafeName(pname)+'.html'
    
def getModuleProjectXMLRelativeUrl(mname,pname,depth=0):
    return getUp(depth)+gumpSafeName(mname)+'/'+gumpSafeName(pname)+'_xml.html'
    
def getModuleProjectRelativeUrlFromModule(mname,pname):
    return getProjectRelativeUrl(mname,pname,1)

def getModuleProjectRelativeUrlFromProject(mname,pname):
    return getProjectRelativeUrl(mname,pname,1)

def getWorkRelativeUrl(type,name):
    tdir=gumpSafeName(lower(workTypeName(type)))
    return tdir+'/'+gumpSafeName(name)+'.html'
    
def getStatePairIcon(pair,depth=0):

    sname=stateName(pair.status)
    rstring=reasonString(pair.reason)    
    
    description=sname    
    uniqueName=sname
    if not pair.reason==REASON_UNSET: 
        description+=' '+rstring
        # Not yet, just have a few icons ... uniqueName+='_'+rstring
    
    # Build the URL
    iconName=gumpSafeName(lower(replace(uniqueName,' ','_')))
    url = getUp(depth)+"gump_icons/"+iconName+".png";
    
    # Build the <icon xdoc
    return '<icon src=\'' + url + '\' alt=\'' + description +'\'/>'
    
def getUp(depth):
    url=''
    i = 0
    while i < int(depth):
        url+='../'
        i += 1
    return url
           
def getLink(href,name=None):
    if not name: name = href
    link='<link href=\'%s\'>%s</link>' % (escape(href),escape(name))
    return link
    
def getXLink(href,xdata=None):
    if not xdata: xdata = escape(href)
    link='<link href=\'%s\'>%s</link>' % (escape(href),xdata)
    return link

def getFork(href,name=None):
    if not name: name = href
    fork='<fork href=\'%s\'>%s</fork>' % (escape(href),escape(name))
    return fork
    
def getXFork(href,xdata=None):
    if not xdata: xdata = escape(href)
    fork='<fork href=\'%s\'>%s</fork>' % (escape(href),xdata)
    return fork
           
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
    f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
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
    f.write('    <p>%s</p>\n' % (escape(content)))
    
def xparagraphXDoc(f, content):
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
    
def titledDataInTableXDoc(f,title,data):
    startTableRowXDoc(f)
    insertTableDataXDoc(f,'<strong>%s</strong>' % (title))
    insertTableDataXDoc(f, escape(data))
    endTableRowXDoc(f)
    
def titledXDataInTableXDoc(f,title,data):
    startTableRowXDoc(f)
    insertTableDataXDoc(f, title)
    insertTableDataXDoc(f, escape(data))
    endTableRowXDoc(f)
    
def endTableXDoc(f):
    f.write('    </table>\n')
    
def startListXDoc(f, title=None):
    if title:
        paragraphXDoc(f,title)
    f.write('    <ul>\n');
    
def addItemXDoc(f,t,i=''):
    f.write('      <li><strong>%s</strong>%s</li>\n' % \
                (escape(str(t)),escape(str(i))))
    
def addXItemXDoc(f,t,i=None):
    if i:
        f.write('      <li><strong>%s</strong>%s</li>\n' % (t, i))    
    else:
        f.write('      <li>%s</li>\n' % (t))  
  
def endListXDoc(f ):
    f.write('    </ul>\n')
    
def insertXmlXDoc(f,nodename,nodexml):
    xmlize(nodename,nodexml,f)

def noteXDoc(f,text):
    f.write('<note>\n')
    f.write(text)
    f.write('</note>\n')   
      
def sourceXDoc(f,text):
    f.write('<source>\n')
    f.write(escape(text))
    f.write('</source>\n')                
    
    
          

# static void main()
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)
  
  args = handleArgv(sys.argv)
  ws=args[0]
  ps=args[1]

  context=GumpContext()
  
      
  # get parsed workspace definition
  from gump import load
  workspace=load(ws, context)

  #
  #from gump.check import checkEnvironment
  #checkEnvironment(workspace, context)
  
  #
  # Store for later
  #
  from gump.logic import GumpSet
  context.gumpset=GumpSet(ps)
    
  # Document
  document(workspace, context);
