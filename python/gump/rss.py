#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/Attic/rss.py,v 1.2 2003/08/29 00:20:22 ajack Exp $
# $Revision: 1.2 $
# $Date: 2003/08/29 00:20:22 $
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

from gump.context import *
from gump.statistics import StatisticsDB,ProjectStatistics

###############################################################################

# Where to find the historical data
gumproot='http://cvs.apache.org/builds/gump/'

# Local time zone, in offset from GMT
TZ='%+.2d:00' % (-time.timezone/3600)

###############################################################################

def rss(workspace,context):
    
    if not os.path.exists(workspace.logdir): os.mkdir(workspace.logdir)
    
    db=StatisticsDB()       
            
    gumprss=open(workspace.logdir + '/index.rss','w')
    gumprss.write("""<rss version="2.0"
  xmlns:admin="http://webns.net/mvcb/" 
  xmlns:dc="http://purl.org/dc/elements/1.1/" 
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
  xmlns:sy="http://purl.org/rss/1.0/modules/syndication/">

  <channel>
    <title>Gump</title>
    <link>http://jakarta.apache.org/gump/</link>
    <description>Life is like a box of chocolates</description>

    <admin:generatorAgent rdf:resource="http://cvs.apache.org/viewcvs/jakarta-gump/python/gumprss.py"/>
    <admin:errorReportsTo rdf:resource="mailto:gump@jakarta.apache.org"/>

    <sy:updateFrequency>1</sy:updateFrequency>
    <sy:updatePeriod>daily</sy:updatePeriod>""")
    
    
    for mctxt in context:
        if not STATUS_SUCCESS == mctxt.status:
            if Module.list.has_key(mctxt.name):
                module=Module.list[mctxt.name]
                for pctxt in mctxt:                            
                    s=db.getProjectStats(pctxt.name)
                    
                    # State changes that are newsworthy...
                    if not s.currentState == s.previousState \
                      and not s.currentState == STATUS_PREREQ_FAILURE \
                      and not s.currentState == STATUS_COMPLETE :
                        project=pctxt.project
                    
                        link = gumproot + '/' + mctxt.name + '/' + pctxt.name + 'index.html'                       
                        datestr=time.strftime('%Y-%m-%d')
                        timestr=time.strftime('%H%M')
                    
                        content='Testing....'
                    
                        # write out the item to the rss feed
                        gumprss.write("""
                            <item>
                              <title>%s %s %s</title>
                              <link>%s</link>
                              <description>&lt;pre&gt;%s&lt;/pre;&gt;</description>
                              <dc:subject>%s</dc:subject>
                              <dc:date>%sT%s%s</dc:date>
                            </item>""" % \
                          (pctxt.name,stateName(pctxt.status),datestr, link, content, module[project], datestr,timestr,TZ))
                        
    # complete the rss feed
    gumprss.write("""
      </channel>
    </rss>
    """)
    gumprss.close()                                            