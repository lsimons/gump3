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

from gump import log
from gump.model.state import *
from gump.output.statistics import ProjectStatistics

###############################################################################


# Local time zone, in offset from GMT
TZ='%+.2d:00' % (-time.timezone/3600)

###############################################################################

def rss(run):
    
    workspace=run.getWorkspace() 
            
    rssFile=os.path.abspath(os.path.join(workspace.logdir,'index.rss'))
    
    gumprss = open(rssFile,'w')
    gumprss.write(("""<rss version="2.0"
  xmlns:admin="http://webns.net/mvcb/" 
  xmlns:dc="http://purl.org/dc/elements/1.1/" 
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
  xmlns:sy="http://purl.org/rss/1.0/modules/syndication/">

  <channel>
    <title>Jakarta Gump : %s</title>
    <link>http://jakarta.apache.org/gump/</link>
    <description>Life is like a box of chocolates</description>

    <admin:generatorAgent rdf:resource="http://cvs.apache.org/viewcvs/jakarta-gump/python/gump/rss.py"/>
    <admin:errorReportsTo rdf:resource="mailto:gump@jakarta.apache.org"/>

    <sy:updateFrequency>1</sy:updateFrequency>
    <sy:updatePeriod>daily</sy:updatePeriod>""") % \
        ( workspace.prefix ) )
        
    for module in workspace.getModules():
        if not module.isSuccess():
                for project in module.getProjects():                            
                
                    s=project.getStats()
                    
                    # State changes that are newsworthy...
                    if 	s.sequenceInState == 1	\
                        and not s.currentState == STATE_PREREQ_FAILED \
                        and not s.currentState == STATE_NONE \
                        and not s.currentState == STATE_COMPLETE :
                            
                        log.info("RSS written for " + project.getName()); 
    
                        link = workspace.logurl + '/' + gumpSafeName(module.getName()) + '/' + gumpSafeName(project.getName()) + '.html'                       
                        datestr=time.strftime('%Y-%m-%d')
                        timestr=time.strftime('%H%M')
                    
                        content='Project ' + project.getName() \
                                + ' : ' \
                                + project.getStateDescription() \
                                + ' ' \
                                + project.getReasonDescription() \
                                + "\n\n"
                        
                        content += 'Previous state: ' \
                                + stateName(s.previousState)  \
                                + "\n\n"
                     
                        for note in project.annotations:
                            content += ("   - " + str(note) + "\n")
                        
                        # write out the item to the rss feed
                        gumprss.write("""
                            <item>
                              <title>%s %s %s</title>
                              <link>%s</link>
                              <description>&lt;pre&gt;%s&lt;/pre;&gt;</description>
                              <dc:subject>%s</dc:subject>
                              <dc:date>%sT%s%s</dc:date>
                            </item>""" % \
                          (project.getName(),project.getStateDescriptionus(),datestr, link, \
                               content, \
                               module.getName() + ":" + project.getName(), \
                               datestr,timestr,TZ))
                        
    # complete the rss feed
    gumprss.write("""
      </channel>
    </rss>
    """)
    gumprss.close()                                 
    
    log.info("RSS Newsfeed written to : " + rssFile);          
    
    return rssFile 
    
