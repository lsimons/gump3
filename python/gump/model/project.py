#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/project.py,v 1.9 2003/11/20 00:57:39 ajack Exp $
# $Revision: 1.9 $
# $Date: 2003/11/20 00:57:39 $
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
from gump.model.object import ModelObject, NamedModelObject, Jar
from gump.model.property import Property
from gump.model.ant import Ant
from gump.model.rawmodel import Single
from gump.utils import getIndent
from gump.model.depend import *

#
# An annotated path has a path entry, plus the context
# of the contributor (i.e. project of Gump.)
#
class AnnotatedPath:
    """Contains a Path plus optional 'contributor' """
    def __init__(self,path,contributor=None,instigator=None,note=None):
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
        return self.contributor
        
    def getContributor(self):
        return self.contributor
        
    def hasInstigator(self):
        return self.instigator
        
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
            

class Project(NamedModelObject):
    """A single project"""
    def __init__(self,xml,workspace):
    	NamedModelObject.__init__(self,xml.getName(),xml,workspace)
    	
    	# Navigation
        self.module=None # Module has to claim ownership
        self.workspace=workspace
    	
    	#############################################################
    	# Dependency Trees
    	#
    	
    	# Those which we rely upon...
    	self.depends=[]
    	
    	# Those which rely upon us...
    	self.dependees=[]
    	
    	#
    	# Fully expanded
    	#
    	self.totalDepends=[]
    	self.totalDependees=[]    
        
    	#############################################################
    	#
    	# Sub-Components
    	#
    	self.ant=None
    	self.script=None

    	
    	#############################################################
    	# Outputs
    	#
        self.jars={}
        
    def getAnt(self):
        return self.ant
        
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
        
    def addJar(self,jar):
        self.jars[jar.getName()]=jar
        
    def getJarCount(self):
        return len(self.jars)
        
    def hasJarWithId(self,id):
        return self.jars.has_key(id)
        
    def hasJars(self):
        return self.jars
        
    def getJars(self):
        return self.jars.values()
    
    def getDependencies(self):
        return self.depends
        
    def getDependencyCount(self):   
        """ Count the direct depenencies """
        return len(self.depends)
        
    def getDependees(self):
        return self.dependees
        
    def getDependeeCount(self):   
        """ Count the direct dependees """
        return len(self.dependees)
        
    def getFullDependencies(self):   
        #
        # Build a set of dependencies (once only)
        #
        if self.totalDepends: 
            return self.totalDepends
        
        for dependency in self.depends:
            if not dependeny in self.totalDepends: 
                self.totalDepends.append(dependency)
                for subdepend in dependency.getProject().getFullDependencies():
                    if not subdepend in self.totalDepends:
                        self.totalDepends.append(subdepend)
        self.totalDepends.sort()
        
        # Return stored
        return self.totalDepends
                    
    def getFullDependenciesCount(self):         
        return len(self.getFullDependencies())                      
    
    def getFullDependees(self):   
        if self.totalDependees: return self.totalDependees
        
        for dependee in self.dependees:
            if not dependee in self.totalDependees: 
                # We have a new dependee
                self.totalDependees.append(dependee)
                for subdependee in dependee.getProject().getFullDependees():
                    if not subdependee in self.totalDependees:
                        self.totalDependees.append(subdependee)
        self.totalDependees.sort()
        
        # Store once
        return self.totalDependees            
                        
    def getFullDependeesCount(self):         
        return len(self.getFullDependees())             
        
    # Stats are loaded separately and cached on here,
    # hence they may exist on an object at all times.
    def hasStats(self):
        return hasattr(self,'stats')
        
    def setStats(self,stats):
        self.stats=stats
        
    def getStats(self):
        if not self.hasStats():
            raise RuntimeError, "Statistics not calculated/updated yet: " \
                    + self.getName()
        return self.stats
        
    def getFOGFactor(self):
        return self.getStats().getFOGFactor()
        
    def getLastModified(self):
        return self.getStats().getLastModified()
        
    def propagateErrorStateChange(self,state,reason,cause,message):
        
        #
        # Mark depend*ee*s as failed for this cause...
        # Warn option*ee*s
        #
        for dependee in self.getDependees():  
    
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
        return type(self.xml.package) in types.StringTypes
    
    # provide elements when not defined in xml
    def complete(self,workspace):
        if self.isComplete(): return

        if not self.inModule():
            self.addWarning("Not in a module")
            return

        # Import any <ant part
        if self.xml.ant:
            self.ant = Ant(self.xml.ant,self)
        
        # :TODO: Scripts
        
        # Compute home directory
        if self.isPackaged():
            # Installed below package directory
            self.home=os.path.abspath(os.path.join(workspace.xml.pkgdir,self.xml.package))
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
                log.error('Unable to complete project.home for [not nested/parent]: ' + self.name)
                self.home=None        
        elif not self.xml.home:
            if self.module:
                module=self.getModule()    
                self.home=os.path.abspath(module.getSourceDirectory())
            else:
                self.home=os.path.abspath(os.path.join(workspace.getBaseDirectory(),self.name))
        else:
            log.error('Unable to complete project.home for: ' + self.name)
            self.home=None

        #
        # Resolve jars (outputs)
        #
        for j in self.xml.jar:
            if self.home and j.getName():
                jar=Jar(j,self)
                jar.setPath(os.path.abspath(os.path.join(self.home,j.name)))
                self.addJar(jar)
            else:
                #:TODO: Warn .. no name
                pass

        # Expand <ant <depends/<properties...
        if self.ant: self.ant.expand(self,workspace)

        # Build Dependencies Map [including depends from <ant/<property/<depend
        (badDepends, badOptions) = self.buildDependenciesMap(workspace)
        
        # Complete dependencies so properties can reference the,
        for dependency in self.getDependencies():
            dependency.getProject().complete(workspace)
        
        # complete properties
        if self.ant: self.ant.complete(self,workspace)
    
        #
        # TODO -- move these back?
        #
        if badDepends or badOptions: 
            for xmldepend in badDepends:
                self.changeState(STATE_FAILED,REASON_CONFIG_FAILED)
                self.addError("Bad Dependency. Project: " + xmldepend.project + " unknown to *this* workspace")
                #log.error("Unknown Dependency [" + xmldepend.project + "] on [" + self.getName()  + "]")                    

            for xmloption in badOptions:                
                self.addWarning("Bad *Optional* Dependency. Project: " + xmloption.project + " unknown to *this* workspace")
                #log.warn("Unknown *Optional* Dependency [" + xmloption.project + "] on [" + self.getName() + "]")    
        
        self.setComplete(1)

    def buildDependenciesMap(self,workspace):        
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
        
        #
        # Provide backwards links  [Note: ant might have added some
        # dependencies, so this is done here * not just with the direct
        # xml depend/option elements]
        #
        for dependency in self.getDependencies():
            dependProject=dependency.getProject()
            # Add us as a dependee on them
            dependProject.addDependee(dependency)  
                        
        return (badDepends, badOptions)
                                
    def addDependency(self,dependency):
        #
        # TODO check this against any matching dependency
        # not equal?
        #
        if not dependency in self.depends:
            if not dependency.getProject()==self:
                self.depends.append(dependency)
            #else:
            #    print 'Not Adding : ' + dependency

    def addDependee(self,dependency):
        #
        # TODO check this against any matching dependency
        # not equal?
        #
        if not dependency in self.dependees:
            if not dependency.getOwnerProject()==self:
                self.dependees.append(dependency)
            #else:
            #    print 'Not Adding : ' + dependency

    # 
    def hasFullDependencyOnNamedProject(self,name):
        for dependency in self.depends:
            if dependency.getProject().getName()==name: return 1
# :TODO:        
#           and not dependency.noclasspath: return 1
#:TODO: noclasspath????
              
    # determine if this project is a prereq of any project on the todo list
    def hasDirectDependencyOn(self,project):
        for dependency in self.depends:
            if dependency.getProject()==project: return 1
    
    def hasDirectDependee(self,project):
        for dependee in self.dependees:
            if dependee.getOwnerProject()==project: return 1
            
    def hasDependee(self,project):
        for dependee in self.getFullDependees():
            if dependee.getOwnerProject()==project: return 1
            
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
        if self.xml.ant or self.xml.script: hasBuild=1    
        return hasBuild

    def getBuildCommand(self):

        # get the ant element (if it exests)
        ant=self.xml.ant

        # get the script element (if it exists)
        script=self.xml.script

        if not (script or ant):
          #  log.debug('Not building ' + project.name + ' (no <ant/> or <script/> specified)')
          return None

        if script and script.name:
            return self.getScriptCommand()
        else:
            return self.getAntCommand()
        
    #
    # Build an ANT command for this project
    #        
    def getAntCommand(self):
        ant=self.xml.ant
    
        # The ant target (or none == ant default target)
        target= ant.target or ''
    
        # The ant build file (or none == build.xml)
        buildfile = ant.buildfile or ''
    
        # Optional 'verbose' or 'debug'
        verbose=ant.verbose
        debug=ant.debug
    
        #
        # Where to run this:
        #
        #	The module src directory (if exists) or Gump base
        #	plus:
        #	The specifier for ANT, or nothing.
        #
        basedir = os.path.normpath(os.path.join(self.getModule().getSourceDirectory() or dir.base,	\
                                                    ant.basedir or ''))
    
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
        if debug: cmd.addParameter('-debug')  
        if verbose: cmd.addParameter('-verbose')  
        
        #
        #	This sets the *defaults*, a workspace could override them.
        #
        cmd.addPrefixedParameter('-D','build.sysclasspath','only','=')
    
        # These are module level plus project level
        cmd.addNamedParameters(properties)
    
        # Pass the buildfile
        if buildfile: cmd.addParameter('-f',buildfile)
    
        # End with the target...
        if target: cmd.addParameter(target)
    
        return cmd


    def getJVMArgs(self):
        """Get JVM arguments for a project"""
        args=Parameters()
        for jvmarg in self.getAnt().xml.jvmarg:
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

    def getScriptCommand(self):
        """ Return the command object for a <script entry """
        script=self.xml.script 
           
        basedir=os.path.normpath(os.path.join(self.getModule().getSourceDirectory() or dir.base,\
                        script.basedir or ''))

        # Add .sh  or .bat as appropriate to platform
        scriptfullname=script.name
        if not os.name == 'dos' and not os.name == 'nt':
            scriptfullname += '.sh'
        else:
            scriptfullname += '.bat'
      
        # Optional 'verbose' or 'debug'
        verbose=script.verbose
        debug=script.debug
       
        scriptfile=os.path.normpath(os.path.join(basedir, scriptfullname))
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
        # Allow ant-level debugging...
        #
        if self.getWorkspace().isDebug() or debug:
            cmd.addParameter('-debug')  
        if self.getWorkspace().isVerbose() or verbose:
            cmd.addParameter('-verbose')  
        
        return cmd
    
    def getDeleteCommand(self,delete,index=0):
        """ Return the delete command for a <delete entry """
        basedir=os.path.abspath(self.getModule().getSourceDirectory() or dir.base)
      
        cmd=Cmd('echo rm','delete_'+	\
                    self.getModule().getName()+'_'	\
                    +self.getName()+'_'+str(index+1),\
            basedir)

        #
        # Delete a directory and/or a file
        #
        # :TODO: Before turning this on, we need to ensure that the command
        # will not run wild. We need to ensure that there is no ";" and we
        # need to ensure the directory/file is under the workspace.
        #
        if delete.dir:
            cmd.addParameter('-rf')  
            cmd.addParameter(os.path.abspath(os.path.join(basedir,delete.dir)))
        elif delete.file:
            cmd.addParameter('-f')  
            cmd.addParameter(os.path.abspath(os.path.join(basedir,delete.file)))
        else:
            log.info('   <delete without \'file\' or \'dir\' attributes.')
            return None
        
        return cmd
    
    def getMkDirCommand(self,mkdir,index=0):
        """ Return the mkdir comment for a <mkdir entry """
        basedir=os.path.abspath(self.getModule().getSourceDirectory() or dir.base)
      
        cmd=Cmd('mkdir','mkdir_'+self.getModule().getName()+'_'	\
                            +self.getName()+'_'	\
                            +str(index+1),\
            basedir)

        #
        # Make a directory
        #
        if mkdir.dir:
            cmd.addParameter(os.path.abspath(os.path.join(basedir,mkdir.dir)))
        else:
            log.info('   <mkdir without \'dir\' attribute.')
            return None
        
        return cmd
                
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        output.write(getIndent(indent)+'Project: ' + self.getName() + '\n')
        
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
            outputs.append(AnnotatedPath(jar,self,None,"Project output"))                    
        return outputs
                 
    #
    # Does this project generate outputs (currently JARs)
    #                  
    def hasOutputs(self):
        return self.hasJars()
    
    #
    # Return a (classpath, bootclaspath) tuple for this project
    #
    def getClasspaths(self):
        #
        # Calculate classpath and bootclasspath
        #
        (classpath, bootclasspath) = self.getClasspathLists()
        
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
        """Get a TOTAL classpath for a project (including it's dependencies)"""

        #
        # Do this once only... storing it on the context. Not as nice as 
        # doing it OO (each project context stores it's own, but a step..)
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
                classpath.addPathPart(AnnotatedPath(path,self,None,'Work Entity'))
              
        # Append dependent projects (including optional)
        visited=[]
  
        # Does it have any depends? Process all of them...
        for dependency in self.getDependencies():
            (subcp, subbcp) = self.getDependOutputList(dependency,visited,0,debug)
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
        """Get a classpath of outputs for a project (including it's dependencies)"""            
   
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
            ids=dependency.ids.split(' ')
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
                path=AnnotatedPath(jar.path,self,dependency.getOwnerProject(),dependStr) 
          
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
        for subdependency in project.getDependencies():        
            #	If the dependency is set to 'all' (or 'hard') we inherit all dependencies
            # If the dependency is set to 'runtime' we inherit all runtime dependencies
            # If the dependent project inherited stuff, we inherit that...
            if    	(inherit==INHERIT_ALL or inherit==INHERIT_HARD) \
                    or (inherit==INHERIT_RUNTIME and subdependency.isRuntime()) \
                    or (subdependency.inherit):      
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
                                                
class ProjectSummary:
    """ Contains an overview """
    def __init__(self,projects=0,successes=0,failures=0,prereqs=0,noworks=0,packages=0,others=0,statepairs=None):
        self.projects=projects
        self.successes=successes
        self.failures=failures
        self.prereqs=prereqs
        self.noworks=noworks
        self.packages=packages
        self.others=others
        self.statepairs=statepairs
        
        if not self.statepairs: self.statepairs=[]
        
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
                
