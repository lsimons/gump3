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

from gump.build.ant import AntBuilder

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
        #self.maven=MavenBuilder(run)

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
        projectCount=len(list)
        projectNo=0
        for project in list:  
                        
            projectNo+=1            
            project.setPosition(projectNo)
            
            # Invoke...
            self.buildProject(project)
            
    def buildProject(self,project):
        
        workspace=self.run.getWorkspace()
                 
        log.info(' Project: #[' + `project.getPosition()` + '] : ' + project.getName())
                    
        # Extract stats (in case we want to do conditional processing)            
        stats=None
        if project.hasStats():
            stats=project.getStats()
            
        #if project.isPackaged():             
        #    self.performProjectPackageProcessing(project, stats)
        #    continue
                
        # Do this even if not ok
        self.performPreBuild(project, stats)

        wasBuilt=0
        if project.okToPerformWork():        
            log.debug(' ------ Building: [' + `project.getPosition()` + '] ' + project.getName())

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

            if project.hasAnt():
                self.ant.buildProject(project, stats)
                    
        # Do this even if not ok
        self.performPostBuild( project, wasBuilt, stats )
    
        if project.isFailed():
            log.warn('Failed to build project #[' + `project.getPosition()` + '] : [' + project.getName() + '], state:' \
                    + project.getStateDescription())                           
                    
        # Generate/process the project event...
        self.run.generateEvent(project)      


    def performDelete(self,project,delete,index=0):
        """ Return the delete command for a <delete entry """
        basedir=os.path.abspath(project.getModule().getSourceDirectory() or dir.base)
    
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
                        os.path.basename(propertiesFile))
                except:
                    log.error('Display Properties [ ' + propertiesFile + '] Failed', exc_info=1)   
                
            except:
                log.error('Generate Maven Properties Failed', exc_info=1)    
                project.changeState(STATE_FAILED,REASON_PREBUILD_FAILED)
            
        if startedOk and not project.okToPerformWork():
            log.warn('Failed to perform pre-build on project [' + project.getName() + ']')

    def performPostBuild(self, project, wasBuilt, stats):
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
                catDirectoryContentsToFileHolder(project, reportDir, FILE_TYPE_OUTPUT)
    
        # Maven generates a maven.log...
        if project.hasMaven() and not project.isPackaged():
            pomFile=project.locateMavenProjectFile() 
            if os.path.exists(pomFile):                               
                project.addDebug('Maven POM in: ' + pomFile) 
                catFileToFileHolder(project, pomFile, FILE_TYPE_CONFIG) 
                    
            projpFile=project.locateMavenProjectPropertiesFile() 
            if os.path.exists(projpFile):                                                
                project.addDebug('Maven project properties in: ' + projpFile)                
                catFileToFileHolder(project, pomFile, FILE_TYPE_CONFIG) 
            
            logFile=project.locateMavenLog()                                
            if os.path.exists(logFile):
                project.addDebug('Maven Log in: ' + logFile)                
                catFileToFileHolder(project, logFile, FILE_TYPE_LOG)
            
                        
    def performProjectPackageProcessing(self, project, stats):
        """Perform Package Processing Actions"""
     
        log.debug(' ------ Performing Package Processing for : '+ project.getName())

        self.checkPackage(project)
        
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
    
            

    def  checkPackage(self,project):
        if self.okToPerformWork():
            #
            # Check the package was installed correctly...
            #
            outputsOk=1
            for jar in project.getJars():
                jarpath=jar.getPath()
                if jarpath:
                    if not os.path.exists(jarpath):
                        project.changeState(STATE_FAILED,REASON_PACKAGE_BAD)
                        outputsOk=0
                        project.addError("Missing Packaged Jar: " + str(jarpath))
    
            if outputsOk:
                project.changeState(STATE_COMPLETE,REASON_PACKAGE)
            else:
                # Just in case it was so bad it thought it had no
                # jars to check
                project.changeState(STATE_FAILED,REASON_PACKAGE_BAD)
                
                #
                # List them, why not...
                #            
                from gump.utils.tools import listDirectoryToFileHolder
                listDirectoryToFileHolder(project,project.getHomeDirectory(),	\
                    FILE_TYPE_PACKAGE, 'list_package_'+project.getName())                                            
        

    def getBuildCommand(self,javaCommand='java'):

        # get the ant element (if it exists)
        ant=self.xml.ant

        # get the maven element (if it exists)
        maven=self.xml.maven

        # get the script element (if it exists)
        script=self.xml.script

        if not (script or ant or maven):
          #  log.debug('Not building ' + project.name + ' (no <ant/> or <maven/> or <script/> specified)')
          return None

        if self.hasScript():
            return self.getScriptCommand()
        elif self.hasMaven() :
            return self.getMavenCommand()
        else:
            return self.getAntCommand(javaCommand)
        
    #
    # Build an ANT command for this project
    #        
    def getAntCommand(self,javaCommand='java'):
        
        ant=self.ant
        antxml=self.xml.ant
    
        # The ant target (or none == ant default target)
        target= antxml.target or ''
    
        # The ant build file (or none == build.xml)
        buildfile = antxml.buildfile or ''
    
        # Optional 'verbose' or 'debug'
        verbose=antxml.verbose
        debug=antxml.debug
    
        #
        # Where to run this:
        #
        basedir = ant.getBaseDirectory() or self.getBaseDirectory()
    
        #
        # Build a classpath (based upon dependencies)
        #
        (classpath,bootclasspath)=self.getClasspaths()
    
        #
        # Get properties
        #
        properties=self.getAntProperties()
   
        #
        # Get properties
        #
        sysproperties=self.getAntSysProperties()
   
        #
        # Get properties
        #
        jvmargs=self.getJVMArgs()
   
        #
        # Run java on apache Ant...
        #
        cmd=Cmd(javaCommand,'build_'+self.getModule().getName()+'_'+self.getName(),\
            basedir,{'CLASSPATH':classpath})
            
        # These are workspace + project system properties
        cmd.addNamedParameters(sysproperties)
        
        
        # :NOTE: Commented out since <sysproperty was implemented.
        #
        # Set this as a system property. Setting it here helps JDK1.4+
        # AWT implementations cope w/o an X11 server running (e.g. on
        # Linux)
        # cmd.addPrefixedParameter('-D','java.awt.headless','true','=')
    
    
        # :NOTE: Commented out since <sysproperty was implemented.
        #
        # This helps ant maintain VM information for sub-VMs it launches.
        #
        # cmd.addPrefixedParameter('-D','build.clonevm','true','=')
        
        #
        # Add BOOTCLASSPATH
        #
        if bootclasspath:
            cmd.addPrefixedParameter('-X','bootclasspath/p',bootclasspath,':')
            
        if jvmargs:
            cmd.addParameters(jvmargs)
            
        cmd.addParameter('org.apache.tools.ant.Main')  
    
        #
        # Allow ant-level debugging...
        #
        if self.getWorkspace().isDebug() or self.isDebug() or debug: 
            cmd.addParameter('-debug')  
        if self.getWorkspace().isVerbose()  or self.isVerbose() or verbose: 
            cmd.addParameter('-verbose')  
        
        #
        #	This sets the *defaults*, a workspace could override them.
        #        
        # :NOTE: Commented out since <property on workspace works.
        # cmd.addPrefixedParameter('-D','build.sysclasspath','only','=')
    
        mergeFile=self.getWorkspace().getMergeFile()
        if mergeFile:
            cmd.addPrefixedParameter('-D','gump.merge',str(mergeFile),'=')        
    
        # These are from the project and/or workspace
        # These are 'normal' properties.
        cmd.addNamedParameters(properties)
    
        # Pass the buildfile
        if buildfile: cmd.addParameter('-f',buildfile)
    
        # End with the target...
        if target: 
            for targetParam in target.split():
                cmd.addParameter(targetParam)
    
        return cmd

                

    def getJVMArgs(self):
        """Get JVM arguments for a project"""
        args=Parameters()
        
        if self.hasAnt():
            jvmargs=self.getAnt().xml.jvmarg
        elif self.hasMaven():
            jvmargs=self.getMaven().xml.jvmarg
                
        for jvmarg in jvmargs:
            if jvmarg.value:
                args.addParameter(jvmarg.value)
            else:
                log.error('Bogus JVM Argument w/ Value')            
        
        return args
  
    def getAntProperties(self):
        """Get properties for a project"""
        properties=Parameters()
        for property in self.getWorkspace().getProperties()+self.getAnt().getProperties():
            properties.addPrefixedNamedParameter('-D',property.name,property.value,'=')
        return properties

    def getAntSysProperties(self):
        """Get sysproperties for a project"""
        properties=Parameters()
        for property in self.getWorkspace().getSysProperties()+self.getAnt().getSysProperties():
            properties.addPrefixedNamedParameter('-D',property.name,property.value,'=')
        return properties
