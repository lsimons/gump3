#!/usr/bin/env python

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
    This module contains information on
"""

from time import localtime, strftime, tzname

from gump.model.state import *
from gump.model.stats import Statable, Statistics
from gump.model.project import *
from gump.model.object import NamedModelObject
from gump.model.misc import Resultable, Positioned, AddressPair
from gump.utils import getIndent
from gump.utils.note import transferAnnotations, Annotatable
from gump.utils.domutils import *

class ModuleCvs(ModelObject):
    def __init__(self,dom,repository):
        ModelObject.__init__(self,dom)
        
        self.repository=repository
        
        # Extract settings
        self.tag			=	self.getDomAttributeValue('tag')
        self.module			=	self.getDomAttributeValue('module')
        self.hostPrefix 	=   self.getDomAttributeValue('host-prefix')
        self.dir			=	self.getDomAttributeValue('dir','')
        
    def getCvsRoot(self):
        """Construct the CVS root for this set of information"""

        # Form the CVS root starting with the method
        root=':' + str(self.repository.getMethod()) + ':'
        # Add the user (if set)
        if self.repository.hasUser(): root+=str(self.repository.getUser())
        # Craft the hostname
        if self.repository.hasHostname():
            root+='@'
            if self.hostPrefix: root+=self.hostPrefix+'.'      
            root+=str(self.repository.getHostname()) + ':'
            
            # :TODO: Allow users to override default port
            if str(self.repository.getMethod())=='pserver': 
                root+='2401'
        root+=str(self.repository.getPath())
        
        # If a subdirectory
        if self.dir: root+='/'+str(self.dir)

        return root
    
    def hasTag(self):
        if self.tag: return True
        return False
        
    def getTag(self):
        return str(self.tag)
        
    def hasHostPrefix(self):
        if self.hostPrefix: return True
        return False
        
    def getHostPrefix(self):
        return str(self.hostPrefix)
        
    def hasDir(self):
        if self.dir: return True
        return False
        
    def getDir(self):
        return str(self.dir)
    
    def hasModule(self):
        if self.module: return True
        return False
        
    def getModule(self):
        return str(self.module)
         
    def getViewUrl(self):
        url=None
        if self.repository.hasCvsWeb():
            if self.dir:
                 url=self.repostory.getCvsWeb()+'/'+str(self.dir)+'/'
            else:
                 url=self.repostory.getCvsWeb()+'/'+self.module.getName()
        return url
        
class ModuleSvn(ModelObject):
    def __init__(self,dom,repository):
        ModelObject.__init__(self,dom)
        
        # Reference to the shared repository
        self.repository=repository    
            
        # Extract settings
        self.dir	=	self.getDomAttributeValue('dir')

    def getRootUrl(self):
        url=self.repository.getUrl()
        if self.hasDir():
            url+=self.getDir()
        return url
        
    def hasDir(self):
        if self.dir: return True
        return False
        
    def getDir(self):
        return self.dir
        
    def getViewUrl(self):
        return self.getRootUrl()
         
class ModuleArtifacts(ModelObject):
    def __init__(self,dom,repository):
        ModelObject.__init__(self,dom)
        
        # Reference to the shared repository
        self.repository=repository
        
        # Extract settings
        self.url = self.getDomAttributeValue('url')
        self.group=self.getDomAttributeValue('group')
    
    def getRootUrl(self):
        url=self.repository.getUrl()
        if self.hasUrl():
            url+=self.getUrl()
        return url
        
    def hasUrl(self):
        if self.url: return True
        return False
        
    def getUrl(self):
        return self.url
        
    def getGroup(self):
        return self.group
        
class Module(NamedModelObject, Statable, Resultable, Positioned):
    """Set of Modules (which contain projects)"""
    def __init__(self,name,dom,owner):
    	NamedModelObject.__init__(self,name,dom,owner)
            	
    	Statable.__init__(self)
    	Resultable.__init__(self)
    	Positioned.__init__(self)
    	
    	self.totalDepends=[]
    	self.totalDependees=[]
    
        
    	self.projects={}
    	
        self.notifys=[]
        
    	self.repository=None
    	self.cvs=None
    	self.svn=None
    	self.artifacts=None
    	
        self.packaged		=	False
        
        # Changes were found (when updating)
    	self.modified		=	False
    	
    	# The task of updating has occured..
    	self.updated		=	False
    	
    	self.affected		=	0
        	
        # Extract settings
        self.tag=''
                
        self.url=None
        self.desc=''
        
        # 
        self.workspace=None
        self.workdir=None
        
           
    def getObjectForTag(self,tag,dom,name=None):
        """
        	Get a new (or spliced) object for this tag	
        """
        
        object=None
      
        if 'project' == tag:
            
            owner=self.getOwner()
            if self.hasProject(name):
                object=self.getProject(name)
                object.splice(dom)
            elif owner.hasProject(name):
                object=owner.getProject(name)
                object.splice(dom)
                self.addProject(object)
            else:
                from gump.model.project import Project    
                object=Project(name,dom,self)
                self.addProject(object)

        return object                                          
      
    def resolve(self):
        
        if self.isResolved(): return
        
        owner=self.getOwner()
        
        for pdom in self.getDomChildIterator('project'):
            if hasDomAttribute(pdom,'name'):
                name=getDomAttributeValue(pdom,'name')
                
                if owner.hasProject(name):
                    project=owner.getProject(name)
                            
                    if not self.hasProject(name):
                        if not project.inModule() or (project.getModule() == self):
                            self.addProject(project)
                        else:
                            pass 
                            # Duplicate project... Hmm
                            # :TODO:
                    project.splice(pdom)
                elif self.hasProject(name):                    
                    project.splice(pdom)
                else:
                    project=Project(name,pdom,self)
                    self.addProject(project) 
        
        self.setResolved()
                
    # provide default elements when not defined in xml
    def complete(self,workspace):
     
        if self.isComplete(): return

        # :TODO: hacky   
        self.workspace=workspace
        
        # Defaults
        self.workdir=self.getName()
             
        # Import overrides from DOM
        transferDomInfo( self.element, self, {'srcdir':'workdir'})
                            
        packaged=False
                
        # Claim ownership & check for packages
        # ###################################################
        # A module which contains only packaged projects might as
        # well be considered packages, no need to update from CVS
        # since we won't be building.
        packageCount=0
        allPackaged=True
                        
        for project in self.getProjects():
          
            #
            # Check for duplications
            #
            if not project.inModule():
                # Claim ownership
                self.addProject(project)
            elif not self == project.getModule():
                workspace.addError('Duplicate project [' + project.getName() + '] in [' \
                        + project.getModule().getName() + '] and now [' + self.getName() + ']')
                
            #
            # Check for packaged
            #
            if not project.isPackaged():
                allPackaged=False
            else:
                self.addInfo('Packaged Project: ' + project.getName())
                packageCount+=1                
       
        # Must be one to be all
        if not packageCount: allPackaged=False
    
        # Give this module a second try,  if some are packaged, and
        # check if the others have no outputs, then call them good.
        if packageCount and not allPackaged:
            allPackaged=True
            for project in self.getProjects():
                if not project.isPackaged():
                    if not project.hasOutputs():
                        # 
                        # Honorary package (allow folks to only mark the main
                        # project in a module as a package, and those that do
                        # not product significant outputs (e.g. test projects)
                        # will be asssumed to be packages.
                        #                
                        project.setHonoraryPackage(True)            
                        project.changeState(STATE_COMPLETE,REASON_PACKAGE)    
                        packageCount+=1
                    else:    
                        allPackaged=False
                        if packageCount:
                            self.addWarning('Incomplete \'Packaged\' Module. Project: ' + \
                                    project.getName() + ' is not packaged')  
               
        # If packages module, accept it... 
        if allPackaged:
            packaged=True
            self.setPackaged(True)
            self.changeState(STATE_COMPLETE,REASON_PACKAGE)  
            self.addInfo("\'Packaged\' Module. (Packaged projects: " + \
                                    `packageCount` + '.)')                                            

    
        # Determine source directory
        self.absWorkingDir=	\
                os.path.abspath(
                        os.path.join(workspace.getBaseDirectory(),	
                                self.workdir))
        
        self.absSrcCtlDir=	\
                 os.path.abspath(
                         os.path.join(	workspace.getSourceControlStagingDirectory(), 
                                            self.getName())) # todo allow override              
                               
        # :TODO: Consolidate this code, less cut-n-paste but also
        # check the 'type' of the repository is appropriate for the
        # use (eg. type='cvs' if referenced by CVS).
        if not packaged:
            # We have a CVS entry, expand it...
            if self.hasDomChild('cvs'):
                cvs=self.getDomChild('cvs')
                repoName=getDomAttributeValue(cvs,'repository')
                if repoName:
                    if workspace.hasRepository(repoName):
                        # It references this repository...
                        repo=workspace.getRepository(repoName)
                        self.repository=repo
                        repo.addModule(self)
                        self.cvs=ModuleCvs(cvs,repo)
                    else:
                        self.changeState(STATE_FAILED,REASON_CONFIG_FAILED)               
                        self.addError('No such repository ['+ str(repoName) +'] in workspace on [' \
                                + self.getName() + ']')
                            
            elif self.hasDomChild('svn'):
                rdom=self.getDomChild('svn')
                repoName=getDomAttributeValue(rdom,'repository')
                if repoName:
                    if workspace.hasRepository(repoName):
                        # It references this repository...
                        repo=workspace.getRepository(repoName)
                        self.repository=repo
                        repo.addModule(self)
                        self.svn=ModuleSvn(rdom,repo)
                    else:
                        self.changeState(STATE_FAILED,REASON_CONFIG_FAILED)               
                        self.addError('No such repository ['+ str(repoName) +'] in workspace on [' \
                                + self.getName() + ']')                 
                                                
            elif self.hasDomChild('artifacts'):
                adom=self.getDomChild('artifacts')
                repoName=getDomAttributeValue(adom,'repository')
                if repoName:
                    if workspace.hasRepository(repoName):
                        # It references this repository...
                        repo=workspace.getRepository(repoName)	
                        self.repository=repo	
                        repo.addModule(self)
                        self.artifacts=ModuleArtifacts(adom,repo)
                    else:
                        self.changeState(STATE_FAILED,REASON_CONFIG_FAILED)               
                        self.addError('No such repository ['+ str(repoName) +'] in workspace on [' \
                                + self.getName() + ']')                 

        # Grab all notifications
        for notifyEntry in self.getDomChildIterator('nag'):
            # Determine where to send
            toaddr=getDomAttributeValue(notifyEntry,'to',workspace.mailinglist)
            fromaddr=getDomAttributeValue(notifyEntry,'from',workspace.email)   
            self.notifys.append(
                    AddressPair(
                        getStringFromUnicode(toaddr),
                        getStringFromUnicode(fromaddr)))  
        

        if self.hasDomChild('url'):
            url=self.getDomChild('url')
            self.url=getDomAttributeValue(url,'href')
            
        if self.hasDomChild('description'):
            self.desc=self.getDomChildValue('description')           

        # For prettiness
        self.sortedProjects=createOrderedList(self.getProjects())
                            
        # Copy over any XML errors/warnings
        # :TODO:#1: transferAnnotations(self.xml, self)  
                
        self.setComplete(1)            
        
    def hasNotifys(self):
        if self.notifys: return True
        return False
        
    def getNotifys(self):
        return self.notifys
        
    def addProject(self,project):
        """
        	Associate this module with this project, and vice verse.
        """
        name=project.getName()
        
        if self.hasProject(name):
            raise RuntimeError, 'Attempt to add duplicate project: ' + name
            
        # Reference this module as owner
        project.setModule(self)
        
        # Stash project
        self.projects[name]=project
        
        # Teach workspace about this also...
        if not self.getOwner().hasProject(name):
            self.getOwner().addProject(project)
        else:
            otherProject=self.getOwner().getProject(name)
            
            if not project is otherProject:
                raise RuntimeError, 'Attempt to add duplicate project (in module): ' + name    
                     
    def hasProject(self,name):
        return self.projects.has_key(name)
        
    def getProject(self,name):
        return self.projects[name]
        
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
        
    def isRedistributable(self):
        # Existence means 'true'
        return self.hasDomAttribute('redistributable') \
            or (self.repository and self.repository.isRedistributable())
        
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
            
        return float(fogFactor)/float(fogFactors)
        
    def getHistoricalOddsOfSuccess(self):
        historicalOdds=0
        historicalOddses=0
        for project in self.getProjects():
                projectHistoricalOddsOfSuccess = project.getHistoricalOddsOfSuccess()
                historicalOdds += projectHistoricalOddsOfSuccess
                historicalOddses += 1
                
        if not historicalOddses:
            historicalOddses=1 # 0/1 is better than 0/0
            
        return float(historicalOdds)/float(historicalOddses)
        
    def getLastModified(self):
        return self.getStats().getLastModified()                
    
    # Get a summary of states for each project
    def getProjectSummary(self,summary=None):  
    
        # Fails 'cos count into other's summary
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
    def dump(self, indent=0, output=sys.stdout):
        output.write(getIndent(indent)+'Module : ' + self.name + '\n')
        NamedModelObject.dump(self, indent+1, output)
        
    def hasTag(self):
        if self.tag: return True
        return False
        
    def getTag(self):
        return str(self.tag)
        
    def getSourceControlStagingDirectory(self):
        return self.absSrcCtlDir
        
    def getWorkingDirectory(self):
        return self.absWorkingDir
        
    def getModuleDirName(self):
        return self.workdir
        
    def hasUrl(self):
        if self.url: return True
        return False
        
    def getUrl(self):
        return self.url
        
    def hasDescription(self):
        if self.desc: return True
        return False
        
    def getDescription(self):
        return self.desc     
        
    def getWorkspace(self):
        return self.workspace
    
    def getMetadataLocation(self):
        return self.metadata            
        
    def getMetadataViewUrl(self):
        location=self.getMetadataLocation()
        if location:
            if location.startswith('http'): return location
            # :TODO: Make configurable
            return 'http://cvs.apache.org/viewcvs.cgi/gump/' + location
        
    def isUpdatable(self):
        return self.hasCvs() or self.hasSvn() or self.hasArtifacts()
                
    def hasCvs(self):
        if self.cvs: return True
        return False
        
    def hasSvn(self):
        if self.svn: return True
        return False
        
    def hasArtifacts(self):
        if self.artifacts: return True
        return False
        
    # Where the contents (at the repository) Modified?
    def isModified(self):
        return self.modified
        
    def setModified(self,modified):
        self.modified=modified
    
    # Where the contents (at the repository) Updated?
    def isUpdated(self):
        return self.updated
        
    def setUpdated(self,updated):
        self.updated=updated
    
    def hasRepository(self):
        return self.repository
        
    def getRepository(self):
        return self.repository
    
    def getViewUrl(self):
        if self.hasCvs():
            return self.cvs.getViewUrl()
        elif self.hasSvn():
            return self.svn.getViewUrl()            

class ModuleStatistics(Statistics):
    """ 
        Module Statistics Holder
    """
    def __init__(self,moduleName):
        Statistics.__init__(self,moduleName)    
        self.lastModified=-1        
        
    def getLastModified(self):
        return (self.lastModified)
        
    def getKeyBase(self):
        return 'module:'+ self.name
        
    def lastModifiedKey(self):
        return self.getKeyBase() + '-last-updated'

    def update(self,module):      
        Statistics.update(self,module)

        #
        # Track code updates/changes
        # 
        if module.isModified():
            self.lastModified=default.time