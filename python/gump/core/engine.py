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
from fnmatch import fnmatch

from gump import log
from gump.core.gumprun import *
from gump.core.config import dir, default, basicConfig

from gump.utils import dump, display, getIndent, logResourceUtilization
from gump.utils.note import Annotatable
from gump.utils.work import *

from gump.utils.tools import *

from gump.model.workspace import *
from gump.model.module import Module
from gump.model.project import Project
from gump.model.depend import  ProjectDependency
from gump.model.stats import *
from gump.model.state import *

from gump.net.cvs import *

from gump.document.text.documenter import TextDocumenter
from gump.document.template.documenter import TemplateDocumenter
from gump.document.forrest.documenter import ForrestDocumenter

from gump.output.statsdb import *
from gump.output.repository import JarRepository
from gump.output.nag import nag
from gump.results.resulter import gatherResults,generateResults
from gump.syndication.syndicator import syndicate

    
###############################################################################
# Functions
###############################################################################
def isAllProjects(pexpr):
    return pexpr=='all' or pexpr=='*'

###############################################################################
# Classes
###############################################################################

class GumpEngine:

    ###########################################
        
    def performUpdate(self,run):
        return self.perform(run, GumpTaskList(['update','document']) )
    
    def performBuild(self,run):
        return self.perform(run, GumpTaskList(['build','document']) )
    
    def performDebug(self,run):
        return self.perform(run, GumpTaskList(['update','build','document']) )
    
    def performIntegrate(self,run):
        return self.perform(run, \
                GumpTaskList(['update','build','syndicate','generateResults','document','notify']) )
        
    def performCheck(self,run):
        return self.perform(run, GumpTaskList(['check','document']) )
        
    ###########################################
    
    def perform(self,run,taskList):     
    
        # Bind this list to these methods (on this engine)
        taskList.bind(self)
        
        # Run the method sequence...
        self.performTasks(run,taskList)      
                
        # Return an exit code based off success
        # :TODO: Move onto run
        if run.getWorkspace().isSuccess():
            result = EXIT_CODE_SUCCESS 
        else: 
            result = EXIT_CODE_FAILED
        
        return result  
    
    def performTasks(self,run,taskList):
        for task in taskList:
            log.info('Perform task [' + task.getName() + ']')
            task.invoke(run)
            
    ###########################################
    
    def preprocess(self,run,exitOnError=1):
        
        logResourceUtilization('Before preprocess')
        
        #
        # Perform start-up logic 
        #
        workspace = run.getWorkspace()
                
        #
        #
        #
        if not run.getOptions().isQuick():
            logResourceUtilization('Before check environment')            
            run.getEnvironment().checkEnvironment(exitOnError)
            logResourceUtilization('After check environment')
        
        #
        # Modify the log location on the fly, if --dated
        #
        if run.getOptions().isDated():
            workspace.setDatedDirectories()
        
        #
        # Use forrest if available & not overridden...
        #
        if run.getEnvironment().noForrest \
            or run.getOptions().isTemplate() \
            or run.getOptions().isText() :
            if run.getOptions().isTemplate():
                documenter=TemplateDocumenter()
            else:
                documenter=TextDocumenter()
        else:
            documenter=ForrestDocumenter(workspace.getBaseDirectory(), \
                                         workspace.getLogUrl())                        
        run.getOptions().setDocumenter(documenter)
                    
        # Check the workspace
        if not workspace.getVersion() >= setting.ws_version:
            message='Workspace version ['+workspace.getVersion()+'] below preferred [' + setting.ws_version + ']'
            workspace.addWarning(message)
            log.warn(message)   
            
        # Check the workspace
        if not workspace.getVersion() >= setting.ws_minimum_version:
            message='Workspace version ['+workspace.getVersion()+'] below minimum [' + setting.ws_minimum_version + ']'
            workspace.addError(message)
            log.error(message)   
            
        # Write workspace to a 'merge' file        
        if not run.getOptions().isQuick():
            workspace.writeXMLToFile(default.merge)
            workspace.setMergeFile(default.merge)
                 
        # :TODO: Put this somewhere else, and/or make it depend upon something...
        workspace.changeState(STATE_SUCCESS)

    """
    
        ******************************************************************
        
            THE UPDATE INTERFACE
        
        ******************************************************************
    
    """
    def update(self, run):        
        logResourceUtilization('Before update')
        
        #
        # Doing a full build?
        #
        all=not run.getOptions().isQuick()
        
        if all:
            modules=run.getGumpSet().getModuleSequence()
        else:
            modules=run.getGumpSet().getModules()
        
        #
        # Checkout from source code repositories
        #
        self.updateModules(run,modules)
  
        # Return an exit code based off success
        # :TODO: Move onto run
        if run.getWorkspace().isSuccess():
            result = EXIT_CODE_SUCCESS 
        else: 
            result = EXIT_CODE_FAILED
        
        return result
  
    def updateModules(self, run, list):    
    
        workspace = run.getWorkspace()
        
        # :TODO: A tad bogus to move here
        os.chdir(workspace.getCvsDirectory())
        log.debug("Workspace CVS Directory: " + workspace.getCvsDirectory())

        #
        # A stash of known logins.
        #
        logins=readLogins()

        #log.debug('Modules to update:') 
    
        moduleCount=len(list)
        moduleNo=1     
        # Update all the modules that have CVS repositories
        for module in list: 
        
            if module.isPackaged(): 
                # Not sure we have anything to do right now
                # self.performModulePackageProcessing(module)
                continue
            
            if not module.hasCvs() \
                and not module.hasSvn()	\
                and not module.hasJars(): continue
            
            log.info('Perform CVS/SVN/Jars Update on #[' + `moduleNo` + \
                        '] of [' + `moduleCount` + ']: ' + module.getName())
    
            if module.okToPerformWork():
                
                # Did we check it out already?
                exists	=	os.path.exists(module.getName())
       
                #
                #  Get the Update Command
                #
                (repository, root, cmd ) = module.getUpdateCommand(exists)
                
                if module.hasCvs():
                    #
                    # Provide CVS logins, if not already there
                    #
                    loginToRepositoryOnDemand(repository,root,logins)
               
                #
                # Execute the command and capture results        
                #
                cmdResult=execute(cmd,workspace.tmpdir)
      
                work=CommandWorkItem(WORK_TYPE_UPDATE,cmd,cmdResult)
    
                # Update Contexts                  
                module.performedWork(work)  
                repository.performedWork(work.clone())
      
                # Update Context w/ Results  
                if not cmdResult.state==CMD_STATE_SUCCESS:              
                    log.error('Failed to checkout/update module: ' + module.name)   
                    if not exists:     
                        module.changeState(STATE_FAILED,REASON_UPDATE_FAILED)
                    else:
                        module.addError('*** Failed to update from source control. Stale contents ***')
                        
                        # Black mark for this repository
                        repository=module.getRepository()
                        repository.addError('*** Failed to update %s from source control. Stale contents ***'	\
                                        % module.getName())
                                        
                        # Kinda bogus, but better than nowt (for now)
                        module.changeState(STATE_SUCCESS,REASON_UPDATE_FAILED)
                else:
                    module.changeState(STATE_SUCCESS)
                    
                    # Were the contents of the repository modified?                                        
                    module.setUpdated(cmdResult.hasOutput())
        
            #
            # Sync if appropriate
            #
            if module.okToPerformWork():
            
                sourcedir = os.path.abspath(	\
                                os.path.join(	workspace.getCvsDirectory(), \
                                                module.name)) # todo allow override
                destdir = module.getSourceDirectory()
                
                # Perform the sync...
                try:
                    syncDirectories(sourcedir,destdir,module)
                    module.changeState(STATE_SUCCESS)
                except:
                    module.changeState(STATE_FAILED,REASON_SYNC_FAILED)
                    
            # Incremental documentation...
            documenter=run.getOptions().getDocumenter()        
            if documenter :
                documenter.entity(module,run)      

           
    """
    
        ******************************************************************
        
            THE BUILD INTERFACE
        
        ******************************************************************
    
    """
    
    

    def build(self,run):
            
        logResourceUtilization('Before build')
        
        #
        # Doing a full build?
        #
        all=not run.getOptions().isQuick()
        
        #
        # Run the build commands
        #
        logResourceUtilization('Before build')
        if all:
            self.buildAll(run)
        else:
            self.buildProjects(run)
  
        # Return an exit code based off success
        # :TODO: Move onto run
        if run.getWorkspace().isSuccess():
            result = EXIT_CODE_SUCCESS 
        else: 
            result = EXIT_CODE_FAILED        
        return result
        
    
    def buildAll(self,run):
        """ Build a GumpRun's Full Project Stack """
        return self.buildProjectList(run,run.getGumpSet().getProjectSequence())
  
    def buildProjects(self,run):
        """ Build a GumpRun's Projects """
        return self.buildProjectList(run,run.getGumpSet().getProjects())
  
    def buildProjectList(self,run,list):
    
        workspace=run.getWorkspace()
        
        log.debug('Total Project Sequence (i.e. build order):');
        for p in list:
            log.debug('  To Build : ' + p.name)

        log.debug('--- Building work directories with sources')

        # Place repository in jardir (to be renamed to repodir)
        repository=run.getOutputsRepository()

        # build all projects this project depends upon, then the project itself
        projectCount=len(list)
        projectNo=1
        for project in list:  
        
            log.info(' Project: #[' + `projectNo` + '] of [' + `projectCount` + '] : ' + project.getName())
                    
            # Extract stats (in case we want to do conditional processing)            
            stats=None
            if project.hasStats():
                stats=project.getStats()
            
            if project.isPackaged():             
                self.performProjectPackageProcessing(run, project, stats)
                continue
                
            # Do this even if not ok
            self.performPreBuild(run, project, stats)

            wasBuilt=0
            if project.okToPerformWork():        
                log.debug(' ------ Building: [' + `projectNo` + '] ' + project.getName())

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

                #
                # Get the appropriate build command...
                #
                cmd=project.getBuildCommand(run.getEnvironment().getJavaCommand())

                if cmd:
                    # Execute the command ....
                    cmdResult=execute(cmd,workspace.tmpdir)
    
                    # Update Context    
                    work=CommandWorkItem(WORK_TYPE_BUILD,cmd,cmdResult)
                    project.performedWork(work)
                    wasBuilt=1
                    
                    # Update Context w/ Results  
                    if not cmdResult.state==CMD_STATE_SUCCESS:
                        reason=REASON_BUILD_FAILED
                        if cmdResult.state==CMD_STATE_TIMED_OUT:
                            reason=REASON_BUILD_TIMEDOUT
                        project.changeState(STATE_FAILED,reason)
                        
                        if not project.isDebug():
                            # Display...
                            project.addInfo('Enable "debug" output, due to build failure.')
                            project.setDebug(1)
                        
                    else:                         
                        # For now, things are going good...
                        project.changeState(STATE_SUCCESS)
                    
            # Do this even if not ok
            self.performPostBuild( run, project, repository, wasBuilt, stats )
    
            if project.isFailed():
                log.warn('Failed to build project #[' + `projectNo` + '] [' + project.getName() + '], state:' \
                        + project.getStateDescription())
                                                
            projectNo+=1
            
            # Incremental documentation...
            documenter=run.getOptions().getDocumenter()        
            if documenter :
                documenter.entity(project,run)


    def performDelete(self,project,delete,index=0):
        """ Return the delete command for a <delete entry """
        basedir=os.path.abspath(project.getModule().getSourceDirectory() or dir.base)
    
        #
        # Delete a directory and/or a file
        #
        # :TODO: Before turning this on, we need to ensure that the command
        # will not run wild. We need to ensure that there is no ";" and we
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
        basedir=os.path.abspath(project.getModule().getSourceDirectory() or dir.base)
         
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
               
    def performPreBuild( self, run, project, stats ):
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
            for delete in project.xml.delete:
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
            for mkdir in project.xml.mkdir:                             
                try:
                    self.performMkDir(project,mkdir,mkdirs)
                    mkdirs+=1
                    project.changeState(STATE_SUCCESS)
                except:
                    log.error('PerformMkdir Failed', exc_info=1)    
                    project.changeState(STATE_FAILED,REASON_PREBUILD_FAILED)
                
        # Maven requires a build.properties to be generated...
        if project.okToPerformWork() and project.hasMaven():
            try:
                propertiesFile=project.generateMavenProperties()                                
                project.addDebug('Maven Properties in: ' + propertiesFile)
                
                try:
                    catFileToFileHolder(project,propertiesFile,	\
                        FILE_TYPE_CONFIG,	\
                        project.getName() + ' ' + os.path.basename(propertiesFile))
                except:
                    log.error('Display Properties [ ' + propertiesFile + '] Failed', exc_info=1)   
                
            except:
                log.error('Generate Maven Properties Failed', exc_info=1)    
                project.changeState(STATE_FAILED,REASON_PREBUILD_FAILED)
            
        if startedOk and not project.okToPerformWork():
            log.warn('Failed to perform pre-build on project [' + project.getName() + ']')

    def performPostBuild(self, run, project, repository, wasBuilt, stats):
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
                        outputsOk=0
                        project.addError("Missing Output: " + str(jarPath))                            
                                 
                if outputsOk: 
                    # If we have a <license name='...
                    if project.hasLicense():
                        licensePath=os.path.abspath(	\
                                        os.path.join( project.getModule().getSourceDirectory(),	\
                                                project.getLicense() ) )
                                          
                        # Add to list of outputs, in case we
                        # fail to find, and need to go list 
                        # directoiries
                        outputs.append(licensePath)
                            
                        if not os.path.exists(licensePath):
                            project.changeState(STATE_FAILED,REASON_MISSING_OUTPUTS)
                            outputsOk=0
                            project.addError("Missing License Output: " + str(licensePath))
                        else:                      
                            try:
                                repository.publish( project.getModule().getName(), licensePath )            
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
                                repository.publish( project.getModule().getName(), jarPath )           
                            except Exception, details:
                                message='Failed to publish [' + jarPath + '] to repository : ' + str(details)
                                project.addError(message)
                                log.error(message)
                        
                    project.changeState(STATE_SUCCESS)
                    
                    # For 'fun' list repository
                    listDirectoryToFileHolder(project,repository.getGroupDir(project.getModule().getName()), \
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
            listDirectoryToFileHolder(project,project.getModule().getSourceDirectory(), \
                                        FILE_TYPE_SOURCE, 'list_source_'+project.getName())           
                                        
        #   
        # Display report output, even if failed...
        #
        if project.hasReports() and wasBuilt:
            #project.addInfo('Project produces reports')    
            for report in project.getReports():
                reportDir=report.getResolvedPath() 
                project.addInfo('Project Reports in: ' + reportDir)
                catDirectoryContentsToFileHolder(project,reportDir,FILE_TYPE_OUTPUT)
    
        # Maven generates a maven.log...
        if project.hasMaven() and wasBuilt and not project.isPackaged():
            try:
                logFile=project.locateMavenLog()                                
                project.addDebug('Maven Log in: ' + logFile)                
                try:
                    catFileToFileHolder(project,logFile,	\
                        FILE_TYPE_LOG,	\
                        project.getName() + ' ' + os.path.basename(logFile))
                except:
                    log.error('Display Log [ ' + logFile + '] Failed', exc_info=1)   
                
            except:
                log.warning('Display Maven Log Failed', exc_info=1)    
                # Not worth crapping out over...
            
                        
    def performProjectPackageProcessing(self, run, project, stats):
        """Perform Package Processing Actions"""
     
        log.debug(' ------ Performing Package Processing for : '+ project.getName())

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
                
            # If we have a <license name='...
            if project.hasLicense():
                licensePath=os.path.abspath(	\
                                os.path.join( project.getModule().getSourceDirectory(),	\
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
                    
                          
    def setEndTime(self,run):
        
        logResourceUtilization('Set End Time')
        # :TODO: Move this to run
        run.getWorkspace().setEndTime()
        
    """
    
        ******************************************************************
        
           CHECK WORKSPACE
        
        ******************************************************************
    
    """
    
    def checkWorkspace(self,run):
        """ Check a GumpRun's Projects """
        workspace=run.getWorkspace()

        log.debug('--- Building work directories with sources')
        
        # :TODO: Check the workspace?
        
        self.checkModules(run)
        self.checkProjects(run)
        
    def checkModules(self,run):
        # Check all the modules
        list=run.getGumpSet().getModuleSequence()
        moduleCount=len(list)
        moduleNo=1
        for module in list:      
        
            log.info(' ------ Check Module: #[' + `moduleNo` + '] of [' + `moduleCount` + '] : ' + module.getName())
                        
            module.changeState(STATE_SUCCESS)        
            moduleNo+=1

    def checkProjects(self,run):
        list=run.getGumpSet().getProjects()
        # Check all projects
                
        projectCount=len(list)
        projectNo=1
        for project in list:  
        
            log.info(' ------ Check Project: #[' + `projectNo` + '] of [' + `projectCount` + '] : ' + project.getName())
            
            # :TODO: Do some actualy checking...
        
            if project.okToPerformWork():        
                # For now, things are going good...
                project.changeState(STATE_SUCCESS)
        
            if not project.okToPerformWork():
                log.warn('Failed to check project #[' + `projectNo` + '] [' + project.getName() + '], state:' \
                        + project.getStateDescription())
            
            projectNo+=1

                                   
    """
    
        ******************************************************************
        
            THE DOCUMENATION INTERFACE
        
        ******************************************************************
    
    """
    
    

    def prepareDocumentation(self,run):
        
        logResourceUtilization('Before document preparation')
        
        # Prepare for documentation        
        documenter=run.getOptions().getDocumenter()        
        if documenter :
            documenter.prepare(run)            
            
    def document(self,run):
        
        #   
        # Build HTML Result (via Forrest or ...)
        #
        logResourceUtilization('Before document')
        documenter=run.getOptions().getDocumenter()        
        if documenter :
            documenter.document(run)
                              
                
    """
    
        ******************************************************************
        
           MISC STUFF
        
        ******************************************************************
    
    """
    
    
    def notify(self,run):
                
        #
        # Only an 'all' is an official build, for them:
        #
        #	Send Naggin E-mails
        #
        if run.getGumpSet().isFull() \
            and run.getWorkspace().isNag():
  
            log.info('Nag about failures... ')            
            
            #
            # Nag about failures
            #
            logResourceUtilization('Before nag')
            nag(run)  
        
    def gatherResults(self,run):
        #
        # Gather results.xml from other servers/workspaces
        #
        logResourceUtilization('Before gather results')
        gatherResults(run)
        
    def generateResults(self,run):
            
        logResourceUtilization('Before generate results')
        # Update Statistics/Results on full runs            
        if run.getGumpSet().isFull():
            
            #
            # Generate results.xml for this run, on this server/workspace
            #
            logResourceUtilization('Before generate results')
            generateResults(run)
            
        
    def syndicate(self,run):
        logResourceUtilization('Before syndicate')
        #
        # Provide a news feed (or few)
        #
        syndicate(run)
                
    
    def loadStatistics(self,run):   
        """ Load Statistics into the run (to get current values) """
        logResourceUtilization('Before load statistics')
        self.processStatistics(run,1)
         
    def updateStatistics(self,run):        
        """ Update Statistics into the run (to set current values) """
        logResourceUtilization('Before update statistics')
        self.processStatistics(run,0)
        
    def processStatistics(self,run,load):
    
        if load:
            log.debug('--- Loading Project Statistics')
        else:
            log.debug('--- Updating Project Statistics')
    
        db=StatisticsDB()   
        
        workspace=run.getWorkspace()        
        
        if not load:
            #
            # Update stats (and stash onto projects)
            #
            db.updateStatistics(workspace)
            
            db.sync()
        else:
            #
            # Load stats (and stash onto projects)
            #    
            db.loadStatistics(workspace)            
          

    
class GumpTask:
    
    def __init__(self, name, dependencyNames):
        self.dependencyNames=dependencyNames
        self.name=name
        self.method=None
        self.performed=0
            
    def __repr__(self):
        return self.__class__.__name__ + ':' + self.getName()
        
    def __str__(self):
        return self.getName()
        
    def getName(self):
        return self.name
        
    def getDependentTaskNames(self):
        return self.dependencyNames
    
    def setPerformed(self,performed):
        self.performed=performed
    
    def isPerformed(self):
        return self.performed
        
        
    def bind(self,engine):
        self.method=getattr(engine,self.name,None)            
        
        # For debugging ...        
        #if not (isinstance(self.method,types.MethodType) and callable(self.method)): 
        #    raise RuntimeError, 'Failed to bind task name [' + self.name + '] to engine [' + `engine` + ']'
        
    def invoke(self,run):
        if self.method:
            return self.method(run)
                                
class GumpTaskList(list):
    
    def __init__(self,taskNames=None):
        self.tasks={}
        if taskNames:
            self.populateForTaskNameList(taskNames)
        
    def addTask(self,task):
        if not self.hasTask(task):
            self.append(task)
            self.tasks[task.getName()]=task
    
    def hasTaskByName(self,name):
        return self.tasks.has_key(name)
        
    def hasTask(self,task):
        return self.hasTaskByName(task.getName())
        
    def getTask(self,name):
        if self.tasks.has_key(name):
            return self.tasks[name]     
                   
        #
        # The rules (the bare minimum of what needs
        # to have run, for a task to run w/o crashing).
        #
        
        
        if 'preprocess'==name:
            # Everything needs this ...
            task=GumpTask(name,[])            
        elif 'loadStatistics'==name:
            # The minimum to load stats onto the tree
            task=GumpTask(name,['preprocess'])  
        elif 'updateStatistics'==name:
            # Publish results to the statistics database
            # NB: Not really true to depend upon load, but cleaner..
            task=GumpTask(name,['preprocess','gatherResults','loadStatistics'])           
        elif 'update'==name:
            # Update from CVS|SVN repositories
            task=GumpTask(name,['preprocess','loadStatistics'])                    
        elif 'build'==name:
            # Build using Ant|Maven|...
            task=GumpTask(name,['preprocess','loadStatistics'])                    
        elif 'check'==name:
            # Check metadata
            task=GumpTask(name,['preprocess','loadStatistics'])             
        elif 'prepareDocumentation'==name:
            # Prepare documentation (e.g. create forest templates)
            task=GumpTask(name,['preprocess',])   
        elif 'document'==name:
            # Perform actual documentation
            task=GumpTask(name,	\
                    ['preprocess','loadStatistics','prepareDocumentation','gatherResults','updateStatistics',])    
        elif 'notify'==name:
            # Was once called 'nag'...
            task=GumpTask(name,['preprocess','loadStatistics'])  
        elif 'syndicate'==name:
            # Syndicate to news feeds
            task=GumpTask(name,['preprocess','loadStatistics','prepareDocumentation'])  
        elif 'gatherResults'==name:
            # Gather results.xml from other servers 
            task=GumpTask(name,['preprocess'])   
        elif 'setEndTime'==name:
            # Gather results.xml from other servers 
            task=GumpTask(name,['preprocess'])   
        elif 'generateResults'==name:
            # Generate the results.xml for this server/workspace
            task=GumpTask(name,['preprocess','loadStatistics','setEndTime','prepareDocumentation'])   
        else:
            raise RuntimeError, 'Unknown task name ['+name+']'            
        return task
            
    def getDependentTasks(self,task):
        dependencies=[]
        taskNames=task.getDependentTaskNames()
        for taskName in taskNames:
            dependencies.append(self.getTask(taskName))        
        return dependencies 
        
    def populateForTaskNameList(self,taskNames):        
        for taskName in taskNames:
            self.populateForTaskName(taskName)
        
    def populateForTaskName(self,taskName):
        self.populateForTask(self.getTask(taskName))
        
    def populateForTask(self,task):
        if not task in self:
            for depend in self.getDependentTasks(task):
                self.populateForTask(depend)
            self.addTask(task)                            
            
    def bind(self,engine):
        for task in self: task.bind(engine)
                    