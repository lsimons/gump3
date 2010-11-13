#!/usr/bin/python


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
  Highly experimental Atom feeds.
"""

import os
import time

from xml.sax.saxutils import escape

from gump import log
from gump.core.model.state import *
from gump.core.model.project import ProjectStatistics

from gump.core.config import setting

from gump.actor.syndication.abstract import AbstractSyndicator

###############################################################################


# Local time zone, in offset from GMT
TZ='%+.2d:00' % (-time.timezone/3600)

###############################################################################

class Entry:

    """
    An entry (news item) in an Atom Feed. 
    Note: Can be added to more than one feed at once.
    """    
    def __init__(self,title,link,description,content=None):
        self.title=title
        self.link=link
        self.description=description        
        self.content=content
     
    def serializeToStream(self, stream, modified, uri, id):
        
        # Write the header part...
        stream.write("""		<entry>
        <author><name>Apache Gump(TM)</name></author>
        <id>gump:%s:%s-%s</id>
        <title>%s</title>
        <link rel="alternate" type="text/html" href="%s"/>
        <issued>%s</issued>        
        <modified>%s</modified>        
        """	\
        % (	    uri, modified, id, \
                self.description, \
                self.link, \
                modified, modified) )

        if self.content:
            stream.write("""<content type='text/html' mode='escaped'>%s</content>"""	\
            % (escape(self.content)) )
            
        # Write the trailer part...
        stream.write("""		</entry>\n""")
        
class AtomFeed:
    
    def __init__(self,url,file,uri,title,link,description):
        self.url=url
        self.file=file
        self.uri=uri
        self.title=title
        self.link=link
        self.description=description
        
        self.entries=[]
        
    def addEntry(self,entry):
        self.entries.append(entry)
        
    def serializeToStream(self, stream, modified):
        
        # Write the header part...
        stream.write("""<?xml version="1.0" encoding="utf-8"?>
<feed version="0.3" xmlns="http://purl.org/atom/ns#">
        <title>%s</title>
        <link rel="alternate" type="text/html" href="%s"/>
        <modified>%s</modified>        
"""	% (self.description, self.link, modified) )
        
        id=0
        for entry in self.entries:
            entry.serializeToStream(stream, modified, self.uri, id)
            id+=1
        
        # Write the trailer part...
        stream.write("""
</feed>
""")
                
    def serialize(self):
        #log.info("Atom News Feed to : " + self.file);         
        stream = open(self.file,'w')
        
        modified=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        
        self.serializeToStream(stream,modified)
            
        # Close the file.
        stream.close()  
        
class AtomSyndicator(AbstractSyndicator):
    def __init__(self,run):
        AbstractSyndicator.__init__(self,run)
        
    def prepareRun(self):
        
        # Main syndication document
        self.workspace=self.run.getWorkspace()   
        
        feedFile=self.run.getOptions().getResolver().getFile(self.workspace,'atom','.xml',1)      
        feedUrl=self.run.getOptions().getResolver().getUrl(self.workspace,'atom','.xml')
    
        self.feed=AtomFeed(feedUrl,feedFile,	\
                        'workspace',	\
                       'Apache Gump',		\
                        self.workspace.getLogUrl(),	\
                        """Life is like a box of chocolates""")
            
    def completeRun(self):
        self.feed.serialize()
            
    def syndicateModule(self,module):
                
        feedFile=self.run.getOptions().getResolver().getFile(module,'atom','.xml',1)
        feedUrl=self.run.getOptions().getResolver().getUrl(module,'atom','.xml')
        moduleUrl=self.run.getOptions().getResolver().getUrl(module)
        
        moduleFeed=AtomFeed(feedUrl,feedFile,	
                        'module',	\
                        'Apache Gump : Module ' + escape(module.getName()),	\
                        moduleUrl,	\
                        escape(module.getDescription() or ''))
                    
          
        # Get a decent description
        content=self.getModuleContent(module,self.run)
                        
        # Entry
        entry=Entry(('%s %s') % (module.getName(),module.getStateDescription()), \
                  moduleUrl, \
                  module.getName(), \
                  content)
        
        # Generate changes, only if the module had changed
        if module.isModified() and not module.getStatePair().isUnset():  
            log.debug("Add module to Atom Newsfeed for : " + module.getName())    
            moduleFeed.addEntry(entry)  
            
        # State changes that are newsworthy...
        if 	self.moduleOughtBeWidelySyndicated(module):      
            log.debug("Add module to widely distributed Atom Newsfeed for : " + module.getName())      
            self.feed.addEntry(entry)
            
        # Syndicate each project
        for project in module.getProjects():  
            if not self.run.getGumpSet().inProjectSequence(project): continue               
            
            self.syndicateProject(project,moduleFeed)      
                  
        moduleFeed.serialize()        
    
    def syndicateProject(self,project,moduleFeed=None):
        
        feedFile=self.run.getOptions().getResolver().getFile(project,'atom','.xml',1)
        feedUrl=self.run.getOptions().getResolver().getUrl(project,'atom','.xml')
        projectUrl=self.run.getOptions().getResolver().getUrl(project)
        
        projectFeed=AtomFeed(feedUrl, feedFile,	\
                        'project',	\
                    'Apache Gump : Project ' + escape(project.getName()),	\
                    projectUrl,	\
                    escape(project.getDescription() or ''))
         
        #           
        # Get a decent description
        #
        content=self.getProjectContent(project,self.run)
                        
        #
        #
        entry=Entry(('%s %s') % (project.getName(),project.getStateDescription()), \
                  projectUrl, \
                  project.getModule().getName() + ":" + project.getName(),	\
                  content )

        # Generate changes, only if the project changed
        if project.getModule().isModified() and not project.getStatePair().isUnset():      
            log.debug("Add project to Atom Newsfeed for : " + project.getName())         
            projectFeed.addEntry(entry)
            if moduleFeed:
                moduleFeed.addEntry(entry)  

        # State changes that are newsworthy...
        if 	self.projectOughtBeWidelySyndicated(project) :
            log.debug("Add project to widely distributed Atom Newsfeed for : " + project.getName())    
            self.feed.addEntry(entry)
                                                        
        projectFeed.serialize()
