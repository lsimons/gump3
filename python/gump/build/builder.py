#!/usr/bin/python


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

"""

import os.path
import sys

from gump import log

from gump.core.gumprun import *
from gump.core.config import dir, default, basicConfig

from gump.build.script import ScriptBuilder
from gump.build.ant import AntBuilder
from gump.build.maven import MavenBuilder

from gump.utils import dump, display, getIndent, logResourceUtilization, \
                            invokeGarbageCollection
                            
from gump.utils.note import Annotatable
from gump.utils.work import *

from gump.utils.tools import *

from gump.model.workspace import *
from gump.model.module import Module
from gump.model.project import Project
from gump.model.depend import  ProjectDependency
from gump.model.stats import *
from gump.model.state import *


###############################################################################
# Classes
###############################################################################

class GumpBuilder(RunSpecific):
    
    def __init__(self,run):
        RunSpecific.__init__(self,run)
        
        self.ant=AntBuilder(run)
        self.maven=MavenBuilder(run)
        self.script=ScriptBuilder(run)

        # Place repository in jardir (to be renamed to repodir)
        self.repository=self.run.getOutputsRepository()

    """
    
        ******************************************************************
        
            THE BUILD INTERFACE
        
        ******************************************************************
    
    """
    

    def build(self):
            
        logResourceUtilization('Before build')
        
        #
        # Doing a full build?
        #
        all=not self.run.getOptions().isQuick()
        
        #
        # Run the build commands
        #
        logResourceUtilization('Before build')
        if all:
            self.buildAll()
        else:
            self.buildProjects()
  
        # Return an exit code based off success
        # :TODO: Move onto self.run
        if self.run.getWorkspace().isSuccess():
            result = EXIT_CODE_SUCCESS 
        else: 
            result = EXIT_CODE_FAILED        
        return result
        
    
    def buildAll(self):
        """ Build a GumpRun's Full Project Stack """
        return self.buildProjectList(self.run.getGumpSet().getProjectSequence())
  
    def buildProjects(self):
        """ Build a GumpRun's Projects """
        return self.buildProjectList(self.run.getGumpSet().getProjects())
  
    def buildProjectList(self,list):
    
        workspace=self.run.getWorkspace()
        
        log.debug('Total Project Sequence (i.e. build order):');
        for p in list:
            log.debug('  To Build : ' + p.name)

        log.debug('--- Building work directories with sources')


        # build all projects this project depends upon, then the project itself
        for project in list:  
            self.buildProject(project)
            
    def buildProject(self,project):
        
        workspace=self.run.getWorkspace()
                 
        log.info('Build Project: #[' + `project.getPosition()` + '] : ' + project.getName())
                    
        # Extract stats (in case we want to do conditional processing)            
        stats=None
        if project.hasStats():
            stats=project.getStats()
        
        # :TODO: Code this nicer, perhaps...    
        if project.isPackaged():             
            self.performProjectPackageProcessing(project, stats)
            return
                
        # Do this even if not ok
        self.performPreBuild(project, stats)

        if project.okToPerformWork():        
            log.debug('Performing Build Upon: [' + `project.getPosition()` + '] ' + project.getName())

            # Turn on --verbose or --debug if failing ...
            if stats:
                if (not STATE_SUCCESS == stats.currentState) and \
                        not project.isVerboseOrDebug():
                    if stats.sequenceInState > INSIGNIFICANT_DURATION:
                        project.addInfo('Enable "debug" output, due to a sequence of %s previous errors.' % stats.sequenceInState)
                        project.setDebug(1)
                    else:
                        project.addInfo('Enable "verbose" output, due to %s previous error(s).' % stats.sequenceInState)    
                        project.setVerbose(1)

            # Pick your poison..
            if project.hasScript():
                self.script.buildProject(project, stats)
            elif project.hasAnt():
                self.ant.buildProject(project, stats)
            elif project.hasMaven():
                self.maven.buildProject(project, stats)
            
            if not project.okToPerformWork() and not project.isDebug():
                # Display...
                project.addInfo('Enable "debug" output, due to build failure.')
                project.setDebug(1)
                    
        # Do this even if not ok
        self.performPostBuild( project, stats )
    
        if project.isFailed():
            log.warn('Failed to build project #[' + `project.getPosition()` + '] : [' + project.getName() + '], state:' \
                    + project.getStateDescription())                           
                    
        # Generate/process the project event...
        self.run.generateEvent(project)      


    def performDelete(self,project,delete,index=0):
        """ Return the delete command for a <delete entry """
        basedir=os.path.abspath(project.getModule().getWorkingDirectory() or dir.base)
    
        #
        # Delete a directory and/or a file
        #
        # :TODO: Before turning this on, we need to ensure that the command
        # will not self.run wild. We need to ensure that there is no ";" and we
        # need to ensure the directory/file is under the workspace.
        #
        if delete.dir:
            dir=os.path.abspath(os.path.join(basedir,delete.dir))
            try:
                os.rmdir(dir)
                project.addInfo('Deleted directory ['+dir+']')
            except:
                project.addError('Failed to delete directory ['+dir+']')
                raise
        elif delete.file:
            file=os.path.abspath(os.path.join(basedir,delete.file))
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
        """ Return the mkdir comment for a <mkdir entry """
        basedir=os.path.abspath(project.getModule().getWorkingDirectory() or dir.base)
         
        #
        # Make a directory
        #
        if mkdir.dir:
            
            dirToMake=os.path.abspath(os.path.join(basedir,mkdir.dir))
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
               
    def performPreBuild( self, project, stats ):
        """ Perform pre-build Actions """
       
        log.debug(' ------ Performing pre-Build Actions (mkdir/delete) for : '+ project.getName())
        
        startedOk =  project.okToPerformWork()
            
        #
        #
        # NOTE --------------- NOT TURNED ON YET!!!!!!
        # Security concerns...
        #
        #
        if 0 and project.okToPerformWork():        
            # Deletes...
            dels=0
            for delete in project.getDeletes():
                try:
                    self.performDelete(project,delete,dels)
                    dels+=1
                    project.changeState(STATE_SUCCESS)
                except:
                    log.error('PerformDelete Failed', exc_info=1)
                    project.changeState(STATE_FAILED,REASON_PREBUILD_FAILED)
                
        if project.okToPerformWork():
            # MkDirs...
            mkdirs=0
            for mkdir in project.getMkDirs():                             
                try:
                    self.performMkDir(project,mkdir,mkdirs)
                    mkdirs+=1
                    project.changeState(STATE_SUCCESS)
                except:
                    log.error('PerformMkdir Failed', exc_info=1)    
                    project.changeState(STATE_FAILED,REASON_PREBUILD_FAILED)
     
            
        if startedOk and not project.okToPerformWork():
            log.warn('Failed to perform pre-build on project [' + project.getName() + ']')

    def performPostBuild(self, project, stats):
        """Perform Post-Build Actions"""
     
        log.debug(' ------ Performing post-Build Actions (check jars) for : '+ project.getName())

        if project.okToPerformWork():
            if project.hasOutputs():                
                outputs = []
                    
                #
                # Ensure the jar output were all generated correctly.
                #
                outputsOk=1
                for jar in project.getJars():
                    jarPath=os.path.abspath(jar.getPath())
                    # Add to list of outputs, in case we
                    # fail to find, and need to go list 
                    # directories
                    outputs.append(jarPath)
                    if not os.path.exists(jarPath):
                        project.changeState(STATE_FAILED,REASON_MISSING_OUTPUTS)
                        outputsOk=False
                        project.addError("Missing Output: " + str(jarPath))                            
                                 
                if outputsOk: 
                    # If we have a <license name='...
                    if project.hasLicense():
                        licensePath=os.path.abspath(	\
                                        os.path.join( project.getModule().getWorkingDirectory(),	\
                                                project.getLicense() ) )
                                          
                        # Add to list of outputs, in case we
                        # fail to find, and need to go list 
                        # directoiries
                        outputs.append(licensePath)
                            
                        if not os.path.exists(licensePath):
                            project.changeState(STATE_FAILED,REASON_MISSING_OUTPUTS)
                            outputsOk=False
                            project.addError("Missing License Output: " + str(licensePath))
                        else:                      
                            try:
                                self.repository.publish( project.getModule().getName(), licensePath )            
                            except Exception, details:
                                message='Failed to publish license [' + licensePath + '] to repository : ' + str(details)
                                project.addError(message)
                                log.error(message)                     
                    elif project.isRedistributable():
                        # :TODO: restore to warning. made info so
                        # annotation page was useful (and not overloaded).
                        project.addInfo('No license on redistributable project with outputs.')                                        
                                    
                if outputsOk: 
                    # Publish them all (if redistributable)
                    if project.isRedistributable():
                        for jar in project.getJars():
                            # :TODO: Relative to module source?
                            jarPath=os.path.abspath(jar.getPath())
                            # Copy to repository
                            try:
                                self.repository.publish( project.getModule().getName(), jarPath )           
                            except Exception, details:
                                message='Failed to publish [' + jarPath + '] to repository : ' + str(details)
                                project.addError(message)
                                log.error(message)
                        
                    project.changeState(STATE_SUCCESS)
                    
                    # For 'fun' list repository
                    listDirectoryToFileHolder(project,self.repository.getGroupDir(project.getModule().getName()), \
                                                FILE_TYPE_REPO, 'list_repo_'+project.getName())                     
                                        
                if not outputsOk:
                    #
                    # List all directories that should've contained
                    # outputs, to see what is there.
                    #
                    dirs=[]
                    dircnt=0
                    listed=0
                    for output in outputs:
                        dir=os.path.dirname(output)
                        if not dir in dirs:                        
                            dircnt += 1            
                            if os.path.exists(dir):
                                listDirectoryToFileHolder(project,dir,\
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
        else:
            # List source directory (when failed) in case it helps debugging...
            listDirectoryToFileHolder(project,project.getModule().getWorkingDirectory(), \
                                        FILE_TYPE_SOURCE, 'list_source_'+project.getName())           
                                        
        #   
        # Display report output, even if failed...
        #
        if project.hasReports() and project.wasBuilt():
            #project.addInfo('Project produces reports')    
            for report in project.getReports():
                reportDir=report.getResolvedPath() 
                project.addInfo('Project Reports in: ' + reportDir)
                catDirectoryContentsToFileHolder(project, reportDir, FILE_TYPE_OUTPUT)
    
                        
    def performProjectPackageProcessing(self, project, stats):
        """Perform Package Processing Actions"""
     
        log.debug(' ------ Performing Package Processing for : '+ project.getName())

        self.checkPackage(project)
        
        if project.hasOutputs():                
            outputs = []
                    
            # Ensure the jar output were all generated correctly.
            for jar in project.getJars():
                jarPath=os.path.abspath(jar.getPath())
                # Add to list of outputs, in case we
                # fail to find, and need to go list 
                # directories
                outputs.append(jarPath)
                
            # If we have a <license name='...
            if project.hasLicense():
                licensePath=os.path.abspath(	\
                                os.path.join( project.getModule().getWorkingDirectory(),	\
                                                project.getLicense() ) )
                                          
                # Add to list of outputs, in case we
                # fail to find, and need to go list 
                # directories
                outputs.append(licensePath)
                                                            
            #
            # List all directories that should've contained
            # outputs, to see what is there.
            #
            dirs=[]
            dircnt=0
            for output in outputs:
                dir=os.path.dirname(output)
                if not dir in dirs:                        
                    dircnt += 1         
                    listDirectoryToFileHolder(project,dir,\
                        FILE_TYPE_PACKAGE,
                        'list_'+project.getName()+'_dir'+str(dircnt)+'_'+os.path.basename(dir))
                    dirs.append(dir)          
    
            

    def  checkPackage(self,project):
        if project.okToPerformWork():
            #
            # Check the package was installed correctly...
            #
            outputsOk=1
            for jar in project.getJars():
                jarpath=jar.getPath()
                if jarpath:
                    if not os.path.exists(jarpath):
                        project.changeState(STATE_FAILED,REASON_PACKAGE_BAD)
                        outputsOk=False
                        project.addError("Missing Packaged Jar: " + str(jarpath))
    
            if outputsOk:
                project.changeState(STATE_COMPLETE,REASON_PACKAGE)
            else:
                # Just in case it was so bad it thought it had no
                # jars to check
                project.changeState(STATE_FAILED,REASON_PACKAGE_BAD)
                
                # List them, why not...
                listDirectoryToFileHolder(project,project.getHomeDirectory(),	\
                    FILE_TYPE_PACKAGE, 'list_package_'+project.getName())                                            
        
        
    def preview(self,project):
        
        # Extract stats (in case we want to do conditional processing)            
        stats=None
        if project.hasStats():
            stats=project.getStats()
        
        if project.isPackaged():             
            print 'Packaged project: ' + project.getName()
        
        # Pick your poison..
        if project.hasScript():
            self.script.preview(project, stats)
        elif project.hasAnt():
            self.ant.preview(project, stats)
        elif project.hasMaven():
            self.maven.preview(project, stats)
        else:
            print 'No builder for project: ' + project.getName()
