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

from gump.utils import dump, display, getIndent
from gump.utils.note import Annotatable
from gump.utils.work import *

from gump.utils.tools import listDirectoryAsWork,syncDirectories

from gump.model.workspace import Workspace
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
from gump.output.rss import rss

###############################################################################
# Initialize
###############################################################################

SUCCESS=0
FAILED=1
MISSING_UTILITY=2
BAD_ENVIRONMENT=3

    
###############################################################################
# Functions
###############################################################################
def isAllProjects(pexpr):
    return pexpr=='all' or pexpr=='*'

###############################################################################
# Classes
###############################################################################


class GumpEngine:
    
    def preprocess(self,run,exitOnError=0):

        #
        # Perform start-up logic 
        #
        workspace = run.getWorkspace()
        
        #
        workspace.checkEnvironment(exitOnError)
        
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
            message='Workspace version ['+workspace.getVersion()+'] below expected [' + setting.ws_version + ']'
            workspace.addWarning(message)
            log.warn(message)   

    def integrate(self,run):
  
        #
        # Prepare the context
        #
        self.preprocess(run)
  
        #
        # Checkout from source code repositories
        #
        self.update(run)
  
        #
        # Run the build commands
        #
        self.build(run)
  
        # Update [or load if not 'all'] Statistics
        self.updateStatistics(run)
    
        # Build HTML Result (via Forrest)
        documenter=run.getOptions().getDocumenter()
        if documenter :
            documenter.document(run)
            
        #
        # Only an 'all' is an official build, for them:
        #
        #	Nag and provide RSS
        #
        if run.getGumpSet().isFull():
  
            #
            # Nag about failures -- only if we are allowed to
            #
            #
            nag(run)
  
            # Provide a news feed
            rss(run)

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
  
    def updateModules(self, run):
 
        workspace = run.getWorkspace()
        
        # :TODO: A tad bogus to move here
        os.chdir(workspace.getCvsDirectory())
        log.debug("Workspace CVS Directory: " + workspace.getCvsDirectory())

        #
        # A stash of known logins.
        #
        logins=readLogins()

        #log.debug('Modules to update:') 
    
        # Update all the modules that have CVS repositories
        for module in run.getGumpSet().getModules():          
        
            if not module.hasCvs() \
                and not module.hasSvn()	\
                and not module.hasJars(): continue
            
            log.debug('Perform CVS/SVN/Jars Update on: ' + module.getName())
    
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
                repository.performedWork(work)
                module.performedWork(work)
      
                # Update Context w/ Results  
                if not cmdResult.state==CMD_STATE_SUCCESS:              
                    log.error('Failed to update module: ' + module.name)        
                    module.changeState(STATE_FAILED,REASON_UPDATE_FAILED)
                else:
                    module.changeState(STATE_SUCCESS)
                    
                    # Were the contents of the repository modified?                                        
                    module.setUpdated(cmdResult.hasOutput())
                
    def syncWorkDirs( self, run ):
        """copy the raw module (project) materials from source to work dir 
          (hopefully using rsync, cp is fallback) """

        workspace = run.getWorkspace()

        log.debug('--- Synchronizing work directories with sources')  

        for module in run.getGumpSet().getModules():
    
            # If no CVS/SVN, nothing to sync   
            if not module.hasCvs() \
                and not module.hasSvn(): continue
    
            if module.okToPerformWork():
            
                sourcedir = os.path.abspath(os.path.join(workspace.getCvsDirectory(),module.name)) # todo allow override
                destdir = os.path.abspath(workspace.getBaseDirectory())
        
        
                # Perform the sync...
                work=syncDirectories(workspace.noRSync,WORK_TYPE_SYNC,\
                        dir.work,workspace.tmpdir,\
                        sourcedir,destdir,module.name)
                        
                # :TODO: Get the repostiory & store this work there also
                # might as well...
                    
                # Store the work as done on this module
                module.performedWork(work)
                

                # Update Context w/ Results  
                if not work.result.state==CMD_STATE_SUCCESS:
                    module.changeState(STATE_FAILED,REASON_SYNC_FAILED)
                else:
                    module.changeState(STATE_SUCCESS)
                
    """
    
        ******************************************************************
        
            THE BUILD INTERFACE
        
        ******************************************************************
    
    """
    
    def build(self,run):
        """ Build a GumpRun """
        sequence=run.getGumpSet().getSequence()

        return self.buildProjectSequence(run,sequence)
  
    def buildProjectSequence(self,run,sequence):
    
        workspace=run.getWorkspace()
        
        log.debug('Total Project Sequence (i.e. build order):');
        for p in sequence:
            log.debug('  Sequence : ' + p.name)

        log.debug('--- Building work directories with sources')

        # Place repository in jardir (to be renamed to repodir)
        repository=run.getOutputsRepository()

        # build all projects this project depends upon, then the project itself
        for project in sequence:  
            if project.isPackaged(): continue
            
            if project.okToPerformWork():     
                self.performPreBuild( run, project )

            if project.okToPerformWork():        
                log.debug(' ------ Building: ' + project.getName())

                cmd=project.getBuildCommand()

                if cmd:
                    # Execute the command ....
                    cmdResult=execute(cmd,workspace.tmpdir)
    
                    # Update Context    
                    work=CommandWorkItem(WORK_TYPE_BUILD,cmd,cmdResult)
                    project.performedWork(work)
            
                    # Update Context w/ Results  
                    if not cmdResult.state==CMD_STATE_SUCCESS:
                        reason=REASON_BUILD_FAILED
                        if cmdResult.state==CMD_STATE_TIMED_OUT:
                            reason=REASON_BUILD_TIMEDOUT
                        project.changeState(STATE_FAILED,reason)
                    else:                         
                        # For now, things are going good...
                        project.changeState(STATE_SUCCESS)
                    
            if project.okToPerformWork():                 
                # Double check the outputs...
                self.performPostBuild( run, project, repository )
    
            if not project.okToPerformWork():
                log.warn('Failed to build project [' + project.getName() + '], state:' \
                        + project.getStateDescription())


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
               
    def performPreBuild( self, run, project ):
        """ Perform pre-build Actions """
        
        
        #
        #
        # NOTE --------------- NOT TURNED ON YET!!!!!!
        #
        #
        if 0 and project.okToPerformWork():
        
            log.debug(' ------ Performing pre-Build Actions (mkdir/delete) for : '+ project.getName())
            
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
                
        if not project.okToPerformWork():
            log.warn('Failed to perform prebuild on project [' + project.getName() + ']')


    def performPostBuild(self, run, project, repository):
        """Perform Post-Build Actions"""
     
        log.debug(' ------ Performing post-Build Actions (check jars) for : '+ project.getName())

        if project.hasOutputs():
            outputsOk=1
            for jar in project.getJars():
                jarPath=os.path.abspath(jar.getPath())
                if not os.path.exists(jarPath):
                    project.changeState(STATE_FAILED,REASON_MISSING_OUTPUTS)
                    outputsOk=0
                    project.addError("Missing Output: " + str(jarPath))
                            
            if outputsOk: 
                for jar in project.getJars():
                    jarPath=os.path.abspath(jar.getPath())
                    # Copy to repository
                    repository.publish( project.getModule().getName(), jarPath )
            
                project.changeState(STATE_SUCCESS)
                    
                # For 'fun' list repository
                listDirectoryAsWork(project,repository.getGroupDir(project.getModule().getName()), \
                                    'list_repo_'+project.getName()) 
                    
            else:
                #
                # List all directories that should've contained
                # outputs, to see what is there.
                #
                dirs=[]
                dircnt=0
                for jar in project.getJars():
                    jarPath=os.path.abspath(jar.getPath())
                    dir=os.path.dirname(jarPath)
                    if not dir in dirs and os.path.exists(dir):
                        dircnt += 1
                        listDirectoryAsWork(project,dir,\
                            'list_'+project.getName()+'_dir'+str(dircnt)+'_'+os.path.basename(dir))
                        dirs.append(dir)
                    else:
                        project.addWarning("No such directory (where output is expect) : " + dir)
        else:
            project.changeState(STATE_SUCCESS)
    
                
    """
    
        ******************************************************************
        
           MISC STUFF
        
        ******************************************************************
    
    """
    
    def updateStatistics(self,run):
    
        log.debug('--- Updating Project Statistics')
    
        db=StatisticsDB()   
        
        workspace=run.getWorkspace()        
        
        if run.getGumpSet().isFull():
            #
            # Update stats (and stash onto projects)
            #
            db.updateStatistics(workspace)
        else:
            #
            # Load stats (and stash onto projects)
            #    
            db.loadStatistics(workspace)
            
