#!/usr/bin/python
"""

"""

import os.path
import os
import sys
from fnmatch import fnmatch

from gump import log
from gump.gumprun import *
from gump.config import dir, default, basicConfig

from gump.utils import dump, display, getIndent, logResourceUtilization
from gump.utils.note import Annotatable
from gump.utils.work import *

from gump.utils.tools import *

from gump.model.workspace import *
from gump.model.module import Module
from gump.model.project import Project
from gump.model.depend import  ProjectDependency
from gump.model.state import *

from gump.net.cvs import *

from gump.document.text import TextDocumenter
from gump.document.forrest import ForrestDocumenter

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
    
    def preprocess(self,run,exitOnError=1):
        

        #
        # Perform start-up logic 
        #
        workspace = run.getWorkspace()
                
        logResourceUtilization('Before check environment')
        
        #
        #
        #
        workspace.checkEnvironment(exitOnError)
        
        
        logResourceUtilization('After check environment')
        
        #
        # Modify the log on the fly, if --dated
        #
        if run.getOptions().isDated():
            workspace.setDatedDirectories()
        
        #
        # Use forrest if available...
        #
        if workspace.noForrest:
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
        workspace.writeXMLToFile(default.merge)
        workspace.setMergeFile(default.merge)

    def continuous(self):
        
        
        # :TODO: WORK IN PROGRESS NOT COMPLETE!!!
        
        while 0:
            
            try:
                # Do the integration
                ok=self.integrate(run)
            except:
                log.error('Failed to integrate...')
                pass
        
    def integrate(self,run):    
      
        
        #
        # Prepare the context
        #
        logResourceUtilization('Before preprocess')
        self.preprocess(run)
        
        #
        # Load the statistics (so we can use them during
        # other operations).
        #
        logResourceUtilization('Before load statistics')
        self.loadStatistics(run)        
        
        #
        # Checkout from source code repositories
        #
        logResourceUtilization('Before update')
        self.update(run)
        
        #
        # Run the build commands
        #
        logResourceUtilization('Before build')
        self.buildAll(run)
  
        #
        # Gather results.xml from other servers/workspaces
        #
        logResourceUtilization('Before generate results')
        gatherResults(run)
          
        # Update Statistics/Results on full runs            
        if run.getGumpSet().isFull():
            
            logResourceUtilization('Before statistics update')
            self.updateStatistics(run)
            
            #
            # Generate results.xml for this run, on this server/workspace
            #
            logResourceUtilization('Before generate results')
            generateResults(run)
                    
        #
        # Provide a news feed (or few)
        #
        logResourceUtilization('Before syndicate')
        syndicate(run)
                        
        #   
        # Build HTML Result (via Forrest or ...)
        #
        logResourceUtilization('Before document')
        documenter=run.getOptions().getDocumenter()
        if documenter :
            documenter.document(run)
                        
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

        # Return an exit code based off success
        # :TODO: Move onto run
        if run.getWorkspace().isSuccess():
            result = SUCCESS 
        else: 
            result = FAILED
        
        return result

       
    def check(self,run):    
  
        #
        # Prepare the context
        #
        self.preprocess(run, 0)
  
        #
        # Load the statistics (so we can use them during
        # other operations).
        #
        logResourceUtilization('Before load statistics')
        self.loadStatistics(run)        
        
        #
        # Gather results.xml from other servers/workspaces
        #
        logResourceUtilization('Before generate results')
        gatherResults(run)
        
        #
        # Check the metadata
        #
        self.checkWorkspace(run)
                 
        #   
        # Build HTML Result (via Forrest or ...)
        #
        documenter=run.getOptions().getDocumenter()
        if documenter :
            documenter.document(run)

        # Return an exit code based off success
        # :TODO: Move onto run
        if run.getWorkspace().isSuccess():
            result = SUCCESS 
        else: 
            result = FAILED
        
        return result


    """
    
        ******************************************************************
        
            THE UPDATE INTERFACE
        
        ******************************************************************
    
    """
    def update(self, run):
        
        #
        # Checkout from source code repositories
        #
        self.updateModules(run)
  
        #
        # Checkout from source code repositories
        #
        self.syncWorkDirs(run)  
  
        # Return an exit code based off success
        # :TODO: Move onto run
        if run.getWorkspace().isSuccess():
            result = SUCCESS 
        else: 
            result = FAILED
        
        return result
  
    def updateModules(self, run):
        return self.performUpdateModules( run, \
                                run.getGumpSet().getModules())
        
    def updateModulesAll(self, run):    
        return self.performUpdateModules( run, \
                                run.getGumpSet().getModuleSequence())

    def performUpdateModules(self, run, list):    
    
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
        
            if not module.hasCvs() \
                and not module.hasSvn()	\
                and not module.hasJars(): continue
            
            log.debug('Perform CVS/SVN/Jars Update on #[' + `moduleNo` + \
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
                
    def syncWorkDirs( self, run ):
        """copy the raw module (project) materials from source to work dir"""

        workspace = run.getWorkspace()

        log.debug('--- Synchronizing work directories with sources')  

        for module in run.getGumpSet().getModuleSequence():
    
            # If no CVS/SVN, nothing to sync   
            if not module.hasCvs() \
                and not module.hasSvn(): continue
    
            if module.okToPerformWork():
            
                sourcedir = os.path.abspath(os.path.join(workspace.getCvsDirectory(), \
                                        module.name)) # todo allow override
                destdir = os.path.abspath(workspace.getBaseDirectory())
                
                # Perform the sync...
                try:
                    syncDirectories(sourcedir,destdir,module)
                    module.changeState(STATE_SUCCESS)
                except:
                    module.changeState(STATE_FAILED,REASON_SYNC_FAILED)
                
    """
    
        ******************************************************************
        
            THE BUILD INTERFACE
        
        ******************************************************************
    
    """
    
    def buildAll(self,run):
        """ Build a GumpRun's Full Project Stack """
        sequence=run.getGumpSet().getProjectSequence()

        return self.buildProjectList(run,sequence)
  
    def buildProjects(self,run):
        """ Build a GumpRun's Projects """
        list=run.getGumpSet().getProjects()

        return self.buildProjectList(run,list)
  
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
        
            log.debug(' ------ Project: #[' + `projectNo` + '] of [' + `projectCount` + '] : ' + project.getName())
        
            
            # Extract stats (in case we want to do conditional processing)            
            stats=project.getStats()
            
            if project.isPackaged():             
                self.performPackageProcessing( run, project, stats)
                continue
                
            # Do this even if not ok
            self.performPreBuild( run, project, stats )

            wasBuilt=0
            if project.okToPerformWork():        
                log.debug(' ------ Building: [' + `projectNo` + '] ' + project.getName())

                # Turn on --verbose or --debug if failing ...
                if not STATE_SUCCESS == stats.currentState:
                    if stats.sequenceInState > 5:
                        project.setDebug(1)
                    else:
                        project.setVerbose(1)

                #
                # Get the appropriate build command...
                #
                cmd=project.getBuildCommand()

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
                    else:                         
                        # For now, things are going good...
                        project.changeState(STATE_SUCCESS)
                    
            # Do this even if not ok
            self.performPostBuild( run, project, repository, wasBuilt, stats )
    
            if project.isFailed():
                log.warn('Failed to build project #[' + `projectNo` + '] [' + project.getName() + '], state:' \
                        + project.getStateDescription())
                                                
            projectNo+=1


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
            
            # ----------------------------------------------------------------
            # :TODO: HACK HACK HACK HACK HACK HACK HACK
            # :TODO: HACK HACK HACK HACK HACK HACK HACK
            # :TODO: HACK HACK HACK HACK HACK HACK HACK
            # Rsync should delete these things, not allow
            # them to exist. We should NOT do this.
            dirToMake=os.path.abspath(os.path.join(basedir,mkdir.dir))
            if not os.path.exists(dirToMake): 
                # :TODO: HACK HACK HACK HACK HACK HACK HACK
                # :TODO: HACK HACK HACK HACK HACK HACK HACK
                # :TODO: HACK HACK HACK HACK HACK HACK HACK
                # ----------------------------------------------------------------  
           
                try:
                    os.makedirs(dirToMake)
                    project.addInfo('Made directory ['+dirToMake+']')
                except:
                    project.addError('Failed to make directory ['+dirToMake+']')
                    raise           
        else:
            project.addError('   <mkdir without \'dir\' attribute.')
            raise RuntimeError('Bad <mkdir, missing \'dir\' attribute')
               
    def performPreBuild( self, run, project, stats ):
        """ Perform pre-build Actions """
       
        log.debug(' ------ Performing pre-Build Actions (mkdir/delete) for : '+ project.getName())
        
        
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
                        project.getName() + ' ' + os.path.basename(propertiesFile))
                except:
                    log.error('Display Properties [ ' + propertiesFile + '] Failed', exc_info=1)   
                
            except:
                log.error('Generate Maven Properties Failed', exc_info=1)    
                project.changeState(STATE_FAILED,REASON_PREBUILD_FAILED)
            
        if not project.okToPerformWork():
            log.warn('Failed to perform prebuild on project [' + project.getName() + ']')

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
                    else:
                        project.addWarning('No license on project with outputs.')                                        
                                    
                if outputsOk: 
                    # Publish them all (if distributable)
                    # :TODO: check for distributable...
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
            project.addInfo('Project produces reports')    
            for report in project.getReports():
                reportDir=report.getResolvedPath() 
                project.addInfo('Reports in: ' + reportDir)
                catDirectoryContentsToFileHolder(project,reportDir,FILE_TYPE_OUTPUT)
    
        # Maven generates a maven.log...
        if project.hasMaven() and wasBuilt and not project.isPackaged():
            try:
                logFile=project.locateMavenLog()                                
                project.addDebug('Maven Log in: ' + logFile)                
                try:
                    catFileToFileHolder(project,logFile,	\
                        FILE_TYPE_LOG,
                        project.getName() + ' ' + os.path.basename(logFile))
                except:
                    log.error('Display Log [ ' + logFile + '] Failed', exc_info=1)   
                
            except:
                log.warning('Display Maven Log Failed', exc_info=1)    
                # Not worth crapping out over...
            
                        
    def performPackageProcessing(self, run, project, stats):
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
                
    """
    
        ******************************************************************
        
           MISC STUFF
        
        ******************************************************************
    
    """
    
    def loadStatistics(self,run):   
        """ Load Statistics into the run (to get current values) """
        self.processStatistics(run,1)
         
    def updateStatistics(self,run):        
        """ Update Statistics into the run (to set current values) """
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

        
    
        