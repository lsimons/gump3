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
from string import lower, capitalize

from gump.utils.work import *
from gump.utils.launcher import *
from gump.utils.tools import *

from gump.model.state import *
from gump.model.repository import Repository
from gump.model.server import Server
from gump.model.tracker import Tracker
from gump.model.module import Module, createUnnamedModule
from gump.model.project import Project, ProjectSummary
from gump.model.profile import Profile
from gump.model.object import NamedModelObject, Resultable
from gump.model.property import PropertyContainer
from gump.model.stats import Statable, Statistics
from gump.utils.note import transferAnnotations, Annotatable
from gump.utils.listener import Listener, Event

#
# :TODO: Need to createa GumpEnvironment to move these to..
#

SUCCESS=0
FAILED=1
MISSING_UTILITY=2
BAD_ENVIRONMENT=3


class Workspace(NamedModelObject, PropertyContainer, Statable, Resultable):
    """Gump Workspace"""
    def __init__(self,xmlworkspace):
    
        # Workspaces
        name='Unnamed'
        if xmlworkspace:
            if xmlworkspace.getName():
                name=xmlworkspace.getName()
            
    	NamedModelObject.__init__(self,name,xmlworkspace)    	
    	PropertyContainer.__init__(self)    
    	Statable.__init__(self)
    	Resultable.__init__(self)
    		
    	#
    	# Named repositories (e.g. CVS,SVN,etc.)
    	# Named modules
    	# Named projects
    	# Named profiles
    	#
    	self.repositories={}
        self.modules={}
        self.projects={}
        self.profiles={}
        self.servers={}
        self.trackers={}
        
        #
    	PropertyContainer.importProperties(self,self.xml)    	
    	                 	
 
        
        #    
        self.startdatetime=time.strftime(setting.datetimeformat, \
                                time.localtime())
        self.timezone=str(time.tzname)    

        # Where the merged XML was put
        self.mergeFile=None
        
        self.listener=ModelListener()
        
    def getChildren(self):
        return self.getModules() 
    

    # Repository Interface
    
    def hasRepository(self,rname):
        return self.repositories.has_key(rname)
        
    def getRepository(self,rname):
        return self.repositories[rname]
        
    def getRepositories(self):
        return self.repositories.values()
        
    def getSortedRepositories(self):
        return self.sortedRepositories


    # Server Interface
    
    def hasServer(self,rname):
        return self.servers.has_key(rname)
        
    def getServer(self,rname):
        return self.servers[rname]
        
    def getServers(self):
        return self.servers.values()
        
    def getSortedServers(self):
        return self.sortedServers


    # Tracker Interface
    
    def hasTracker(self,rname):
        return self.trackers.has_key(rname)
        
    def getTracker(self,rname):
        return self.trackers[rname]
        
    def getTrackers(self):
        return self.trackers.values()
        
    def getSortedTrackers(self):
        return self.sortedTrackers


    # Profile Interface
        
    def hasProfile(self,mname):
        return self.profiles.has_key(mname)
        
    def getProfile(self,mname):
        return self.profiles.get(mname,None)

    def getProfiles(self):
        return self.profiles.values()              
                
    def getSortedProfiles(self):
        return self.sortedProfiles   
                
    # Module Interface
        
    def hasModule(self,mname):
        return self.modules.has_key(mname)
        
    def getModule(self,mname):
        return self.modules.get(mname,None)

    def getModules(self):
        return self.modules.values()              
                
    def getSortedModules(self):
        return self.sortedModules   
                
                
    # All projects in the workspace (also available
    # through the owned moduleS)
                
    def hasProject(self,pname):
        return self.projects.has_key(pname)
        
    def getProject(self,pname):
        return self.projects[pname]
                
    def getProjects(self):
        return self.projects.values() 
                
    def getSortedProjects(self):
        return self.sortedProjects       
        
    def complete(self, xmlprofiles, xmlrepositories, \
                    xmlmodules, xmlprojects,	\
                    xmlservers, xmltrackers):        
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
            self.bannerLink="http://gump.apache.org"
        else:
            self.bannerLink=self.xml['banner-link']

        self.completeDirectories()
        
        # Allow per workspace overrides
    
        if not self.xml.logurl: 
            self.logurl = default.logurl
        else:
            self.logurl = self.xml.logurl
            
        # Keep some details private, if requested...
        if self.xml.private:
            self.private=1
        else:
            self.private=0
            
        # Sending e-mail address
        if not self.xml.email: 
            self.email = default.email
        else:
            self.email = self.xml.email
            
        # Gump List...
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
        # Import all profiles
        #  
        for xmlprofile in xmlprofiles.values(): 
            profile=Profile(xmlprofile,self)
            profileName=profile.getName()
            if profileName in self.profiles:
                # Duplicate, uh oh...
                self.addError("Duplicate profile name [" + profileName + "]")
            else:        
                profile.complete(self)
                self.profiles[profileName] = profile
        
            self.listener.handleEvent(ModelEvent())

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
        
            self.listener.handleEvent(ModelEvent())

        #
        # Import all servers
        #  
        for xmlserver in xmlservers.values(): 
            server=Server(xmlserver,self)
            serverName=server.getName()
            if serverName in self.servers:
                # Duplicate, uh oh...
                self.addError("Duplicate server name [" + serverName + "]")
            else:        
                server.complete(self)
                self.servers[serverName] = server
        
            self.listener.handleEvent(ModelEvent())

        #
        # Import all trackers
        #  
        for xmltracker in xmltrackers.values(): 
            tracker=Tracker(xmltracker,self)
            trackerName=tracker.getName()
            if trackerName in self.trackers:
                # Duplicate, uh oh...
                self.addError("Duplicate tracker name [" + trackerName + "]")
            else:        
                tracker.complete(self)
                self.trackers[trackerName] = tracker
        
            self.listener.handleEvent(ModelEvent())

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
        
            self.listener.handleEvent(ModelEvent())
            
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
        
            self.listener.handleEvent(ModelEvent())

        # Complete the modules
        for module in self.getModules():
            module.complete(self)
        
            self.listener.handleEvent(ModelEvent())
            
        #
        # Check repositories, now modules have been imported,
        # so we can report those unused ones.
        #
        for repository in self.getRepositories(): 
            repository.check(self)           
        
            self.listener.handleEvent(ModelEvent()) 
        
        #
        # Check servers.
        #
        for server in self.getServers(): 
            server.check(self)            
        
            self.listener.handleEvent(ModelEvent())
        
        #
        # Check trackers.
        #
        for tracker in self.getTrackers(): 
            tracker.check(self)           
        
            self.listener.handleEvent(ModelEvent()) 
        
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
        
            self.listener.handleEvent(ModelEvent())
        
        # Check they are complete...
        for project in self.getProjects():
            if not project.isPackaged(): continue
            project.checkPackage()          
        
            self.listener.handleEvent(ModelEvent())         
                                                             
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
        transferAnnotations(self.xml, self)  
                
        
        self.listener.handleEvent(ModelEvent())
            
        self.setComplete(1)

    def completeDirectories(self):
            
        # Construct tmp on demand
        if not self.xml.tmpdir: 
            self.tmpdir=os.path.join(self.getBaseDirectory(),"tmp")
        else:
            self.tmpdir=self.xml.tmpdir
            
        if not os.path.exists(self.tmpdir): 
            os.makedirs(self.tmpdir)    
    
        # Construct logdir on demand
        if not self.xml.logdir: 
            self.logdir=os.path.join(self.getBaseDirectory(),"log")
        else:
            self.logdir=self.xml.logdir
        
        if not os.path.exists(self.logdir): os.makedirs(self.logdir)
    
        # Construct repository dir on demand
        if not self.xml.jardir: 
            self.jardir=os.path.join(self.getBaseDirectory(),"repo")
        else:
            self.jardir=self.xml.jardir
                
        if not os.path.exists(self.jardir): os.makedirs(self.jardir)
    
        # Construct CVS directory on demand
        if not self.xml.cvsdir: 
            self.cvsdir=os.path.join(self.getBaseDirectory(),"cvs")
        else:
            self.cvsdir=self.xml.cvsdir

        if not os.path.exists(self.cvsdir): os.makedirs(self.cvsdir)
    
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
        
   
    def setDatedDirectories(self,date=None):
        
        # This build date
        if not date: date = gump.default.date
            
        # Construct tmp on demand
        self.tmpdir=os.path.join(self.tmpdir,date)            
        if not os.path.exists(self.tmpdir): 
            os.makedirs(self.tmpdir)    
    
        # Construct logdir on demand
        self.logdir=os.path.join(self.logdir,date)
        if not os.path.exists(self.logdir): os.makedirs(self.logdir)

            
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
        ModelObject.dump(self, indent+1, output)
        
        for profile in self.profiles.values():
            profile.dump(indent+1,output)
            
        for repo in self.repositories.values():
            repo.dump(indent+1,output)
        
        for module in self.getModules():
            module.dump(indent+1,output)
        
        for project in self.getProjects():
            project.dump(indent+1,output)

    def isNag(self):
        return self.xml.nag
        
    def hasNagToOverride(self):
        return self.isNag() and hasattr(self.xml.nag,'to')
        
    def getNagToOverride(self):
        return getattr(self.xml.nag,'to')
        
    def hasNagFromOverride(self):
        return self.isNag() and hasattr(self.xml.nag,'from')
        
    def getNagFromOverride(self):
        return getattr(self.xml.nag,'from')
        
    def getNagOverrides(self):
          
        #
        # Nag Overrides
        #
        wsNagToOverrideAddr=None
        wsNagFromOverrideAddr=None
        
        if self.hasNagToOverride():
            wsNagToOverrideAddr=self.getNagToOverride()
            
        if self.hasNagFromOverride():
            wsNagFromOverrideAddr=self.getNagFromOverride()
        
        return ( wsNagToOverrideAddr, wsNagFromOverrideAddr)
             
    def getVersion(self):
        return self.xml.version

    def getBaseDirectory(self):
        return self.xml.basedir
            
    def getLogDirectory(self):
        return self.xml.logdir or \
            os.path.abspath(os.path.join(self.getBaseDirectory(),'log'))
            
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
        
    def getCvsDirectory(self):
        return self.cvsdir


class WorkspaceStatistics(Statistics):
    """Statistics Holder"""
    def __init__(self):
        Statistics.__init__(self,'workspace')    
        self.lastUpdated=-1        
        
    def getLastUpdated(self):
        return (self.lastUpdated)
        
    def getKeyBase(self):
        return self.name
        
    def lastUpdatedKey(self):
        return self.getKeyBase() + '-last-updated'

    def update(self,module):      
        Statistics.update(self,module)

        #
        # Track code updates/changes
        # 
        if module.isUpdated():
            self.lastUpdated=default.time        
            
            
class ModelEvent(Event):
    def __init__(self):		pass

class ModelListener(Listener):
    def __init__(self):  	pass
    
    #
    # Called with events
    #
    def notify(self,event):
        pass
        #print '.',
        
            