#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/document/Attic/forrest.py,v 1.51 2004/01/12 23:47:58 ajack Exp $
# $Revision: 1.51 $f
# $Date: 2004/01/12 23:47:58 $
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

from gump import log
from gump.config import *
from gump.document.documenter import Documenter
from gump.document.text import TextDocumenter
from gump.document.xdoc import *
from gump.document.resolver import *
from gump.utils import *
from gump.utils.xmlutils import xmlize
from gump.model import *
from gump.model.project import AnnotatedPath,  ProjectStatistics
from gump.output.statsdb import StatisticsGuru
from gump.output.xref import XRefGuru
from gump.gumprun import *

def getUpUrl(depth):
    url=''
    i = 0
    while i < int(depth):
        url+='../'
        i += 1
    return url
    
class ForrestDocumenter(Documenter):
    
    def __init__(self, dirBase, urlBase):
        Documenter.__init__(self)            
        self.resolver=Resolver(dirBase,urlBase)
        
    def getResolverForRun(self,run):
        return self.resolver
    
    def documentRun(self, run):
    
        log.debug('--- Documenting Results')

        workspace=run.getWorkspace()
        gumpSet=run.getGumpSet()
    
        # Seed with default/site skins/etc.
        self.seedForrest(workspace)
       
        self.documentWorkspace(run,workspace,gumpSet)    
        self.documentStatistics(run,workspace,gumpSet)
        self.documentXRef(run,workspace,gumpSet)

        # Launch Forrest...
        self.executeForrest(workspace)

    #####################################################################
    #
    # Forresting...
    def getForrestParentDirectory(self,workspace):
        return workspace.getBaseDirectory()
        
    def getForrestDirectory(self,workspace):
        fdir=os.path.abspath(os.path.join(workspace.getBaseDirectory(),'forrest'))
        return fdir
        
    def getForrestTemplateDirectory(self):
        fdir=os.path.abspath(os.path.join(dir.template,'forrest'))
        return fdir  
        
    def getForrestSiteTemplateDirectory(self):
        fdir=os.path.abspath(os.path.join(dir.template,'site-forrest'))
        return fdir  
    
    def seedForrest(self,workspace):   
        
        forrestParentDir=self.getForrestParentDirectory(workspace)    
        
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
        #workspace.performedWork(work)
        
        # Consider syncDirectories (to start with)
        # cp -Rf doesn't seem to be doing a nice job of overwritting :(
        # rsynch would disallow default/site though :(
        
        # Copy in the defaults        
        forrestTemplate=self.getForrestTemplateDirectory()   
        
        forrestSeed=Cmd('cp','forrest_seed',forrestParentDir)
        forrestSeed.addParameter('-Rfv')
        forrestSeed.addParameter(forrestTemplate)    
        forrestSeed.addParameter(os.path.abspath(workspace.getBaseDirectory()))    
        forrestSeedResult=execute(forrestSeed)
        work=CommandWorkItem(WORK_TYPE_DOCUMENT,forrestSeed,forrestSeedResult)
        workspace.performedWork(work)
        
        # Copy over the local site defaults (if any)        
        forrestSiteTemplate=self.getForrestSiteTemplateDirectory()  
        if os.path.exists(forrestSiteTemplate):
            forrestSiteSeed=Cmd('cp','forrest_site_seed',forrestParentDir)
            forrestSiteSeed.addParameter('-Rfv')
            forrestSiteSeed.addParameter(forrestSiteTemplate)    
            forrestSiteSeed.addParameter(workspace.getBaseDirectory())  
            forrestSiteSeedResult=execute(forrestSiteSeed)
            work=CommandWorkItem(WORK_TYPE_DOCUMENT,forrestSiteSeed,forrestSiteSeedResult)
            workspace.performedWork(work)
             
         
    def executeForrest(self,workspace):
        # The project tree
        xdocs=self.resolver.getDirectory(workspace)      
        forrestDir=self.getForrestDirectory(workspace)      
        
        # Then generate...        
        forrest=Cmd('forrest','forrest',forrestDir)
      
        forrest.addPrefixedParameter('-D','java.awt.headless','true','=')
        #forrest.addPrefixedParameter('-D','project.content-dir',  \
        #    content, '=')    
        #forrest.addPrefixedParameter('-D','project.xdocs-dir',  \
        #    xdocs, '=')
            
        forrest.addPrefixedParameter('-D','project.site-dir',  \
            workspace.getLogDirectory(), '=')
         
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
        #    getWorkspaceSiteDirectory(workspace), '=' )
          
        # Temporary
        # Too verbose ... forrest.addParameter('-debug')
        #forrest.addParameter('-verbose')
        
        # A sneak preview ... 
        work=CommandWorkItem(WORK_TYPE_DOCUMENT,forrest)
        workspace.performedWork(work)
        
        #
        # Do the actual work...
        #
        forrestResult=execute(forrest)
    
        # Update Context    
        work=CommandWorkItem(WORK_TYPE_DOCUMENT,forrest,forrestResult)
        workspace.performedWork(work)    
         
    #####################################################################           
    #
    # Model Pieces
    #      
    def documentWorkspace(self,run,workspace,gumpSet):
        
        # Pretty sorting...
        sortedModuleList=createOrderedList(gumpSet.getModules())
        sortedProjectList=createOrderedList(gumpSet.getSequence())
        sortedRepositoryList=createOrderedList(gumpSet.getRepositories())
        
        #
        # ----------------------------------------------------------------------
        #
        # Index.xml
        #
        
        document=XDocDocument('Workspace',	\
                self.resolver.getFile(workspace))    
        
        document.createNote('This install runs Python Gump, not Traditional Gump.')  
                    
        definitionSection=document.createSection('Workspace Definition')    
        
        definitionTable=definitionSection.createTable()
        definitionTable.createEntry('Gump Version', setting.version)
        if workspace.xml.description:
                definitionTable.createEntry('Description', workspace.xml.description)
        if workspace.xml.version: 
            definitionTable.createEntry('Workspace Version', workspace.xml.version)
        if not workspace.xml.version or not workspace.xml.version == setting.ws_version:
            definitionTable.createEntry('Gump Preferred Workspace Version', setting.ws_version)
        definitionTable.createEntry('Java Command', workspace.javaCommand)
        definitionTable.createEntry('Python', str(sys.version))
        definitionTable.createEntry('Operating System (Name)', str(os.name))
        definitionTable.createEntry('@@DATE@@', str(default.date))
        definitionTable.createEntry('Start Date/Time', workspace.startdatetime)
        definitionTable.createEntry('Timezone', workspace.timezone)
        
        rssSyndRow=definitionTable.createRow()
        rssSyndRow.createData('Syndication')
        rssSyndRow.createData().createFork('index.rss','RSS')
        atomSyndRow=definitionTable.createRow()
        atomSyndRow.createData('Syndication')
        atomSyndRow.createData().createFork('index.atom','Atom')
                
        textRow=definitionTable.createRow()
        textRow.createData('Workspace Documentation')
        textRow.createData().createLink('context.html','Text')
                
        syndRow=definitionTable.createRow()
        syndRow.createData('Definition')
        syndRow.createData().createLink('workspace.html','XML')
                
        if not gumpSet.isFull():
            note=definitionSection.createNote()
            
            note.createText("""This output does not represent the a complete workspace,
            but a partial one.         
            Only projects, and their dependents, matching this regular expression """)
            note.createStrong(gumpSet.projectexpression)
            note.createBreak()
            note.createBreak()            
            note.createText('Requested Projects:')
            note.createBreak()
            for project in gumpSet.projects:
                note.createText(project.name)
                note.createText(' ')
                            
        
        self.documentSummary(document,workspace.getProjectSummary())        
        self.documentAnnotations(document,workspace)
        #self.documentXML(document,workspace)
        
        detailsSection=document.createSection('Details')
                    
        detailsTable=detailsSection.createTable()
        detailsTable.createEntry("State : ", workspace.getStateDescription()) 

        e = secsToElapsedString(workspace.getElapsedSecs())
        if e : detailsTable.createEntry("Elapsed Time : ", e)
        detailsTable.createEntry("Base Directory : ", workspace.getBaseDirectory())
        detailsTable.createEntry("Temporary Directory : ", workspace.tmpdir)
        #if workspace.scratchdir:
        #    detailsTable.createEntry("Scratch Directory : ", workspace.scratchdir))    
        # :TODO: We have duplicate dirs? tmp = scratch?
        detailsTable.createEntry("Log Directory : ", workspace.logdir)
        detailsTable.createEntry("Jars Repository : ", workspace.jardir)
        detailsTable.createEntry("CVS Directory : ", workspace.cvsdir)
        detailsTable.createEntry("Package Directory : ", workspace.pkgdir)
        detailsTable.createEntry("List Address: ", workspace.mailinglist)
        detailsTable.createEntry("E-mail Address: ", workspace.email)
        detailsTable.createEntry("E-mail Server: ", workspace.mailserver)
        detailsTable.createEntry("Prefix: ", workspace.prefix)
        detailsTable.createEntry("Signature: ", workspace.signature)
        
        self.documentProperties(detailsSection, workspace, 'Workspace Properties')
        
        # Does this workspace send nag mails?
        if workspace.xml.nag:
            nag='true'
        else:
            nag='false'
        detailsTable.createEntry("Send Nag E-mails: ", nag)
        
        #document.createRaw('<p><strong>Context Tree:</strong> <link href=\'workspace.html\'>workspace</link></p>')
        # x.write('<p><strong>Workspace Config:</strong> <link href=\'xml.txt\'>XML</link></p>')
        # x.write('<p><strong>RSS :</strong> <link href=\'index.rss\'>News Feed</link></p>')
        
        self.documentWorkList(document,workspace,'Workspace-level Work')
     
        document.serialize()
          
        #
        # ----------------------------------------------------------------------
        #
        # Repositories.xml
        #
        document=XDocDocument( 'All Repositories',	\
            self.resolver.getFile(workspace,'repositories'))
        
        
        reposSection=document.createSection('All Repositories')
        reposTable=reposSection.createTable(['Name'])

        rcount=0
        for repo in sortedRepositoryList:
            if not gumpSet.inRepositories(repo): continue
            
            rcount+=1
                    
            repoRow=reposTable.createRow()
            repoRow.createComment(repo.getName())
                       
            self.insertLink( repo, workspace, repoRow.createData())
            
        if not rcount: reposTable.createLine('None')
        
        document.serialize()
       
        #
        # ----------------------------------------------------------------------
        #
        # buildLog.xml -- Projects in build order
        #
        document=XDocDocument('Project Build Log',	\
                self.resolver.getFile(workspace,'buildLog'))        
        self.documentSummary(document, workspace.getProjectSummary())
        
        projectsSection=document.createSection('Projects (in build order)')
        projectsTable=projectsSection.createTable(['Time','Updated','Name','Project State','Duration\nin state','Last Modified','Elapsed'])
        pcount=0
        for project in gumpSet.getSequence():
            # :TODO: Next line irrelevent?
            if not gumpSet.inSequence(project): continue       
            
            pcount+=1
    
            projectRow=projectsTable.createRow()            
            projectRow.createComment(project.getName())  
            
            projectRow.createData(secsToTime(project.getStartSecs()))  
            
            projectRow.createData(secsToTime(project.getModule().getStartSecs()))             
                        
            self.insertLink(project,workspace,projectRow.createData())   
            self.insertStateIcon(project,workspace,projectRow.createData())      
            projectRow.createData(project.getStats().sequenceInState)    
            projectRow.createData(	\
                getGeneralSinceDescription(	\
                    project.getModule().getStats().getLastUpdated()))
            projectRow.createData(secsToElapsedString(project.getElapsedSecs())) 
                
        if not pcount: projectsTable.createLine('None')
        
        document.serialize()
           
        #
        # ----------------------------------------------------------------------
        #
        # projects.xml -- Projects in aphanumeric order
        #
        document=XDocDocument('All Projects',	\
                self.resolver.getFile(workspace,'projects'))        
        self.documentSummary(document, workspace.getProjectSummary())
        
        projectsSection=document.createSection('Projects')
        projectsTable=projectsSection.createTable(['Name','Project State','Elapsed Time','FOG Factor'])
        pcount=0
        for project in sortedProjectList:
            if not gumpSet.inSequence(project): continue    
            
            pcount+=1
    
            projectRow=projectsTable.createRow()            
            projectRow.createComment(project.getName())          
            self.insertLink(project,workspace,projectRow.createData())     
            self.insertStateIcon(project,workspace,projectRow.createData())    
            projectRow.createData(secsToElapsedString(project.getElapsedSecs()))  
            
            projectRow.createData(round(project.getFOGFactor(),2))
                
        if not pcount: projectsTable.createLine('None')    
        document.serialize()
           
        #
        # ----------------------------------------------------------------------
        #
        # project_todos.xml -- Projects w/ issues in build order
        #
        document=XDocDocument('Projects with issues',	\
            self.resolver.getFile(workspace,'project_todos'))        
        self.documentSummary(document, workspace.getProjectSummary())
        
        projectsSection=document.createSection('Projects with issues...')
        projectsTable=projectsSection.createTable(['Name','Affected',	\
                    'Duration\nin state','Project State','Elapsed'])
        pcount=0
        for project in sortedProjectList:
            if not gumpSet.inSequence(project): continue       
            
            if not project.getState()==STATE_FAILED:
                continue
                
            pcount+=1
        
            #
            # Determine the number of projects this module (or it's projects)
            # cause not to be run.
            #
            affected=project.determineAffected()
            
            # How long been like this
            seq=stats=project.getStats().sequenceInState
                    
            projectRow=projectsTable.createRow()
            projectRow.createComment(project.getName())
                                    
            self.insertLink(project,workspace,projectRow.createData())   
                        
            projectRow.createData(affected)
            projectRow.createData(seq)
            
            self.insertStateIcon(project,workspace,projectRow.createData())
            projectRow.createData(secsToElapsedString(project.getElapsedSecs())) 
                
        if not pcount: projectsTable.createLine('None')    
        document.serialize()
           
        #
        # ----------------------------------------------------------------------
        #
        # module_todos.xml
        #
        document=XDocDocument('Modules with issues',
                    self.resolver.getFile(workspace,'module_todos'),)            
        self.documentSummary(document, workspace.getProjectSummary())
        
        modulesSection=document.createSection('Modules with TODOs')        
        modulesTable=modulesSection.createTable(['Name','Affected','Duration\nin state','Module State',	\
                                    'Project State(s)','Elapsed'])
        
        mcount=0
        for module in sortedModuleList:      
            if not gumpSet.inModules(module): continue
            
            #
            # Determine if there are todos, otherwise continue
            #
            todos=0
            for pair in module.aggregateStates():
                if pair.state==STATE_FAILED:
                    todos=1
                    
            if not todos: continue
    
            # Shown something...
            mcount+=1
            
            # Determine longest sequence in this (failed) state...
            # for any of the projects
            seq=0
            for project in module.getProjects():
                if project.getState()==STATE_FAILED:
                    stats=project.getStats()        
                    if stats.sequenceInState > seq: seq = stats.sequenceInState
    
            #
            # Determine the number of projects this module (or it's projects)
            # cause not to be run.
            #
            affected=module.determineAffected()
            
            # Display
            moduleRow=modulesTable.createRow()
            moduleRow.createComment(module.getName())     
            self.insertLink(module,workspace,moduleRow.createData())
            
            moduleRow.createData(affected)
            moduleRow.createData(seq)
                        
            self.insertStateIcon(module,workspace,moduleRow.createData())
            self.insertStateIcons(gumpSet,module,workspace,moduleRow.createData())
            
            moduleRow.createData(secsToElapsedString(module.getElapsedSecs()))
            
        if not mcount: modulesTable.createLine('None')
    
        document.serialize()
        
        #
        # ----------------------------------------------------------------------
        #
        # Modules.xml
        #
        document=XDocDocument( 'All Modules',	\
            self.resolver.getFile(workspace,'modules'))
        
        self.documentSummary(document, workspace.getProjectSummary())
        
        modulesSection=document.createSection('All Modules')
        modulesTable=modulesSection.createTable(['Name','Module State','Project State(s)','Elapsed','FOG Factor'])

        mcount=0
        for module in sortedModuleList:
            if not gumpSet.inModules(module): continue
            
            mcount+=1
                    
            moduleRow=modulesTable.createRow()
            moduleRow.createComment(module.getName())
                       
            self.insertLink( module, workspace, moduleRow.createData())
            self.insertStateIcon(module,workspace,moduleRow.createData())
            self.insertStateIcons(gumpSet,module,workspace,moduleRow.createData())
            
            moduleRow.createData(secsToElapsedString(module.getElapsedSecs()))
            moduleRow.createData(round(module.getFOGFactor(),2))
            
        if not mcount: modulesTable.createLine('None')
        
        document.serialize()
       
        #
        # ----------------------------------------------------------------------
        #
        # Packages.xml
        #
        document=XDocDocument('Packages',	\
                self.resolver.getFile(workspace,'packages'))
        
        mpkgSection=document.createSection('Packaged Modules')
        mpkgTable=mpkgSection.createTable(['Name','State','Project State(s)'])
        mcount=0
        for module in sortedModuleList:           
            if not gumpSet.inModules(module): continue
            
            packaged=0
            #
            # Determine if there are todos, otherwise continue
            #
            if module.getState()==STATE_COMPLETE and \
                module.getReason()==REASON_PACKAGE:
                packaged=1
                    
            if not packaged: continue
        
            mcount+=1
    
            moduleRow=mpkgTable.createRow()
            moduleRow.createComment(module.getName())
            self.insertLink( module, workspace, moduleRow.createData())
            self.insertStateIcon(module,workspace,moduleRow.createData())
            self.insertStateIcons(gumpSet,module,workspace,moduleRow.createData())
            
        if not mcount: mpkgTable.createLine('None')
        
        pkgsSection=document.createSection('Packaged Projects')
        packages=gumpSet.getPackagedProjects()
        if packages:
            pkgsTable=pkgsSection.createTable(['Name','State','Location'])
            for project in sortedProjectList:
                if not gumpSet.inSequence(project): continue   
                if not project.isPackaged(): continue
                
                packageRow=pkgsTable.createRow()                
                packageRow.createComment(project.getName())       
                            
                self.insertLink( project, workspace, packageRow.createData())
                self.insertStateIcon( project, workspace, packageRow.createData())
                
                packageRow.createData(project.getHomeDirectory())    
        else:
            pkgsSection.createNote('No packaged projects installed.')   
        
        document.serialize()
        
        #
        # Document repositories
        #
        for repo in workspace.getRepositories():            
            if not gumpSet.inRepositories(repo): continue
            self.documentRepository(repo,workspace,gumpSet)
            
        #
        # Document modules
        #
        for module in workspace.getModules():
            if not gumpSet.inModules(module): continue  
            self.documentModule(module,workspace,gumpSet)
            
        # Document workspace
        document=XDocDocument('Context',self.resolver.getFile(workspace,'context.xml'))
        stream=StringIO.StringIO() 
        texter=TextDocumenter(stream)  
        texter.document(run)
        stream.seek(0)
        document.createSource(stream.read())
        stream.close()
        document.serialize()
            
        # Document the workspace XML    
        document=XDocDocument('Definition',self.resolver.getFile(workspace,'workspace.xml'))
        stream=StringIO.StringIO() 
        xmlize('workspace',workspace.xml,stream)
        stream.seek(0)
        document.createSource(stream.read())
        stream.close()
        document.serialize()
      
    def documentRepository(self,repo,workspace,gumpSet):
        
        document=XDocDocument( 'Repository : ' + repo.getName(),	\
                self.resolver.getFile(repo))   
            
        # Provide a description/link back to the repo site.
#        descriptionSection=document.createSection('Description') 
#        description=''
#        if repo.hasDescription():
#            description=escape(repo.getDescription())
#            if not description.strip().endswith('.'):
#                description+='. '    
#        if not description:
#            description='No description provided.'        
#        if repo.hasURL():
#            description+=' For more information, see: ' + self.getFork(repo.getURL())
#        else:
#            description+=' (No repo URL provided).'
#                
#        descriptionSection.createParagraph().createRaw(description)
        
        self.documentAnnotations(document,repo)    
        
        detailSection=document.createSection('Repository Details')
        detailList=detailSection.createList()        
        
        if repo.hasTitle():
            detailList.createEntry('Title: ', repo.getTitle())
            
        if repo.hasType():
            detailList.createEntry('Type: ', repo.getType())
            
        if repo.hasHomePage():
            detailList.createEntry('Homepage: ') \
                .createLink(repo.getHomePage(),repo.getHomePage())
            
        if repo.hasCvsWeb():
            detailList.createEntry('Web Interface: ') \
                .createLink(repo.getCvsWeb(),repo.getCvsWeb())
            
        detailList.createEntry('State: ' + repo.getStateDescription())
        if not repo.getReason() == REASON_UNSET:
            detailList.createEntry('Reason: ', repo.getReasonDescription())    
    
        if repo.hasUser():
            detailList.createEntry('Username: ', repo.getUser())
            
        if repo.hasMethod():
            detailList.createEntry('Method: ', repo.getMethod())
    
        if repo.hasPath():
            detailList.createEntry('Path: ', repo.getPath())
            
        if repo.hasHostname():
            detailList.createEntry('Hostname: ', repo.getHostname())
    
        self.documentXML(document,repo)
        
        self.documentWorkList(document,repo,'Repository-level Work')

        document.serialize()
      
        
    def documentModule(self,module,workspace,gumpSet):
        
        document=XDocDocument( 'Module : ' + module.getName(),	\
                self.resolver.getFile(module))   
            
        # Provide a description/link back to the module site.
        descriptionSection=document.createSection('Description') 
        description=''
        if module.hasDescription():
            description=escape(module.getDescription())
            if not description.strip().endswith('.'):
                description+='. '    
        if not description:
            description='No description provided.'        
        if module.hasURL():
            description+=' For more information, see: ' + self.getFork(module.getURL())
        else:
            description+=' (No module URL provided).'
                
        descriptionSection.createParagraph().createRaw(description)

        if module.isPackaged():
            document.createNote('This is a packaged module, not Gumped.')
            
        stateSection=document.createSection('State')
        stateList=stateSection.createList()
        stateList.createEntry("State: " + module.getStateDescription())
        if not module.getReason() == REASON_UNSET:
            stateList.createEntry("Reason: ", module.getReasonDescription())
        if module.cause and not module==module.cause:
             self.insertTypedLink( module.cause, module, stateList.createEntry( "Root Cause: ")) 
             
        self.documentAnnotations(document,module)
        
        projectsSection=document.createSection('Projects') 
        if (len(module.getProjects()) > 1):
            self.documentSummary(projectsSection,module.getProjectSummary())
                                            
        if (len(module.getProjects()) > 1):
            ptodosSection=projectsSection.createSection('Projects with Issues')
            ptodosTable=ptodosSection.createTable(['Name','State','Elapsed'])
            pcount=0
            for project in module.getProjects():     
                if not gumpSet.inSequence(project): continue  
            
                #
	            # Determine if there are todos, otherwise continue
	            #
                todos=0
                for pair in project.aggregateStates():
	                if pair.state==STATE_FAILED:
	                    todos=1
	                    
                if not todos: continue
	             
                pcount+=1
            
                projectRow=ptodosTable.createRow()
                projectRow.createComment(project.getName())
                self.insertLink(project,module,projectRow.createData())  
                self.insertStateIcon(project,module,projectRow.createData())                        
                projectRow.createData(secsToElapsedString(project.getElapsedSecs())) 
	            
	        if not pcount: ptodosTable.createLine('None')
	        
        pallSection=projectsSection.createSection('All Projects')
        pallTable=pallSection.createTable(['Name','State','Elapsed'])
        
        pcount=0
        for project in module.getProjects():     
            if not gumpSet.inSequence(project): continue  
            pname=project.getName()
            pcount+=1
            
            projectRow=pallTable.createRow()
            projectRow.createComment(project.getName())
            self.insertLink(project,module,projectRow.createData())
            self.insertStateIcon(project,module,projectRow.createData())                        
            projectRow.createData(secsToElapsedString(project.getElapsedSecs())) 
            
        if not pcount: pallTable.createLine('None')
                           
        self.documentWorkList(document,module,'Module-level Work')
        
        addnSection=document.createSection('Additional Details')
        addnPara=addnSection.createParagraph()
        addnPara.createLink('index_details.html',	\
                            'More module details ...')
                                                                            
        document.serialize()
        
        document=XDocDocument('Module Details : ' + module.getName(),	\
                    self.resolver.getFile(module, \
                                    'index_details', \
                                        '.xml'))
            
        detailSection=document.createSection('Module Details')
        detailList=detailSection.createList()
        detailList.createEntry("State: " + module.getStateDescription())
        if not module.getReason() == REASON_UNSET:
            detailList.createEntry("Reason: ", module.getReasonDescription())
        if module.cause and not module==module.cause:
             self.insertTypedLink( module.cause, module, detailList.createEntry( "Root Cause: ")) 
             
        if module.hasRepository():
            
            repoSection=detailSection.createSection('Repository')
            repoList=repoSection.createList()
            self.insertLink( 	module.getRepository(), \
                                module, \
                                repoList.createEntry( "Repository: ") )
                                
            if module.hasCvs():
                if module.cvs.hasModule():
                     repoList.createEntry( "CVS Module: ", module.cvs.getModule()) 
                     
                if module.cvs.hasTag():
                     repoList.createEntry( "CVS Tag: ", module.cvs.getTag()) 
                    
                if module.cvs.hasDir():
                     repoList.createEntry( "CVS Dir: ", module.cvs.getDir()) 
                    
                if module.cvs.hasHostPrefix():
                     repoList.createEntry( "CVS Host Prefix: ", module.cvs.getHostPrefix()) 
                     
                repoList.createEntry( "CVSROOT: ", module.cvs.getCvsRoot()) 

            if module.hasSvn():
                if module.svn.hasDir():
                     repoList.createEntry( "SVN Directory: ", module.svn.getDir()) 
                repoList.createEntry( "SVN URL: ", module.svn.getRootUrl())                 

            if module.hasJars():
                if module.jars.hasUrl():
                     repoList.createEntry( "Jars URL: ", module.jars.getUrl())                 

                
           
    #   x.write('<p><strong>Module Config :</strong> <link href=\'xml.html\'>XML</link></p>')
            
        self.documentXML(detailSection,module)

        document.serialize()
      
        # Document Projects
        for project in module.getProjects():
            if not gumpSet.inSequence(project): continue      
            self.documentProject(project,workspace,gumpSet)
       
    # Document the module XML
    #    x=startXDoc(getModuleXMLDocument(workspace,modulename,mdir))
    #    headerXDoc('Module XML')    
    #    x.write('<source>\n')
    #    xf=StringIO.StringIO()
    #    xml = xmlize('module',module,xf)
    #    x.write(escape(xml))    
    #    x.write('</source>\n')   
    #    footerXDoc(x)
    #    endXDoc(x)
        
    def documentProject(self,project,workspace,gumpSet): 
        
        document=XDocDocument('Project : ' + project.getName(),	\
                self.resolver.getFile(project))       
         
        # Provide a description/link back to the module site.
        projectsSection=document.createSection('Description') 
        description=''
        if project.hasDescription():
            description=escape(project.getDescription())
        if not description.strip().endswith('.'):
            description+='. '
        if not description:
            description='No description provided.'        
        if project.hasURL():
            description+=' For more information, see: ' + self.getFork(project.getURL())
        else:        
            description=' (No project URL provided.)'   
                
        projectsSection.createParagraph().createRaw(description)
        
        if project.isPackaged():
            document.createNote('This is a packaged project, not Gumped.')
        elif not project.hasBuildCommand():
            document.createNote('This project is not built by Gump.')        
            
        stateSection=document.createSection('State')
        
        stateList=stateSection.createList()
        stateList.createEntry("State: ", project.getStateDescription())  
        if not project.getReason() == REASON_UNSET:
            stateList.createEntry("Reason: " + reasonString(project.getReason()))
            
        if project.cause and not project==project.cause:
             self.insertTypedLink( project.cause, project, stateList.createEntry( "Root Cause: ")) 
             
        self.documentAnnotations(document,project)        
            
        detailsSection=document.createSection('Details')
        
        detailsList=detailsSection.createList()
        detailsList.createEntry("State: ", project.getStateDescription())  
        if not project.getReason() == REASON_UNSET:
            detailsList.createEntry("Reason: " + reasonString(project.getReason()))
            
            
        self.insertLink(project.getModule(),project,detailsList.createEntry('Module: '))
        if project.hasCause() and not project==project.getCause():
            self.insertTypedLink(project.getCause(),project,detailsList.createEntry('Root Cause: '))
        e = secsToElapsedString(project.getElapsedSecs())
        if e: detailsList.createEntry("Elapsed: ", e)
                                                      
        # Display nag information
        for nagEntry in project.xml.nag:
            toaddr=getattr(nagEntry,'to') or workspace.mailinglist
            fromaddr=getStringFromUnicode(getattr(nagEntry,'from') or workspace.email)
            detailsList.createEntry("Nag To: ").createFork('mailto:'+toaddr,toaddr)
            detailsList.createEntry("Nag From: ").createFork('mailto:'+fromaddr,fromaddr)
                             
        # Note: Leverages previous extraction from project statistics DB
        stats=project.getStats()
        
        statsSection=document.createSection('Statistics')  
        statsTable=statsSection.createTable()           
        statsTable.createEntry("FOG Factor: ", round(stats.getFOGFactor(),2))
        statsTable.createEntry("Successes: ", stats.successes)
        statsTable.createEntry("Failures: ", stats.failures)
        statsTable.createEntry("Prerequisite Failures: ", stats.prereqs)
        statsTable.createEntry("Previous State: ", stateName(stats.previousState))
        
        if stats.first:
            statsTable.createEntry("First Success: ", secsToDate(stats.first))
        if stats.last:
            statsTable.createEntry("Last Success: ", secsToDate(stats.last))
                
        self.documentWorkList(document,project,'Project-level Work')  
                
        addnSection=document.createSection('Additional Details')
        addnPara=addnSection.createParagraph()
        addnPara.createLink(gumpSafeName(project.getName()) + '_details.html',	\
                            'More project details ...')
                                                                            
        document.serialize()
        
        document=XDocDocument('Project Details : ' + project.getName(),	\
                    self.resolver.getFile(project, \
                                    project.getName() + '_details', \
                                        '.xml'))     
 
    #    x.write('<p><strong>Project Config :</strong> <link href=\'%s\'>XML</link></p>' \
    #                % (getModuleProjectRelativeUrl(modulename,project.name)) )                     
           
        miscSection=document.createSection('Miscellaneous')
            
        if project.hasBuildCommand():
            
            if project.hasAnt():                
                self.documentProperties(miscSection, project.getAnt(), 'Ant Properties')
            
            (classpath,bootclasspath)=project.getClasspathLists()            
            self.displayClasspath(miscSection, classpath,'Classpath',project)        
            self.displayClasspath(miscSection, bootclasspath,'Boot Classpath',project) 
       
        self.documentXML(miscSection,project)
        
        dependencySection=document.createSection('Dependency')
        
        self.documentDependenciesList(dependencySection, "Project Dependees",		\
                    project.getDependees(), 1, project)
                    
        self.documentDependenciesList(dependencySection, "Full Project Dependees",		\
                    project.getFullDependees(), 1, project)
        
        self.documentDependenciesList(dependencySection, "Project Dependencies",	\
                    project.getDependencies(), 0, project)
                    
        self.documentDependenciesList(dependencySection, "Full Project Dependencies",	\
                    project.getFullDependencies(), 0, project)
                                                
        
        document.serialize()
        
        # Document the project XML
    #    x=startXDoc(getProjectXMLDocument(workspace,modulename,project.name))
    #    headerXDoc('Project XML')    
    #    x.write('<source>\n')
    #    xf=StringIO.StringIO()
    #    xml = xmlize('project',project,xf)
    #    x.write(escape(xml))    
    #    x.write('</source>\n')   
    #    footerXDoc(x)
    #    endXDoc(x)
    
    def displayClasspath(self,document,classpath,title,referencingObject):
        
        if not classpath.getPathParts(): return
        
        pathSection=document.createSection(title)
        pathTable=pathSection.createTable(['Path Entry','Contributor','Instigator','Annotation'])       
        paths=0
        for path in classpath.getPathParts(): 
            if isinstance(path,AnnotatedPath):
                pathStr=path.getPath()
                contributor=path.getContributor()
                instigator=path.getInstigator()
                note=path.note
            else:
                pathStr=path
                contributor=referencingObject.getWorkspace()
                instigator=None
                note=''
            
            pathRow=pathTable.createRow()
            pathRow.createData(pathStr)
            
            # Contributor
            if contributor:
                self.insertLink( contributor, referencingObject, pathRow.createData())
            else:
                pathRow.createData('')
            
            # Instigator (if not Gump)
            if instigator:
                self.insertLink( instigator, referencingObject, pathRow.createData())
            else:
                pathRow.createData('')
            
            # Additional Notes...
            pathRow.createData(note)
            
            paths+=1
    
        if not paths:        
            pathTable.createLine('No ' + title + ' entries')
                     
    def documentDependenciesList(self,xdocNode,title,dependencies,dependees,referencingObject):
      if dependencies:
            projectSection=xdocNode.createSection(title)
            projectTable=projectSection.createTable(['Name','Type','Inheritence','Ids','State'])
            for depend in dependencies:
                
                # Project/Owner
                if not dependees:
                    project=depend.getProject()
                else:
                    project=depend.getOwnerProject()
                projectRow=projectTable.createRow()    
                projectRow.createComment(project.getName())
                self.insertLink( project, referencingObject, projectRow.createData())                
                
                # Type
                type=''
                if depend.isRuntime():
                    if type: type += ' '    
                    type+='Runtime'              
                if depend.isOptional():
                    if type: type += ' '
                    type+='Optional'                
                projectRow.createData(type)
                
                # Inheritence
                projectRow.createData(depend.getInheritenceDescription())
                
                # Ids
                ids = depend.getIds() or 'All'
                projectRow.createData(ids)
                
                # State description
                self.insertStateDescription(project,referencingObject,projectRow.createData())
                
    def documentAnnotations(self,xdocNode,annotatable):
        
        annotations=annotatable.getAnnotations()
        if not annotations: return        
        
        annotationsSection=xdocNode.createSection('Annotations')
        
        if annotatable.containsNasties():
            annotationsSection.createWarning('Some warnings and/or errors are present within these annotations.')
        
        annotationsTable=annotationsSection.createTable()
        for note in annotations:      
            noteRow=annotationsTable.createRow()
            noteRow.createData(levelName(note.level))
            # TODO if 'text' is a list go through list and
            # when not string get the object link and <link it...
            noteRow.createData(note.text) 
                        
    def documentProperties(self,xdocNode,propertyContainer,title='Properties'):
        
        properties=propertyContainer.getProperties()
        if not properties: return        
        
        propertiesSection=xdocNode.createSection(title)
        
        propertiesTable=propertiesSection.createTable(['Name','Value','XML'])
        for property in properties:      
            propertyRow=propertiesTable.createRow()
            propertyRow.createData(property.getName())
            propertyRow.createData(property.getValue())
            propertyRow.createData(property.getXMLData())
                        
    def documentXML(self,xdocNode,xmlOwner):
        
        xml=xmlOwner.xml
        if not xml: return        
        
        xmlSection=xdocNode.createSection('Definition')
        stream=StringIO.StringIO() 
        try:
            xmlize(xml.getTagName(),xml,stream)
        except Exception, details:
            stream.write('Failed to XML serialize the data. ' + str(details))
        stream.seek(0)
        xmlSection.createSource(stream.read())
        stream.close()
            
    def documentSummary(self,xdocNode,summary,description='Project Summary'):
        if not summary or not summary.projects: return
        
        summarySection=xdocNode.createSection(description)
        summaryTable=summarySection.createTable(['Projects','Successes','Failures','Prereqs',	\
            'No Works','Packages'])
        
        summaryTable.createRow([ `summary.projects`, `summary.successes`, \
                                `summary.failures`,	`summary.prereqs`, \
                                `summary.noworks`, `summary.packages`] )
        
      
    def documentWorkList(self,xdocNode,workable,description='Work'):
        worklist=workable.getWorkList()
        
        if not worklist: return
        
        workSection=xdocNode.createSection(description)        
        workTable=workSection.createTable(['Name','Type','State','Start','Elapsed'])
        
        for work in worklist:
            workRow=workTable.createRow()
            workRow.createComment(work.getName())
            
            self.insertLink(work,workable,workRow.createData())                             
            workRow.createData(work.getName()) 
            workRow.createData(stateName(work.state))
            workRow.createData(secsToDate(work.result.start_time))
            workRow.createData(secsToElapsedString(work.getElapsedSecs()))
        
        #
        # Do a tail on all work that failed...
        #
        for work in worklist:
            if isinstance(work,CommandWorkItem):      
                if not STATE_SUCCESS == work.state:
                    tail=work.tail()
                    if tail:
                        #
                        # Write out the 'tail'
                        #
                        workSection	\
                            .createSection(workTypeName(work.type) + ' : ' + work.command.name)	\
                            .createSource(tail)
                
        
        #
        # Go document the others...
        #
        for work in worklist:
            self.documentWork(workspace,work)
            
    def documentWork(self,workspace,work):
        if isinstance(work,CommandWorkItem):    
            wdocument=XDocDocument(	\
                workTypeName(work.type) + ' : ' + work.command.name,	\
                    self.resolver.getFile(work))
                    
            workSection=wdocument.createSection('Details')
            
            workList=workSection.createList() 
            workList.createEntry("State: ", stateName(work.state))
            
            self.insertTypedLink(work.getOwner(),	\
                    work,	\
                    workList.createEntry("For: "))
            
            # addItemXDoc("Command: ", work.command.name)
            if work.command.cwd:
                workList.createEntry("Working Directory: ", work.command.cwd)
            if work.result.output:
                workList.createEntry("Output: ", work.result.output)
            else:
                workList.createEntry("Output: ", "None")
                
            if work.result.signal:
                workList.createEntry("Termination Signal: ", str(work.result.signal))
            workList.createEntry("Exit Code: ", str(work.result.exit_code))
                                
            workList.createEntry("Start Time: ", secsToDate(work.result.start_time))
            workList.createEntry("End Time: ", secsToDate(work.result.end_time))
            e = secsToElapsedString(work.getElapsedSecs())
            if e : workList.createEntry("Elapsed Time: ", e)
                   
            #
            # Show parameters
            #
            if work.command.params:
                title='Parameter'
                if len(work.command.params.items()) > 1:
                    title += 's'
                parameterSection=wdocument.createSection(title)  
                parameterTable=parameterSection.createTable(['Prefix','Name','Value'])

                for param in work.command.params.items():
                    paramRow=parameterTable.createRow()
                    paramRow.createData(param.prefix or '')
                        
                    paramRow.createData(param.name)
                    val = param.value
                    # :TODO: Hack for BOOTCLASSPATH
                    if param.name.startswith('bootclasspath'):
                       val=default.classpathSeparator+'\n'.join(val.split(default.classpathSeparator))

                    paramRow.createData(val or'')
                        
            #
            # Show ENV overrides
            #
            if work.command.env:
                envSection=wdocument.createSection('Environment Overrides')                                   
                envTable=envSection.createTable(['Name','Value'])
                
                for (name, value) in work.command.env.iteritems():
                    envRow=envTable.createRow()
                    envRow.createData(name)
                    if value:
                        # :TODO: Hack for CLASSPATH
                        if name == "CLASSPATH":
                            value=default.classpathSeparator+'\n'.join(value.split(default.classpathSeparator))
                        envRow.createData(escape(value))
                    else:
                        envRow.createData('N/A')
                        
            
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
            wdocument	\
                .createSection('Command Line')	\
                .createSource(commandLine)
            
            #
            # Show the content...
            #
            outputSection=wdocument.createSection('Output')
            outputSource=outputSection.createSource()
            output=work.result.output
            if output:
                try:
                    o=None
                    try:
                        # Keep a length count to not exceed 32K
                        size=0
                        o=open(output, 'r')
                        line=o.readline()
                        while line:
                            
                            line=wrapLine(line,'...<br/>','    ',100)
                            
                            length = len(line)
                            size += length
                            # Crude to 'ensure' that escaped
                            # it doesn't exceed 32K.
                            if size > 20000:
                                outputSection.createParagraph('Continuation...')
                                outputSource=outputSection.createSource()
                                size = length
                            outputSource.createText(line)
                            line=o.readline()
                    finally:
                        if o: o.close()
                except Exception, details:
                    outputSource.createText('Failed to copy contents from :' + output + ' : ' + str(details))
            else:
                outputSource.createText('No output to stdout/stderr from this command.')
           
        wdocument.serialize()
        wdocument=None
            
    #####################################################################           
    #
    # Helper Methods
    #     
    def getFork(self,href,name=None):
        if not name: name = href
        return '<fork href=\'%s\'>%s</fork>' % (escape(href),escape(name))
            
    def insertStateDescription(self,toObject,fromObject,xdocNode):
        node=xdocNode.createText(stateName(toObject.getState()))
        if not toObject.getReason()==REASON_UNSET: 
            xdocNode.createText(' with reason '+reasonString(toObject.getReason()))
            
        if toObject.cause and not toObject.cause == toObject:
        
            givenCause=0
            for cause in toObject.getCauses():
                if not cause == object:
                    if not givenCause:
                        xdocNode.createText(', caused by ')
                        givenCause=1
                    else:
                        xdocNode.createText(' ')
                    self.insertStateLink(cause,fromObject,xdocNode,1)
                
        return node
        
    def insertStateIcons(self,gumpSet,module,fromObject,xdocNode):
        icons=''
        for project in module.getProjects():
            if not gumpSet.inSequence(project): continue     
            self.insertStateIcon(project,fromObject,xdocNode)
            # A separator, to allow line wrapping
            xdocNode.createText(' ')
        return icons
        
    def insertStateIcon(self,toObject,fromObject,xdocNode):
        return self.insertLink(toObject,fromObject,xdocNode,1,1,1)
    
    def insertTypedLink(self,toObject,fromObject,xdocNode,state=0,icon=0):
        return self.insertLink(toObject,fromObject,xdocNode,1,state,icon)
        
    def insertStateLink(self,toObject,fromObject,xdocNode,typed=0,icon=0):
        return self.insertLink(toObject,fromObject,xdocNode,typed,1,icon)
        
    def insertLink(self,toObject,fromObject,xdocNode,typed=0,state=0,icon=0):
        description=''
        if typed:
           description=toObject.__class__.__name__
                
        try: # Add a name, if present
            name=toObject.getName()             
            if description: description +=': '
            description+=name
        except: 
            if not description:
                description=toObject.__class__.__name__
        
        # If showing 'state' then find the 
        link=self.getLink(toObject,fromObject,state)  
        
        if not state:
            # Just install the <link
            return xdocNode.createLink(link,description)
        else:                  
            # Install the <link with an <icon inside
            if icon:
                node=xdocNode.createLink(link)
                return self.insertStatePairIcon(node,toObject,fromObject)
            else:
                return xdocNode.createLink(link,description)
            
   
    def getLink(self,toObject,fromObject=None,state=0):
        url=''
        
        #
        # If we are looking for what set the state, look at
        # work first. Pick the first...
        #
        if state and isinstance(toObject,Workable):
            for work in toObject.getWorkList():
                if not url:
                    if not work.state==STATE_SUCCESS:
                        url=getRelativeLocation(work,fromObject,'.html').serialize()
        
        if not url:
            if fromObject:
                url=getRelativeLocation(toObject,fromObject,'.html').serialize()
            else:
                url=self.resolver.getAbsoluteUrl(toObject)
            
        return url
    
    def insertStatePairIcon(self,xdocNode,toObject,fromObject):
        pair=toObject.getStatePair()
        depth=getDepthForObject(fromObject)
        
        # :TODO: Move this to some resolver, and share with RSS
        sname=stateName(pair.state)
        rstring=reasonString(pair.reason)    

        description=sname    
        uniqueName=sname
        if not pair.reason==REASON_UNSET: 
            description+=' '+rstring
            # Not yet, just have a few icons ... uniqueName+='_'+rstring
        
        # Build the URL to the icon
        iconName=gumpSafeName(lower(replace(uniqueName,' ','_')))
        url = getUpUrl(depth)+"gump_icons/"+iconName+".png";
        
        # Build the <icon tag at location...
        return xdocNode.createIcon(url,description)
        
    #####################################################################           
    #
    # Statistics Pages
    #           
    def documentStatistics(self,run,workspace,gumpSet):
        
        stats=StatisticsGuru(workspace)
        
        document=XDocDocument('Statistics',self.resolver.getFile(stats))
        
        document.createParagraph("""
        Statistics from Gump show the depth and health of relationship. 
        See side menu for choices.
        """)
        
        overviewSection=document.createSection('Overview')
        overviewList=overviewSection.createList()
        overviewList.createEntry('Modules: ', stats.wguru.modulesInWorkspace)
        overviewList.createEntry('Projects: ', stats.wguru.projectsInWorkspace)
        overviewList.createEntry('Avg Projects Per Module: ', stats.wguru.averageProjectsPerModule)
                
        document.serialize()        
        
        # Individual Pages...
        self.documentModulesByElapsed(stats, run, workspace, gumpSet)
        self.documentModulesByProjects(stats, run, workspace, gumpSet)
        self.documentModulesByDependencies(stats, run, workspace, gumpSet)
        self.documentModulesByDependees(stats, run, workspace, gumpSet)
        self.documentModulesByFOGFactor(stats, run, workspace, gumpSet)        
        # Individual Pages...
        self.documentProjectsByElapsed(stats, run, workspace, gumpSet)
        self.documentProjectsByDependencies(stats, run, workspace, gumpSet)
        self.documentProjectsByDependees(stats, run, workspace, gumpSet)
        self.documentProjectsByFOGFactor(stats, run, workspace, gumpSet)        
    
    def documentModulesByElapsed(self,stats,run,workspace,gumpSet):
        document=XDocDocument('Modules By Elapsed Time',	\
            self.resolver.getFile(stats,'module_elapsed.xml'))
        
        elapsedTable=document.createTable(['Modules By Elapsed'])
        for module in stats.modulesByElapsed:        
            if not gumpSet.inModules(module): continue
            elapsedRow=elapsedTable.createRow()
            self.insertLink( module, stats, elapsedRow.createData())
            elapsedRow.createData(secsToElapsedString(module.getElapsedSecs()))
            
        document.serialize()
    
    def documentModulesByProjects(self,stats,run,workspace,gumpSet):
        document=XDocDocument('Modules By Project Count',	\
            self.resolver.getFile(stats,'module_projects.xml'))
        
        mprojsTable=document.createTable(['Modules By Project Count'])
        for module in stats.modulesByProjectCount:         
            if not gumpSet.inModules(module): continue     
            mprojsRow=mprojsTable.createRow()
            
            self.insertLink( module, stats, mprojsRow.createData())
            
            mprojsRow.createData(len(module.getProjects()))
            
            #
            # :TODO:
            #projectsString=''
            #for project in module.getProjects():
            #    projectsString+=getContextLink(project)
            #    projectsString+=' '            
            # mprojsRow.createData(projectsString)
                    
        document.serialize()
     
    def documentModulesByDependencies(self,stats,run,workspace,gumpSet):
        document=XDocDocument('Modules By Dependency Count',	\
            self.resolver.getFile(stats,'module_dependencies.xml'))
        
        dependenciesTable=document.createTable(['Module','Full Dependency Count'])
        for module in stats.modulesByTotalDependencies:         
            if not gumpSet.inModules(module): continue   
            dependenciesRow=dependenciesTable.createRow()
            self.insertLink( module, stats, dependenciesRow.createData())
            dependenciesRow.createData( module.getFullDependencyCount())
            
            #projectsString=''
            #for project in module.getDepends():
            #    projectsString+=getContextLink(project)
            #    projectsString+=' '            
            #dependenciesRow.createData(projectsString)        
        
        document.serialize()
             
     
    def documentModulesByDependees(self,stats,run,workspace,gumpSet):
        document=XDocDocument('Modules By Dependee Count',
                    self.resolver.getFile(stats,'module_dependees.xml'))
        
        dependeesTable=document.createTable(['Module','Full Dependee Count'])
        for module in stats.modulesByTotalDependees:         
            if not gumpSet.inModules(module): continue   
            dependeesRow=dependeesTable.createRow()
            self.insertLink( module, stats, dependeesRow.createData())
            dependeesRow.createData(module.getFullDependeeCount())
            
            #projectsString=''
            #for project in module.getDependees():
            #    projectsString+=getContextLink(project)
            #    projectsString+=' '            
            #dependeesRow.createData(projectsString)
        
        document.serialize()
        
    def documentModulesByFOGFactor(self,stats,run,workspace,gumpSet):
        document=XDocDocument('Modules By FOG Factor',	\
                    self.resolver.getFile(stats,'module_fogfactor.xml'),)        
        fogTable=document.createTable(['Module','FOG Factor'])
        for module in stats.modulesByFOGFactor:        
            if not gumpSet.inModules(module): continue    
            fogRow=fogTable.createRow()            
            self.insertLink( module, stats, fogRow.createData())                
            fogRow.createData(round(module.getFOGFactor(),2))
            
        document.serialize()
    
    def documentProjectsByElapsed(self,stats,run,workspace,gumpSet):
        document=XDocDocument('Projects By Elapsed Time',	\
            self.resolver.getFile(stats,'project_elapsed.xml'))
        
        elapsedTable=document.createTable(['Projects By Elapsed'])
        for project in stats.projectsByElapsed:        
            if not gumpSet.inSequence(project): continue
            elapsedRow=elapsedTable.createRow()
            self.insertLink( project, stats, elapsedRow.createData())
            elapsedRow.createData(secsToElapsedString(project.getElapsedSecs()))
            
        document.serialize()
     
    def documentProjectsByDependencies(self,stats,run,workspace,gumpSet):
        document=XDocDocument('Projects By Dependency Count',	\
            self.resolver.getFile(stats,'project_dependencies.xml'))
        
        dependenciesTable=document.createTable(['Project','Direct Dependency Count', 'Full Dependency Count'])
        for project in stats.projectsByTotalDependencies:         
            if not gumpSet.inSequence(project): continue   
            dependenciesRow=dependenciesTable.createRow()
            self.insertLink( project, stats, dependenciesRow.createData())
            dependenciesRow.createData( project.getDependencyCount())
            dependenciesRow.createData( project.getFullDependencyCount())
            
            #projectsString=''
            #for project in module.getDepends():
            #    projectsString+=getContextLink(project)
            #    projectsString+=' '            
            #dependenciesRow.createData(projectsString)        
        
        document.serialize()
             
     
    def documentProjectsByDependees(self,stats,run,workspace,gumpSet):
        document=XDocDocument('Projects By Dependee Count',
                    self.resolver.getFile(stats,'project_dependees.xml'))
        
        dependeesTable=document.createTable(['Project','Direct Dependee Count', 'Full Dependee Count'])
        for project in stats.projectsByTotalDependees:         
            if not gumpSet.inSequence(project): continue   
            dependeesRow=dependeesTable.createRow()
            self.insertLink( project, stats, dependeesRow.createData())
            dependeesRow.createData(project.getDependeeCount())
            dependeesRow.createData(project.getFullDependeeCount())
            
            #projectsString=''
            #for project in module.getDependees():
            #    projectsString+=getContextLink(project)
            #    projectsString+=' '            
            #dependeesRow.createData(projectsString)
        
        document.serialize()
        
    def documentProjectsByFOGFactor(self,stats,run,workspace,gumpSet):
        document=XDocDocument('Projects By FOG Factor',	\
                    self.resolver.getFile(stats,'project_fogfactor.xml'),)        
        fogTable=document.createTable(['Project','Successes','Failures','Preq-Failures','FOG Factor'])
        for project in stats.projectsByFOGFactor:        
            if not gumpSet.inSequence(project): continue    
            fogRow=fogTable.createRow()            
            self.insertLink( project, stats, fogRow.createData())  
                 
            pstats=project.getStats()
            
            fogRow.createData(pstats.successes)
            fogRow.createData(pstats.failures)
            fogRow.createData(pstats.prereqs)
            fogRow.createData(round(pstats.getFOGFactor(),2))
            
        document.serialize()
   

        
    #####################################################################           
    #
    # XRef Pages
    #           
    def documentXRef(self,run,workspace,gumpSet):
        
        xref=XRefGuru(workspace)
        
        document=XDocDocument('Cross Reference',self.resolver.getFile(xref))
    
        document.createParagraph("""
        Gump is about relationships, and this section shows relationship. 
        See side menu for choices.
        """)
    
        document.serialize()
        
         # Individual Pages...
        self.documentModulesByRepository(xref, run, workspace, gumpSet)
        self.documentModulesByPackage(xref, run, workspace, gumpSet)
        
        self.documentProjectsByPackage(xref, run, workspace, gumpSet)
        
        
    def documentModulesByRepository(self,xref,run,workspace,gumpSet):
        document=XDocDocument('Modules By Repository',	\
            self.resolver.getFile(xref,'repo_module.xml'))
        
        repoMap=xref.getRepositoryToModuleMap()
        for repo in createOrderedList(repoMap.keys()):
            moduleList=createOrderedList(repoMap.get(repo))            
            repoSection=document.createSection(repo.getName())            
            self.insertLink( repo, xref, 	\
                repoSection.createParagraph('Repository Definition: '))
            
            moduleRepoTable=repoSection.createTable(['Modules'])
            for module in moduleList:        
                if not gumpSet.inModules(module): continue
                moduleRepoRow=moduleRepoTable.createRow()
                self.insertLink( module, xref, moduleRepoRow.createData())
          
        document.serialize()    
        
    def documentModulesByPackage(self,xref,run,workspace,gumpSet):
        document=XDocDocument('Modules By Package',	\
            self.resolver.getFile(xref,'package_module.xml'))
        
        packageTable=document.createTable(['Modules By Package'])
        
        packageMap=xref.getPackageToModuleMap()
        for package in createOrderedList(packageMap.keys()):
            
            moduleList=createOrderedList(packageMap.get(package)) 
            
            hasSome=0
            for module in moduleList:        
                if not gumpSet.inModules(module): continue
                hasSome=1
                
            if hasSome:
                packageRow=packageTable.createRow()
                packageRow.createData(package)
            
                moduleData=packageRow.createData()
                for module in moduleList:        
                    if not gumpSet.inModules(module): continue                
                    self.insertLink(module, xref, moduleData)
                    moduleData.createText(' ')
          
        document.serialize()
        
    def documentProjectsByPackage(self,xref,run,workspace,gumpSet):
        document=XDocDocument('Projects By Package',	\
            self.resolver.getFile(xref,'package_project.xml'))
        
        packageTable=document.createTable(['Projects By Package'])
        
        packageMap=xref.getPackageToProjectMap()
        for package in createOrderedList(packageMap.keys()):
                            
            projectList=createOrderedList(packageMap.get(package)) 
            
            hasSome=0
            for project in projectList:        
                if not gumpSet.inSequence(project): continue
                hasSome=1
                
            if hasSome:
                packageRow=packageTable.createRow()
                packageRow.createData(package)
            
                projectData=packageRow.createData()
                for project in projectList:        
                    if not gumpSet.inSequence(project): continue                
                    self.insertLink(project, xref, projectData)
                    projectData.createText(' ')
          
        document.serialize()
 
        
        