#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/module.py,v 1.35 2004/03/04 17:26:08 ajack Exp $
# $Revision: 1.35 $
# $Date: 2004/03/04 17:26:08 $
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
from gump.model.stats import Statable, Statistics
from gump.model.project import *
from gump.model.object import NamedModelObject, Resultable
from gump.utils import getIndent
from gump.utils.note import transferAnnotations, Annotatable

class ModuleCvs(ModelObject):
    def __init__(self,xml,repository):
        ModelObject.__init__(self,xml)
        
        self.repository=repository
        
        # Extract settings
        self.tag			=	xml.tag
        self.module			=	xml.module
        self.hostPrefix 	=   xml['host-prefix']
        self.dir			=	xml.dir    
        
    def getCvsRoot(self):
        """Construct the CVS root for this set of information"""

        # Form the CVS root starting with the method
        root=':' + str(self.repository.getMethod()) + ':'
        # Add the user (if set)
        if self.repository.hasUser(): root+=str(self.repository.getUser())
        # Forge the hostname
        if self.repository.hasHostname():
            root+='@'
            if self.hostPrefix: root+=self.hostPrefix+'.'      
            root+=str(self.repository.getHostname()) + ':'
            
            # :TODO: Allow users to override default port
            if str(self.repository.getMethod())=='pserver': 
                root+='2401'
        root+=str(self.repository.getPath())
        
        # If a subdirect
        if self.dir: root+='/'+str(self.dir)

        return root
    
    def hasTag(self):
        if self.tag: return 1
        return 0
        
    def getTag(self):
        return str(self.tag)
        
    def hasHostPrefix(self):
        if self.hostPrefix: return 1
        return 0
        
    def getHostPrefix(self):
        return str(self.hostPrefix)
        
    def hasDir(self):
        if self.dir: return 1
        return 0
        
    def getDir(self):
        return str(self.dir)
    
    def hasModule(self):
        if self.module: return 1
        return 0
        
    def getModule(self):
        return str(self.module)
         
class ModuleSvn(ModelObject):
    def __init__(self,xml,repository):
        ModelObject.__init__(self,xml)
        
        # Reference to the shared repository
        self.repository=repository    
            
        # Extract settings
        if xml.dir:
            self.dir	=	str(xml.dir)

    def getRootUrl(self):
        url=self.repository.getUrl()
        if self.hasDir():
            url+=self.getDir()
        return url
        
    def hasDir(self):
        return (hasattr(self,'dir') and self.dir)
        
    def getDir(self):
        return self.dir
         
class ModuleJars(ModelObject):
    def __init__(self,xml,repository):
        ModelObject.__init__(self,xml)
        
        # Reference to the shared repository
        self.repository=repository
        
        # Extract settings
        if xml.url:
            self.url	=	str(xml.url)
        elif self.repository.hasUrl():
            self.url 	=  self.repository.getUrl()
    
    def getRootUrl(self):
        url=self.repository.getUrl()
        if self.hasUrl():
            url+=self.getUrl()
        return url
        
    def hasUrl(self):
        return (hasattr(self,'url') and self.url)
        
    def getUrl(self):
        return self.url
         
def createUnnamedModule(workspace):
    #
    # Create an Unnamed Module (for projects not in modules)
    #
    from gump.model.rawmodel import XMLModule
    unnamedXML=XMLModule({'name':'Anonymous'})
    unnamedModule=Module(unnamedXML,workspace)
    unnamedModule.complete(workspace)
    return unnamedModule
        
class Module(NamedModelObject, Statable, Resultable):
    """Set of Modules (which contain projects)"""
    def __init__(self,xml,workspace):
    	NamedModelObject.__init__(self,xml.getName(),xml,workspace)
            	
    	Statable.__init__(self)
    	Resultable.__init__(self)
    	
    	self.totalDepends=[]
    	self.totalDependees=[]
    	
    	self.workspace=workspace 
    	self.projects={}
    	
    	self.repository=None
    	
        self.packaged		=	0
    	self.updated		=	0
        	
        # Extract settings
        self.tag			=	xml.tag

    # provide default elements when not defined in xml
    def complete(self,workspace):
      
        if self.isComplete(): return
           
        #if self.getName() == 'broken1':
        #    print "------------------------------------------------------------------------"
        #    print "COMPLETE MODULE"
        #    self.xml.dump()
        #    print "------------------------------------------------------------------------"        
        #    print "COMPLETE MODULE"
        #    dump(self.xml)
        #    print "------------------------------------------------------------------------"
        #    from gump.utils.xmlutils import xmlize
        #    print xmlize('module',self.xml)
        #    print "COMPLETED MODULE"
        #    print "------------------------------------------------------------------------"        
        
        packaged=0
                
        # Claim ownership & check for packages
        # ###################################################
        # A module which contains only packaged projects might as
        # well be considered packages, no need to update from CVS
        # since we won't be building.
        packageCount=0
        allPackaged=1
                        
        for xmlproject in self.xml.project:
            if workspace.hasProject(xmlproject.name):
                
                #
                # The project pretty much better be in the
                # workspace, but avoid crashing...
                #
                project=workspace.getProject(xmlproject.name)
                
                if not project.inModule():
                    #
                    # Claim ownership
                    #
                    self.addProject(project)
                else:
                    workspace.addError('Duplicate project [' + xmlproject.name + '] in [' \
                            + project.getModule().getName() + '] and now [' + self.getName() + ']')
                
                #
                # Check for packaged
                #
                if not project.isPackaged():
                    allPackaged=0  
                else:
                    self.addInfo('Packaged Project: ' + project.getName())
                    packageCount+=1                
            else:
                log.error(':TODO: No such project in w/s ['+ `xmlproject.name` +'] on [' \
                      + self.getName() + ']')
                
            # Must be one to be all
            if not packageCount: allPackaged=0
    
            #
            # Give this module a second try,  if some are packaged, and
            # check if the others have no outputs, then call them good.
            #
            if packageCount and not allPackaged:
                allPackaged=1
                for project in self.getProjects():
                    if not project.isPackaged():
                        if not project.hasOutputs():
                            # 
                            # Honorary package (allow folks to only mark the main
                            # project in a module as a package, and those that do
                            # not product significant outputs (e.g. test projects)
                            # will be asssumed to be packages.
                            #                
                            project.setHonoraryPackage(1)            
                            project.changeState(STATE_COMPLETE,REASON_PACKAGE)    
                            packageCount+=1
                        else:    
                            allPackaged=0  
                            if packageCount:
                                self.addWarning('Incomplete \'Packaged\' Module. Project: ' + \
                                        project.getName() + ' is not packaged')  
               
            # If packages module, accept it... 
            if allPackaged:
                packaged=1
                self.setPackaged(1)                
                self.changeState(STATE_COMPLETE,REASON_PACKAGE)  
                self.addInfo("\'Packaged\' Module. (Packaged projects: " + \
                                    str(packageCount) + '.)')                                            

    
        # Determine source directory
        self.srcdir=self.xml.srcdir or self.xml.name        
        self.absSrcDir=os.path.join(workspace.getBaseDirectory(),self.srcdir)
                               
                               
        # :TODO: Consolidate this code, less cut-n-paste but also
        # check the 'type' of the repository is appropriate for the
        # use (eg. type='cvs' if referenced by CVS).
        if not packaged:
            # We have a CVS entry, expand it...
            if self.xml.cvs:
                repoName=self.xml.cvs.repository
                if repoName:
                    if workspace.hasRepository(repoName):
                        # It references this repository...
                        repo=workspace.getRepository(repoName)
                        self.repository=repo
                        repo.addModule(self)
                        self.cvs=ModuleCvs(self.xml.cvs,repo)
                    else:
                        self.changeState(STATE_FAILED,REASON_CONFIG_FAILED)               
                        self.addError('No such repository in w/s ['+ str(repoName) +'] on [' \
                                + self.getName() + ']')
                            
            elif self.xml.svn:                
                repoName=self.xml.svn.repository
                if repoName:
                    if workspace.hasRepository(repoName):
                        # It references this repository...
                        repo=workspace.getRepository(repoName)
                        self.repository=repo
                        repo.addModule(self)
                        self.svn=ModuleSvn(self.xml.svn,repo)
                    else:
                        self.changeState(STATE_FAILED,REASON_CONFIG_FAILED)               
                        self.addError('No such repository in w/s ['+ str(repoName) +'] on [' \
                                + self.getName() + ']')                 
                                                
            elif self.xml.jars:                
                repoName=self.xml.jars.repository
                if repoName:
                    if workspace.hasRepository(repoName):
                        # It references this repository...
                        repo=workspace.getRepository(repoName)	
                        self.repository=repo	
                        repo.addModule(self)
                        self.jars=ModuleJars(self.xml.jars,repo)
                    else:
                        self.changeState(STATE_FAILED,REASON_CONFIG_FAILED)               
                        self.addError('No such repository in w/s ['+ str(repoName) +'] on [' \
                                + self.getName() + ']')                 


        # For prettiness
        self.sortedProjects=createOrderedList(self.getProjects())
                            
        # Copy over any XML errors/warnings
        transferAnnotations(self.xml, self)  
                
        self.setComplete(1)            
        
    def addProject(self,project):
        project.setModule(self)
        self.projects[project.getName()]=project
                     
    def getProject(self,projectname):
        return self.projects[projectname]
        
    def getProjects(self):
        return self.projects.values()
        
    def getSortedProjects(self):
        return self.sortedProjects        
  
    def getChildren(self):
        return self.getProjects()        
        
    def isPackaged(self):
        return self.packaged
                
    def setPackaged(self,packaged):
        self.packaged=packaged
        
    #
    # Get a full list of all the projects that depend
    # upon projects in this module 
    #
    def getFullDependees(self):   
        # Calculated once only...
        if self.totalDependees: return self.totalDependees
                
        for project in self.getProjects():
            if not project in self.totalDependees:
                self.totalDependees.append(project)
                for dependee in project.getFullDependees():
                    dependeeProject=dependee.getOwnerProject()
                    if not dependeeProject in self.totalDependees:
                        self.totalDependees.append(dependeeProject)   
                        
        # Sort for prettiness...                     
        self.totalDependees.sort()
        return self.totalDependees
            
    def getFullDependeeCount(self):         
        return len(self.getFullDependees())   
            
    def getFullDepends(self):   
        if self.totalDepends: return self.totalDepends
                
        for project in self.getProjects():
            if not project in self.totalDepends:
                self.totalDepends.append(project)
                for depend in project.getFullDependencies():
                    dependProject=depend.getProject()
                    if not dependProject in self.totalDepends:
                        self.totalDepends.append(dependProject)                        
        self.totalDepends.sort()
        return self.totalDepends
            
    def getFullDependencyCount(self):         
        return len(self.getFullDepends())   
        
    def getFOGFactor(self):
        fogFactor=0
        fogFactors=0
        for project in self.getProjects():
                projectFOGFactor = project.getFOGFactor()
                fogFactor += projectFOGFactor
                fogFactors += 1
                
        if not fogFactors:
            fogFactors=1 # 0/1 is better than 0/0
            
        return fogFactor/fogFactors
        
    def getLastUpdated(self):
        return self.getStats().getLastUpdated()                
    
    # Get a summary of states for each project
    def getProjectSummary(self,summary=None):  
    
        # Fails 'ocs count into other's summary
        # if hasattr(self,'summary'): return self.summary
        
        if not summary: 
            summary=ProjectSummary()
        
        #
        # Subordinates are projects, so get their summary
        #
        for project in self.getProjects():
            summary.addState(project.getStatePair())
        
        # Fails, see above.
        # Store for later...
        # self.summary = summary
        
        return summary
           
    def determineAffected(self):
        affected=0
        
        # Get all dependenees (optional/otherwise)
        dependees=self.getFullDependees()
        
        # Look through all dependees
        for project in dependees:
            cause=project.getCause()
            #
            # Something caused this some grief
            #
            if cause:
                #
                # The something was this module or one of it's projects
                #
                if cause == self or cause in self.getProjects():
                    affected += 1            
        
        return affected
                   
    def getProjectStatistics(self,db=None):
        if not hasattr(self,'stats'):
            # Load the DB, if not loaded
            if not db:
                db=StatisticsDB()
            # Extract from project statistics DB
            stats=db.getProjectStats(pctxt.name)
            self.stats=stats
            
        return self.stats                
    
    def dump(self, indent=0, output=sys.stdout):
        output.write(getIndent(indent)+'Module : ' + self.name + '\n')
        NamedModelObject.dump(self, indent+1, output)
        
    def hasTag(self):
        if self.tag: return 1
        return 0
        
    def getTag(self):
        return str(self.tag)
        
    def getSourceDirectory(self):
        return self.absSrcDir
        
    def getSourceDirName(self):
        return self.srcdir
        
    def hasURL(self):
        return self.getURL()
        
    def getURL(self):
        if self.xml.url and self.xml.url.href: return str(self.xml.url.href)
        
    def hasDescription(self):
        return str(self.xml.description)   
        
    def getDescription(self):
        return str(self.xml.description)        
        
    def getWorkspace(self):
        return self.workspace
    
    def getMetadataLocation(self):
        # I think the bogus 'anonymous' module, needs this safety check
        if self.xml: return str(self.xml.href)
        
        
    def hasCvs(self):
        if hasattr(self,'cvs') and self.cvs: return 1
        return 0
        
    def hasSvn(self):
        if hasattr(self,'svn') and self.svn: return 1
        return 0
        
    def hasJars(self):
        if hasattr(self,'jars') and self.jars: return 1
        return 0
        
    # Where the contents (at the repository) updated?
    def isUpdated(self):
        return self.updated
        
    def setUpdated(self,updated):
        self.updated=updated
    
    def hasRepository(self):
        return self.repository
        
    def getRepository(self):
        return self.repository
        
    def getUpdateCommand(self,exists=0):
        if self.hasCvs():
            return self.getCvsUpdateCommand(exists)
        elif self.hasSvn():
            return self.getSvnUpdateCommand(exists)
        elif self.hasJars():
            return self.getJarsUpdateCommand(exists)        
           
    def getCvsUpdateCommand(self,exists=0):
        
        log.debug("CVS Update Module " + self.getName() + \
                       ", Repository Name: " + str(self.repository.getName()))
                                        
        root=self.cvs.getCvsRoot()
      
        log.debug("CVS Root " + root + " on Repository: " + self.repository.getName())
     
        #
        # Prepare CVS checkout/update command...
        # 
        cmd=Cmd('cvs','update_'+self.getName(),self.getWorkspace().cvsdir)
          
        #
        # Be 'quiet' (but not silent) unless requested otherwise.
        #
        if 	not self.isDebug() 	\
            and not self.isVerbose() \
            and not self.cvs.isDebug()	\
            and not self.cvs.isVerbose():    
            cmd.addParameter('-q')
          
        #
        # Allow trace for debug
        #
        if self.isDebug():
            cmd.addParameter('-t')
          
        #
        # Request compression
        #
        cmd.addParameter('-z3')
          
        #
        # Set the CVS root
        #
        cmd.addParameter('-d', root)
    
        #
        # Determine if a tag is set, on <cvs or on <module
        #
        tag=None
        if self.cvs.hasTag():
            tag=self.cvs.getTag()
        elif self.hasTag():
            tag=self.getTag()
            
        if exists:

            # do a cvs update
            cmd.addParameter('update')
            cmd.addParameter('-P')
            cmd.addParameter('-d')
            if tag:
                cmd.addParameter('-r',tag,' ')
            else:
                cmd.addParameter('-A')
            cmd.addParameter(self.getName())

        else:

            # do a cvs checkout
            cmd.addParameter('checkout')
            cmd.addParameter('-P')
            if tag:
                cmd.addParameter('-r',tag,' ')

            if 	not self.cvs.hasModule() or \
                not self.cvs.getModule() == self.getName(): 
                    cmd.addParameter('-d',self.getName(),' ')
                    
            if self.cvs.hasModule():
                cmd.addParameter(self.cvs.getModule())
            else:
                cmd.addParameter(self.getName())            
        
        return (self.repository, root, cmd)
     
     
    def getSvnUpdateCommand(self,exists=0):
        
        log.debug("SubVersion Update Module " + self.getName() + \
                       ", Repository Name: " + str(self.repository.getName()))
                                        
        url=self.svn.getRootUrl()
      
        log.debug("SVN URL: [" + url + "] on Repository: " + self.repository.getName())
     
        #
        # Prepare SVN checkout/update command...
        # 
        cmd=Cmd('svn','update_'+self.getName(),self.getWorkspace().cvsdir)
       
        #
        # Be 'quiet' (but not silent) unless requested otherwise.
        #
        if 	not self.isDebug() 	\
            and not self.isVerbose() \
            and not self.svn.isDebug()	\
            and not self.svn.isVerbose():    
            cmd.addParameter('--quiet')
                  
        #
        # Allow trace for debug
        #
        #
        # SVN complains about -v|--verbose, don't ask me why
        #
        # if self.isDebug() or  self.svn.isDebug():
        #    cmd.addParameter('--verbose')
            
        if exists:

            # do a cvs update
            cmd.addParameter('update')

        else:

            # do a cvs checkout
            cmd.addParameter('checkout')
            cmd.addParameter(url)
       
        #
        # Request non-interactive
        #
        cmd.addParameter('--non-interactive')

        #
        # If module name != SVN directory, tell SVN to put it into
        # a directory named after our module
        #
        if self.svn.hasDir():
            if not self.svn.getDir() == self.getName():
                cmd.addParameter(self.getName())
        

        return (self.repository, url, cmd)
         
     
    def getJarsUpdateCommand(self,exists=0):
        
        log.debug("Jars Update Module " + self.getName() + \
                       ", Repository Name: " + str(self.repository.getName()))

        url=self.jars.getRootUrl()
      
        log.debug("Jars URL: [" + url + "] on Repository: " + self.repository.getName())
     
        #
        # Prepare Jars checkout/update command...
        # 
        cmd=Cmd('ruper',	\
                'update_'+self.getName(),	\
                self.getWorkspace().cvsdir)
    
        cmd.addParameter(url)
          
        #
        # Be 'quiet' (but not silent) unless requested otherwise.
        #
        if 	not self.isDebug() 	\
            and not self.isVerbose() \
            and not self.jars.isDebug()	\
            and not self.jars.isVerbose():    
            cmd.addParameter('-q')

        return (self.repository, url, cmd)
     
     
class ModuleStatistics(Statistics):
    """Statistics Holder"""
    def __init__(self,moduleName):
        Statistics.__init__(self,moduleName)    
        self.lastUpdated=-1        
        
    def getLastUpdated(self):
        return (self.lastUpdated)
        
    def getKeyBase(self):
        return 'module:'+ self.name
        
    def lastUpdatedKey(self):
        return self.getKeyBase() + '-last-updated'

    def update(self,module):      
        Statistics.update(self,module)

        #
        # Track code updates/changes
        # 
        if module.isUpdated():
            self.lastUpdated=default.time