#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/syndication/atom.py,v 1.3 2004/01/07 18:12:50 ajack Exp $
# $Revision: 1.3 $
# $Date: 2004/01/07 18:12:50 $
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
  Highly experimental Atom feeds.
"""

import os
from time import strftime, gmtime

from xml.sax.saxutils import escape

from gump import log
from gump.model.state import *
from gump.model.project import ProjectStatistics

from gump.config import setting

from gump.syndication.syndicator import Syndicator

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
     
    def serializeToStream(self, stream, modified):
        
        # Write the header part...
        stream.write("""		<entry>
        <title>%s</title>
        <link rel="alternate" type="text/html" href="%s"/>
        <modified>%s</modified>        
        """	\
        % (self.description, self.link, modified) )

        if self.content:
            stream.write("""<content>%s</content>"""	\
            % (escape(self.content)) )
            
        # Write the trailer part...
        stream.write("""		</entry>\n""")
        
class AtomFeed:
    
    def __init__(self,url,file,title,link,description):
        self.url=url
        self.file=file
        self.title=title
        self.link=link
        self.description=description
        
        self.entries=[]
        
    def addEntry(self,entry):
        self.entries += entry
        
    def serializeToStream(self, stream, modified):
        
        # Write the header part...
        stream.write("""<?xml version="1.0" encoding="utf-8"?>
<feed version="0.3" xmlns="http://purl.org/atom/ns#">
        <title>%s</title>
        <link rel="alternate" type="text/html" href="%s"/>
        <modified>%s</modified>        
"""	% (self.description, self.link, modified) )
        
        for entry in self.entries:
            entry.serializeToStream(stream, modified)
        
        # Write the trailer part...
        stream.write("""
</feed>
""")
                
    def serialize(self):
        log.info("Atom Feed to : " + self.file);         
        
        stream = open(self.file,'w')
        
        modified=time.strftime('%Y-%m-%dT%H:%M:%SZ', gmtime())
        
        self.serializeToStream(stream,modified)
            
        # Close the file.
        stream.close()  
        
class AtomSyndicator(Syndicator):
    def __init__(self):
        Syndicator.__init__(self)
        
    def syndicate(self,run):
        
        # Main syndication document
        self.run = run
        self.workspace=run.getWorkspace()   
        
        feedFile=self.run.getOptions().getResolver().getFile(self.workspace,'index','.atom')      
        feedUrl=self.run.getOptions().getResolver().getUrl(self.workspace,'index','.atom')
    
        self.feed=AtomFeed(feedUrl,feedFile,	\
                       'Jakarta Gump',		\
                        self.workspace.logurl,	\
                        """Life is like a box of chocolates""")
                    
        # build information 
        for module in self.workspace.getModules():
            self.syndicateModule(module,self.feed)
            
        self.feed.serialize()
            
        
    def syndicateModule(self,module,mainFeed):
                
        feedFile=self.run.getOptions().getResolver().getFile(module,'index','.atom')
        feedUrl=self.run.getOptions().getResolver().getUrl(module,'index','.atom')
        moduleUrl=self.run.getOptions().getResolver().getUrl(module)
        
        moduleFeed=AtomFeed(feedUrl,feedFile,	
                        'Gump : Module ' + escape(module.getName()),	\
                        moduleUrl,	\
                        escape(module.getDescription()))
                    
         
        #           
        # Get a decent description
        #
        content=self.getModuleContent(module,self.run)
                        
        #
        #
        #
        entry=Entry(('%s %s') % (module.getName(),module.getStateDescription()), \
                  moduleUrl, \
                  module.getName(), \
                  content)
        
        # Generate changes, only if the module had changed
        if module.isUpdated():
            if not s.currentState == STATE_NONE and	\
                not s.currentState == STATE_UNSET:   
                moduleFeed.addEntry(entry)  
            
        # State changes that are newsworthy...
        if 	self.moduleOughtBeWidelySyndicated(module):            
            mainFeed.addEntry(entry)
            
        # Syndicate each project
        for project in module.getProjects():  
            self.syndicateProject(project,moduleFeed,mainFeed)      
                  
        moduleFeed.serialize()        
    
    def syndicateProject(self,project,moduleFeed,mainFeed):
        
        feedFile=self.run.getOptions().getResolver().getFile(project,project.getName(),'.atom')
        feedUrl=self.run.getOptions().getResolver().getUrl(project,'index','.atom')
        projectUrl=self.run.getOptions().getResolver().getUrl(project)
        
        projectFeed=AtomFeed(feedUrl, feedFile,	\
                    'Gump : Project ' + escape(project.getName()),	\
                    projectUrl,	\
                    escape(project.getDescription()))
         
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
        if project.getModule().isUpdated() and not project.getStatePair().isUnset():            
            projectFeed.addEntry(entry)
            moduleFeed.addEntry(entry)  

        # State changes that are newsworthy...
        if 	self.projectOughtBeWidelySyndicated(project) :
            mainFeed.addEntry(entry)
                                                        
        projectFeed.serialize()