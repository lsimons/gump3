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

import gump.core.config

#
#
#

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
                    
        # Set times
        self.initializeTimes()

        # Where the merged XML was put
        self.mergeFile=None
        
        self.listener=ModelListener()
        
    def initializeTimes(self):
        # Store timezone
        self.timezone=str(time.tzname)    
        
        self.startDateTimeUtc=''
        self.startDateTime=''
                                 
        self.endDateTimeUtc=''
        self.endDateTime=''
                
    # :TODO: Move these to run, like much dynamic stuff on W/S

    def setStartTime(self):                
                
        # :TODO: Ensure no clock ticks between these two,
        # i.e. make one.
        self.startDateTimeUtc=time.strftime(setting.utcdatetimeformat, \
                                            time.gmtime())
        self.startDateTime=time.strftime(setting.datetimeformat, \
                                            time.localtime())
                                                    
        self.endDateTimeUtc=''
        self.endDateTime=''
        
    def setEndTime(self):
        
        # Don't do more than once.
        if self.endDateTimeUtc and self.endDateTime: return
            
        
        # :TODO: Ensure no clock ticks between these two,
        # i.e. make one.
        self.endDateTimeUtc=time.strftime(setting.utcdatetimeformat, \
                                            time.gmtime())
        self.endDateTime=time.strftime(setting.datetimeformat, \
                                            time.localtime())
                                            
        
    def getTimezone(self):
        return self.timezone
        
    def getStartDateTime(self):
        return self.startDateTime
        
    def getStartDateTimeUtc(self):
        return self.startDateTimeUtc
        
    def getEndDateTime(self):
        return self.endDateTime
        
    def getEndDateTimeUtc(self):
        return self.endDateTimeUtc
        
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
        if not hasattr(self.xml,'banner-image'):
            self.bannerImage=default.bannerimage
        else:
            self.bannerImage=getattr(self.xml,'banner-image')
            
        if not hasattr(self.xml,'banner-link'): 
            self.bannerLink="http://gump.apache.org"
        else:
            self.bannerLink=getattr(self.xml,'banner-link')

        self.completeDirectories()
        
        # Allow per workspace overrides
        self.logurl = self.xml.transfer('logurl',default.logurl)
            
        # Keep some details private, if requested...
        self.private=hasattr(self.xml,'private')
            
        # Sending e-mail address
        self.email = self.xml.transfer('email', default.email)            
        # Gump List...
        self.mailinglist = self.xml.transfer('mailinglist',default.mailinglist)        
        # Mail server
        self.mailserver = self.xml.transfer('mailserver',default.mailserver)
            
        # Get mailport as an int
        self.mailport = int(self.xml.transfer('mailport',default.mailport))
            
        # Mail subject prefix
        self.prefix = self.xml.transfer('prefix',default.prefix)
            
        # Mail .sig
        self.signature = self.xml.transfer('signature',default.signature)        
      
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
        # Check Trackers.
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
                
        self.listener.handleEvent(ModelEvent())
            
        self.setComplete(1)

    def completeDirectories(self):
            
        if self.xml.basedir:
            self.basedir=self.xml.basedir
        else:
            raise RuntimeError, "A workspace cannot operate without a 'basedir'."
            
        # Construct tmp on demand
        self.tmpdir=self.xml.transfer('tmpdir',os.path.join(self.getBaseDirectory(),"tmp"))            
        if not os.path.exists(self.tmpdir): 
            os.makedirs(self.tmpdir)    
    
        # Construct logdir on demand
        self.logdir=self.xml.transfer('logdir',os.path.join(self.getBaseDirectory(),"log"))        
        if not os.path.exists(self.logdir): os.makedirs(self.logdir)
    
        # Construct repository dir on demand
        self.jardir=self.xml.transfer('jardir',os.path.join(self.getBaseDirectory(),"repo"))   
        if not os.path.exists(self.jardir): os.makedirs(self.jardir)
    
        # Construct CVS directory on demand
        self.cvsdir=self.xml.transfer('cvsdir',os.path.join(self.getBaseDirectory(),"cvs"))
        if not os.path.exists(self.cvsdir): os.makedirs(self.cvsdir)
    
        # Package Dir Ought Exist
        self.pkgdir=self.xml.transfer('pkgdir',self.getBaseDirectory())
        
        if not hasattr(self.xml,'deliver'):
            self.scratchdir=self.xml.transfer('scratchdir',os.path.join(self.getBaseDirectory(),"scratch"))
   
    def setDatedDirectories(self,date=None):
        
        # This build date
        if not date: date = default.date
            
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
        
        for profile in self.profiles.values():
            profile.dump(indent+1,output)
            
        for repo in self.repositories.values():
            repo.dump(indent+1,output)
        
        for module in self.getModules():
            module.dump(indent+1,output)
        
        for project in self.getProjects():
            project.dump(indent+1,output)

    def isNotify(self):
        return hasattr(self.xml,'nag')
        
    def hasNotifyToOverride(self):
        return self.isNotify() and hasattr(self.xml.nag,'to')
        
    def getNotifyToOverride(self):
        return getattr(self.xml.nag,'to')
        
    def hasNotifyFromOverride(self):
        return self.isNotify() and hasattr(self.xml.nag,'from')
        
    def getNotifyFromOverride(self):
        return getattr(self.xml.nag,'from')
        
    def getNotifyOverrides(self):
          
        #
        # Nag Overrides
        #
        wsNotifyToOverrideAddr=None
        wsNotifyFromOverrideAddr=None
        
        if self.hasNotifyToOverride():
            wsNotifyToOverrideAddr=self.getNotifyToOverride()
            
        if self.hasNotifyFromOverride():
            wsNotifyFromOverrideAddr=self.getNotifyFromOverride()
        
        return ( wsNotifyToOverrideAddr, wsNotifyFromOverrideAddr)
             
    def getVersion(self):
        if hasattr(self.xml,'version'):
            return self.xml.version.value()

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


class WorkspaceStatistics(Statistics):
    """Statistics Holder"""
    def __init__(self,workspaceName):
        Statistics.__init__(self,workspaceName)    
        
    def getKeyBase(self):
        return 'workspace:'+ self.name        
    
            
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
        
            