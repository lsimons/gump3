#!/usr/bin/env python

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
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

from gump.util.work import *
from gump.util.tools import *

from gump.core.model.state import *
from gump.core.model.repository import Repository
from gump.core.model.server import Server
from gump.core.model.tracker import Tracker
from gump.core.model.module import Module
from gump.core.model.project import Project, ProjectSummary
from gump.core.model.profile import Profile
from gump.core.model.object import NamedModelObject,ModelObject
from gump.core.model.misc import Resultable
from gump.core.model.property import PropertyContainer
from gump.core.model.stats import Statable, Statistics
from gump.util.note import transferAnnotations, Annotatable
from gump.util.domutils import *

import gump.core.config

class DatabaseInformation(ModelObject):
    def __init__(self,dom):    
        ModelObject.__init__(self,dom)  
        
        # Some defaults...
        self.host='localhost'
        self.user='root'
        self.passwd=''
        self.database='gump'
        
    def complete(self,workspace): 
        if self.isComplete(): return
        
        # In case we care
        self.workspace=workspace
        
        # Import DOM attributes into self as attributes
        transferDomInfo(self.element, self, {})   
        
        self.setComplete()
        
    def getHost(self): return self.host
    def getUser(self): return self.user
    def getPasswd(self): return self.passwd
    def getDatabase(self): return self.database
    
class DotNetInformation(ModelObject):
    def __init__(self,dom):    
        ModelObject.__init__(self,dom)  
        
        # Some defaults...
        self.framework=None
        
    def complete(self,workspace): 
        if self.isComplete(): return
        
        # In case we care
        self.workspace=workspace
        
        # Import DOM attributes into self as attributes
        transferDomInfo(self.element, self, {})   
        
        self.setComplete()
        
    def hasFramework(self): 
        if self.framework: return True
        return False
        
    def getFramework(self):
        return self.framework

        
class Workspace(NamedModelObject, PropertyContainer, Statable, Resultable):
    """
            
    Gump Workspace: Contains where/what ... lots of good stuff
            
    """
    def __init__(self,name,dom):
                
        NamedModelObject.__init__(self,name,dom)   
         
        PropertyContainer.__init__(self)    
        Statable.__init__(self)
        Resultable.__init__(self)

        # Named repositories (e.g. CVS,SVN,etc.)
        # Named modules
        # Named projects
        # Named profiles
        # Named servers
        # Named trackers
        self.repositories={}
        self.modules={}
        self.projects={}
        self.profiles={}
        self.servers={}
        self.trackers={}        
        
        # Treads
        self.updaters=0
        self.builders=0
                    
        # Database Informaton
        self.dbInfo=None

        # DotNet Informaton
        self.dotnetInfo=None

        # Where the merged XML was put
        self.mergeFile=None

        # make executable
        self.makeCommand = 'make'
 
    def getChildren(self):
        return self.getModules() 
    
    # Repository Interface    
    def hasRepository(self,rname):
        return rname in self.repositories
        
    def getRepository(self,rname):
        return self.repositories[rname]
        
    def getRepositories(self):
        return list(self.repositories.values())
        
    def getSortedRepositories(self):
        return self.sortedRepositories

    # Server Interface    
    def hasServer(self,rname):
        return rname in self.servers
        
    def getServer(self,rname):
        return self.servers[rname]
        
    def getServers(self):
        return list(self.servers.values())
        
    def getPythonServers(self):
        """
            Return the Python servers
        """
        return [server for server in self.getServers() if server.isPython() ]
        
    def hasMultiplePythonServers(self):
        """
            Has more than one server (typically, for assuming that this one
            is the one, if one, so not doing server stuff).
        """
        return len(self.getPythonServers()) > 1
        
    def getSortedServers(self):
        return self.sortedServers

    # Tracker Interface    
    def hasTracker(self,rname):
        return rname in self.trackers
        
    def getTracker(self,rname):
        return self.trackers[rname]
        
    def getTrackers(self):
        return list(self.trackers.values())
        
    def getSortedTrackers(self):
        return self.sortedTrackers

    # Profile Interface        
    def hasProfile(self,mname):
        return mname in self.profiles
        
    def getProfile(self,mname):
        return self.profiles.get(mname,None)

    def getProfiles(self):
        return list(self.profiles.values())              
                
    def getSortedProfiles(self):
        return self.sortedProfiles   
                
    # Module Interface        
    def hasModule(self,mname):
        return mname in self.modules
        
    def addModule(self,module):
        if self.hasModule(name):
            raise RuntimeError('Attempt to add duplicate module: ' + name)    
        self.modules[module.getName()]=module
        
    def getModule(self,mname):
        return self.modules.get(mname,None)

    def getModules(self):
        return list(self.modules.values())              
                
    def getSortedModules(self):
        return self.sortedModules   
                
    # All projects in the workspace (also available
    # through the owning modules)
                
    def hasProject(self,pname):
        return pname in self.projects
        
    def addProject(self,project):
        name=project.getName()
        if self.hasProject(name):
            raise RuntimeError('Attempt to add duplicate project: ' + name)    
        self.projects[name]=project
        
    def getProject(self,pname):
        return self.projects[pname]
                
    def getProjects(self):
        return list(self.projects.values()) 
                
    def getSortedProjects(self):
        return self.sortedProjects       
        
    def hasDatabaseInformation(self):
        if self.dbInfo: return True
        return False
        
    def getDatabaseInformation(self):
        return self.dbInfo
        
    def hasDotNetInformation(self):
        if self.dotnetInfo: return True
        return False
        
    def getDotNetInformation(self):
        return self.dotnetInfo
        
    def isMultithreading(self):
        return self.hasUpdaters() or self.hasBuilders()
        
    def hasUpdaters(self):
        return (0 < self.updaters)
        
    def getUpdaters(self):
        return self.updaters
        
    #:TODO: Note, not implemented yet
    def hasBuilders(self):
        return (0 < self.builders)
        
    #:TODO: Note, not implemented yet
    def getBuilders(self):
        return self.builders
        
    def complete(self):        
        if self.isComplete(): return
                
        # Set defaults...        
        self.basedir=''
        self.bannerImnage=default.bannerimage
        self.bannerLink="http://gump.apache.org"
        
        self.tmpdir=''
        self.logdir=''
        self.repodir=''
        self.cvsdir=''
        self.pkgdir=''
        
        self.logurl=''
        
        self.private=False
        self.email = default.email     
        self.administrator = default.administrator  
        self.mailserver = default.mailserver
        self.mailport = int(default.mailport)
        self.prefix=default.prefix
        self.signature=default.signature
        self.mvnRepoProxyPort = default.mvnRepoProxyPort
        
        # Import overrides from DOM
        transferDomInfo(self.element, 
                        self, 
                        {   'jardir':'repodir',
                            'banner-image':'bannerImage',
                            'banner-link' :'bannerLink'})
    
        if not self.basedir:
            raise RuntimeError("A workspace cannot operate without a 'basedir'.")
            
        if not self.tmpdir: self.tmpdir=os.path.join(self.getBaseDirectory(),"tmp")
        if not self.logdir: self.logdir=os.path.join(self.getBaseDirectory(),"log")
        if not self.repodir: self.repodir=os.path.join(self.getBaseDirectory(),"repo") 
        if not self.cvsdir: self.cvsdir=os.path.join(self.getBaseDirectory(),"cvs")
        if not self.pkgdir: self.pkgdir=self.getBaseDirectory()
            
        # Construct dirs on demand         
        if not os.path.exists(self.tmpdir): os.makedirs(self.tmpdir)    
        if not os.path.exists(self.logdir): os.makedirs(self.logdir)
        if not os.path.exists(self.repodir): os.makedirs(self.repodir)
        if not os.path.exists(self.cvsdir): os.makedirs(self.cvsdir)
    
        # Get all properties
        PropertyContainer.importProperties(self,self.element)        
        
        # Complete all profiles
        for profile in list(self.profiles.values()): 
            profile.complete(self)
            
        # Complete all repositories
        for repository in list(self.repositories.values()): 
            repository.complete(self)

        # Complete all servers
        for server in list(self.servers.values()): 
            server.complete(self)

        # Complete all trackers
        for tracker in list(self.trackers.values()): 
            tracker.complete(self)

        # Complete the modules
        for module in self.getModules():
            if not module.isComplete():
                module.complete(self)
        
        # Check repositories, now modules have been imported,
        # so we can report those unused ones.
        for repository in self.getRepositories(): 
            repository.check(self)           
        
        # Check servers.
        for server in self.getServers(): 
            server.check(self)            
        
        # Check Trackers.
        for tracker in self.getTrackers(): 
            tracker.check(self)           
        
        # Complete the projects   
        for project in self.getProjects():
            # Projects needs a module (even if pseudo)
            if not project.inModule():
                log.error('Project not in module. ' + project.getName())
            
            # Complete the project
            if not project.isComplete():
                project.complete(self)   
                
        # Mutlithreading
        if self.hasDomChild('threads'):
            threads=self.getDomChild('threads')
            if hasDomAttribute(threads,'updaters'):
                self.updaters=int(getDomAttributeValue(threads,'updaters'))
            if hasDomAttribute(threads,'builders'):
                self.builders=int(getDomAttributeValue(threads,'builders'))
                
        if self.hasDomChild('database'):
            self.dbInfo=DatabaseInformation(self.getDomChild('database'))
            self.dbInfo.complete(self)
                                                             
        if self.hasDomChild('dotnet'):
            self.dotnetInfo=DotNetInformation(self.getDomChild('dotnet'))
            self.dotnetInfo.complete(self)
                                                             
        # Complete the properies
        self.completeProperties()
                                     
        # Sort contents (for 'prettiness')
        
        # Pretty sorting...
        self.sortedModules=createOrderedList(self.getModules())
        self.sortedProjects=createOrderedList(self.getProjects())
        self.sortedRepositories=createOrderedList(self.getRepositories())
        self.sortedProfiles=createOrderedList(self.getProfiles())
        self.sortedServers=createOrderedList(self.getServers())
        self.sortedTrackers=createOrderedList(self.getTrackers())
        
        # Copy over any XML errors/warnings
        # :TODO:#1: transferAnnotations(self.xml, self)  
            
        self.setComplete(True)

   
    def setDatedDirectories(self,date=None):
        
        # This build date
        if not date: date = default.date_s
            
        # Construct tmp on demand
        self.tmpdir=os.path.join(self.tmpdir,date)            
        if not os.path.exists(self.tmpdir): 
            os.makedirs(self.tmpdir)    
    
        # Construct logdir on demand
        self.logdir=os.path.join(self.logdir,date)
        if not os.path.exists(self.logdir): os.makedirs(self.logdir)
        
        # Extend Log URL
        if not self.logurl.endswith('/'): self.logurl+='/'
        self.logurl+=date
            
    def addModule(self,module):
        self.modules[module.getName()]=module                         
        
    # Get a summary of states for each project
    def getProjectSummary(self,summary=None): 
        #if hasattr(self,'summary'): return self.summary
                
        if not summary: 
            summary=ProjectSummary()
        
        # Subordinates are modules, get their summary
        # information into this summary
        for module in self.getModules():
            module.getProjectSummary(summary)
            
        # Store for later...
        #self.summary = summary
        
        return summary
        
    def dump(self, indent=0, output=sys.stdout):
        output.write('Workspace : \n')
        NamedModelObject.dump(self, indent+1, output)
        
        for profile in list(self.profiles.values()):
            profile.dump(indent+2,output)            
        
        for module in self.getModules():
            module.dump(indent+2,output)
        
        for project in self.getProjects():
            project.dump(indent+2,output)
        
        for repo in list(self.repositories.values()):
            repo.dump(indent+2,output)
            
        for server in self.getServers():
            server.dump(indent+2,output)
        
        for tracker in self.getTrackers():
            tracker.dump(indent+2,output)

    def isNotify(self):
        return self.hasDomChild('nag')
        
    def hasNotifyToOverride(self):
        if not self.isNotify(): return False
        nag=self.getDomChild('nag')
        return hasDomAttribute(nag,'to')
        
    def getNotifyToOverride(self):
        if self.isNotify():
            nag=self.getDomChild('nag')
            return getDomAttributeValue(nag,'to')
        
    def hasNotifyFromOverride(self):
        if not self.isNotify(): return False
        nag=self.getDomChild('nag')
        return hasDomAttribute(nag,'from')        
        
    def getNotifyFromOverride(self):
        if self.isNotify():
            nag=self.getDomChild('nag')
            return getDomAttributeValue(nag,'from')    
            
    def getNotifyOverrides(self):
        
        # Nag Overrides
        wsNotifyToOverrideAddr=None
        wsNotifyFromOverrideAddr=None
        
        if self.hasNotifyToOverride():
            wsNotifyToOverrideAddr=self.getNotifyToOverride()
            
        if self.hasNotifyFromOverride():
            wsNotifyFromOverrideAddr=self.getNotifyFromOverride()
        
        return ( wsNotifyToOverrideAddr, wsNotifyFromOverrideAddr )
             
    def getVersion(self):
        if self.hasDomAttribute('version'):
            return self.getDomAttributeValue('version')

    def getBaseDirectory(self):
        return self.basedir
            
    def getLogDirectory(self):
        return self.logdir
            
    def getLogUrl(self):
        return self.logurl            
        
    def setMergeFile(self,file):
        self.mergeFile=file
    
    def getMergeFile(self):
        return self.mergeFile
    
    # :TODO: Inefficient, ought store sorted
    def getProjectIterator(self):
        return AlphabeticDictionaryIterator(self.projects)        
        
    # :TODO: Inefficient, ought store sorted
    def getModuleIterator(self):
        return AlphabeticDictionaryIterator(self.modules)    
        
    def getSourceControlStagingDirectory(self):
        return self.cvsdir

    def getMakeCommand(self):
        return self.makeCommand

    def getObjectForTag(self,tag,dom,name=None):
        """
            If we are parsing  document (given this object as
            parent context) then construct the child appropriately.
            Sometimes that means splicing the new XML into the
            existing.
        """
        object=None
        
        if 'profile' == tag:
            if self.hasProfile(name):
                object=self.getProfile(name)
                object.splice(dom)
            else:
                object=Profile(name,dom,self)
                self.profiles[name]=object      
        elif 'repository' == tag:
            if self.hasRepository(name):
                object=self.getRepository(name)
                object.splice(dom)
            else:
                object=Repository(name,dom,self)
                self.repositories[name]=object
        elif 'server' == tag:
            if self.hasServer(name):
                object=self.getServer(name)
                object.splice(dom)
            else:
                object=Server(name,dom,self)
                self.servers[name]=object
        elif 'tracker' == tag:
            if self.hasTracker(name):
                object=self.getTracker(name)
                object.splice(dom)
            else:
                object=Tracker(name,dom,self)
                self.trackers[name]=object
        elif 'module' == tag:
            if self.hasModule(name):
                object=self.getModule(name)
                object.splice(dom)
            else:
                object=Module(name,dom,self)
                self.modules[name]=object
        elif 'project' == tag:
            if self.hasProject(name):
                object=self.getProject(name)
                object.splice(dom)
            else:
                object=Project(name,dom,self)
                self.projects[name]=object

        return object
        
    def resolve(self):
        """
        
            Work through the child elements extracting the
            main objects.
        
        """
        if self.isResolved(): return
        
        for pdom in self.getDomChildIterator('project'):
            if hasDomAttribute(pdom,'name'):
                name=getDomAttributeValue(pdom,'name')
                
                if self.hasProject(name):
                    project=self.getProject(name)
                    project.splice(pdom)
                else:
                    project=Project(name,pdom,self)
                    self.addProject(project)   
        
        self.setResolved()  

    def getLocalRepositoryDirectory(self):
        #
        # Where to put the local repository
        #
        return os.path.abspath(os.path.join(self.getBaseDirectory(),
                                            "mvnlocalrepo"))

class WorkspaceStatistics(Statistics):
    """Statistics Holder"""
    def __init__(self,workspaceName):
        Statistics.__init__(self,workspaceName)    
        
    def getKeyBase(self):
        return 'workspace:'+ self.name        
            
