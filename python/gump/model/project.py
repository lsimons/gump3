#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/project.py,v 1.64 2004/03/14 20:16:30 ajack Exp $
# $Revision: 1.64 $
# $Date: 2004/03/14 20:16:30 $
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
    This module contains information on
"""

from time import localtime, strftime, tzname

from gump.model.state import *
from gump.model.object import ModelObject, NamedModelObject, Jar,	\
                                Resultable, \
                                 Mkdir, Delete, JunitReport, Work
from gump.model.stats import Statable, Statistics
from gump.model.property import Property
from gump.model.ant import Ant,Maven,Script
from gump.model.rawmodel import Single
from gump.utils import getIndent
from gump.utils.file import *
from gump.model.depend import *
from gump.utils.note import transferAnnotations, Annotatable

#
# An annotated path has a path entry, plus the context
# of the contributor (i.e. project of Gump.)
#
class AnnotatedPath:
    """Contains a Path plus optional 'contributor' """
    def __init__(self,id,path,contributor=None,instigator=None,note=None):
        self.id=id
        self.path=path
        self.contributor=contributor
        self.instigator=instigator
        self.note=note
        
    def __repr__(self):
        return self.path
        
    def __str__(self):
        return self.path
        
    # Equal if same string
    def __eq__(self,other):
        if not isinstance(other,AnnotatedPath):
            otherPath = other
        else:
            otherPath = other.path             
        return self.path == otherPath
                
    # Equal if same string
    def __cmp__(self,other):
        if not isinstance(other,AnnotatedPath):
            otherPath = other
        else:
            otherPath = other.path                         
        c = cmp(self.path,otherPath)
        return c
        
    def hasContributor(self):
        if self.contributor: return 1
        return 0
        
    def getContributor(self):
        return self.contributor
        
    def hasId(self):
        if self.id: return 1
        return 0
        
    def getId(self):
        return self.id
        
    def hasInstigator(self):
        if self.instigator: return 1
        return 0
        
    def getInstigator(self):
        return self.instigator
        
    def getPath(self):
        return self.path
        
class Classpath(Annotatable):
    def __init__(self,name):
        Annotatable.__init__(self)
        self.name=name
        self.parts=[]
    
    def getName(self):
        return self.name
        
    def addPathPart(self,part):
        if part in self.parts:
            self.addDebug('Duplicate Path Part [' + `part` + ']')
        else:
            self.parts.append(part)
        
    def importFlattenedParts(self,parts):
        for part in split(parts,os.pathsep):
            self.addPathPart(part)
            
    def importClasspath(self,cp):
        for part in cp.getPathParts():
            self.addPathPart(part)
    
    def getPathParts(self):
        return self.parts
                        
    #
    # Convert path and AnnotatedPath to simple paths.
    # 
    def getSimpleClasspathList(self):
        """ Return simple string list """
        simple=[]
        for p in self.parts:
            if isinstance(p,AnnotatedPath):
                simple.append(p.path)
            else:
                simple.append(p)
        return simple
        
    def getFlattened(self):
        return os.pathsep.join(self.getSimpleClasspathList())
            

class Project(NamedModelObject, Statable, Resultable, Dependable):
    """A single project"""
    def __init__(self,xml,workspace):
    	NamedModelObject.__init__(self,xml.getName(),xml,workspace)
    	
    	Statable.__init__(self)
    	Resultable.__init__(self)
    	Dependable.__init__(self)
    	
    	# Navigation
        self.module=None # Module has to claim ownership
        self.workspace=workspace
    	
    	self.home=None
    	self.basedir=None
    	
    	self.license=None
    	
    	self.affected=0
        
    	#############################################################
    	#
    	# Sub-Components
    	#
    	self.ant=None
    	self.maven=None
    	self.script=None

    	self.works=[]
    	self.mkdirs=[]
    	self.deletes=[]
    	self.reports=[]
    	
    	#############################################################
    	# Outputs
    	#
        self.jars={}        
        
    	#############################################################
    	# Misc
    	#        
        self.honoraryPackage=0
        
    def hasAnt(self):
        if hasattr(self,'ant') and self.ant: return 1
        return 0
        
    def hasMaven(self):
        if hasattr(self,'maven') and self.maven: return 1
        return 0
        
    def hasScript(self):
        if hasattr(self,'script') and self.script: return 1
        return 0
    
    def getAnt(self):
        return self.ant
        
    def getMaven(self):
        return self.maven
        
    def getScript(self):
        return self.script
    
    def hasURL(self):
        return self.getURL()
    
    def getURL(self):
        if self.xml.url and self.xml.url.href: return str(self.xml.url.href)
        return self.getModule().getURL()            
        
    def hasDescription(self):
        return str(self.xml.description) or self.getModule().hasDescription()  
        
    def getDescription(self):
        return str(self.xml.description) or self.getModule().getDescription()    
        
    def getMetadataLocation(self):
        if self.xml.href and str(self.xml.href): return self.xml.href
        return self.getModule().getMetadataLocation()
                     
    def getMetadataViewUrl(self):
        if self.xml.href and str(self.xml.href):
            location=str(self.xml.href)
            if location.startswith('http'): return location
            # :TODO: Make configurable
            return 'http://cvs.apache.org/viewcvs.cgi/gump/' + location
        return self.getModule().getMetadataViewUrl()
                        
    def getViewUrl(self):
        # :TODO: if a basedir then offset?
        return self.getModule().getViewUrl()
            
    def addJar(self,jar):
        self.jars[jar.getName()]=jar
        
    def getJarCount(self):
        return len(self.jars)
        
    def hasJarWithId(self,id):
        return self.jars.has_key(id)
        
    def hasLicense(self):
        if self.license: return 1
        return 0
        
    def getLicense(self):
        return self.license
        
    def hasJars(self):
        return self.jars
        
    def getJars(self):
        return self.jars.values()
        
    def getJarAt(self,index):
        return self.jars.values()[index]
        
    def hasReports(self):
        if self.reports: return 1
        return 0
        
    def getReports(self):
        return self.reports
        
    def getFOGFactor(self):
        return self.getStats().getFOGFactor()
        
    # Only modules get updated.
    def getLastUpdated(self):
        return self.getModule().getStats().getLastUpdated()  
        
    def determineAffected(self):
        if self.affected: return self.affected
        
        # Look through all dependees
        for dependee in self.getFullDependees():
            project=dependee.getOwnerProject()
            
            cause=project.getCause()
            #
            # Something caused this some grief
            #
            if cause:
                #
                # The something was this module or one of its projects
                #
                if cause == self:
                    self.affected += 1            
        
        return self.affected
        
    def propagateErrorStateChange(self,state,reason,cause,message):
        
        #
        # Mark depend*ee*s as failed for this cause...
        # Warn option*ee*s
        #
        for dependee in self.getDirectDependees():  
    
            # This is a backwards link, so use the owner
            dependeeProject=dependee.getOwnerProject()
        
            if dependee.isOptional():
                dependeeProject.addWarning("Optional dependency " + self.name + " " + message)
            else:
                dependee.addError("Dependency " + self.name + " " + message)
                dependeeProject.changeState(STATE_PREREQ_FAILED,reason,cause)
    #
    # We have a potential clash between the <project package attribute and
    # the <project <package element. The former indicates a packages install
    # the latter the (Java) package name for the project contents. As such
    # we test the attribute for type.
    #                                      
    def isPackaged(self):
        return self.isPackageMarked() or self.honoraryPackage
    
    def isPackageMarked(self):
        return (type(self.xml.package) in types.StringTypes)
                  
    def setHonoraryPackage(self,honorary):
        self.honoraryPackage=honorary
    
    # provide elements when not defined in xml
    def complete(self,workspace):
        if self.isComplete(): return

        if not self.inModule():
            self.addWarning("Not in a module")
            return
    
        #
        # Packaged Projects don't need the full treatment..
        #
        packaged=self.isPackaged()

        # Import any <ant part [if not packaged]
        if self.xml.ant and not packaged:
            self.ant = Ant(self.xml.ant,self)
        
        # Import any <maven part [if not packaged]
        if self.xml.maven and not packaged:
            self.maven = Maven(self.xml.maven,self)
            
        # Import any <maven part [if not packaged]
        if self.xml.maven and not packaged:
            self.maven = Maven(self.xml.maven,self)
            
        # Import any <script part [if not packaged]
        if self.xml.script and not packaged:
            self.script = Script(self.xml.script,self)
        
        # Set this up to be the base directory of this project,
        # if one is set
        if self.xml.basedir:
            self.basedir = os.path.abspath(os.path.join(	\
                                self.getModule().getSourceDirectory() or dir.base,	\
                                self.xml.basedir))
         
        # Compute home directory
        if self.isPackaged():
            # Installed below package directory
            if self.isPackageMarked():
                self.home=os.path.abspath(	\
                    os.path.join(workspace.xml.pkgdir,	self.xml.package))
            else:
                self.home=os.path.abspath(workspace.xml.pkgdir)
        elif self.xml.home and isinstance(self.xml.home,Single):
            if self.xml.home.nested:
                module=self.getModule()    
                self.home=os.path.abspath(\
                    os.path.join(module.getSourceDirectory(),\
                        self.xml.home.nested))
            elif self.xml.home.parent:
                self.home=os.path.abspath(	\
                    os.path.join(workspace.getBaseDirectory(),	\
                        self.xml.home.parent))
            else:
                message='Unable to complete project.home for [not nested/parent]: ' + self.name
                self.addError(message)
                self.home=None        
        elif not self.xml.home:
            if self.module:
                module=self.getModule()    
                self.home=os.path.abspath(module.getSourceDirectory())
            else:
                self.home=os.path.abspath(os.path.join(workspace.getBaseDirectory(),self.name))
        else:
            message='Unable to complete project.home for: ' + self.name 
            self.addError(message)
            self.home=None

        # Extract license 
        if self.xml.license and self.xml.license.name:
            self.license = self.xml.license.name
        
        #
        # Resolve jars (outputs)
        #
        for j in self.xml.jar:
            if self.home and j.getName():
                jar=Jar(j,self)
                jar.setPath(os.path.abspath(os.path.join(self.home,j.name)))
                self.addJar(jar)
            else:
                self.addError('Found a <jar with no name...')
                
        #
        # Fix 'ids' on all Jars which don't have them
        #
        if self.hasJars():
            if 1 == self.getJarCount():
                jar=self.getJarAt(0)
                if not jar.hasId():
                    self.addInfo('Sole jar [' + jar.getPath() + '] identifier set to project name')
                    jar.setId(self.getName())    
            else:
                #
                # :TODO: A work in progress, not sure how
                # we ought 'construct' ids.
                #
                for jar in self.getJars():
                    if not jar.hasId():
                        basename=os.path.basename(jar.getPath())
                        self.addWarning('Jar [' + jar.getPath() + '] identifier set to jar basename: [' + basename + ']')    
                        jar.setId(basename)
        
        # Grab all the work
        for w in self.xml.work:
            work=Work(w,self)
            self.works.append(work)

        # Grab all the mkdirs
        for m in self.xml.mkdir:
            mkdir=Mkdir(m,self)
            self.mkdirs.append(mkdir)

        # Grab all the deleted
        for d in self.xml.delete:
            delete=Delete(d,self)
            self.deletes.append(delete)

        # Grab all the reports (junit for now)
        if self.xml.junitreport:
            report=JunitReport(self.xml.junitreport,self)
            self.reports.append(report)

        # Build Dependencies Map [including depends from <ant|maven/<property/<depend
        if not packaged:
            (badDepends, badOptions) = self.importDependencies(workspace)                        

        # Expand <ant <depends/<properties...
        if self.ant: self.ant.expand(self,workspace)
        if self.maven: self.maven.expand(self,workspace)

        if not packaged:
            # Complete dependencies so properties can reference the,
            # completed metadata within a dependent project
            for dependency in self.getDirectDependencies():
                dependency.getProject().complete(workspace)

            self.buildDependenciesMap(workspace)                        
        
        #
        # complete properties
        #
        if self.ant: 
            self.ant.complete(self,workspace)
            transferAnnotations(self.ant, self)  
            
        if self.maven: 
            self.maven.complete(self,workspace)
            transferAnnotations(self.maven, self)    
            
        if self.script: 
            self.script.complete(self,workspace)
            transferAnnotations(self.script, self)              
            
        if not packaged:    
            #
            # TODO -- move these back?
            #
            if badDepends or badOptions: 
                for xmldepend in badDepends:
                    self.changeState(STATE_FAILED,REASON_CONFIG_FAILED)
                    self.addError("Bad Dependency. Project: " \
                            + xmldepend.project + " unknown to *this* workspace")

                for xmloption in badOptions:                
                    self.addWarning("Bad *Optional* Dependency. Project: " \
                            + xmloption.project + " unknown to *this* workspace")
        else:
            self.addInfo("This is a packaged project, location: " + str(self.home))        
                                    
        # Copy over any XML errors/warnings
        transferAnnotations(self.xml, self)  
        
        # Done, don't redo
        self.setComplete(1)

    def  checkPackage(self):
        if self.okToPerformWork():
            #
            # Check the package was installed correctly...
            #
            outputsOk=1
            for jar in self.getJars():
                jarpath=jar.getPath()
                if jarpath:
                    if not os.path.exists(jarpath):
                        self.changeState(STATE_FAILED,REASON_PACKAGE_BAD)
                        outputsOk=0
                        self.addError("Missing Packaged Jar: " + str(jarpath))
    
            if outputsOk:
                self.changeState(STATE_COMPLETE,REASON_PACKAGE)
            else:
                # Just in case it was so bad it thought it had no
                # jars to check
                self.changeState(STATE_FAILED,REASON_PACKAGE_BAD)
                
                #
                # List them, why not...
                #            
                from gump.utils.tools import listDirectoryToFileHolder
                listDirectoryToFileHolder(self,self.getHomeDirectory(),	\
                    FILE_TYPE_PACKAGE, 'list_package_'+self.getName())                                            
        
    def importDependencies(self,workspace):        
        badDepends=[]
        # Walk the XML parts converting
        for xmldepend in self.xml.depend:
            dependProjectName=xmldepend.project
            if workspace.hasProject(dependProjectName):
                dependProject=workspace.getProject(dependProjectName)
                
                # Import the dependency
                dependency=importXMLDependency(self, dependProject, xmldepend, 0)
                                
                # Add a dependency
                self.addDependency(dependency)
            else:
                badDepends.append(xmldepend)    
                
        # Walk the XML parts converting
        badOptions=[]
        for xmloption in self.xml.option:
            optionProjectName=xmloption.project
            if workspace.hasProject(optionProjectName):
                optionProject=workspace.getProject(optionProjectName)
                                
                # Import the dependency
                dependency=importXMLDependency(self, optionProject, xmloption, 1)
                                
                # Add a dependency
                self.addDependency(dependency)                    
            else:
                badOptions.append(xmloption)

        return (badDepends, badOptions)
        
    def hasBaseDirectory(self):
        if hasattr(self,'basedir') and self.basedir: return 1
        return 0
        
    def getBaseDirectory(self):
         return self.basedir
         
    def hasHomeDirectory(self):
        if hasattr(self,'home') and self.home: return 1
        return 0
        
    def getHomeDirectory(self):
        return self.home
        
    def inModule(self):
        return hasattr(self,'module') and self.module
        
    def setModule(self,module):
        if hasattr(self,'module') and self.module:
            raise RuntimeError, 'Project [' + self.name + '] already has a module set'
        self.module=module
        
    def getModule(self):
        if not self.inModule(): raise RuntimeError, 'Project [' + self.name + '] not in a module.]'
        return self.module 
        
    def getWorkspace(self):
        return self.workspace
        
    def hasBuildCommand(self):
        hasBuild=0
        # I.e has an <ant or <script element
        if self.xml.ant or self.xml.script or self.xml.maven: hasBuild=1    
        return hasBuild

    def getBuildCommand(self):

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
            return self.getAntCommand()
        
    #
    # Build an ANT command for this project
    #        
    def getAntCommand(self):
        
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
        jvmargs=self.getJVMArgs()
   
        #
        # Run java on apache Ant...
        #
        cmd=Cmd(self.getWorkspace().getJavaCommand(),'build_'+self.getModule().getName()+'_'+self.getName(),\
            basedir,{'CLASSPATH':classpath})
            
        # Set this as a system property. Setting it here helps JDK1.4+
        # AWT implementations cope w/o an X11 server running (e.g. on
        # Linux)
        cmd.addPrefixedParameter('-D','java.awt.headless','true','=')
    
        #
        # This helps ant maintain VM information for sub-VMs it launches.
        #
        cmd.addPrefixedParameter('-D','build.clonevm','true','=')
        
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
        cmd.addPrefixedParameter('-D','build.sysclasspath','only','=')
    
        mergeFile=self.getWorkspace().getMergeFile()
        if mergeFile:
            cmd.addPrefixedParameter('-D','gump.merge',str(mergeFile),'=')        
    
        # These are module level plus project level
        cmd.addNamedParameters(properties)
    
        # Pass the buildfile
        if buildfile: cmd.addParameter('-f',buildfile)
    
        # End with the target...
        if target: 
            for targetParam in target.split():
                cmd.addParameter(targetParam)
    
        return cmd

    #
    # Build an ANT command for this project
    #        
    def getMavenCommand(self):
        maven=self.maven
        mavenxml=self.xml.maven
    
        # The ant goal (or none == ant default goal)
        goal=maven.getGoal()
    
        # Optional 'verbose' or 'debug'
        verbose=mavenxml.verbose
        debug=mavenxml.debug
    
        #
        # Where to run this:
        #
        basedir = maven.getBaseDirectory() or self.getBaseDirectory()
    
        #
        # Build a classpath (based upon dependencies)
        #
        (classpath,bootclasspath)=self.getClasspaths()
    
        #
        # Get properties
        #
        #jvmargs=self.getJVMArgs()
   
        #
        # Run Maven...
        #
        cmd=Cmd('maven','build_'+self.getModule().getName()+'_'+self.getName(),\
            basedir,{'CLASSPATH':classpath})
            
        # Set this as a system property. Setting it here helps JDK1.4+
        # AWT implementations cope w/o an X11 server running (e.g. on
        # Linux)
        # cmd.addPrefixedParameter('-D','java.awt.headless','true','=')
    
        #
        # Add BOOTCLASSPATH
        #
        #if bootclasspath:
        #    cmd.addPrefixedParameter('-X','bootclasspath/p',bootclasspath,':')
            
        #if jvmargs:
        #    cmd.addParameters(jvmargs)
            
        # cmd.addParameter('org.apache.maven.cli.App')  
    
        #
        # Allow maven-level debugging...
        #
        if self.getWorkspace().isDebug() or self.isDebug() or debug: 
            cmd.addParameter('--debug')  
        if self.getWorkspace().isVerbose()  or self.isVerbose() or verbose: 
            cmd.addParameter('--exception') 
        
        #
        # Suppress downloads
        #          
        cmd.addParameter('--offline')  
        
        #
        #	This sets the *defaults*, a workspace could override them.
        #
        #cmd.addPrefixedParameter('-D','build.sysclasspath','only','=')
    
        # End with the goal...
        cmd.addParameter(goal)
    
        return cmd
  
    def getScriptCommand(self):
        """ Return the command object for a <script entry """
        script=self.script
        scriptxml=self.xml.script 
           
        #
        # Where to run this:
        #
        basedir = script.getBaseDirectory() or self.getBaseDirectory()

        # Add .sh  or .bat as appropriate to platform
        scriptfullname=scriptxml.name
        if not os.name == 'dos' and not os.name == 'nt':
            scriptfullname += '.sh'
        else:
            scriptfullname += '.bat'
      
        # Optional 'verbose' or 'debug'
        verbose=scriptxml.verbose
        debug=scriptxml.debug
       
        scriptfile=os.path.abspath(os.path.join(basedir, scriptfullname))
        
        # Not sure this is relevent...
        (classpath,bootclasspath)=self.getClasspaths()

        cmd=Cmd(scriptfile,'buildscript_'+self.getModule().getName()+'_'+self.getName(),\
            basedir,{'CLASSPATH':classpath})    
            
        # Set this as a system property. Setting it here helps JDK1.4+
        # AWT implementations cope w/o an X11 server running (e.g. on
        # Linux)
        #    
        cmd.addPrefixedParameter('-D','java.awt.headless','true','=')
    
        #
        # Add BOOTCLASSPATH
        #
        if bootclasspath:
            cmd.addPrefixedParameter('-X','bootclasspath/p',bootclasspath,':')
                    
        #
        # Allow script-level debugging...
        #
        if self.getWorkspace().isDebug() or self.isDebug() or debug:
            cmd.addParameter('-debug')  
        if self.getWorkspace().isVerbose()  or self.isVerbose() or verbose:
            cmd.addParameter('-verbose')  
        
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

    # The propertiesFile parameter is primarily for testing.
    def generateMavenProperties(self,propertiesFile=None):
        """Set properties/overrides for a Maven project"""
        
        #
        # Where to put this:
        #
        basedir = self.maven.getBaseDirectory() or self.getBaseDirectory()
        if not propertiesFile: 
            propertiesFile=os.path.abspath(os.path.join(	\
                    basedir,'build.properties'))
        
        if os.path.exists(propertiesFile):
            self.addWarning('Overriding Maven properties: ['+propertiesFile+']')
    
        
        props=open(propertiesFile,'w')
        
        props.write(("""# ------------------------------------------------------------------------
# DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT 
#
# File Automatically Generated by Gump, see http://gump.apache.org/
#
# Generated For : %s
# Generated At  : %s
#
#
# DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT  DO NOT EDIT
# ------------------------------------------------------------------------
""")	%	(self.getName(), time.strftime('%Y-%m-%d %H:%M:%S')) )
        
        #
        # Output basic properties
        #
        for property in self.getWorkspace().getProperties()+self.getMaven().getProperties():
            # build.sysclasspath makes Maven sick.
            if not 'build.sysclasspath' == property.name:
                props.write(('%s=%s\n') % (property.name,property.value))            
        
        #
        # Output classpath properties
        #
        props.write("""
# ------------------------------------------------------------------------
# M A V E N  J A R  O V E R R I D E
# ------------------------------------------------------------------------
maven.jar.override = on

# ------------------------------------------------------------------------
# Jars set explicity by path.
# ------------------------------------------------------------------------
""")
        
        (classpath,bootclasspath)=self.getClasspathLists()
        
        # :TODO: write...
        for annotatedPath in classpath.getPathParts():
            if isinstance(annotatedPath,AnnotatedPath):
                id=annotatedPath.getId()
                path=annotatedPath.getPath()
                props.write(('maven.jar.%s=%s\n') % (id,path))

        return propertiesFile
      
    def locateMavenLog(self):
        """Return Maven log location"""
        
        #
        # Where to put this:
        #
        basedir = self.maven.getBaseDirectory() or self.getBaseDirectory()
        logFile=os.path.abspath(os.path.join(\
                    basedir,'maven.log'))
        
        return logFile
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        output.write(getIndent(indent)+'Project: ' + self.getName() + '\n')
        NamedModelObject.dump(self, indent+1, output)
        
        for dependency in self.depends:
            dependency.dump(indent+1,output)
                        
        if self.ant:
            self.ant.dump(indent+1,output)
            
    #
    # Return a list of the outputs this project generates
    #    
    def getAnnotatedOutputsList(self): 
        outputs=[]
        for jar in self.getJars():
            jarpath=jar.getPath()
            outputs.append(AnnotatedPath(jar.getId(),jarpath,self,None,"Project output"))                    
        return outputs
                 
    #
    # Does this project generate outputs (currently JARs)
    #                  
    def hasOutputs(self):
        return self.hasJars() or self.hasLicense()
    
    #
    # Return a (classpath, bootclaspath) tuple for this project
    #
    def getClasspaths(self,debug=0):
        #
        # Calculate classpath and bootclasspath
        #
        (classpath, bootclasspath) = self.getClasspathLists(debug)
        
        #
        # Return them simple/flattened
        #
        return ( classpath.getFlattened(), bootclasspath.getFlattened() )



    #
    # Maybe this is dodgy (it is inefficient) but we need some
    # way to get the sun tools for a javac compiler for ant and
    # I don't know a more portable way.
    #
    # When we get closer to done perhaps strip out the tools only, 
    # and not allow the users classpath to pollute ours...
    #
    def getSystemClasspathList(self):
        sysClasspath=Classpath('System Classpath')
        try:
            syscp=os.environ['CLASSPATH']
        except:
            syscp=''
            
        sysClasspath.importFlattenedParts(syscp)
        
        return sysClasspath

    #
    # Return a tuple of (CLASSPATH, BOOTCLASSPATH) for a project
    #
    def getClasspathLists(self,debug=0):
        """Get a TOTAL classpath for a project (including its dependencies)"""

        #
        # Do this once only... storing it on the context. Not as nice as 
        # doing it OO (each project context stores its own, but a step..)
        #
        if hasattr(self,'resolvedClasspath') and hasattr(self,'resolvedBootclasspath') :
          if debug: print "Classpath/Bootclasspath previously resolved..."
          return ( self.resolvedClasspath, self.resolvedBootclasspath )
  
        # Start with the system classpath (later remove this)
        classpath=self.getSystemClasspathList()
        bootclasspath=Classpath('Boot Classpath')

        #
        # Add this project's work directories (these go into
        # CLASSPATH, never BOOTCLASSPATH)
        #
        srcdir=self.getModule().getSourceDirectory()
          
        for work in self.xml.work:
            path=None
            if work.nested:
                path=os.path.abspath(os.path.join(srcdir,work.nested))
            elif work.parent:
                path=os.path.abspath(os.path.join(self.getWorkspace().getBaseDirectory(),work.parent))
            else:
                log.error("<work element without nested or parent attributes on " \
                  + self.getName() + " in " + self.getModule().getName())

            if path:
                if debug: print "Work Entity:   " + path               
                classpath.addPathPart(AnnotatedPath('',path,self,None,'Work Entity'))
              
        # Append dependent projects (including optional)
        visited=[]
  
        # Does it have any depends? Process all of them...
        for dependency in self.getDirectDependencies():
            (subcp, subbcp) = self.getDependOutputList(dependency,visited,1,debug)
            self.importClasspaths(classpath,bootclasspath,subcp,subbcp)
    
        #
        # Store so we don't do this twice.
        #            
        self.resolvedClasspath = classpath
        self.resolvedBootclasspath = bootclasspath
  
        return (self.resolvedClasspath ,self.resolvedBootclasspath)

    #
    # Perform this 'dependency' (mandatory or optional)
    #
    # 1) Bring in the JARs (or those specified by id in depend ids)
    # 2) Do NOT bring in the working entities (directories/jars)
    # 3) Bring in the sub-depends (or optional) if inherit='all' or 'hard'
    # 4) Bring in the runtime sub-depends if inherit='runtime'
    # 5) Also: *** Bring in any depenencies that the dependency inherits ***
    #
    def getDependOutputList(self,dependency,visited,depth=0,debug=0):      
        """Get a classpath of outputs for a project (including its dependencies)"""            
   
        # Don't loop...
        if dependency in visited:  
            # beneficiary.addInfo("Duplicated dependency [" + str(depend) + "]")          
            if debug:
                print str(depth) + ") Already Visited : " + str(depend)
                print str(depth) + ") Previously Visits  : "
                for v in visited:
                    print str(depth) + ")  - " + str(v)
            return (None,None)
            
        visited.append(dependency)
        
        if debug:
            print str(depth) + ") Perform : " + `dependency`
                  
        # 
        #
        #
        classpath=Classpath('Classpath for ' + `dependency`)
        bootclasspath=Classpath('Bootclasspath for ' + `dependency`)

        #
        # Context for this dependecy project...
        #
        project=dependency.getProject()
  
        # The dependency drivers...
        #
        # runtime (i.e. this is a runtime dependency)
        # inherit (i.e. inherit stuff from a dependency)
        #
        runtime=dependency.runtime
        inherit=dependency.inherit
        if dependency.ids:
            ids=dependency.ids.split()
        else:
            ids=None
  
        #
        # Explain..
        #
        dependStr=''
        if inherit: 
            if dependStr: dependStr += ', '
            dependStr += 'Inherit:'+dependency.getInheritenceDescription()
        if runtime: 
            if dependStr: dependStr += ', '
            dependStr += 'Runtime'
  
        #
        # Append JARS for this project
        #	(respect ids)
        #
        projectIds=[]
        for jar in project.getJars():
            # Store for double checking
            if jar.getId(): projectIds.append(jar.getId())
            
            # If 'all' or in ids list:
            if (not ids) or (jar.getId() in ids):   
                if ids: dependStr += ' Id = ' + jar.getId()
                path=AnnotatedPath(jar.getId(),jar.path,project,dependency.getOwnerProject(),dependStr) 
          
                # Add to CLASSPATH
                if not jar.getType() == 'boot':
                    if debug:   print str(depth) + ') Append JAR : ' + str(path)
                    classpath.addPathPart(path)
                else:
                    # Add to BOOTCLASSPATH
                    if debug:   print str(depth) + ') Append *BOOTCLASSPATH* JAR : ' + str(path)
                    bootclasspath.addPathPart(path)    

        #
        # Double check IDs (to reduce stale ids in metadata)
        #
        if ids:
            for id in ids:
                if not id in projectIds:
                    # :TODO: This will cause repeats of this message
                    # for every dep who tries to use this
                    # Gumpy really needs to be OO!!!!
                    dependency.getOwnerProject().addWarning("Invalid ID [" + id \
                          + "] for dependency on [" + project.getName() + "]")

        # Append sub-projects outputs, if inherited
        for subdependency in project.getDirectDependencies():        
            #	If the dependency is set to 'all' (or 'hard') we inherit all dependencies
            # If the dependency is set to 'runtime' we inherit all runtime dependencies
            # If the dependent project inherited stuff, we inherit that...
            if    	(inherit==INHERIT_ALL or inherit==INHERIT_HARD) \
                    or (inherit==INHERIT_RUNTIME and subdependency.isRuntime()) \
                    or (subdependency.inherit > INHERIT_NONE):      
                (subcp, subbcp) = self.getDependOutputList(subdependency,visited,depth+1,debug)
                self.importClasspaths(classpath,bootclasspath,subcp,subbcp)   
            elif debug:
                print str(depth) + ') Skip : ' + str(subdependency) + ' in ' + project.name

        return (classpath, bootclasspath)
    

    #
    # Import cp and bcp into classpath and bootclasspath,
    # but do not accept duplicates. Report duplicates.
    #
    def importClasspaths(self,classpath,bootclasspath,cp,bcp):
        if cp:
            classpath.importClasspath(cp)                
        if bcp:
            bootclasspath.importClasspath(bcp)                      


class ProjectStatistics(Statistics):
    """Statistics Holder"""
    def __init__(self,projectName):
        Statistics.__init__(self,projectName)

    def getKeyBase(self):
        return 'project:'+ self.name        

                                                
class ProjectSummary:
    """ Contains an overview """
    def __init__(self,	\
                    projects=0,successes=0,failures=0,	\
                    prereqs=0,noworks=0,packages=0,	\
                    others=0,statepairs=None):
                        
        # Counters
        self.projects=projects
        self.successes=successes
        self.failures=failures
        self.prereqs=prereqs
        self.noworks=noworks
        self.packages=packages
        self.others=others
        self.statepairs=statepairs
        
        # Percentages
        self.overallPercentage=0
        self.successesPercentage=0
        self.failuresPercentage=0
        self.prereqsPercentage=0
        self.noworksPercentage=0
        self.packagesPercentage=0
        self.othersPercentage=0
        
        #
        if not self.statepairs: self.statepairs=[]
        
        self.calculatePercentages()
        
    def addState(self,state):            
        # Stand up and be counted
        if state.isSuccess():
            self.successes+=1
        elif state.isPrereqFailed():
            self.prereqs+=1
        elif state.isFailed():
            self.failures+=1
        elif state.isUnset():
            self.noworks+=1
        elif state.isComplete():
            # :TODO: Accurate?
            self.packages+=1
        else:
            self.others+=1
                
        # One more project...
        self.projects += 1
                
        # Add state, if not already there
        if not state.isUnset() and not state in self.statepairs: \
            self.statepairs.append(state)
        
        self.calculatePercentages()
        
    def addSummary(self,summary):
                 
        self.projects += summary.projects
        
        self.successes += summary.successes
        self.failures += summary.failures
        self.prereqs += summary.prereqs
        self.noworks += summary.noworks
        self.packages += summary.packages
        self.others += summary.others
        
        # Add state pair, if not already there
        for pair in summary.statepairs:
            if not pair.isUnset() and not pair in self.statepairs: \
                self.statepairs.append(pair)
                
        self.calculatePercentages()
        
    def calculatePercentages(self):
        """ Keep counters correct """
        if self.projects > 0:            
            self.successesPercentage=(float(self.successes)*100)/self.projects
            self.failuresPercentage=(float(self.failures)*100)/self.projects
            self.prereqsPercentage=(float(self.prereqs)*100)/self.projects
            self.noworksPercentage=(float(self.noworks)*100)/self.projects
            self.packagesPercentage=(float(self.packages)*100)/self.projects
            self.othersPercentage=(float(self.others)*100)/self.projects
            
            # This is the overall success of a run...
            self.overallPercentage=(float(self.successes + self.packages)*100)/self.projects
            
    def getOverallPercentage(self):
        """ Return the overall success """
        return self.overallPercentage
