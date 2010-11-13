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
  
    RSS feeds.
  
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


# Local time zone, in offset from UTC
TZ='%+.2d:00' % (-time.timezone/3600)

###############################################################################

class Image:
    def __init__(self,url,title,link):
        self.url=url    
        self.title=title
        self.link=link
                
    def startItem(self):
        self.rssStream.write('   <image>\n')
        
        # Mandatory Fields
        self.rssStream.write(('  <url>%s</url>\n') %(escape(self.url)))
        self.rssStream.write(('  <link>%s</link>\n') %(escape(self.link)))
        self.rssStream.write(('  <title>%s</title>\n') %(escape(self.title)))
            
    def endItem(self):
        self.rssStream.write('  </image>\n')
        
    def serialize(self,rssStream):
        self.rssStream = rssStream
        
        self.rssStream.write('   <image>\n')
        
        # Mandatory Fields
        self.rssStream.write(('    <url>%s</url>\n') %(escape(self.url)))
        self.rssStream.write(('    <link>%s</link>\n') %(escape(self.link)))
        self.rssStream.write(('    <title>%s</title>\n') %(escape(self.title)))
            
        self.rssStream.write('   </image>\n')

class Item:
    def __init__(self,title,link,description,subject,date,url=None,image=None):
        self.title=title
        self.link=link
        self.description=description
        self.subject=subject
        self.date=date
        self.url=url
        self.image=image
        
    def serialize(self,rssStream,rssUrl):
        self.rssStream = rssStream    
        self.rssUrl=rssUrl   
        
        self.rssStream.write('   <item>\n')
        
        # Tag on description
#        tagOn=("""
#        <a href="http://feedvalidator.org/check?url=%s">
#            <img align="right" src="http://feedvalidator.org/images/valid-rss.png" 
#                alt="[Valid RSS]" title="Validate my RSS feed" width="88" height="31" />
#        </a><br clear='ALL'><hr>""") % (self.rssUrl)
        
        # Mandatory Fields
        self.rssStream.write(('    <title>%s</title>\n') %(escape(self.title)))
        self.rssStream.write(('    <link>%s</link>\n') %(escape(self.link)))
        self.rssStream.write(('    <description>%s</description>\n') \
                %(escape(self.description)))
# Not yet                
#        self.rssStream.write(('    <description>%s%s</description>\n') \
#               %(escape(self.description),escape(tagOn)))
        self.rssStream.write('    <author>general@gump.apache.org</author>\n')                
        
        self.rssStream.write(('      <dc:subject>%s</dc:subject>\n') %(escape(self.subject)))
        self.rssStream.write(('      <dc:date>%s</dc:date>\n') %(escape(self.date)))
        
        # Optional Fields
        if self.image:
            self.rssStream.write(('  <image>%s</image>\n') %(escape(self.image)))
        if self.url:
            self.rssStream.write(('  <url>%s</url>\n') %(escape(self.url)))
            
        self.rssStream.write('  </item>\n')
    
class Channel:
    def __init__(self,title,link,description,image=None):
        self.title=title
        self.link=link
        self.description=description
        self.image=image
        
        self.items=[]
            
        
    def startChannel(self): 
        
        self.rssStream.write('  <channel>\n')
        
        # Mandatory Fields
        self.rssStream.write(('  <title>Apache Gump(TM): %s</title>\n') %(escape(self.title)))
        self.rssStream.write(('  <link>%s</link>\n') %(escape(self.link)))
        self.rssStream.write(('  <description>%s</description>\n') %(escape(self.description)))
        
        self.rssStream.write('  <language>en-us</language>\n')
        self.rssStream.write('  <copyright>Copyright 2003, Apache Software Foundation</copyright>\n')
        self.rssStream.write(('  <generator>Apache Gump : %s</generator>\n') % (escape(setting.VERSION)))
        self.rssStream.write('  <webMaster>general@gump.apache.org</webMaster>\n')
        self.rssStream.write('  <docs>http://blogs.law.harvard.edu/tech/rss</docs>\n')
        self.rssStream.write('  <category domain="http://www.apache.org/namespaces">Apache Gump</category>\n')
                
        # Optional Fields
        if self.image:
            self.image.serialize(self.rssStream)
        
        # Admin stuff
        self.rssStream.write("""
    <gump:version>%s</gump:version>
    
    <admin:errorReportsTo rdf:resource="mailto:general@gump.apache.org"/>

    <sy:updateFrequency>1</sy:updateFrequency>
    <sy:updatePeriod>daily</sy:updatePeriod>
""" % setting.VERSION)
            
    def endChannel(self):
        self.rssStream.write('  </channel>\n')
        
    def serialize(self,rssStream,rssUrl):
        self.rssStream = rssStream
        self.rssUrl=rssUrl
        
        self.startChannel()
        
        # Serialize all items
        for item in self.items:
            item.serialize(self.rssStream,self.rssUrl)
            
        self.endChannel()
        
    def addItem(self,item):
        self.items.append(item)
    
class RSS:
    def __init__(self,url,file,channel=None):
        self.rssUrl=url
        self.rssFile=file
        
        self.channels=[]
        
        if channel: self.addChannel(channel)

    def startRSS(self):
        self.rssStream.write("""<rss version="2.0"
  xmlns:gump="http://gump.apache.org/" 
  xmlns:admin="http://webns.net/mvcb/" 
  xmlns:dc="http://purl.org/dc/elements/1.1/" 
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
  xmlns:sy="http://purl.org/rss/1.0/modules/syndication/">""")
                
    def endRSS(self):                    
        # complete the rss feed
        self.rssStream.write('</rss>\n')                
        #log.info("RSS Newsfeed written to : " + self.rssFile);          
        
    def serialize(self):
        #log.info("RSS Newsfeed to : " + self.rssFile);         
        self.rssStream = open(self.rssFile,'w')
        
        self.startRSS()
        
        for channel in self.channels:
            channel.serialize(self.rssStream,self.rssUrl)
        
        self.endRSS()
        
        # Close the file.
        self.rssStream.close()  
  
    def addChannel(self,channel):
        self.channels.append(channel)
        
    def getCurrentChannel(self):
        return self.channels[len(self.channels)-1]
        
    def addItem(self,item,channel=None):
        if not channel: channel = self.getCurrentChannel()
        channel.addItem(item)
           
class RSSSyndicator(AbstractSyndicator):
    def __init__(self,run):
        AbstractSyndicator.__init__(self,run)
        self.gumpImage=Image('http://gump.apache.org/images/bench.png',	\
                    'Apache Gump', \
                    'http://gump.apache.org/')
        
    def prepareRun(self):
        
        # Main syndication document
        self.workspace=self.run.getWorkspace()   
        self.rssFile=self.run.getOptions().getResolver().getFile(self.workspace,'rss','.xml',1)      
        self.rssUrl=self.run.getOptions().getResolver().getUrl(self.workspace,'rss','.xml')
    
        self.rss=RSS(self.rssUrl,self.rssFile,	\
            Channel('Apache Gump',		\
                    self.workspace.getLogUrl(),	\
                    """Life is like a box of chocolates""", \
                self.gumpImage))
       
    def completeRun(self):
        self.rss.serialize()
    
    def syndicateModule(self,module):
        
        rssFile=self.run.getOptions().getResolver().getFile(module,'rss','.xml',1)
        rssUrl=self.run.getOptions().getResolver().getUrl(module,'rss','.xml')
        moduleUrl=self.run.getOptions().getResolver().getUrl(module)
        
        moduleRSS=RSS(rssUrl,rssFile,	\
            Channel('Apache Gump : Module ' + escape(module.getName()),	\
                    moduleUrl,	\
                    escape(module.getDescription() or ''), \
                    self.gumpImage))
                    
        datestr=time.strftime('%Y-%m-%d')
        timestr=time.strftime('%H:%M:%S')
         
        # Get a decent description
        content=self.getModuleContent(module,self.run)
                        
        # Create the item
        item=Item(('%s %s') % (module.getName(),module.getStateDescription()), \
                  moduleUrl, \
                  content, \
                  module.getName(), \
                  ('%sT%s%s') % (datestr,timestr,TZ))
        
        # Generate changes, only if the module had changed
        if module.isModified() and not module.getStatePair().isUnset(): 
            log.debug("Add module to RSS Newsfeed for : " + module.getName())    
            moduleRSS.addItem(item)  
            
        # State changes that are newsworthy...
        if 	self.moduleOughtBeWidelySyndicated(module):
            log.debug("Add module to widely distributed RSS Newsfeed for : " + module.getName())
            self.rss.addItem(item)
            
        for project in module.getProjects():  
            if not self.run.getGumpSet().inProjectSequence(project): continue               
            
            self.syndicateProject(project,moduleRSS)      
                  
        moduleRSS.serialize()        
    
    def syndicateProject(self,project,moduleRSS=None):
                
        rssFile=self.run.getOptions().getResolver().getFile(project,'rss','.xml',1)
        rssUrl=self.run.getOptions().getResolver().getUrl(project,'rss','.xml')
        projectUrl=self.run.getOptions().getResolver().getUrl(project)
        
        projectRSS=RSS(rssUrl, rssFile,	\
            Channel('Apache Gump : Project ' + escape(project.getName()),	\
                    projectUrl,	\
                    escape(project.getDescription() or ''), \
                    self.gumpImage))
                    
        datestr=time.strftime('%Y-%m-%d')
        timestr=time.strftime('%H:%M:%S')
         
        #           
        # Get a decent description
        #
        content=self.getProjectContent(project,self.run)
                        
        #
        #
        item=Item(('%s %s') % (project.getName(),project.getStateDescription()), \
                  projectUrl, \
                  content, \
                  project.getModule().getName() + ":" + project.getName(), \
                  ('%sT%s%s') % (datestr,timestr,TZ))

        # Generate changes, only if the module changed
        if project.getModule().isModified() and not project.getStatePair().isUnset():    
            log.debug("Add project to RSS Newsfeed for : " + project.getName())
            projectRSS.addItem(item)
            if moduleRSS: 
                moduleRSS.addItem(item)  

        # State changes that are newsworthy...
        if self.projectOughtBeWidelySyndicated(project) :      
            log.debug("Add project to widely distributed RSS Newsfeed for : " + project.getName())
            self.rss.addItem(item)
                                                        
        projectRSS.serialize()
