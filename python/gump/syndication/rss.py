#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/syndication/rss.py,v 1.20 2004/04/16 17:28:43 ajack Exp $
# $Revision: 1.20 $
# $Date: 2004/04/16 17:28:43 $
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
  Highly experimental RSS feeds.
"""

import os
import time

from xml.sax.saxutils import escape

from gump import log
from gump.model.state import *
from gump.model.project import ProjectStatistics

from gump.core.config import setting

from gump.syndication.syndicator import Syndicator

###############################################################################


# Local time zone, in offset from GMT
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
        self.rssStream.write(('  <title>Gump: %s</title>\n') %(escape(self.title)))
        self.rssStream.write(('  <link>%s</link>\n') %(escape(self.link)))
        self.rssStream.write(('  <description>%s</description>\n') %(escape(self.description)))
        
        self.rssStream.write('  <language>en-us</language>\n')
        self.rssStream.write('  <copyright>Copyright 2003, Apache Software Foundation</copyright>\n')
        self.rssStream.write(('  <generator>Jakarta Gump : %s</generator>\n') % (escape(setting.version)))
        self.rssStream.write('  <webMaster>general@gump.apache.org</webMaster>\n')
        self.rssStream.write('  <docs>http://blogs.law.harvard.edu/tech/rss</docs>\n')
        self.rssStream.write('  <category domain="http://www.apache.org/namespaces">Gump</category>\n')
                
        # Optional Fields
        if self.image:
            self.image.serialize(self.rssStream)
        
        # Admin stuff
        self.rssStream.write("""
    <gump:version>%s</gump:version>
    
    <admin:errorReportsTo rdf:resource="mailto:general@gump.apache.org"/>

    <sy:updateFrequency>1</sy:updateFrequency>
    <sy:updatePeriod>daily</sy:updatePeriod>
""" % setting.version)
            
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
        log.debug("RSS Newsfeed written to : " + self.rssFile);          
        
    def serialize(self):
        log.debug("RSS Newsfeed to : " + self.rssFile);         
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
           
class RSSSyndicator(Syndicator):
    def __init__(self):
        Syndicator.__init__(self)
        self.gumpImage=Image('http://gump.apache.org/images/bench.png',	\
                    'Apache Gump', \
                    'http://gump.apache.org/')
        
    def syndicate(self,run):
        
        # Main syndication document
        self.run = run
        self.workspace=run.getWorkspace()   
        self.rssFile=self.run.getOptions().getResolver().getFile(self.workspace,'rss','.xml',1)      
        self.rssUrl=self.run.getOptions().getResolver().getUrl(self.workspace,'rss','.xml')
    
        self.rss=RSS(self.rssUrl,self.rssFile,	\
            Channel('Jakarta Gump',		\
                    self.workspace.logurl,	\
                    """Life is like a box of chocolates""", \
                self.gumpImage))
        
        # build information 
        for module in self.workspace.getModules():
            self.syndicateModule(module,self.rss)
            
        self.rss.serialize()
    
    def syndicateModule(self,module,mainRSS):
        
        rssFile=self.run.getOptions().getResolver().getFile(module,'rss','.xml',1)
        rssUrl=self.run.getOptions().getResolver().getUrl(module,'rss','.xml')
        moduleUrl=self.run.getOptions().getResolver().getUrl(module)
        
        moduleRSS=RSS(rssUrl,rssFile,	\
            Channel('Gump : Module ' + escape(module.getName()),	\
                    moduleUrl,	\
                    escape(module.getDescription()), \
                    self.gumpImage))
                    
        datestr=time.strftime('%Y-%m-%d')
        timestr=time.strftime('%H:%M:%S')
         
        #           
        # Get a decent description
        #
        content=self.getModuleContent(module,self.run)
                        
        #
        #
        #
        item=Item(('%s %s') % (module.getName(),module.getStateDescription()), \
                  moduleUrl, \
                  content, \
                  module.getName(), \
                  ('%sT%s%s') % (datestr,timestr,TZ))
        
        # Generate changes, only if the module had changed
        if module.isUpdated() and not module.getStatePair().isUnset(): 
            log.debug("Add module to RSS Newsfeed for : " + module.getName())    
            moduleRSS.addItem(item)  
            
        # State changes that are newsworthy...
        if 	self.moduleOughtBeWidelySyndicated(module):
            log.debug("Add module to widely distributed RSS Newsfeed for : " + module.getName())
            mainRSS.addItem(item)
            
        for project in module.getProjects():  
            self.syndicateProject(project,moduleRSS,mainRSS)      
                  
        moduleRSS.serialize()        
    
    def syndicateProject(self,project,moduleRSS,mainRSS):
                
        rssFile=self.run.getOptions().getResolver().getFile(project,'rss','.xml',1)
        rssUrl=self.run.getOptions().getResolver().getUrl(project,'rss','.xml')
        projectUrl=self.run.getOptions().getResolver().getUrl(project)
        
        projectRSS=RSS(rssUrl, rssFile,	\
            Channel('Gump : Project ' + escape(project.getName()),	\
                    projectUrl,	\
                    escape(project.getDescription()), \
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
        if project.getModule().isUpdated() and not project.getStatePair().isUnset():    
            log.debug("Add project to RSS Newsfeed for : " + project.getName())
            projectRSS.addItem(item)
            moduleRSS.addItem(item)  

        # State changes that are newsworthy...
        if self.projectOughtBeWidelySyndicated(project) :      
            log.debug("Add project to widely distributed RSS Newsfeed for : " + project.getName())
            mainRSS.addItem(item)
                                                        
        projectRSS.serialize()