#!/usr/bin/env python

# $Header: /home/cvs/jakarta-gump/python/gump/rss.py,v 1.7 2003/09/11 21:11:42 ajack Exp $
# $Revision: 1.7 $
# $Date: 2003/09/11 21:11:42 $
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
        self.rssStream.write(('  <url>%s</url>\n') %(escape(self.url)))
        self.rssStream.write(('  <link>%s</link>\n') %(escape(self.link)))
        self.rssStream.write(('  <title>%s</title>\n') %(escape(self.title)))
            
        self.rssStream.write('  </image>\n')

class Item:
    def __init__(self,title,link,description,subject,date,url=None,image=None):
        self.title=title
        self.link=link
        self.description=description
        self.subject=subject
        self.date=date
        self.url=url
        self.image=image
        
    def serialize(self,rssStream):
        self.rssStream = rssStream       
        
        self.rssStream.write('   <item>\n')
        
        # Mandatory Fields
        self.rssStream.write(('    <title>Jakarta Gump: %s</title>\n') %(escape(self.title)))
        self.rssStream.write(('    <link>%s</link>\n') %(escape(self.link)))
        self.rssStream.write(('    <description>%s</description>\n') %(escape(self.description)))
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
        self.rssStream.write(('  <title>Jakarta Gump: %s</title>\n') %(escape(self.title)))
        self.rssStream.write(('  <link>%s</link>\n') %(escape(self.link)))
        self.rssStream.write(('  <description>%s</description>\n') %(escape(self.description)))
        
        # Optional Fields
        if self.image:
            self.image.serialize(self.rssStream)
        
        # Admin stuff
        self.rssStream.write("""
    <admin:generatorAgent rdf:resource="http://cvs.apache.org/viewcvs/jakarta-gump/python/gump/output/rss.py"/>
    <admin:errorReportsTo rdf:resource="mailto:gump@jakarta.apache.org"/>

    <sy:updateFrequency>1</sy:updateFrequency>
    <sy:updatePeriod>daily</sy:updatePeriod>
""")
            
    def endChannel(self):
        self.rssStream.write('  </channel>\n')
        
    def serialize(self,rssStream):
        self.rssStream = rssStream
        
        self.startChannel()
        
        # Serialize all items
        for item in self.items:
            item.serialize(self.rssStream)
            
        self.endChannel()
        
    def addItem(self,item):
        self.items.append(item)
    
class RSS:
    def __init__(self,file,channel=None):
        self.rssFile=file
        
        self.channels=[]
        
        if channel: self.addChannel(channel)

    def startRSS(self):
        self.rssStream.write("""<rss version="2.0"
  xmlns:admin="http://webns.net/mvcb/" 
  xmlns:dc="http://purl.org/dc/elements/1.1/" 
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
  xmlns:sy="http://purl.org/rss/1.0/modules/syndication/">""")
                
    def endRSS(self):                    
        # complete the rss feed
        self.rssStream.write('</rss>')
                
        log.info("RSS Newsfeed written to : " + self.rssFile);          
        
    def serialize(self):
        log.info("RSS Newsfeed to : " + self.rssFile);         
        self.rssStream = open(self.rssFile,'w')
        
        self.startRSS()
        
        for channel in self.channels:
            channel.serialize(self.rssStream)
        
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
           
class Syndicator:
    def __init__(self):
        pass
        
    def syndicate(self,run):
        
        # Main syndication document
        self.run = run
        self.workspace=run.getWorkspace()   
        self.rssFile=os.path.abspath(os.path.join(	\
                    self.workspace.logdir,'index.rss'))
    
        self.rss=RSS(self.rssFile,	\
            Channel(self.workspace.logurl,	\
                    'Jakarta Gump',		\
                    """Life is like a box of chocolates""", \
                Image('http://jakarta.apache.org/images/bench.png',	\
                    'Jakarta Gump', \
                    'http://jakarta.apache.org/')))
        
        # build information 
        for module in self.workspace.getModules():
            self.syndicateModule(module,self.rss)
            
        self.rss.serialize()
        
    def syndicateModule(self,module,mainRSS):
        
        rssFile=self.run.getOptions().getResolver().getFile(module,'index','.rss')
        moduleURL=self.run.getOptions().getResolver().getUrl(module)
        
        moduleRSS=RSS(rssFile,	\
            Channel(moduleURL,\
                    'Jakarta Gump : Module ' + escape(module.getName()),	\
                    escape(module.getDescription())))
        
        for project in module.getProjects():  
            self.syndicateProject(project,moduleRSS,mainRSS)      
                  
        moduleRSS.serialize()        
    
    def syndicateProject(self,project,moduleRSS,mainRSS):
                
        rssFile=self.run.getOptions().getResolver().getFile(project,project.getName(),'.rss')
        projectURL=self.run.getOptions().getResolver().getUrl(project)
        
        projectRSS=RSS(rssFile,	\
            Channel(projectURL,\
                    'Jakarta Gump : Project ' + escape(project.getName()),	\
                    escape(project.getDescription())))
                    
        s=project.getStats()
        datestr=time.strftime('%Y-%m-%d')
        timestr=time.strftime('%H%M')
                    
        content='Project ' + project.getName() \
                                + ' : ' \
                                + project.getStateDescription() \
                                + ' ' \
                                + project.getReasonDescription() \
                                + '\n\n'
                        
        content += 'Previous state: ' \
                                + stateName(s.previousState)  \
                                + '\n\n'
                     
        for note in project.annotations:
                content += ("   - " + str(note) + "\n")
                        
        item=Item(('%s %s %s') % (project.getName(),project.getStateDescription(),datestr), \
                  projectURL, \
                  content, \
                  project.getModule().getName() + ":" + project.getName(), \
                  ('%sT%s%s') % (datestr,timestr,TZ))

        projectRSS.addItem(item)
        moduleRSS.addItem(item)  

        # State changes that are newsworthy...
        if 	s.sequenceInState == 1	\
            and not s.currentState == STATE_PREREQ_FAILED \
            and not s.currentState == STATE_NONE \
            and not s.currentState == STATE_COMPLETE :       
            mainRSS.addItem(item)
                                                        
        projectRSS.serialize()
    
def syndicate(run):
    simple=Syndicator()
    simple.syndicate(run)