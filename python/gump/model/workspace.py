#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/workspace.py,v 1.4 2003/11/18 21:49:12 ajack Exp $
# $Revision: 1.4 $
# $Date: 2003/11/18 21:49:12 $
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
from string import lower, capitalize

from gump.model.state import *
from gump.model.work import *
from gump.model.repository import Repository
from gump.model.module import Module, createUnnamedModule
from gump.model.project import Project, ProjectSummary
from gump.model.object import ModelObject
from gump.model.property import PropertyContainer
from gump.utils.launcher import *
from gump.utils.tools import *

class Workspace(ModelObject,PropertyContainer):
    """Gump Workspace"""
    def __init__(self,xmlworkspace):
    	ModelObject.__init__(self,xmlworkspace)    	
    	PropertyContainer.__init__(self)
    	
    	#
    	# Named repositories (e.g. CVS)
    	# Named modules
    	# named projects
    	#
    	self.repositories={}
        self.modules={}
        self.projects={}
        
        #
    	PropertyContainer.importProperties(self,self.xml)    	
    	                 	
        #
    	# Set to true if not found, see checkEnvironment
    	#
    	self.noRSync=0
    	self.noForrest=0    	
    	
    	#
    	# JAVACMD can override this, see checkEnvironment
    	#
        self.javaCommand = 'java'
        
        #    
        self.startdatetime=time.strftime(setting.datetimeformat, \
                                time.localtime())
        self.timezone=str(time.tzname)    
    
    def hasRepository(self,rname):
        return self.repositories.has_key(rname)
        
    def getRepository(self,rname):
        return self.repositories[rname]
        
    def getRepositories(self):
        return self.repositories.values()
        
    def hasModule(self,mname):
        return self.modules.has_key(mname)
        
    def getModule(self,mname):
        return self.modules.get(mname,None)
        
    def hasProject(self,pname):
        return self.projects.has_key(pname)
        
    def getProject(self,pname):
        return self.projects[pname]
        
    def complete(self, xmlprofiles, xmlrepositories, xmlmodules, xmlprojects):        
        if self.isComplete(): return
        
        #
        # provide default elements when not defined in xml
        # expand those in XML
        #
        if not self.xml['banner-image']:
            self.bannerImage=default.bannerimage
        else:
            self.bannerImage=self.xml['banner-image']
            
        if not self.xml['banner-link']: 
            self.bannerLink="http://jakarta.apache.org"
        else:
            self.bannerLink=self.xml['banner-link']
    
        # Construct tmp on demand
        if not self.xml.tmpdir: 
            self.tmpdir=os.path.join(self.getBaseDirectory(),"tmp")
        else:
            self.tmpdir=self.xml.tmpdir
            
        if not os.path.exists(self.tmpdir): 
            os.mkdir(self.tmpdir)    
    
        # Construct logdir on demand
        if not self.xml.logdir: 
            self.logdir=os.path.join(self.getBaseDirectory(),"log")
        else:
            self.logdir=self.xml.logdir
        
        if not os.path.exists(self.logdir): os.mkdir(self.logdir)
    
        # Construct repository dir on demand
        if not self.xml.jardir: 
            self.jardir=os.path.join(self.getBaseDirectory(),"repo")
        else:
            self.jardir=self.xml.jardir
                
        if not os.path.exists(self.jardir): os.mkdir(self.jardir)
    
        # Construct CVS directory on demand
        if not self.xml.cvsdir: 
            self.cvsdir=os.path.join(self.getBaseDirectory(),"cvs")
        else:
            self.cvsdir=self.xml.cvsdir

        if not os.path.exists(self.cvsdir): os.mkdir(self.cvsdir)
    
        # Package Dir Ought Exist
        if not self.xml.pkgdir: 
            self.pkgdir=self.getBaseDirectory()
        else:
            self.pkgdir=self.xml.pkgdir
        
        if self.xml.deliver:
            if not self.xml.scratchdir: 
                self.scratchdir=os.path.join(self.getBaseDirectory(),"scratch")
            else:
                self.scratchdir=self.xml.scratchdir

        # Allow per workspace overrides
    
        if not self.xml.logurl: 
            self.logurl = default.logurl
        else:
            self.logurl = self.xml.logurl
            
        # Sending e-mail address
        if not self.xml.email: 
            self.email = default.email
        else:
            self.email = self.xml.email
            
        # Sending server
        if not self.xml.mailinglist: 
            self.mailinglist = default.mailinglist    
        else:
            self.mailinglist = self.xml.mailinglist
            
        # Mail server
        if not self.xml.mailserver: 
            self.mailserver = default.mailserver
        else:
            self.mailserver = self.xml.mailserver
            
        # Get mailport as an int
        if not self.xml.mailport: 
            self.mailport = default.mailport
        else:
            self.mailport = int(self.xml.mailport)
            
        # Mail subject prefix
        if not self.xml.prefix: 
            self.prefix = default.prefix
        else:
            self.prefix = self.xml.prefix
            
        # Mail .sig
        if not self.xml.signature: 
            self.signature = default.signature
        else:
            self.signature=self.xml.signature
      
      
        #
        # Import all repositories
        #  
        for xmlrepository in xmlrepositories.values(): 
            repository=Repository(xmlrepository,self)
            repoName=repository.getName()
            if repoName in self.repositories:
                # Duplicate, uh oh...
                self.addError("Duplicate repository name [" + repoName + "]")
            else:        
                repository.complete(self)
                self.repositories[repoName] = repository

        #
        # Import all modules
        #  
        for xmlmodule in xmlmodules.values(): 
            module=Module(xmlmodule,self)
            moduleName=module.getName()
            if moduleName in self.modules:
                # Duplicate, uh oh...
                self.addError("Duplicate Module name [" + moduleName + "]")
            else:        
                self.modules[moduleName] = module
        #
        # Import all projects
        #  
        for xmlproject in xmlprojects.values(): 
            project=Project(xmlproject,self)
            projectName=project.getName()
            if projectName in self.projects:
                # Duplicate, uh oh...
                self.addError("Duplicate Project name [" + projectName + "]")
            else:        
                self.projects[projectName] = project

        # Complete the modules
        for module in self.getModules():
            module.complete(self)
            
        #
        # Check repositories, now modules have been imported,
        # so we can report those unused ones.
        #
        for repository in self.getRepositories(): 
            repository.check(self)            
        
        # Complete the projects   
        haveUnnamedModule=0
        for project in self.getProjects():
            # Projects needs a module (even if pseudo)
            if not project.inModule():
                if not haveUnnamedModule:
                    # A container for projects outside of
                    # modules
                    unnamedModule=createUnnamedModule(self)
                    self.addModule(unnamedModule)
                    haveUnnamedModule=1
        
                unnamedModule.addProject(project)
            
            # Complete the project
            project.complete(self)        
                                                             
        # Complete the properies
        self.completeProperties()
                                        
        self.setComplete(1)
            
    def addModule(self,module):
        self.modules[module.getName()]=module                         
        
    # Get a summary of states for each project
    def getProjectSummary(self,summary=None): 
        if hasattr(self,'summary'): return self.summary
                
        if not summary: 
            summary=ProjectSummary()
        
        # Subordinates are modules, get their simmary
        # information into this summary
        for module in self.getModules():
            module.getProjectSummary(summary)
            
        # Store for later...
        self.summary = summary
        
        return summary
        
    def dump(self, indent=0, output=sys.stdout):
        output.write('Workspace : \n')
        
        for repo in self.repositories.values():
            repo.dump(indent+1,output)
        
        for module in self.getModules():
            module.dump(indent+1,output)
        
        for project in self.getProjects():
            project.dump(indent+1,output)

    def isNag(self):
        return self.xml.nag
        
    def getVersion(self):
        return self.xml.version

    def getBaseDirectory(self):
        return self.xml.basedir
            
    def getLogDirectory(self):
        return self.xml.logdir or \
            os.path.abspath(os.path.join(self.getBaseDirectory(),'log'))
            
    def getLogUrl(self):
        return self.logurl
            
    def getProjects(self):
        return self.projects.values()        
    
    # :TODO: Inefficient, ought store sorted
    def getProjectIterator(self):
        return AlphabeticDictionaryIterator(self.projects)
        
    def getChildren(self):
        return self.getModules() 
    
    def getModules(self):
        return self.modules.values()    
        
    # :TODO: Inefficient, ought store sorted
    def getModuleIterator(self):
        return AlphabeticDictionaryIterator(self.modules)    
        
    def getCVSDirectory(self):
        return self.cvsdir

    def checkEnvironment(self,exitOnError=0):
        """ Check Things That are Required """
    
        #
        # :TODO: Complete this, it ought be an important early warning...
        #
    
    
        #:TODO: Take more from runAnt.py on:
        # - ANT_OPTS?
        # - How to ensure lib/tools.jar is in classpath
        # - Others?
    
        #
        #	Directories...
    
    
        #
        # JAVACMD can be set (perhaps for JRE verse JDK)
        #
        if os.environ.has_key('JAVACMD'):        
            self.javaCommand  = os.environ['JAVACMD']
            self.addInfo('JAVACMD environmental variable setting java command to ' \
                + self.javaCommand )
    
    
        #	Envs:
        #	JAVA_HOME for bootstrap ant?
        #	CLASSPATH
        #	FORREST_HOME?
    
        if not self.checkEnvVariable('JAVA_HOME',0):    
            self.noJavaHome=1    
            self.addWarning('JAVA_HOME environmental variable not found. Might not be needed.')
                
        if not self.checkEnvVariable('CLASSPATH',0):    
            self.noClasspath=1    
            self.addWarning('CLASSPATH environmental variable not found. Might not be needed.')
                
        if not self.checkEnvVariable('FORREST_HOME',0): 
            self.noForrest=1
            self.addWarning('FORREST_HOME environmental variable not found, no xdoc output')
            
        #
        # Check for executables:
        #
        #	java
        #	javac (for bootstrap ant & beyond)
        #	cvs
        #
        #	These ought set a switch..
        #
        #	rsync or cp
        #	forrest (for documentation)
        #
        self.checkExecutable('env','',0)
        self.checkExecutable(self.javaCommand,'-version',exitOnError,1)
        self.checkExecutable('javac','-help',exitOnError)
        self.checkExecutable('java com.sun.tools.javac.Main','-help',exitOnError,0,'check_java_compiler')    
        self.checkExecutable('cvs','--version',exitOnError)
        if not self.noForrest and not self.checkExecutable('forrest','-projecthelp',0): 
            self.noForrest=1
            self.addWarning('"forrest" command not found, no xdoc output')
        
        if not self.checkExecutable('rsync','-help',0): 
            self.noRSync=1
            self.addWarning('"rsync" command not found, so attempting recursive copy "cp -R"')
        
        if not self.checkExecutable('pgrep','-help',0): 
            self.noPGrep=1
            self.addWarning('"pgrep" command not found, no process clean-ups can occur')        
    
        self.changeState(STATE_SUCCESS)
    
    def checkExecutable(self,command,options,mandatory,logOutput=0,name=None):
        ok=0
        try:
            if not name: name='check_'+command
            cmd=getCmdFromString(command+" "+options,name)
            result=execute(cmd)
            ok=result.state==CMD_STATE_SUCCESS 
            if not ok:
                log.error('Failed to detect [' + command + ']')   
        except Exception, details:
            ok=0
            log.error('Failed to detect [' + command + '] : ' + str(details))
            result=None
       
        # Update 
        self.performedWork(CommandWorkItem(WORK_TYPE_CHECK,cmd,result))
        
        if not ok and mandatory:
            banner()
            print
            print " Unable to detect/test mandatory [" + command+ "] in path (see next)."
            for p in sys.path:
                print "  " + str(os.path.normpath(p))
            sys.exit(MISSING_UTILITY)
        
        # Store the output
        if logOutput and result.output:
            out=tailFileToString(result.output,10)
            self.addInfo(name + ' produced: \n' + out)
            
        return ok
    
    def checkEnvVariable(self,env,mandatory=1):
        ok=0
        try:
            ok=os.environ.has_key(env)
            if not ok:
                log.error('Failed to find environment variable [' + env + ']')
        
        except Exception, details:
            ok=0
            log.error('Failed to find environment variable [' + env + '] : ' + str(details))
    
        if not ok and mandatory:
            banner()
            print
            print " Unable to find mandatory [" + env + "] in environment (see next)."
            for e in os.environ.keys():
                try:
                    v=os.environ[e]
                    print "  " + e + " = " + v
                except:
                    print "  " + e 
            sys.exit(BAD_ENVIRONMENT)
    
        return ok
        
    def getJavaCommand(self):
        return self.javaCommand