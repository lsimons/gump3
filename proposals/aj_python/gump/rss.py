#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/proposals/aj_python/gump/Attic/rss.py,v 1.1 2003/08/21 19:38:14 nickchalko Exp $
# $Revision: 1.1 $
# $Date: 2003/08/21 19:38:14 $
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

import re
import time
import urllib

from xml.sax.saxutils import escape
from xml.sax import parse
from xml.sax.handler import ContentHandler

###############################################################################

# Where to find the historical data
gumproot='http://cvs.apache.org/builds/gump/'

# Format of index files entries
summary=re.compile('<td>\s(\d\d:\d\d:\d\d)\s</td>\s' +
                   '<td.*?>\s<a href="(.*?)">([-\w]*)</a>\s</td>\s' +
                   '<td.*?>\s(\w+)\s</td>\s')

# Local time zone, in offset from GMT
TZ='%+.2d:00' % (-time.timezone/3600)

###############################################################################

# parse the gump data for a list of projects/modules, and the logdir
module={}
class Workspace(ContentHandler):
  logdir='.'
  def startElement(self, name, attrs):
    if name=='workspace':
      attrs=dict(attrs)
      if 'logdir' in attrs:
        Workspace.logdir=attrs['logdir']
    if name=='project':
      attrs=dict(attrs)
      if 'name' in attrs and 'module' in attrs:
        module[attrs['name']]=attrs['module']

parse(open(config.work),Workspace())

# update project summary based on a single days run
def analyze(file,pstat,date):
  print file
  index=urllib.urlopen(file).read()
  for (time, url, project, status) in summary.findall(index):
    if project not in pstat:
      pstat[project]=(date, time, status, url, project, 1) # first
    elif pstat[project][2]<>status: 
      pstat[project]=(date, time, status, url, project, 0) # non-first

# analyze all of the historical data
pstat={}
builds=urllib.urlopen(gumproot).read()
for date in re.findall('<a href="([\d-]*)/">',builds):
  analyze(gumproot+date,pstat,date)

# analyze today's run
today=time.strftime('%Y-%m-%d')
analyze(Workspace.logdir+'/index.html',pstat,today)

# order the values in reverse chronological order 
result=pstat.values()
result.sort()
result.reverse()

# dump the output in rss format
gumprss=open(Workspace.logdir + '/index.rss','w')
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

for (date,time,status,url,project,first) in result:
  if first: continue # not newsworthy
  if not project in module: continue # no longer relevant

  link = gumproot + date + '/' + url
  print link

  # read the details for the selected build
  if date==today:
    data=urllib.urlopen(Workspace.logdir+'/'+url).read()
  else:
    data=urllib.urlopen(link).read()

  # extract out only the relevant content
  content=re.split('</?XMP>',data)
  if len(content)<2: 
    content=(re.split('</?p>',data)+[''])[1]
  else:
    content=escape('\n'.join((content+[''])[1].splitlines()[-25:]))

  # write out the item to the rss feed
  gumprss.write("""
    <item>
      <title>%s %s %s</title>
      <link>%s</link>
      <description>&lt;pre&gt;%s&lt;/pre;&gt;</description>
      <dc:subject>%s</dc:subject>
      <dc:date>%sT%s%s</dc:date>
    </item>""" % (project,status,date, link, content, module[project], date,time,TZ))

# complete the rss feed
gumprss.write("""
  </channel>
</rss>
""")
gumprss.close()
