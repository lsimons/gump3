#!/usr/bin/env python

# Copyright 2003-2004 The Apache Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
from gump.core.config import *
from gump.document.documenter import Documenter
from gump.document.text.documenter import TextDocumenter
from gump.document.forrest.xdoc import *
from gump.document.forrest.resolver import *
from gump.utils import *
from gump.utils.xmlutils import xmlize
from gump.utils.tools import syncDirectories,copyDirectories,wipeDirectoryTree

from gump.model.stats import *
from gump.model.project import AnnotatedPath,  ProjectStatistics
from gump.model.state import *
from gump.model.workspace import Workspace
from gump.model.module import Module
from gump.model.project import Project

from gump.output.statsdb import StatisticsGuru
from gump.output.xref import XRefGuru
from gump.core.gumprun import *

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
        self.resolver=ForrestResolver(dirBase,urlBase)
        
    def getResolverForRun(self,run):
        return self.resolver
    
    def prepareRun(self, run):
    
        log.debug('--- Prepare for Documenting Results')

        workspace=run.getWorkspace()
        gumpSet=run.getGumpSet()
    
        # Seed with default/site skins/etc.
        self.prepareForrest(workspace)
        
    def documentEntity(self, entity, run):
        
        verbose=run.getOptions().isVerbose()
        debug=run.getOptions().isDebug()
        
        if isinstance(entity,Workspace):
            pass
        elif isinstance(entity,Module):
            pass
        elif  isinstance(entity,Project):
            pass
            
        # :TODO: A work in progress
        # 1) Document entityi (in realtime so no lookahead links)
        # 2) Sync
        # 3) update build log        
    
    def documentRun(self, run):
    
        log.debug('--- Documenting Results')

        workspace=run.getWorkspace()
        gumpSet=run.getGumpSet()
        runOptions=run.getOptions()
        
        # Document...
        self.documentEnvironment(run,workspace)    
        self.documentWorkspace(run,workspace,gumpSet)  
        self.documentRunOptions(run,workspace)    
        
        # Document these (even if not a full build)
        self.documentStatistics(run,workspace,gumpSet)
        self.documentXRef(run,workspace,gumpSet)

        #
        # Launch Forrest, if we aren't just leaving xdocs...
        #
        ret=0
        
        if not runOptions.isXDocs():
            ret=self.executeForrest(workspace)
        else:
            ret=self.syncXDocs(workspace)
            
        return ret

    #####################################################################
    #
    # Forresting...
    def getForrestWorkDirectory(self,workspace):
        fdir=os.path.abspath(os.path.join(workspace.getBaseDirectory(),'forrest-work'))
        return fdir
        
    def getForrestStagingDirectory(self,workspace):
        """ Staging Area for built output """
        fdir=os.path.abspath(os.path.join(workspace.getBaseDirectory(),'forrest-staging'))
        return fdir
        
    def getForrestTemplateDirectory(self):
        """ Template (forrest skin/config) """
        fdir=os.path.abspath(os.path.join(dir.template,'forrest'))
        return fdir  
        
    def getForrestSiteTemplateDirectory(self):
        """ Site Template (forrest skin/config tweaks) """    
        fdir=os.path.abspath(os.path.join(dir.template,'site-forrest'))
        return fdir  
    
    def prepareForrest(self,workspace):   
        """ 
        
        Copy the main template (perhaps with site tweaks) to prepare
        
        """        
        #
        # First deleted the work tree (if exists), then ensure created
        #
        forrestWorkDir=self.getForrestWorkDirectory(workspace)
        wipeDirectoryTree(forrestWorkDir)
                    
        # Sync in the defaults [i.e. cleans also]
        forrestTemplate=self.getForrestTemplateDirectory()   
        syncDirectories(	forrestTemplate,	\
                            forrestWorkDir,	\
                            workspace)    
                                    
        # Copy over the local site defaults (if any)        
        forrestSiteTemplate=self.getForrestSiteTemplateDirectory()  
        if os.path.exists(forrestSiteTemplate):
            copyDirectories(forrestSiteTemplate,	\
                            forrestWorkDir,	\
                            workspace)                               
                             
        #    
        # Wipe the staging tree
        #   
        stagingDirectory=self.getForrestStagingDirectory(workspace)
        wipeDirectoryTree(stagingDirectory)
                 
    def executeForrest(self,workspace):
        # The project tree
        xdocs=self.resolver.getDirectory(workspace)      
        
        # The three dirs, work, output (staging), public
        forrestWorkDir=self.getForrestWorkDirectory(workspace)
        stagingDirectory=self.getForrestStagingDirectory(workspace)
        logDirectory=workspace.getLogDirectory()
        
        # Generate...        
        forrest=Cmd('forrest','forrest',forrestWorkDir)
      
        forrest.addPrefixedParameter('-D','java.awt.headless','true','=')
        forrest.addPrefixedParameter('-D','project.site-dir',  \
            stagingDirectory, '=')
                
        # Temporary:   
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
        
        # If ok move from staging to publish
        #
        # :TODO: Forrest returns failure if the site isn't perfect
        # let's not shoot so high.
        #
        success=1
        if 1 or (forrestResult.state==CMD_STATE_SUCCESS):
            try:
                #
                # Sync over public pages...
                #
                syncDirectories(stagingDirectory,logDirectory)
                # 
                # Clean up
                wipeDirectoryTree(stagingDirectory)
                
                # Clean only if successful.
                if  (forrestResult.state==CMD_STATE_SUCCESS):
                    wipeDirectoryTree(forrestWorkDir)
            except:        
                log.error('--- Failed to staging->log sync and/or clean-up', exc_info=1)
                success=0
        
        return success
                            
    def syncXDocs(self,workspace):
        
        
        # The three dirs, work, output (staging), public
        forrestWorkDir=self.getForrestWorkDirectory(workspace)
        logDirectory=workspace.getLogDirectory()
        
        success=1
        try:
            #
            # Sync over public pages...
            #
            syncDirectories(forrestWorkDir,logDirectory)
            # 
            # Clean up
            #
            wipeDirectoryTree(forrestWorkDir)
        except:        
            log.error('--- Failed to work->log sync and/or clean-up', exc_info=1)
            success=0
        
        return success
              
    #####################################################################           
    #
    # Environment
    #      
    def documentEnvironment(self,run,workspace):
        
        environment=run.getEnvironment()
           
        #
        # ----------------------------------------------------------------------
        #
        # env.xml
        #
        
        document=XDocDocument('Gump Environment',	\
                self.resolver.getFile(workspace, 'environment.xml'))       
                        
        envSection=document.createSection('Gump Environment')
        envSection.createParagraph(
            """The environment that this Gump run was within.""")            
        
        self.documentAnnotations(document,environment)        
        #self.documentFileList(run,document,environment,'Environment-level Files')        
        self.documentWorkList(run,document,environment,'Environment-level Work')
     
        document.serialize()
                
    #####################################################################           
    #
    # Options
    #      
    def documentRunOptions(self,run,workspace):
        
        options=run.getOptions()
           
        #
        # ----------------------------------------------------------------------
        #
        # env.xml
        #
        
        document=XDocDocument('Run Options',	\
                self.resolver.getFile(workspace, 'options.xml'))       
                        
        optSection=document.createSection('Gump Run Options')
        optSection.createParagraph(
            """The options selected for this Gump run.""")            
        
        #self.documentAnnotations(document,options)        
        
        optTable=optSection.createTable(['Name','Value'])
        opts=0
        # iterate over this suites properties
        for (name,value) in getBeanAttributes(options).items():
            optTable.createEntry(str(name),str(value))
            opts+=1
            
        if not opts: optTable.createEntry('None')
     
        document.serialize()
                
    #####################################################################           
    #
    # Model Pieces
    #      
    def documentWorkspace(self,run,workspace,gumpSet):
        
        # Pretty sorting...
        sortedModuleList=createOrderedList(gumpSet.getModuleSequence())
        sortedProjectList=createOrderedList(gumpSet.getProjectSequence())
        sortedRepositoryList=createOrderedList(gumpSet.getRepositories())        
        sortedServerList=createOrderedList(workspace.getServers())       
        sortedTrackerList=createOrderedList(workspace.getTrackers())
        
        #
        # ----------------------------------------------------------------------
        #
        # Index.xml
        #
        
        document=XDocDocument('Workspace',	\
                self.resolver.getFile(workspace))    
        
        definitionSection=document.createSection('Workspace Definition')    
        
        definitionSection.createNote('This install runs Python Gump, not Traditional Gump.') 
        
        definitionTable=definitionSection.createTable()
        definitionTable.createEntry('Gump Version', setting.version)
        if workspace.xml.description:
                definitionTable.createEntry('Description', workspace.xml.description)
        if workspace.xml.version: 
            definitionTable.createEntry('Workspace Version', workspace.xml.version)
        if not workspace.xml.version or not workspace.xml.version == setting.ws_version:
            definitionTable.createEntry('Gump Preferred Workspace Version', setting.ws_version)
        definitionTable.createEntry('Java Command', run.getEnvironment().javaCommand)
        definitionTable.createEntry('Python', str(sys.version))
        definitionTable.createEntry('Operating System (Name)', str(os.name))
        definitionTable.createEntry('@@DATE@@', str(default.date))
        definitionTable.createEntry('Start Date/Time (UTC)', workspace.getStartDateTimeUtc())
        definitionTable.createEntry('Start Date/Time', workspace.getStartDateTime())
        definitionTable.createEntry('Timezone', workspace.timezone)

        javaproperties=run.getEnvironment().getJavaProperties()
        for name in ['java.vendor', 'java.version', 'os.name', 'os.arch', 'os.version']:
            if name in javaproperties:
                definitionTable.createEntry(name, javaproperties[name])	  
        
        rssSyndRow=definitionTable.createRow()
        rssSyndRow.createData('Syndication')
        rssSyndRow.createData().createFork('rss.xml','RSS')
        atomSyndRow=definitionTable.createRow()
        atomSyndRow.createData('Syndication')
        atomSyndRow.createData().createFork('atom.xml','Atom')
                
        textRow=definitionTable.createRow()
        textRow.createData('Workspace Documentation')
        textRow.createData().createLink('context.html','Text')
                
        if not workspace.private:            
            syndRow=definitionTable.createRow()
            syndRow.createData('Definition')
            syndRow.createData().createLink('workspace.html','XML')
                
        if not gumpSet.isFull():
            warning=definitionSection.createWarning()
            
            warning.createText("""This output does not represent the a complete workspace,
            but a partial one.         
            Only projects, and their dependents, matching this regular expression """)
            warning.createStrong(gumpSet.projectexpression)
            warning.createBreak()
            warning.createBreak()            
            warning.createText('Requested Projects:')
            warning.createBreak()
            for project in gumpSet.projects:
                warning.createText(project.name)
                warning.createText(' ')
                            
        
        self.documentSummary(document,workspace.getProjectSummary())        
        self.documentAnnotations(document,workspace)
        #self.documentXML(document,workspace)
        
        detailsSection=document.createSection('Details')
                    
        detailsTable=detailsSection.createTable()
        detailsTable.createEntry("State : ", workspace.getStateDescription()) 

        e = secsToElapsedTimeString(workspace.getElapsedSecs())
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
        if not workspace.private:
            detailsTable.createEntry("E-mail Server: ", workspace.mailserver)
            detailsTable.createEntry("E-mail Port: ", workspace.mailport)
            detailsTable.createEntry("List Address: ", workspace.mailinglist)
            detailsTable.createEntry("E-mail Address: ", workspace.email)            
            detailsTable.createEntry("Prefix: ", workspace.prefix)
            detailsTable.createEntry("Signature: ", workspace.signature)
        
        self.documentProperties(detailsSection, workspace, 'Workspace Properties')
        
        # Does this workspace send notification (nag) mails?
        detailsTable.createEntry("Send Nag E-mails: ", getBooleanString(workspace.isNag()))
        
        #document.createRaw('<p><strong>Context Tree:</strong> <link href=\'workspace.html\'>workspace</link></p>')
        # x.write('<p><strong>Workspace Config:</strong> <link href=\'xml.txt\'>XML</link></p>')
        # x.write('<p><strong>RSS :</strong> <link href=\'index.rss\'>News Feed</link></p>')
        
        self.documentFileList(run,document,workspace,'Workspace-level Files')
        self.documentWorkList(run,document,workspace,'Workspace-level Work')
     
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
        # Servers.xml
        #
        document=XDocDocument( 'All Servers',	\
            self.resolver.getFile(workspace,'servers'))
                
        serversSection=document.createSection('All Servers')
        serversTable=serversSection.createTable(['Name','Notes','Results','Start (Local)','Start (UTC)','End (UTC)'])

        scount=0
        for server in sortedServerList:
            
            scount+=1
                    
            serverRow=serversTable.createRow()
            serverRow.createComment(server.getName())
                       
            self.insertLink( server, workspace, serverRow.createData())
                                        
            if server.hasNote():
                serverRow.createData(server.getNote())
            else:
                serverRow.createData('')
            
            if server.hasResultsUrl():
                serverRow.createData().createFork(	\
                            server.getResultsUrl(),	\
                            'Results')
            else:
                serverRow.createData('Not Available')
                
            if server.hasResults():
                serverRow.createData(server.getResults().getStartDateTime())
                serverRow.createData(server.getResults().getStartDateTimeUtc())
                serverRow.createData(server.getResults().getEndDateTimeUtc())
            else:
                serverRow.createData('N/A')
                serverRow.createData('N/A')
                serverRow.createData('N/A')
        
                        
        if not scount: serversTable.createLine('None')
        
        document.serialize()
       
        #
        # ----------------------------------------------------------------------
        #
        # Trackers.xml
        #
        document=XDocDocument( 'All Trackers',	\
            self.resolver.getFile(workspace,'trackers'))
                
        trackersSection=document.createSection('All Trackers')
        trackersTable=trackersSection.createTable(['Name'])

        scount=0
        for tracker in sortedTrackerList:
            
            scount+=1
                    
            trackerRow=trackersTable.createRow()
            trackerRow.createComment(tracker.getName())
                       
            self.insertLink( tracker, workspace, trackerRow.createData())
            
        if not scount: trackersTable.createLine('None')
        
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
        for project in gumpSet.getProjectSequence():
            # :TODO: Next line irrelevent?
            if not gumpSet.inProjectSequence(project): continue       
            
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
            projectRow.createData(secsToElapsedTimeString(project.getElapsedSecs())) 
                
        if not pcount: projectsTable.createLine('None')
        
        document.serialize()
      
        #
        # ----------------------------------------------------------------------
        #
        # notesLog.xml -- Notes log
        #
        document=XDocDocument('Annotations',	\
                self.resolver.getFile(workspace,'notesLog'))  
                    
        notesSection=document.createSection('Negative Annotations')
        notesSection.createParagraph(
            """This page displays entities with errors and/or warning annotations.""")
            
        ncount=0
        for module in gumpSet.getModuleSequence():
            if not gumpSet.inModuleSequence(module): continue               
                                
            moduleSection=None
 
            if module.containsNasties():              
                moduleSection=document.createSection('Module : ' + module.getName())                
                # Link to the module
                self.insertLink(module,workspace,moduleSection.createParagraph()) 
            
                # Display the module annotations
                self.documentAnnotations(moduleSection,module,1)     
                
            for project in module.getProjects():
                if not gumpSet.inProjectSequence(project): continue               
                if not project.containsNasties(): continue
            
                if not moduleSection:				
                    moduleSection=document.createSection('Module : ' + module.getName())

                projectSection=moduleSection.createSection('Project : ' + project.getName())
        
                # Link to the project
                self.insertLink(project,workspace,projectSection.createParagraph())    
            
                # Display the annotations
                self.documentAnnotations(projectSection,project,1)     
        
                ncount+=1
                
        if not ncount: notesSection.createParagraph('None.')
        
        document.serialize()
           
        
        #
        # ----------------------------------------------------------------------
        #
        # diffsLog.xml -- Server Differences log
        #
        document=XDocDocument('Server Differences',	\
                self.resolver.getFile(workspace,'diffsLog'))  
                    
        diffsSection=document.createSection('Server Differences')
        diffsSection.createParagraph(
            """This page displays entities with different states on different servers.""")
            
        dcount=0
        for module in gumpSet.getModuleSequence():
            if not gumpSet.inModuleSequence(module): continue               
                                
            moduleSection=None
            if module.hasServerResults() \
                and module.getServerResults().hasDifferences()	\
                and module.getServerResults().containsFailure() :
                moduleSection=document.createSection('Module : ' + module.getName())                
                # Link to the module
                self.insertLink(module,workspace,moduleSection.createParagraph()) 
            
                # Display the module server links
                self.documentServerLinks(moduleSection,module,workspace,getDepthForObject(workspace))   
                
            for project in module.getProjects():
                if not gumpSet.inProjectSequence(project): continue         
                if not project.hasServerResults(): continue
                if not project.getServerResults().hasDifferences(): continue
                if not project.getServerResults().containsFailure(): continue
            
                if not moduleSection:				
                    moduleSection=document.createSection('Module : ' + module.getName())

                projectSection=moduleSection.createSection('Project : ' + project.getName())
        
                # Link to the project
                self.insertLink(project,workspace,projectSection.createParagraph())    
            
                # Display the project server links
                self.documentServerLinks(projectSection,project,workspace,getDepthForObject(workspace))      
        
                dcount+=1
                
        if not dcount: diffsSection.createParagraph('None.')
        
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
            if not gumpSet.inProjectSequence(project): continue    
            
            pcount+=1
    
            projectRow=projectsTable.createRow()            
            projectRow.createComment(project.getName())          
            self.insertLink(project,workspace,projectRow.createData())     
            self.insertStateIcon(project,workspace,projectRow.createData())    
            projectRow.createData(secsToElapsedTimeString(project.getElapsedSecs()))  
            
            projectRow.createData('%02.2f' % project.getFOGFactor())
                
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
        
        totalAffected=0
        
        projectsSection=document.createSection('Projects with issues...')
        projectsSection.createParagraph("""These are the project that need 'fixing'.
This page helps Gumpmeisters (and others) locate the main areas to focus attention. 
The count of affected indicates relative importance of fixing this project.""")        
        projectsTable=projectsSection.createTable(['Name','Affected',	\
                    'Dependees',	\
                    'Duration\nin state','Project State'])
        pcount=0
        for project in sortedProjectList:
            if not gumpSet.inProjectSequence(project): continue       
            
            if not project.getState()==STATE_FAILED:
                continue
                
            pcount+=1
        
            #
            # Determine the number of projects this module (or its projects)
            # cause not to be run.
            #
            affected=project.determineAffected()
            
            totalAffected += affected
            
            # How long been like this
            seq=stats=project.getStats().sequenceInState
                    
            projectRow=projectsTable.createRow()
            projectRow.createComment(project.getName())
                                    
            self.insertLink(project,workspace,projectRow.createData())   
                        
            projectRow.createData(affected)
            
            projectRow.createData( project.getFullDependeeCount())
            
            projectRow.createData(seq)
            
            self.insertStateIcon(project,workspace,projectRow.createData())
                
        if not pcount: 
            projectsTable.createLine('None')    
        else:
            projectsSection.createParagraph(
                    'Total Affected Projects: ' + str(totalAffected))
                    
        document.serialize()
                 
        #
        # ----------------------------------------------------------------------
        #
        # project_fixes.xml -- Projects w/ fixes in build order
        #
        document=XDocDocument('Project Fixes',	\
            self.resolver.getFile(workspace,'project_fixes'))        
        self.documentSummary(document, workspace.getProjectSummary())
        
        projectsSection=document.createSection('Projects recently fixed...')
        projectsSection.createParagraph("""These are the projects that were 'fixed' (state changed to success) within %s runs.
This page helps Gumpmeisters (and others) observe community progress.
        """ % INSIGNIFICANT_DURATION)      
        
        projectsTable=projectsSection.createTable(['Name',	\
                    'Dependees',	\
                    'Duration\nin state','Project State'])
        pcount=0
        for project in sortedProjectList:
            if not gumpSet.inProjectSequence(project): continue       
            
            if not project.getState()==STATE_SUCCESS or \
                not project.getStats().sequenceInState < INSIGNIFICANT_DURATION:
                continue
                
            pcount+=1
            
            # How long been like this
            seq=stats=project.getStats().sequenceInState
                    
            projectRow=projectsTable.createRow()
            projectRow.createComment(project.getName())
                                    
            self.insertLink(project,workspace,projectRow.createData())   
            
            projectRow.createData( project.getFullDependeeCount())
            
            projectRow.createData(seq)
            
            self.insertStateIcon(project,workspace,projectRow.createData())
                
        if not pcount: 
            projectsTable.createLine('None')   
                    
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
        modulesSection.createParagraph("""These are the modules that need 'fixing', or contained projects that need fixing.
This page helps Gumpmeisters (and others) locate the main areas to focus attention. 
The count of affected indicates relative importance of fixing this module.""")        
        modulesTable=modulesSection.createTable(['Name','Affected','Duration\nin state','Module State',	\
                                    'Project State(s)','Elapsed'])
        
        mcount=0
        for module in sortedModuleList:      
            if not gumpSet.inModuleSequence(module): continue
            
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
            # Determine the number of projects this module (or its projects)
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
            
            moduleRow.createData(secsToElapsedTimeString(module.getElapsedSecs()))
            
        if not mcount: modulesTable.createLine('None')
    
        document.serialize()
        
           
        #
        # ----------------------------------------------------------------------
        #
        # module_fixes.xml
        #
        document=XDocDocument('Modules with fixes',
                    self.resolver.getFile(workspace,'module_fixes'),)            
        self.documentSummary(document, workspace.getProjectSummary())
        
        modulesSection=document.createSection('Modules recently fixed')           
        modulesSection.createParagraph("""These are the modules that were 'fixed' (state changed to success), or contained projects that were fixed, within %s runs.
This page helps Gumpmeisters (and others) observe community progress.
        """ % INSIGNIFICANT_DURATION)      
             
        modulesTable=modulesSection.createTable(['Name','Duration\nin state','Module State',	\
                                    'Project State(s)','Elapsed'])
        
        mcount=0
        for module in sortedModuleList:      
            if not gumpSet.inModuleSequence(module): continue
            
            #
            # Determine if there are mcount, otherwise continue
            #
            mcount=0
            for pair in module.aggregateStates():
                if pair.state == STATE_SUCCESS \
                    and project.getStats().sequenceInState < INSIGNIFICANT_DURATION:
                    mcount=1
                    
            if not mcount: continue
    
            # Shown something...
            mcount+=1
            
            # Determine longest sequence in this (failed) state...
            # for any of the projects
            seq=0
            for project in module.getProjects():
                if project.getState()==STATE_FAILED:
                    stats=project.getStats()        
                    if stats.sequenceInState > seq: seq = stats.sequenceInState
            
            # Display
            moduleRow=modulesTable.createRow()
            moduleRow.createComment(module.getName())     
            self.insertLink(module,workspace,moduleRow.createData())
            
            moduleRow.createData(seq)
                        
            self.insertStateIcon(module,workspace,moduleRow.createData())
            self.insertStateIcons(gumpSet,module,workspace,moduleRow.createData())
            
            moduleRow.createData(secsToElapsedTimeString(module.getElapsedSecs()))
            
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
            if not gumpSet.inModuleSequence(module): continue
            
            mcount+=1
                    
            moduleRow=modulesTable.createRow()
            moduleRow.createComment(module.getName())
                       
            self.insertLink( module, workspace, moduleRow.createData())
            self.insertStateIcon(module,workspace,moduleRow.createData())
            self.insertStateIcons(gumpSet,module,workspace,moduleRow.createData())
            
            moduleRow.createData(secsToElapsedTimeString(module.getElapsedSecs()))
            moduleRow.createData('%02.2f' % module.getFOGFactor())
            
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
            if not gumpSet.inModuleSequence(module): continue
            
            packaged=0
            #
            # Determine if there are packages, otherwise continue
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
                if not gumpSet.inProjectSequence(project): continue   
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
            self.documentRepository(run,repo,workspace,gumpSet)
            
        #
        # Document servers
        #
        for server in workspace.getServers():            
            self.documentServer(run,server,workspace,gumpSet)
            
        #
        # Document trackers
        #
        for tracker in workspace.getTrackers():            
            self.documentTracker(run,tracker,workspace,gumpSet)
            
        #
        # Document modules
        #
        for module in workspace.getModules():
            if not gumpSet.inModuleSequence(module): continue  
            self.documentModule(run,module,workspace,gumpSet)
            
        # Document workspace
        document=XDocDocument('Context',self.resolver.getFile(workspace,'context.xml'))
        stream=StringIO.StringIO() 
        texter=TextDocumenter(stream)  
        texter.document(run)
        stream.seek(0)
        document.createSource(stream.read())
        stream.close()
        document.serialize()
            
        if not workspace.private:
            # Document the workspace XML    
            document=XDocDocument('Definition',self.resolver.getFile(workspace,'workspace.xml'))
            stream=StringIO.StringIO() 
            xmlize('workspace',workspace.xml,stream)
            stream.seek(0)
            document.createSource(stream.read())
            stream.close()
            document.serialize()
      
    def documentRepository(self,run,repo,workspace,gumpSet):
        
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
            
        detailList.createEntry('Redistributable: ', getBooleanString(repo.isRedistributable()))
    
        self.documentXML(document,repo)
        
        self.documentFileList(run,document,repo,'Repository-level Files')
        self.documentWorkList(run,document,repo,'Repository-level Work')

        document.serialize()
      
    def documentServer(self,run,server,workspace,gumpSet):
        
        document=XDocDocument( 'Server : ' + server.getName(),	\
                self.resolver.getFile(server))   
            
        # Provide a description/link back to the server site.
#        descriptionSection=document.createSection('Description') 
#        description=''
#        if server.hasDescription():
#            description=escape(server.getDescription())
#            if not description.strip().endswith('.'):
#                description+='. '    
#        if not description:
#            description='No description provided.'        
#        if server.hasURL():
#            description+=' For more information, see: ' + self.getFork(server.getURL())
#        else:
#            description+=' (No server URL provided).'
#                
#        descriptionSection.createParagraph().createRaw(description)
        
        self.documentAnnotations(document,server)    
        
        detailSection=document.createSection('Server Details')
        detailList=detailSection.createList()        
        
        detailList.createEntry('Name: ', server.getName())
    
        if server.hasType():
            detailList.createEntry('Type: ', server.getType())
    
        if server.hasTitle():
            detailList.createEntry('Title: ', server.getTitle())
    
        if server.hasUrl():
            detailList.createEntry('URL: ').createFork(	\
                    server.getUrl(),server.getUrl())
    
            # Parent 'site' (owner reference)
            if server.hasSite() and not server.getSite() == server.getUrl():
                detailList.createEntry('Site: ').createFork(	\
                        server.getSite(), server.getSite())
                        
        if server.hasResults():
            # :TODO: Do a lot more ....
            if server.hasResultsUrl():
                detailList.createEntry('Results URL: ').createFork(	\
                        server.getResultsUrl(),server.getResultsUrl())    
                                                
                detailList.createEntry('Start Time: ',	\
                        server.getResults().getStartDateTime() + ' ' + \
                        server.getResults().getTimezone())
                                                
                detailList.createEntry('End Time: ',	\
                        server.getResults().getEndDateTime() + ' ' + \
                        server.getResults().getTimezone())
                        
                detailList.createEntry('Start Time (UTC): ',	\
                        server.getResults().getStartDateTimeUtc())
                detailList.createEntry('End Time (UTC): ',	\
                        server.getResults().getEndDateTimeUtc())
        
            
        self.documentXML(document,server)
        
        self.documentFileList(run,document,server,'Server-level Files')
        self.documentWorkList(run,document,server,'Server-level Work')

        document.serialize()
      
             
    def documentTracker(self,run,tracker,workspace,gumpSet):
        
        document=XDocDocument( 'Tracker : ' + tracker.getName(),	\
                self.resolver.getFile(tracker))   
            
        # Provide a description/link back to the tracker site.
#        descriptionSection=document.createSection('Description') 
#        description=''
#        if tracker.hasDescription():
#            description=escape(tracker.getDescription())
#            if not description.strip().endswith('.'):
#                description+='. '    
#        if not description:
#            description='No description provided.'        
#        if tracker.hasURL():
#            description+=' For more information, see: ' + self.getFork(tracker.getURL())
#        else:
#            description+=' (No tracker URL provided).'
#                
#        descriptionSection.createParagraph().createRaw(description)
        
        self.documentAnnotations(document,tracker)    
        
        detailSection=document.createSection('Tracker Details')
        detailList=detailSection.createList()        
        
        detailList.createEntry('Name: ', tracker.getName())
    
        if tracker.hasType():
            detailList.createEntry('Type: ', tracker.getType())
    
        if tracker.hasTitle():
            detailList.createEntry('Title: ', tracker.getTitle())
    
        if tracker.hasUrl():
            detailList.createEntry('URL: ').createFork(	\
                    tracker.getUrl(),tracker.getUrl())
    
            # Parent 'site' (owner reference)
            if tracker.hasSite() and not tracker.getSite() == tracker.getUrl():
                detailList.createEntry('Site: ').createFork(	\
                        tracker.getSite(), tracker.getSite())
            
        self.documentXML(document,tracker)
        
        self.documentFileList(run,document,tracker,'Tracker-level Files')
        self.documentWorkList(run,document,tracker,'Tracker-level Work')

        document.serialize()
      
        
    def documentModule(self,run,module,workspace,gumpSet):
        
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

        metadataLocation=module.getMetadataLocation()
        metadataUrl=module.getMetadataViewUrl()
        if metadataLocation and metadataUrl:  
            descriptionSection.createParagraph('Gump Metadata: ').createFork(metadataUrl, metadataLocation)
            
        if module.cause and not module==module.cause:
             self.insertTypedLink( module.cause, module, \
                 document.createNote( "This module failed due to: "))     
            
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
        self.documentServerLinks(document,module,workspace)     
        
        projectsSection=document.createSection('Projects') 
        if (len(module.getProjects()) > 1):
            self.documentSummary(projectsSection,module.getProjectSummary())
                                            
        if (len(module.getProjects()) > 1):
            ptodosSection=projectsSection.createSection('Projects with Issues')
            ptodosTable=ptodosSection.createTable(['Name','State','Elapsed'])
            pcount=0
            for project in module.getProjects():     
                if not gumpSet.inProjectSequence(project): continue  
            
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
                projectRow.createData(secsToElapsedTimeString(project.getElapsedSecs())) 
	            
	        if not pcount: ptodosTable.createLine('None')
	        
        pallSection=projectsSection.createSection('All Projects')
        pallTable=pallSection.createTable(['Name','State','Elapsed'])
        
        pcount=0
        for project in module.getProjects():     
            if not gumpSet.inProjectSequence(project): continue  
            pcount+=1
            
            projectRow=pallTable.createRow()
            projectRow.createComment(project.getName())
            self.insertLink(project,module,projectRow.createData())
            self.insertStateIcon(project,module,projectRow.createData())                        
            projectRow.createData(secsToElapsedTimeString(project.getElapsedSecs())) 
            
        if not pcount: pallTable.createLine('None')
                           
        self.documentFileList(run,document,module,'Module-level Files')
        self.documentWorkList(run,document,module,'Module-level Work')
        
        #addnSection=document.createSection('Additional Details')
        #addnPara=addnSection.createParagraph()
        #addnPara.createLink('index_details.html',	\
        #                    'More module details ...')
        #                                                                    
        #document.serialize()
        #
        #document=XDocDocument('Module Details : ' + module.getName(),	\
        #            self.resolver.getFile(module, \
        #                            'index_details', \
        #                                '.xml'))
            
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


            repoList.createEntry('Redistributable: ', getBooleanString(module.isRedistributable()))
                
            if module.isRedistributable():
        
                if module.hasJars():
                    if module.jars.hasUrl():
                         repoList.createEntry( "Jars URL: ", module.jars.getUrl())                 
                
           
    #   x.write('<p><strong>Module Config :</strong> <link href=\'xml.html\'>XML</link></p>')
            
        self.documentXML(detailSection,module)

        document.serialize()
      
        # Document Projects
        for project in module.getProjects():
            if not gumpSet.inProjectSequence(project): continue      
            self.documentProject(run,project,workspace,gumpSet)
       
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
        
    def documentProject(self,run,project,workspace,gumpSet): 
        
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
        
        #
        # The 'cause' is something upstream.
        #
        if project.cause and not project==project.cause:
             self.insertTypedLink( project.cause, project, \
                 document.createNote( "This project failed due to: "))              
             
        if project.isPackaged():
            document.createNote('This is a packaged project, not Gumped.')
        elif not project.hasBuildCommand():
            document.createNote('This project is not built by Gump.')        
            
        stateSection=document.createSection('State')
        
        stateList=stateSection.createList()
        stateList.createEntry("Current State: ", project.getStateDescription())  
        if not project.getReason() == REASON_UNSET:
            stateList.createEntry("Reason: " + reasonDescription(project.getReason()))            
        if project.cause and not project==project.cause:
             self.insertTypedLink( project.cause, project, stateList.createEntry( "Root Cause: ")) 
             
        self.documentAnnotations(document,project)     
        
        self.documentServerLinks(document,project,workspace)        
            
        # Project Details (main ones)
        detailsSection=document.createSection('Details')
        detailsList=detailsSection.createList()
            
        self.insertLink(project.getModule(),project,	\
                detailsList.createEntry('Containing Module: '))        
        
        if project.hasHomeDirectory() and project.isVerboseOrDebug():
            detailsList.createEntry('Home Directory: ', project.getHomeDirectory())
            
        if project.hasBaseDirectory() and project.isVerboseOrDebug():
            detailsList.createEntry('Base Directory: ', project.getBaseDirectory())
            
        if project.hasCause() and not project==project.getCause():
            self.insertTypedLink(project.getCause(),project,detailsList.createEntry('Root Cause: '))
            
        e = secsToElapsedTimeString(project.getElapsedSecs())
        if e and project.isVerboseOrDebug(): detailsList.createEntry("Elapsed: ", e)
                
        detailsList.createEntry('Redistributable: ', getBooleanString(project.isRedistributable()))                
                                                      
        # Display nag information
        if project.xml.nag:
            if project.isVerboseOrDebug():
                for nagEntry in project.xml.nag:
                    toaddr=getattr(nagEntry,'to') or workspace.mailinglist
                    fromaddr=getStringFromUnicode(getattr(nagEntry,'from') or workspace.email)
                    detailsList.createEntry('Nag To: ').createFork('mailto:'+toaddr,toaddr)
                    detailsList.createEntry('Nag From: ').createFork('mailto:'+fromaddr,fromaddr)
        elif not project.isPackaged() and project.hasBuildCommand():            
            document.createWarning('This project does not utilize Gump nagging.')  
                             
        metadataLocation=project.getMetadataLocation()
        metadataUrl=project.getMetadataViewUrl()
        if metadataLocation and metadataUrl:  
            detailsList.createEntry('Gump Metadata: ').createFork(metadataUrl, metadataLocation)
                             
        # Note: Leverages previous extraction from project statistics DB
        stats=project.getStats()
        
        statsSection=document.createSection('Statistics')  
        
        #
        # Start annotating with issues...
        #
        if project.isNotOk() and stats.sequenceInState >= SIGNIFICANT_DURATION:
            statsSection.createWarning(	\
                'This project has existed in this failed state for a significant duration.')
        
        statsTable=statsSection.createTable()           
        
        # Generate an SVG for FOG:
        (pngFile,pngTitle) = self.documentFOG(project)
        if pngFile:
            statsTable.createEntry('FOG Factor').createData().createIcon(pngFile,pngTitle)
            
        statsTable.createEntry("FOG Factor: ", '%02.2f' % stats.getFOGFactor())
        statsTable.createEntry('Dependency Depth: ', project.getDependencyDepth())        
        statsTable.createEntry('Total Dependency Depth: ', project.getTotalDependencyDepth())        
        statsTable.createEntry("Successes: ", stats.successes)
        statsTable.createEntry("Failures: ", stats.failures)
        statsTable.createEntry("Prerequisite Failures: ", stats.prereqs)
        statsTable.createEntry("Current State: ", stateDescription(stats.currentState))
        statsTable.createEntry("Duration in state: ", stats.sequenceInState)
        statsTable.createEntry("Start of state: ", secsToDate(stats.startOfState))
        statsTable.createEntry("Previous State: ", stateDescription(stats.previousState))
        
        if stats.first:
            statsTable.createEntry("First Success: ", secsToDate(stats.first))
        if stats.last:
            statsTable.createEntry("Last Success: ", secsToDate(stats.last))
                
        self.documentFileList(run,document,project,'Project-level Files')  
        self.documentWorkList(run,document,project,'Project-level Work')  
                
        #addnSection=document.createSection('Additional Details')
        #addnPara=addnSection.createParagraph()
        #addnPara.createLink(gumpSafeName(project.getName()) + '_details.html',	\
        #                    'More project details ...')                                                                         
        #document.serialize()
        #
        #document=XDocDocument('Project Details : ' + project.getName(),	\
        #            self.resolver.getFile(project, \
        #                            project.getName() + '_details', \
        #                                '.xml'))     
 
    #    x.write('<p><strong>Project Config :</strong> <link href=\'%s\'>XML</link></p>' \
    #                % (getModuleProjectRelativeUrl(modulename,project.name)) )                     
           
           
        if project.isDebug():
            miscSection=document.createSection('Miscellaneous')
        
            #
            #	Outputs (e.g. Jars)
            #
            if project.hasJars():
                outputSection = miscSection.createSection('Outputs')
                outputTable = outputSection.createTable(['Name','Id'])
            
                for jar in project.getJars():
                    outputRow=outputTable.createRow()
                
                    # The name (path) of the jar
                    outputRow.createData(jar.getName())
                
                    # The jar id
                    id=jar.getId() or 'N/A'
                    outputRow.createData(id)                                
        
            
            if project.hasBuildCommand():
            
                if project.hasAnt():                
                    self.documentProperties(miscSection, project.getAnt(), 'Ant Properties')
            
                (classpath,bootclasspath)=project.getClasspathObjects()            
                self.displayClasspath(miscSection, classpath,'Classpath',project)        
                self.displayClasspath(miscSection, bootclasspath,'Boot Classpath',project) 
       
            self.documentXML(miscSection,project)
        
        dependencySection=document.createSection('Dependency')
        
        deps = 0
        depens = 0
        depees = 0
        
        
        #
        # The 'cause' is something upstream. Possibly a project,
        # possibly a module (so determine paths to module projects).
        #
        
#        
#        if project.cause and not project==project.cause:
#            if isinstance(project.cause, Project):
#                for path in project.getDependencyPaths(project.cause):
#                    self.documentDependenciesPath(dependencySection, 'Root Cause Dependency Path',	\
#                            path, 0, 1, project, gumpSet)
#            elif isinstance(project.cause, Module):
#                for causeProject in project.cause.getProjects():
#                    for path in project.getDependencyPaths(causeProject):
#                        self.documentDependenciesPath(dependencySection, 'Root Cause Module Dependency Path',	\
#                                path, 0, 1, project, gumpSet)
#
                
        depens += self.documentDependenciesList(dependencySection, 'Project Dependencies',	\
                    project.getDirectDependencies(), 0, 0, project, gumpSet)
                    
        depees += self.documentDependenciesList(dependencySection, 'Project Dependees',		\
                    project.getDirectDependees(), 1, 0, project, gumpSet)
                    
        if project.isVerboseOrDebug():
            self.documentDependenciesList(dependencySection, 'Full Project Dependencies',	\
                    project.getFullDependencies(), 0, 1, project, gumpSet)
                                                
            self.documentDependenciesList(dependencySection, 'Full Project Dependees',		\
                    project.getFullDependees(), 1, 1, project, gumpSet)
        
        deps = depees + depens
        
        if not deps:
            dependencySection.createNote(	\
            """This project depends upon no others, and no others depend upon it. This project is an island...""")
        else:
            if not depees:
                dependencySection.createNote('No projects depend upon this project.')    
            if not depens:
                dependencySection.createNote('This project depends upon no others.')    
                
        
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
                     
    def documentDependenciesPath(self,xdocNode,title,path,dependees,full,referencingObject,gumpSet):        
        # :TODO: show start and end?
        self.documentDependenciesList(xdocNode,title,path,dependees,full,referencingObject,gumpSet)
        
    def documentDependenciesList(self,xdocNode,title,dependencies,dependees,full,referencingObject,gumpSet):        
        totalDeps=0
                
        if dependencies:
            dependencySection=xdocNode.createSection(title)
            titles=['Name','Type','Inheritence','Ids','State','FOG']
            if full:
                titles.append('Contributor')
            titles.append('Notes')
            dependencyTable=dependencySection.createTable(titles)
            for depend in dependencies:
                
                # Don't document out of scope...
                if not gumpSet.inProjectSequence(depend.getProject()) \
                    or not gumpSet.inProjectSequence(depend.getOwnerProject()) : 
                    continue      
                
                totalDeps += 1
                
                # Project/Owner
                if not dependees:
                    project=depend.getProject()
                else:
                    project=depend.getOwnerProject()
                dependencyRow=dependencyTable.createRow()    
                dependencyRow.createComment(project.getName())
                self.insertLink( project, referencingObject, dependencyRow.createData())                
                
                # Type
                type=''
                if depend.isRuntime():
                    if type: type += ' '    
                    type+='Runtime'              
                if depend.isOptional():
                    if type: type += ' '
                    type+='Optional'               
                if depend.isNoClasspath():
                    if type: type += ' '
                    type+='NoClasspath'                
                dependencyRow.createData(type)
                
                # Inheritence
                dependencyRow.createData(depend.getInheritenceDescription())
                
                # Ids
                ids = depend.getIds() or 'All'
                dependencyRow.createData(ids)
                
                # State Icon
                self.insertStateIcon(project,referencingObject,dependencyRow.createData())
                
                # FOG Factor
                dependencyRow.createData('%02.2f' % project.getFOGFactor())
                
                if full:
                    # Contributor
                    if not dependees:
                        contributor=depend.getOwnerProject()
                    else:
                        contributor=depend.getProject()
                    self.insertLink( contributor, referencingObject, dependencyRow.createData())      
                
                # Dependency Annotations
                noteData=dependencyRow.createData()
                if depend.getAnnotations():
                    for note in depend.getAnnotations():
                        noteData.createText(str(note))
                        noteData.createBreak()                    
                else:
                    noteData.createText('')
        
            dependencySection.createParagraph(
                    'Total ' + title + ' : ' + str(totalDeps))
                    
        return totalDeps            
                
    def documentAnnotations(self,xdocNode,annotatable,noWarn=0):
        
        annotations=annotatable.getAnnotations()
        if not annotations: return        
        
        annotationsSection=xdocNode.createSection('Annotations')
        
        if annotatable.containsNasties() and not noWarn:
            annotationsSection.createWarning(	\
                'Some warnings and/or errors are present within these annotations.')
        
        annotationsTable=annotationsSection.createTable()
        for note in annotations:      
            noteRow=annotationsTable.createRow()
            noteRow.createData(levelName(note.level))
            # TODO if 'text' is a list go through list and
            # when not string get the object link and <link it...
            noteRow.createData(note.text) 
            
    def documentServerLinks(self,xdocNode,linkable,workspace,depth=-1):
        
        servers=workspace.getServers()
        if not servers: return    
        if len(servers) == 1: return # Assume this one.     
        
        # Hack to keep 'tighter' in diffsLog page
        serversSection=xdocNode
        if -1 == depth:
            serversSection=xdocNode.createSection('Servers')  
            serversSection.createParagraph('These links represent this location (and, when available, the status and time) on other servers.')
            
        serversTable=serversSection.createTable()
        serverRow=serversTable.createRow()
        
        serverResults=None
        if isinstance(linkable,Resultable) and linkable.hasServerResults():
            serverResults=linkable.getServerResults()
            
        for server in servers: 
        
            # If we know state on the other server.
            statePair=None
            utcTime=None
            if serverResults and serverResults.has_key(server):
                results=serverResults[server]
                if results:
                    statePair=results.getStatePair()
                    utcTime=results.getStartDateTimeUtc()
                                
            # If we can resolve this object to a URL, then do                        
            if server.hasResolver():
                dataNode=serverRow.createData()    
            
                xdocNode=dataNode.createFork(	\
                        server.getResolver().getUrl(linkable))
            
                xdocNode.createText('On ' + server.getName())
                
                if statePair:
                    xdocNode.createBreak()
                    # Insert the Icon...
                    if -1 == depth:
                        depth=getDepthForObject(linkable)
                    self.insertStatePairIconAtDepth(xdocNode,statePair,depth)      
                    
                if utcTime:
                    xdocNode.createBreak()    
                    xdocNode.createText(utcTime)                                    
                        
    def documentProperties(self,xdocNode,propertyContainer,title='Properties'):
        
        properties=propertyContainer.getProperties()
        sysproperties=propertyContainer.getSysProperties()
        if not properties and not sysproperties: return        
        
        propertiesSection=xdocNode.createSection(title)
                
        if sysproperties:
            # System Properties
            sysPropertiesSection=propertiesSection.createSection('System Properties')  
            syspropertiesTable=sysPropertiesSection.createTable(['Name','Value','XML'])
            for sysproperty in sysproperties:      
                syspropertyRow=syspropertiesTable.createRow()
                syspropertyRow.createData(sysproperty.getName())
                syspropertyRow.createData(sysproperty.getValue())
                syspropertyRow.createData(sysproperty.getXMLData())
        
        if properties:
            # Standard Properties
            standardPropertiesSection=propertiesSection.createSection('Standard Properties')    
            propertiesTable=standardPropertiesSection.createTable(['Name','Value','XML'])
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
        xmldata=stream.read()
        if len(xmldata) < 32000:
            xmlSection.createSource(xmldata)
        else:
            xmlSection.createParagraph('XML Data too large to display.')
        stream.close()
            
    def documentSummary(self,xdocNode,summary,description='Project Summary'):
        if not summary or not summary.projects \
            or not (summary.projects > 1) : return
        
        summarySection=xdocNode.createSection(description)
        
        summarySection.createParagraph('Overall project success : ' +	\
                '%02.2f' % summary.overallPercentage + '%')
        
        summaryTable=summarySection.createTable(['Projects','Successes','Failures','Prereqs',	\
            'No Works','Packages'])
        
        summaryTable.createRow([ '%02d' % summary.projects, \
                                '%02d' % summary.successes + \
                                ' (' + '%02.2f' % summary.successesPercentage + '%)', \
                                '%02d' % summary.failures + \
                                ' (' + '%02.2f' % summary.failuresPercentage + '%)',	\
                                '%02d' % summary.prereqs + \
                                ' (' + '%02.2f' % summary.prereqsPercentage + '%)', \
                                '%02d' % summary.noworks + \
                                ' (' + '%02.2f' % summary.noworksPercentage + '%)', \
                                '%02d' % summary.packages + \
                                ' (' + '%02.2f' % summary.packagesPercentage + '%)'] )
        
      
    def documentWorkList(self,run,xdocNode,workable,description='Work'):
        worklist=workable.getWorkList()
        
        if not worklist: return
        
        workSection=xdocNode.createSection(description)        
        workTable=workSection.createTable(['Name','State','Start','Elapsed'])
        
        for work in worklist:
            workRow=workTable.createRow()
            workRow.createComment(work.getName())
            
            self.insertLink(work,workable,workRow.createData())  
            workRow.createData(stateDescription(work.state))
            if isinstance(work,TimedWorkItem):      
                workRow.createData(secsToDate(work.result.start_time))
                workRow.createData(secsToElapsedTimeString(work.getElapsedSecs()))
            else:
                workRow.createData('N/A')
                workRow.createData('N/A')
        
        #
        # Do a tail on all work that failed...
        #
        for work in worklist:
            if isinstance(work,CommandWorkItem):      
                if not STATE_SUCCESS == work.state:
                    tail=work.tail(50,100,'...\n','    ')
                    if tail:
                        #
                        # Write out the 'tail'
                        #
                        workSection	\
                            .createSection('Tail of ' + workTypeName(work.type) + ' : ' + work.command.name)	\
                            .createSource(tail)
                
        
        #
        # Go document the others...
        #
        for work in worklist:
            self.documentWork(run.getWorkspace(),work)
            
    def documentWork(self,workspace,work):
        if isinstance(work,CommandWorkItem):    
            wdocument=XDocDocument(	\
                workTypeName(work.type) + ' : ' + work.command.name,	\
                    self.resolver.getFile(work))
                    
            workSection=wdocument.createSection('Details')
            
            workList=workSection.createList() 
            workList.createEntry("State: ", stateDescription(work.state))
            
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
            e = secsToElapsedTimeString(work.getElapsedSecs())
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
                            
                            line=wrapLine(line,100,'...\n','    ')
                            
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
          
    def documentFileList(self,run,xdocNode,holder,description='Files'):
        filelist=holder.getFileList()
        
        if not filelist: return
        
        fileSection=xdocNode.createSection(description)        
        fileTable=fileSection.createTable(['Name','Type','Path'])
        
        for listedFile in filelist:
            fileRow=fileTable.createRow()
            fileRow.createComment(listedFile.getName())            
            self.insertLink(listedFile,holder,fileRow.createData())  
            fileRow.createData(listedFile.getTypeDescription())
            fileRow.createData(listedFile.getPath())
                        
        #
        # Go document the others...
        #
        for fileReference in filelist:
            self.documentFile(run.getWorkspace(),fileReference)
            
    def documentFile(self,workspace,fileReference):
        
        fdocument=XDocDocument(	\
                fileReference.getTypeDescription() + ' : ' + fileReference.getName(),	\
                self.resolver.getFile(fileReference))
                    
        fileSection=fdocument.createSection('Details')
            
        fileList=fileSection.createList() 
        fileList.createEntry("Type: ", fileReference.getTypeDescription())
            
        self.insertTypedLink(fileReference.getOwner(),	\
                    fileReference,	\
                    fileList.createEntry("Owner (Referencer): "))
            
        if fileReference.exists():
            if fileReference.isDirectory():                
                
                listingSection=fdocument.createSection('Directory Contents')
                listingTable=listingSection.createTable(['Filename','Type','Size'])
                
                directory=fileReference.getPath()
                
                # Change to os.walk once we can move to Python 2.3
                files=os.listdir(directory)
                files.sort()
                for listedFile in files:
                    
                    filePath=os.path.abspath(os.path.join(directory,listedFile))
                    listingRow=listingTable.createRow()
                    
                    #
                    listingRow.createData(listedFile)    
                    
                    if os.path.isdir(filePath):
                        listingRow.createData('Directory')
                        listingRow.createData('N/A')
                    else:
                        listingRow.createData('File')    
                        listingRow.createData(str(os.path.getsize(filePath)))                                                
            else:    
                #
                # Show the content...
                #
                outputSection=fdocument.createSection('File Contents')
                outputSource=outputSection.createSource()
                output=fileReference.getPath()
                if output:
                    try:
                        o=None
                        try:
                            # Keep a length count to not exceed 32K
                            size=0
                            o=open(output, 'r')
                            line=o.readline()
                            while line:
                            
                                line=wrapLine(line,100,'...\n','    ')
                            
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
                    outputSource.createText('No contents in this file.')
        else:
            fdocument.createParagraph('No such file or directory.')
           
        fdocument.serialize()
        fdocument=None
            
    def documentFOG(self,object,base=None):
    
        stats = object.getStats()
        name=object.getName()
        if not base: base=object
    
        #
        # Generate an SVG: 'FOG'
        #
        if stats.successes+stats.failures+stats.prereqs > 0:
            svgFile=self.resolver.getFile(base,name+'_FOG','.svg')
            pngFile=os.path.basename(svgFile).replace('.svg','.png')
            from gump.svg.scale import ScaleDiagram
            diagram=ScaleDiagram([stats.successes,stats.prereqs,stats.failures])
            diagram.generateDiagram().serializeToFile(svgFile)
            
            return (pngFile, 'FOG Factor')
            
        return (None, None)
                
    #####################################################################           
    #
    # Helper Methods
    #     
    def getFork(self,href,name=None):
        if not name: name = href
        return '<fork href=\'%s\'>%s</fork>' % (escape(href),escape(name))
            
    def insertStateDescription(self,toObject,fromObject,xdocNode):
        node=xdocNode.createText(stateDescription(toObject.getState()))
        if not toObject.getReason()==REASON_UNSET: 
            xdocNode.createText(' with reason '+reasonDescription(toObject.getReason()))
            
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
            if not gumpSet.inProjectSequence(project): continue     
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
        postfix=''
        
        #
        # If we are looking for what set the state, look at
        # work first. Pick the first not working. If not found
        # link to the annotations section.
        #
        if state and isinstance(toObject,Workable):
            for work in toObject.getWorkList():
                if not url:
                    if not work.state==STATE_SUCCESS:
                        url=getRelativeLocation(work,fromObject,'.html').serialize()
                        
            # This assumes that if it failed, but doesn't have work that
            # mark's it as failed then something in the nasties must refer
            # to the problem.
            if not url:
                if isinstance(toObject,Annotatable) and toObject.containsNasties():
                    postfix='#Annotations'
        
        if not url:
            if fromObject:
                url=getRelativeLocation(toObject,fromObject,'.html').serialize()
            else:
                url=self.resolver.getAbsoluteUrl(toObject)
            
        return url + postfix
    
    def insertStatePairIcon(self,xdocNode,toObject,fromObject):
        pair=toObject.getStatePair()
        depth=getDepthForObject(fromObject)
        self.insertStatePairIconAtDepth(xdocNode,pair,depth)
                
    def insertStatePairIconAtDepth(self,xdocNode,pair,depth):
        # :TODO: Move this to some resolver, and share with RSS
        sname=stateDescription(pair.state)
        rstring=reasonDescription(pair.reason)    

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
        Statistics from Gump show the depth and health of inter-relationships. 
        """)
            
        
        overviewSection=document.createSection('Overview')
        overviewList=overviewSection.createList()
        overviewList.createEntry('Modules: ', stats.wguru.modulesInWorkspace)
        overviewList.createEntry('Projects: ', stats.wguru.projectsInWorkspace)
        overviewList.createEntry('Avg Projects Per Module: ', stats.wguru.averageProjectsPerModule)                      
          
        self.documentSummary(overviewSection,workspace.getProjectSummary())    
        
        mstatsSection=document.createSection('Module Statistics')
        mstatsTable=mstatsSection.createTable(['Page','Description'])
                
        # Modules By Elapsed Time
        mByE=self.documentModulesByElapsed(stats, run, workspace, gumpSet)                
        mstatsRow=mstatsTable.createRow()
        mstatsRow.createData().createLink(mByE, 'Modules By Elapsed Time')
        mstatsRow.createData('Time spent working on this module.')
                
        # Modules By Project #
        mByP=self.documentModulesByProjects(stats, run, workspace, gumpSet)           
        mstatsRow=mstatsTable.createRow()
        mstatsRow.createData().createLink(mByP, 'Modules By Project #')
        mstatsRow.createData('Number of projects within the module.')
        
        # Modules By Dependencies
        mByDep=self.documentModulesByDependencies(stats, run, workspace, gumpSet)           
        mstatsRow=mstatsTable.createRow()
        mstatsRow.createData().createLink(mByDep, 'Modules By Dependencies #')
        mstatsRow.createData('Number of dependencies within the module.')        
        
        # Modules By Dependees
        mByDepees=self.documentModulesByDependees(stats, run, workspace, gumpSet)           
        mstatsRow=mstatsTable.createRow()
        mstatsRow.createData().createLink(mByDepees, 'Modules By Dependees #')
        mstatsRow.createData('Number of dependees on the module.')
        
        # Modules By FOG Factor
        mByFOG=self.documentModulesByFOGFactor(stats, run, workspace, gumpSet)           
        mstatsRow=mstatsTable.createRow()
        mstatsRow.createData().createLink(mByFOG, 'Modules By FOG Factor')
        mstatsRow.createData('Friend of Gump (FOG) Factor. A measure of dependability (for other Gumpers).')
                
        # Modules By Last Updated
        mByLU=self.documentModulesByLastUpdated(stats, run, workspace, gumpSet)           
        mstatsRow=mstatsTable.createRow()
        mstatsRow.createData().createLink(mByLU, 'Modules By Last Updated')
        mstatsRow.createData('Best guess at last code change (in source control).')
                                
        pstatsSection=document.createSection('Project Statistics')
        pstatsTable=pstatsSection.createTable(['Page','Description'])
        
        # Projects By Elapsed
        pByE=self.documentProjectsByElapsed(stats, run, workspace, gumpSet)           
        pstatsRow=pstatsTable.createRow()
        pstatsRow.createData().createLink(pByE, 'Projects By Elapsed Time')
        pstatsRow.createData('Time spent working on this project.')
                                        
        # Projects By Dependencies
        pByDep=self.documentProjectsByDependencies(stats, run, workspace, gumpSet)           
        pstatsRow=pstatsTable.createRow()
        pstatsRow.createData().createLink(pByDep, 'Projects By Dependencies')
        pstatsRow.createData('Number of dependencies for the project.')
                                        
        # Projects By Dependees
        pByDepees=self.documentProjectsByDependees(stats, run, workspace, gumpSet)           
        pstatsRow=pstatsTable.createRow()
        pstatsRow.createData().createLink(pByDepees, 'Projects By Dependees')
        pstatsRow.createData('Number of dependees for the project.')
                                        
        # Projects By FOG Factor
        pByFOG=self.documentProjectsByFOGFactor(stats, run, workspace, gumpSet)           
        pstatsRow=pstatsTable.createRow()
        pstatsRow.createData().createLink(pByFOG, 'Projects By FOG Factor')
        pstatsRow.createData('Friend of Gump (FOG) Factor. A measure of dependability (for other Gumpers).')
                                        
        # Projects By Sequence
        pBySeq=self.documentProjectsBySequenceInState(stats, run, workspace, gumpSet)           
        pstatsRow=pstatsTable.createRow()
        pstatsRow.createData().createLink(pBySeq, 'Projects By Duration in state')
        pstatsRow.createData('Duration in current state.')
        
        document.serialize()  
    
    def documentModulesByElapsed(self,stats,run,workspace,gumpSet):
        fileName='module_elapsed'
        documentFile=self.resolver.getFile(stats,fileName)
        document=XDocDocument('Modules By Elapsed Time', documentFile)
        
        elapsedTable=document.createTable(['Modules By Elapsed'])
        for module in stats.modulesByElapsed:        
            if not gumpSet.inModuleSequence(module): continue
            elapsedRow=elapsedTable.createRow()
            self.insertLink( module, stats, elapsedRow.createData())
            elapsedRow.createData(secsToElapsedTimeString(module.getElapsedSecs()))
            
        document.serialize()
        
        return fileName + '.html'
    
    def documentModulesByProjects(self,stats,run,workspace,gumpSet):
        fileName='module_projects'
        documentFile=self.resolver.getFile(stats,fileName)
        document=XDocDocument('Modules By Project Count',	documentFile)
        
        mprojsTable=document.createTable(['Modules By Project Count'])
        for module in stats.modulesByProjectCount:         
            if not gumpSet.inModuleSequence(module): continue     
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
        
        return fileName + '.html'
     
    def documentModulesByDependencies(self,stats,run,workspace,gumpSet):
        fileName='module_dependencies'
        documentFile=self.resolver.getFile(stats,fileName)
        document=XDocDocument('Modules By Dependency Count', documentFile)
        
        dependenciesTable=document.createTable(['Module','Full Dependency Count'])
        for module in stats.modulesByTotalDependencies:         
            if not gumpSet.inModuleSequence(module): continue   
            dependenciesRow=dependenciesTable.createRow()
            self.insertLink( module, stats, dependenciesRow.createData())
            dependenciesRow.createData( module.getFullDependencyCount())
            
            #projectsString=''
            #for project in module.getDepends():
            #    projectsString+=getContextLink(project)
            #    projectsString+=' '            
            #dependenciesRow.createData(projectsString)        
        
        document.serialize()
        
        return fileName + '.html'
             
     
    def documentModulesByDependees(self,stats,run,workspace,gumpSet):
        fileName='module_dependees'
        documentFile=self.resolver.getFile(stats,fileName)    
        document=XDocDocument('Modules By Dependee Count', documentFile)
        
        dependeesTable=document.createTable(['Module','Full Dependee Count'])
        for module in stats.modulesByTotalDependees:         
            if not gumpSet.inModuleSequence(module): continue   
            dependeesRow=dependeesTable.createRow()
            self.insertLink( module, stats, dependeesRow.createData())
            dependeesRow.createData(module.getFullDependeeCount())
            
            #projectsString=''
            #for project in module.getDependees():
            #    projectsString+=getContextLink(project)
            #    projectsString+=' '            
            #dependeesRow.createData(projectsString)
        
        document.serialize()
        
        return fileName + '.html'
        
    def documentModulesByFOGFactor(self,stats,run,workspace,gumpSet):
        fileName='module_fogfactor'
        documentFile=self.resolver.getFile(stats,fileName)    
        document=XDocDocument('Modules By FOG Factor',	documentFile)        
        fogTable=document.createTable(['Module','FOG Factor'])
        for module in stats.modulesByFOGFactor:        
            if not gumpSet.inModuleSequence(module): continue    
            fogRow=fogTable.createRow()            
            self.insertLink( module, stats, fogRow.createData())                
            fogRow.createData('%02.2f' % module.getFOGFactor())
            
        document.serialize()
        
        return fileName + '.html'
    
    def documentModulesByLastUpdated(self,stats,run,workspace,gumpSet):
        fileName='module_updated'
        documentFile=self.resolver.getFile(stats,fileName)    
        document=XDocDocument('Modules By Last Updated', documentFile)        
        updTable=document.createTable(['Module','Last Updated Date','Last Updated'])
        modules=0
        for module in stats.modulesByLastUpdated:        
            if not gumpSet.inModuleSequence(module): continue   
            if module.isPackaged(): continue 
            updRow=updTable.createRow()            
            self.insertLink( module, stats, updRow.createData())                
            updRow.createData(secsToDate(module.getLastUpdated()))
            updRow.createData(	\
                getGeneralSinceDescription(module.getLastUpdated()))
            modules+=1                    
        if not modules: updTable.createLine('None')
            
        document.serialize()
        
        return fileName + '.html'
    
    def documentProjectsByElapsed(self,stats,run,workspace,gumpSet):
        fileName='project_elapsed'
        documentFile=self.resolver.getFile(stats,fileName)    
        document=XDocDocument('Projects By Elapsed Time',	documentFile)
        
        elapsedTable=document.createTable(['Projects By Elapsed'])
        for project in stats.projectsByElapsed:        
            if not gumpSet.inProjectSequence(project): continue
            elapsedRow=elapsedTable.createRow()
            self.insertLink( project, stats, elapsedRow.createData())
            elapsedRow.createData(secsToElapsedTimeString(project.getElapsedSecs()))
            
        document.serialize()
        
        return fileName + '.html'
     
    def documentProjectsByDependencies(self,stats,run,workspace,gumpSet):
        fileName='project_dependencies'
        documentFile=self.resolver.getFile(stats,fileName)    
        document=XDocDocument('Projects By Dependency Count',	 documentFile)
        
        dependenciesTable=document.createTable(['Project','Direct Dependency Count', 'Full Dependency Count'])
        for project in stats.projectsByTotalDependencies:         
            if not gumpSet.inProjectSequence(project): continue   
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
        
        return fileName + '.html'
             
     
    def documentProjectsByDependees(self,stats,run,workspace,gumpSet):
        fileName='project_dependees'
        documentFile=self.resolver.getFile(stats,fileName)    
        document=XDocDocument('Projects By Dependee Count', documentFile)
        
        dependeesTable=document.createTable(['Project','Direct Dependee Count', 'Full Dependee Count'])
        for project in stats.projectsByTotalDependees:         
            if not gumpSet.inProjectSequence(project): continue   
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
        
        return fileName + '.html'
        
    def documentProjectsByFOGFactor(self,stats,run,workspace,gumpSet):
        fileName='project_fogfactor'
        documentFile=self.resolver.getFile(stats,fileName)    
        document=XDocDocument('Projects By FOG Factor',	 documentFile)        
        fogTable=document.createTable(['Project','Successes','Failures','Preq-Failures','FOG Factor'])
        for project in stats.projectsByFOGFactor:        
            if not gumpSet.inProjectSequence(project): continue    
            fogRow=fogTable.createRow()            
            self.insertLink( project, stats, fogRow.createData())  
                 
            pstats=project.getStats()
            
            fogRow.createData(pstats.successes)
            fogRow.createData(pstats.failures)
            fogRow.createData(pstats.prereqs)
            fogRow.createData('%02.2f' % pstats.getFOGFactor())
            
            
            # Generate an SVG for FOG:
            (pngFile,pngTitle) = self.documentFOG(project,stats)
            if pngFile:
                fogRow.createData().createIcon(pngFile,pngTitle)
            else:
                fogRow.createData('Not Available')    
                
                
            
        document.serialize()   
        
        return fileName + '.html'
        
    def documentProjectsBySequenceInState(self,stats,run,workspace,gumpSet):
        fileName='project_durstate'
        documentFile=self.resolver.getFile(stats,fileName)    
        document=XDocDocument('Projects By Duration In State',	documentFile)        
        durTable=document.createTable(['Project','Duration\nIn State','State'])
        for project in stats.projectsBySequenceInState:        
            if not gumpSet.inProjectSequence(project): continue    
            durRow=durTable.createRow()            
            self.insertLink( project, stats, durRow.createData())  
                 
            pstats=project.getStats()
            
            durRow.createData(pstats.sequenceInState)
            durRow.createData(stateDescription(pstats.currentState))
            
        document.serialize()
        
        return fileName + '.html'

        
    #####################################################################           
    #
    # XRef Pages
    #           
    def documentXRef(self,run,workspace,gumpSet):
        
        xref=XRefGuru(workspace)
        
        document=XDocDocument('Cross Reference',self.resolver.getFile(xref))
    
        document.createParagraph("""
        Obscure views into projects/modules... 
        """)
            
        ##################################################################3
        # Modules ...........
        mxrefSection=document.createSection('Module Cross Reference')
        mxrefTable=mxrefSection.createTable(['Page','Description'])
                
        # Modules By Repository
        mByR=self.documentModulesByRepository(xref, run, workspace, gumpSet)                
        mxrefRow=mxrefTable.createRow()
        mxrefRow.createData().createLink(mByR, 'Modules By Repository')
        mxrefRow.createData('The repository that contains the module.')
        
        # Modules By Package
        mByP=self.documentModulesByPackage(xref, run, workspace, gumpSet)                
        mxrefRow=mxrefTable.createRow()
        mxrefRow.createData().createLink(mByP, 'Modules By Package')
        mxrefRow.createData('The package(s) contained in the module.')
        
        # Modules By Description
        mByD=self.documentModulesByDescription(xref, run, workspace, gumpSet)                
        mxrefRow=mxrefTable.createRow()
        mxrefRow.createData().createLink(mByD, 'Modules By Description')
        mxrefRow.createData('The descriptions for the module.')
        
        ##################################################################3
        # Projects ...........
        
        pxrefSection=document.createSection('Project Cross Reference')
        pxrefTable=pxrefSection.createTable(['Page','Description'])
                        
        # Projects By Package
        pByP=self.documentProjectsByPackage(xref, run, workspace, gumpSet)                
        pxrefRow=pxrefTable.createRow()
        pxrefRow.createData().createLink(pByP, 'Projects By Package')
        pxrefRow.createData('The package(s) contained in the project.')
        
        # Projects By Description
        pByD=self.documentProjectsByDescription(xref, run, workspace, gumpSet)                
        pxrefRow=pxrefTable.createRow()
        pxrefRow.createData().createLink(pByD, 'Projects By Description')
        pxrefRow.createData('The descriptions for the project.')
                
        # Projects By Outputs
        pByO=self.documentProjectsByOutput(xref, run, workspace, gumpSet)                
        pxrefRow=pxrefTable.createRow()
        pxrefRow.createData().createLink(pByO, 'Projects By Output')
        pxrefRow.createData('The outputs for the project, e.g. jars.')
             
        # Projects By Output Ids
        pByOI=self.documentProjectsByOutputId(xref, run, workspace, gumpSet)                
        pxrefRow=pxrefTable.createRow()
        pxrefRow.createData().createLink(pByOI, 'Projects By Output Identifier')
        pxrefRow.createData('The identifiers for outputs for the project, e.g. jars.')
             
        # Projects By Descriptor Location
        pByDL=self.documentProjectsByDescriptorLocation(xref, run, workspace, gumpSet)                
        pxrefRow=pxrefTable.createRow()
        pxrefRow.createData().createLink(pByDL, 'Projects By Descriptor Location')
        pxrefRow.createData('The descriptor for the project.')
        
        document.serialize()
        
    def documentModulesByRepository(self,xref,run,workspace,gumpSet):
        fileName='repo_module'
        documentFile=self.resolver.getFile(xref,fileName)        
        document=XDocDocument('Modules By Repository',	documentFile)
        
        repoMap=xref.getRepositoryToModuleMap()
        repoList=createOrderedList(repoMap.keys())
        if repoList:
            for repo in repoList:
                moduleList=createOrderedList(repoMap.get(repo))            
                repoSection=document.createSection(repo.getName())            
                self.insertLink( repo, xref, 	\
                    repoSection.createParagraph('Repository Definition: '))
        
                moduleRepoTable=repoSection.createTable(['Modules'])
                for module in moduleList:        
                    if not gumpSet.inModuleSequence(module): continue
                    moduleRepoRow=moduleRepoTable.createRow()
                    self.insertLink( module, xref, moduleRepoRow.createData())
                    
        else:
            document.createParagraph('No repositories')
          
        document.serialize()    
        
        return fileName + '.html'
        
    def documentModulesByPackage(self,xref,run,workspace,gumpSet):
        fileName='package_module'
        documentFile=self.resolver.getFile(xref,fileName)            
        document=XDocDocument('Modules By Package',	documentFile)
        
        packageTable=document.createTable(['Modules By Package'])
        
        packageMap=xref.getPackageToModuleMap()
        for package in createOrderedList(packageMap.keys()):
            
            moduleList=createOrderedList(packageMap.get(package)) 
            
            hasSome=0
            for module in moduleList:        
                if not gumpSet.inModuleSequence(module): continue
                hasSome=1
                
            if hasSome:
                packageRow=packageTable.createRow()
                packageRow.createData(package)
            
                moduleData=packageRow.createData()
                for module in moduleList:        
                    if not gumpSet.inModuleSequence(module): continue                
                    self.insertLink(module, xref, moduleData)
                    moduleData.createText(' ')
          
        document.serialize()
        
        return fileName + '.html'
        
        
    def documentModulesByDescription(self,xref,run,workspace,gumpSet):
        fileName='description_module'
        documentFile=self.resolver.getFile(xref,fileName)            
        document=XDocDocument('Modules By Description',	documentFile)
        
        descriptionTable=document.createTable(['Modules By Description'])
        
        descriptionMap=xref.getDescriptionToModuleMap()
        for description in createOrderedList(descriptionMap.keys()):
            
            moduleList=createOrderedList(descriptionMap.get(description)) 
            
            hasSome=0
            for module in moduleList:        
                if not gumpSet.inModuleSequence(module): continue
                hasSome=1
                
            if hasSome:
                descriptionRow=descriptionTable.createRow()
                descriptionRow.createData(description)
            
                moduleData=descriptionRow.createData()
                for module in moduleList:        
                    if not gumpSet.inModuleSequence(module): continue                
                    self.insertLink(module, xref, moduleData)
                    moduleData.createText(' ')
          
        document.serialize()
        
        return fileName + '.html'
        
    def documentProjectsByPackage(self,xref,run,workspace,gumpSet):
        fileName='package_project'
        documentFile=self.resolver.getFile(xref,fileName)            
        document=XDocDocument('Projects By Package',	documentFile)
        
        packageTable=document.createTable(['Projects By Package'])
        
        packageMap=xref.getPackageToProjectMap()
        for package in createOrderedList(packageMap.keys()):
                            
            projectList=createOrderedList(packageMap.get(package)) 
            
            hasSome=0
            for project in projectList:        
                if not gumpSet.inProjectSequence(project): continue
                hasSome=1
                
            if hasSome:
                packageRow=packageTable.createRow()
                packageRow.createData(package)
            
                projectData=packageRow.createData()
                for project in projectList:        
                    if not gumpSet.inProjectSequence(project): continue                
                    self.insertLink(project, xref, projectData)
                    projectData.createText(' ')
          
        document.serialize()
        
        return fileName + '.html'

    def documentProjectsByDescription(self,xref,run,workspace,gumpSet):
        fileName='description_project'
        documentFile=self.resolver.getFile(xref,fileName)            
        document=XDocDocument('Projects By Description',	documentFile)
        
        descriptionTable=document.createTable(['Projects By Description'])
        
        descriptionMap=xref.getDescriptionToProjectMap()
        for description in createOrderedList(descriptionMap.keys()):
                            
            projectList=createOrderedList(descriptionMap.get(description)) 
            
            hasSome=0
            for project in projectList:        
                if not gumpSet.inProjectSequence(project): continue
                hasSome=1
                
            if hasSome:
                descriptionRow=descriptionTable.createRow()
                descriptionRow.createData(description)
            
                projectData=descriptionRow.createData()
                for project in projectList:        
                    if not gumpSet.inProjectSequence(project): continue                
                    self.insertLink(project, xref, projectData)
                    projectData.createText(' ')
          
        document.serialize()
        
        return fileName + '.html'
 
        
    def documentProjectsByOutput(self,xref,run,workspace,gumpSet):
        fileName='output_project'
        documentFile=self.resolver.getFile(xref,fileName)            
        document=XDocDocument('Projects By Outputs (e.g. Jars)',	documentFile)
        
        outputTable=document.createTable(['Projects By Outputs (e.g. Jars)'])
        
        outputMap=xref.getOutputToProjectMap()
        for output in createOrderedList(outputMap.keys()):
                            
            projectList=createOrderedList(outputMap.get(output)) 
            
            hasSome=0
            for project in projectList:        
                if not gumpSet.inProjectSequence(project): continue
                hasSome=1
                
            if hasSome:
                outputRow=outputTable.createRow()
                outputRow.createData(output)
                
                projectData=outputRow.createData()
                for project in projectList:        
                    if not gumpSet.inProjectSequence(project): continue                
                    self.insertLink(project, xref, projectData)
                    projectData.createText(' ')
          
        document.serialize()
        
        return fileName + '.html'
        
    def documentProjectsByOutputId(self,xref,run,workspace,gumpSet):
        fileName='output_id_project'
        documentFile=self.resolver.getFile(xref,fileName)            
        document=XDocDocument('Projects By Output Identifiers',	documentFile)
        
        outputTable=document.createTable(['Projects By Output Identifiers'])
        
        outputMap=xref.getOutputIdToProjectMap()
        for outputId in createOrderedList(outputMap.keys()):
                            
            projectList=createOrderedList(outputMap.get(outputId)) 
            
            hasSome=0
            for project in projectList:        
                if not gumpSet.inProjectSequence(project): continue
                hasSome=1
                
            if hasSome:
                outputRow=outputTable.createRow()
                outputRow.createData(outputId)
                
                projectData=outputRow.createData()
                for project in projectList:        
                    if not gumpSet.inProjectSequence(project): continue                
                    self.insertLink(project, xref, projectData)
                    projectData.createText(' ')
          
        document.serialize()
        
        return fileName + '.html'
        
    def documentProjectsByDescriptorLocation(self,xref,run,workspace,gumpSet):
        fileName='descriptor_project'
        documentFile=self.resolver.getFile(xref,fileName)            
        document=XDocDocument('Projects By Descriptor Location',	documentFile)
        
        descLocnTable=document.createTable(['Projects By Descriptor Location'])
        
        descLocnMap=xref.getDescriptorLocationToProjectMap()
        for descLocn in createOrderedList(descLocnMap.keys()):
                            
            projectList=createOrderedList(descLocnMap.get(descLocn)) 
            
            hasSome=0
            for project in projectList:        
                if not gumpSet.inProjectSequence(project): continue
                hasSome=1
                
            if hasSome:
                descLocnRow=descLocnTable.createRow()
                descLocnRow.createData(descLocn)
            
                projectData=descLocnRow.createData()
                for project in projectList:        
                    if not gumpSet.inProjectSequence(project): continue                
                    self.insertLink(project, xref, projectData)
                    projectData.createText(' ')
          
        document.serialize()
        
        return fileName + '.html'
 
        
        
