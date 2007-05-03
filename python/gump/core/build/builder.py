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

__revision__  = "$Rev: 36667 $"
__date__      = "$Date: 2004-08-20 08:55:45 -0600 (Fri, 20 Aug 2004) $"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"


"""
	
	This is the main project builder for gump. 
	
	1) Pre build tasks (deleting directories/files, making directories)
	are performed here.
	
	2) Leveraging ant and/or maven and/or script 'assistants' the
	project work is done (based of 'stat's, so --debug can be set in
	a series of failures)
	
	3) Post build tasks (verifying outputs exist, publishing to repositories,
	etc).

"""

import os.path
import sys

from gump import log

from gump.core.run.gumprun import *
from gump.core.config import dir, default, basicConfig

from gump.core.build.script import ScriptBuilder
from gump.core.build.ant import AntBuilder
from gump.core.build.nant import NAntBuilder
from gump.core.build.maven import MavenBuilder
from gump.core.build.mvn import Maven2Builder
from gump.core.build.configure import ConfigureBuilder
from gump.core.build.make import MakeBuilder

from gump.util import dump, display, getIndent, logResourceUtilization, \
                            invokeGarbageCollection
                            
from gump.util.note import Annotatable
from gump.util.work import *

from gump.util.tools import *

from gump.core.model.workspace import *
from gump.core.model.module import Module
from gump.core.model.project import Project
from gump.core.model.depend import  ProjectDependency
from gump.core.model.stats import *
from gump.core.model.state import *


###############################################################################
# Classes
###############################################################################

class GumpBuilder(gump.core.run.gumprun.RunSpecific):
    
    def __init__(self,run):
        gump.core.run.gumprun.RunSpecific.__init__(self,run)
        
        self.ant=AntBuilder(run)
        self.nant=NAntBuilder(run)
        self.maven=MavenBuilder(run)
        self.mvn=Maven2Builder(run)
        self.script=ScriptBuilder(run)
        self.configure = ConfigureBuilder(run)
        self.make = MakeBuilder(run);

        # Place repository in repodir
        self.repository=self.run.getOutputsRepository()        
            
    def buildProject(self,project):
        """
        
        Build a single project (within the overall context)
        
        """
        
        workspace=self.run.getWorkspace()
                 
        log.info('Build Project: #[' + `project.getPosition()` + '] : ' + project.getName() + ' :  [state:' \
                        + project.getStateDescription() + ']')
                  
        languageHelper=self.run.getLanguageHelper(project.getLanguageType())
          
        # Extract stats (in case we want to do conditional processing)            
        stats=None
        if project.hasStats():
            stats=project.getStats()
        
        # :TODO: Code this nicer, perhaps...    
        if project.isPackaged():             
            self.performProjectPackageProcessing(project, languageHelper, stats)
        else:
            # Do this even if not ok
            self.performPreBuild(project, languageHelper, stats)

            if project.okToPerformWork():        
                log.debug('Performing Build Upon: [' + `project.getPosition()` + '] ' + project.getName())

                #if project.isPrereqFailed():
                #    project.addWarning('Building despite certain prerequisite failures [repository build].')
                    
                # Turn on --verbose or --debug if failing ...
                #if stats:
                #    if (not STATE_SUCCESS == stats.currentState) and \
                #            not project.isVerboseOrDebug():
                #        if stats.sequenceInState > SIGNIFICANT_DURATION:
                #            project.addInfo('Enable "debug" output, due to a sequence of %s previous errors.' % stats.sequenceInState)
                #            project.setDebug(True)
                #        else:
                #            project.addInfo('Enable "verbose" output, due to %s previous error(s).' % stats.sequenceInState)    
                #            project.setVerbose(True)

                # Pick your poison..
                if project.hasScript():
                    self.script.buildProject(project, languageHelper, stats)
                elif project.hasAnt():
                    self.ant.buildProject(project, languageHelper, stats)
                elif project.hasNAnt():
                    self.nant.buildProject(project, languageHelper, stats)
                elif project.hasMaven():
                    self.maven.buildProject(project, languageHelper, stats)
                elif project.hasMvn():
                    self.mvn.buildProject(project, languageHelper, stats)
                elif project.hasConfigure():
                    self.configure.buildProject(project, languageHelper, stats)
                elif project.hasMake():
                    self.make.buildProject(project, languageHelper, stats)
              
            # Do this even if not ok
            self.performPostBuild( project, languageHelper, stats )
        
            # If not ok, we might have some artifacts in the repository that
            # are of value...
            if not project.okToPerformWork() and project.hasOutputs():
                self.extractFromRepository(project, languageHelper)
    
            if project.isFailed():
                log.warn('Failed to build project #[' + `project.getPosition()` + '] : [' + project.getName() + '], state:' \
                        + project.getStateDescription())                                              

    def performDelete(self,project,delete,index=0):
        """ 
        Perform the delete command for a <delete entry 
        
        no Return
        """
        
        # Delete a directory and/or a file
        if delete.hasDirectory():
            dir=delete.getDirectory()
            try:
                import shutil
                shutil.rmtree(dir)
                project.addInfo('Deleted directory ['+dir+']')
            except:
                project.addError('Failed to delete directory ['+dir+']')
                raise
        elif delete.hasFile():
            file=delete.getFile()
            try:
                os.remove(file)
                project.addInfo('Deleted file ['+file+']')
            except:
                project.addError('Failed to delete file ['+file+']')
                raise           
        else:
            project.addError('   <delete without \'file\' or \'dir\' attributes.')
            raise RuntimeError('Bad <delete')
    
    def performMkDir(self,project,mkdir,index=0):
        """ Perform the mkdir comment for a <mkdir entry """
        basedir=os.path.abspath(project.getModule().getWorkingDirectory() or dir.base)
         
        #
        # Make a directory
        #
        if mkdir.hasDirectory(): 
            dirToMake=mkdir.getDirectory()
            try:
                if not os.path.exists(dirToMake):
                    os.makedirs(dirToMake)
                    project.addInfo('Made directory ['+dirToMake+']')
                else:
                    project.addInfo('MkDir attempt on pre-existing directory ['+dirToMake+']')                    
            except:
                project.addError('Failed to make directory ['+dirToMake+']')
                raise           
        else:
            project.addError('   <mkdir without \'dir\' attribute.')
            raise RuntimeError('Bad <mkdir, missing \'dir\' attribute')
               
    def performPreBuild( self, project, languageHelper, stats ):
        
        """ 
        	Perform pre-build Actions 
        	
        	No return.
        """
       
        log.debug(' ------ Performing pre-Build Actions (mkdir/delete) for : '+ project.getName())
        
        startedOk =  project.okToPerformWork()
            
        if project.okToPerformWork():        
            # Deletes...
            dels=0
            for delete in project.getDeletes():
                try:
                    self.performDelete(project,delete,dels)
                    dels+=1
                    project.changeState(STATE_SUCCESS)
                except Exception, details:
                    message='Failed to perform delete ' + `delete` + ':' + str(details)
                    log.error(message, exc_info=1)
                    project.addError(message)
                    project.changeState(STATE_FAILED,REASON_PREBUILD_FAILED)
                
        if project.okToPerformWork():
            # MkDirs...
            mkdirs=0
            for mkdir in project.getMkDirs():                             
                try:
                    self.performMkDir(project,mkdir,mkdirs)
                    mkdirs+=1
                    project.changeState(STATE_SUCCESS)
                except Exception, details:
                    message='Failed to perform mkdir ' + `mkdir` + ':' + str(details)
                    log.error(message, exc_info=1)
                    project.addError(message)
                    project.changeState(STATE_FAILED,REASON_PREBUILD_FAILED)
     
        if startedOk and not project.okToPerformWork():
            log.warn('Failed to perform pre-build on project [' + project.getName() + ']')

    def performPostBuild(self, project, languageHelper, stats):
        """
        	Perform Post-Build Actions
        	
        	No return.
        """
        log.debug(' ------ Performing post-Build Actions (check outputs) for : '+ project.getName())

        if project.okToPerformWork():
            if project.hasAnyOutputs():                
                outputs = []
                    
                # Ensure the outputs were all generated correctly.
                outputsOk=True
                for output in project.getOutputs():
                    outputPath=os.path.abspath(output.getPath())
                    # Add to list of outputs, in case we
                    # fail to find, and need to go list 
                    # directories
                    outputs.append(outputPath)
                    if not os.path.exists(outputPath):
                        project.changeState(STATE_FAILED,REASON_MISSING_OUTPUTS)
                        outputsOk=False
                        project.addError("Missing Output: " + str(outputPath))                            
                                 
                if outputsOk: 
                    # If we have a <license name='...
                    if project.hasLicense():
                        licensePath=os.path.abspath(
                                        os.path.join( project.getModule().getWorkingDirectory(),
                                                project.getLicense() ) )
                                          
                        # Add to list of outputs, in case we
                        # fail to find, and need to go list 
                        # directories
                        outputs.append(licensePath)
                            
                        if not os.path.exists(licensePath):
                            project.changeState(STATE_FAILED,REASON_MISSING_OUTPUTS)
                            outputsOk=False
                            project.addError("Missing License Output: " + str(licensePath))                        
                    elif project.isRedistributable():
                        # :TODO: restore to warning. made info so
                        # annotation page was useful (and not overloaded).
                        project.addInfo('No license on redistributable project with outputs.')                                        
                                    
                if outputsOk:                     
                    project.changeState(STATE_SUCCESS)
                else:
                    # List all directories that should've contained
                    # outputs, to see what is there.
                    dirs=[]
                    dircnt=0
                    listed=0
                    for output in outputs:
                        dir=os.path.dirname(output)
                        if not dir in dirs:                        
                            dircnt += 1            
                            if os.path.exists(dir):
                                listDirectoryToFileHolder(project,dir,
                                    FILE_TYPE_OUTPUT,
                                    'list_'+project.getName()+'_dir'+str(dircnt)+'_'+os.path.basename(dir))
                                dirs.append(dir)
                                listed += 1
                            else:
                                project.addError("No such directory (where output is expected) : " + dir)
                            
                    if listed:
                        project.addError("See Directory Listing Work for Missing Outputs")
            else:
                project.changeState(STATE_SUCCESS)
        elif project.inModule():
            # List source directory (when failed) in case it helps debugging...
            listDirectoryToFileHolder(project,project.getModule().getWorkingDirectory(), 
                                        FILE_TYPE_SOURCE, 'list_source_'+project.getName())           
            
        # Display JUnit report output, even if failed...
        if project.hasReports() and project.wasBuilt():
            #project.addInfo('Project produces reports')    
            for report in project.getReports():
                reportDir=report.getResolvedPath() 
                project.addInfo('Project Reports in: ' + reportDir)
                catDirectoryContentsToFileHolder(project, reportDir, FILE_TYPE_OUTPUT)
    
                        
    def performProjectPackageProcessing(self, project, languageHelper, stats):
        """
        	Perform Package Processing Actions
        """
     
        log.debug(' ------ Performing Package Processing for : '+ project.getName())

        self.checkPackage(project)
        
        if project.hasAnyOutputs():                
            outputs = []
                    
            # Ensure the output output were all generated correctly.
            for output in project.getOutputs():
                outputPath=os.path.abspath(output.getPath())
                # Add to list of outputs, in case we
                # fail to find, and need to go list 
                # directories
                outputs.append(outputPath)
                
            # If we have a <license name='...
            if project.hasLicense():
                licensePath=os.path.abspath(	\
                                os.path.join( project.getModule().getWorkingDirectory(),
                                                project.getLicense() ) )
                                          
                # Add to list of outputs, in case we
                # fail to find, and need to go list 
                # directories
                outputs.append(licensePath)
                                                       
            # List all directories that should've contained
            # outputs, to see what is there.
            dirs=[]
            dircnt=0
            for output in outputs:
                dir=os.path.dirname(output)
                if not dir in dirs:                        
                    dircnt += 1         
                    listDirectoryToFileHolder(project,dir,
                        FILE_TYPE_PACKAGE,
                        'list_'+project.getName()+'_dir'+str(dircnt)+'_'+os.path.basename(dir))
                    dirs.append(dir)          
    
            

    def  checkPackage(self,project):
        """
        
        Check if a package has the requisite files
        
        """
        if project.okToPerformWork():
            # Check the package was installed correctly...
            outputsOk=1
            for output in project.getOutputs():
                outputpath=output.getPath()
                if outputpath:
                    if not os.path.exists(outputpath):
                        project.changeState(STATE_FAILED,REASON_PACKAGE_BAD)
                        outputsOk=False
                        project.addError("Missing Packaged Output: " + str(outputpath))
    
            if outputsOk:
                project.changeState(STATE_COMPLETE,REASON_PACKAGE)
            else:
                # Just in case it was so bad it thought it had no
                # outputs to check
                project.changeState(STATE_FAILED,REASON_PACKAGE_BAD)
                
                # List them, why not...
                listDirectoryToFileHolder(project,project.getHomeDirectory(),
                    FILE_TYPE_PACKAGE, 'list_package_'+project.getName())                                                   

    def extractFromRepository(self, project, languageHelper):
        """
            If failed to build, see if we have a copy in the repo...
            
            No return.
        """
        
        if not project.hasOutputs(): return
     
        log.info(' ------ Perform Artifact Repository Search for : '+ project.getName())

        group=project.getArtifactGroup()
        
        # See if we have any...
        artifacts = self.repository.extractMostRecentGroup(group)
        if not artifacts:
            # Then try again...
            artifacts = self.repository.extractMostRecentGroup(group)
            
        # :TODO:
        # If not artifacts, download.
        
        artifactsOk=False
            
        if artifacts:    
            # Be a positive thinker...
            artifactsOk=True   
        
            # See if we can use 'stored' artifacts.
            for output in project.getOutputs():
                id = output.getId()
                
                # Use the repository one...
                if artifacts.has_key(id):
                    (aid,date,extn,path)=artifacts[id]                
                    
                    log.info('Utilize %s from Gump artifact repository for id: %s' % (path, id))
                    
                    # Stash this fallback...
                    output.setPath(path)
                else:
                    log.info('Failed to find artifact for id %s (Gump Repo has %s in %s)' % \
                            (id, artifacts.keys(), group))
                            
                    artifactsOk=False
                    break
                    
        if artifactsOk:
            log.debug(' ------ Extracted (fallback) artifacts from Repository : '+ project.getName())  
            project.addDebug('Extracted fallback artifacts from Gump Repository') 
        else:                                 
            log.error(' ------ Extracted (fallback) artifacts from Repository : '+ project.getName())  
            project.addInfo('Failed to extract fallback artifacts from Gump Repository')  
         
    def preview(self,project,languageHelper):
        """
        Preview what a build would do.
        """
        
        # Extract stats (in case we want to do conditional processing)            
        stats=None
        if project.hasStats():
            stats=project.getStats()
        
        if project.isPackaged():             
            print 'Packaged project: ' + project.getName()
        
        # Pick your poison..
        if project.hasScript():
            self.script.preview(project, languageHelper, stats)
        elif project.hasAnt():
            self.ant.preview(project,  languageHelper, stats)
        elif project.hasNAnt():
            self.nant.preview(project,  languageHelper, stats)
        elif project.hasMaven():
            self.maven.preview(project,  languageHelper, stats)
        elif project.hasMvn():
            self.mvn.preview(project, languageHelper, stats);
        else:
            print 'No builder for project: ' + project.getName()
