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

    'Nag' (notification) e-mail generation...
    
"""

import socket
import time
import os
import sys
import logging
import types
import StringIO

from string import lower, upper, capitalize

from gump import log
from gump.core.config import *
from gump.core.gumprun import *
from gump.core.actor import AbstractRunActor
from gump.model.project import *
from gump.model.module import *
from gump.model.state import *
from gump.utils.smtp import *
from gump.utils import *

LINE     ='--   --   --   --   --   --   --   --   --   --   --   --   G U M P'
SEPARATOR='*********************************************************** G U M P'


class Notification(RunSpecific):
    
    def __init__(self,run,entity,positive=0,intro=''):      
        RunSpecific.__init__(self,run)
        
        self.entity=entity
        self.positive=positive
        self.intro=intro
        
        # Init
        self.title=''
        
    def setTitle(self,message):
        self.title=title
        
    def getTitle(self):
        return self.title
        
    def setIntroduction(self,message):
        self.intro=intro
        
    def getIntroduction(self):
        return self.intro
        
    def hasIntroduction(self):
        if self.intro: return 1
        return 0
        
    def resolveContent(self,resolver,stream=None):
        
        # If not passed, create temporary
        if not stream:
            stream=StringIO.StringIO()
   
        if self.positive:
            stream.write('To whom it may satisfy...')
        else:
            stream.write('To whom it may engage...')
        
        stream.write("""
        
This is an automated request, but not an unsolicited one. For 
more information please visit http://gump.apache.org/nagged.html, 
and/or contact folk at general@gump.apache.org.

""")
    
        # Get our facts straight.
        name=self.entity.getName()
        type=self.entity.__class__.__name__
        affected=0        
        if isinstance(self.entity,Project):
            affected=self.entity.countAffectedProjects()
        duration=self.entity.getStats().sequenceInState        
                    
        stream.write(type + ' ' + name)
        
        if self.hasIntroduction():
            stream.write(self.getIntroduction())
        
        if not self.positive:        
            if affected:
                stream.write('.\nThis issue affects ' + `affected` + ' projects')
            
            if duration and duration > 1:
                stream.write(', and has been outstanding for ' + `duration` + ' runs')
        
        stream.write('.\n')
        
        # Add State (and reason)
        stream.write(type + ' State : \'' + self.entity.getStateDescription() + '\'')
    
        if self.entity.hasReason():
            stream.write(', Reason \'' + self.entity.getReasonDescription() + '\'')
        
        stream.write("\n")
        
        # Show those affected
        if affected:
            affectedProjects=self.entity.getAffectedProjects()
            if True or ((duration and duration > 3) and affectedProjects):
                # Show those negatively affected
                stream.write('The following are affected:\n')
            
                for project in affectedProjects:
                    stream.write('    - ' + project.getName())
                    
                    if project.hasDescription():
                        stream.write(' :  ')
                        stream.write(project.getLimitedDescription())
                        
                    stream.write('\n')
            
                stream.write('\n')      
                                
        # Link them back here...
        url=resolver.getUrl(self.entity)
        stream.write('\nFull details are available at:\n\n    ')
        stream.write(url)
        stream.write('\n')
        
        snippets=0        
        if isinstance(self.entity,Annotatable):
            if self.entity.annotations:
                snippets=1
        if isinstance(self.entity,Workable):
            if self.entity.worklist:
                snippets=1
            
        if snippets:
            stream.write('\nThat said, some snippets follow:\n')
            
        stream.write('\n')
      
        if isinstance(self.entity,Annotatable):
            self.resolveAnnotations(resolver,stream)
            
        if isinstance(self.entity,Workable):
            self.resolveWork(resolver,stream)
            
        if isinstance(self.entity,Statable):
            self.resolveStats(resolver,stream)

        self.resolveSyndication(resolver, stream)
        
        self.resolveFooter(resolver, stream)
    
        # If passed (or created) a StringIO, return String
        # containing contents.
        if isinstance(stream,StringIO.StringIO):
            stream.seek(0)
            return stream.read()      
      
        return
        
        
    def resolveAnnotations(self, resolver, stream):
          
        #
        # Add an info/error/etc...
        #
        if self.entity.annotations:
            stream.write("\n")
            stream.write("The following annotations were provided:")
            stream.write("\n")
            for note in self.entity.annotations:      
                stream.write(' -%s- %s\n' % (upper(levelName(note.level)), note.text))
        
    def resolveWork(self, resolver, stream):
    
        #
        # Work
        #
        if self.entity.worklist: 
            stream.write('\n\n')
            stream.write('The following work was performed:\n')
            for workitem in self.entity.worklist:
                workurl=resolver.getUrl(workitem)
                stream.write(workurl)
                stream.write('\n')
                stream.write(workitem.overview())
                stream.write('\n')
    
        
    def resolveStats(self, resolver, stream):
        stats=self.entity.getStats()
        stream.write('\n\n')
        
    def resolveSyndication(self, resolver, stream):
        
        stream.write('\n')
        stream.write('To subscribe to this information via syndicated feeds:')
        stream.write('\n')
            
        #
        # Link them back here...
        #
        rssurl=resolver.getUrl(self.entity,'rss','.xml')
        atomurl=resolver.getUrl(self.entity,'atom','.xml')
            
        stream.write(' RSS: ' + rssurl + '\n')
        stream.write(' Atom: ' + atomurl + '\n')
        
    def resolveFooter(self, resolver, stream):
        
        stream.write('\n\n--\n')
        stream.write('Produced by Gump %s.\n[Run (%s, %s)]' %	\
                        (	setting.version, 
                            default.datetime, 
                            self.run.getRunGuid() ))
        stream.write('\n')

        topurl=resolver.getUrl(self.run)
        opturl=resolver.getUrl(self.run,'options')
        stream.write(topurl)
        stream.write('\n')
        stream.write(opturl)
        stream.write('\n')
        
class PositiveNotification(Notification):
    def __init__(self,run,entity,intro=' *no longer* has an issue'):
        Notification.__init__(self,run,entity,1,intro)
        
class NegativeNotification(Notification):
    def __init__(self,run,entity,intro=' has an issue affecting its community integration'):
        Notification.__init__(self,run,entity,0,intro)
        