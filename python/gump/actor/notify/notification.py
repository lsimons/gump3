#!/usr/bin/env python
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

    A 'Nag' (notification) content.
    
"""

import socket
import time
import os
import sys
import logging
import types
import io

from gump import log
from gump.core.config import *
from gump.core.run.gumprun import *
from gump.core.run.actor import AbstractRunActor
from gump.core.model.project import *
from gump.core.model.module import *
from gump.core.model.state import *
from gump.util.smtp import *
from gump.util import *
from gump.util.work import *
from gump.util.note import *

LINE     ='--   --   --   --   --   --   --   --   --   --   --   --   G U M P'
SEPARATOR='*********************************************************** G U M P'

class Notification(RunSpecific):

    UNSET_TYPE=0
    SUCCESS_TYPE=1
    FAILURE_TYPE=2
    WARNING_TYPE=3    
    
    def __init__(self,run,entity,type=SUCCESS_TYPE,intro=''):   
        """
        	Create a notification (of success/failure/etc.)
        """
        
        RunSpecific.__init__(self,run)
        
        self.entity=entity
        self.type=type
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
        if self.intro: return True
        return False
        
    def isSuccess(self):
        return Notification.SUCCESS_TYPE == self.type
        
    def isFailure(self):
        return Notification.FAILURE_TYPE == self.type
        
    def isWarning(self):
        return Notification.WARNING_TYPE == self.type
        
    def resolveContent(self,resolver,id=None,stream=None):
        
        # If not passed, create temporary
        if not stream:
            stream=io.StringIO()
   
        if self.isSuccess():
            stream.write('To whom it may satisfy...')
        else:
            stream.write('To whom it may engage...')
        
        stream.write("""
        
This is an automated request, but not an unsolicited one. For 
more information please visit http://gump.apache.org/nagged.html, 
and/or contact the folk at general@gump.apache.org.

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
        
        if self.isFailure():        
            if affected:
                stream.write('.\nThis issue affects %s projects' % affected)
            
            if duration and duration > 1:
                stream.write(',\n and has been outstanding for %s runs' % duration)
        
        stream.write('.\n')
        
        # Add State (and reason)
        stream.write('The current state of this %s is \'%s\'' % (type.lower(), self.entity.getStateDescription()))   
        if self.entity.hasReason():
            stream.write(', with reason \'' + self.entity.getReasonDescription() + '\'')        
        stream.write('.\n')
        
        # Show those affected
        if affected:
            affectedProjects=self.entity.getAffectedProjects()
            if True or ((duration and duration > 3) and affectedProjects):
                # Show those negatively affected
                stream.write('For reference only, the following projects are affected by this:\n')
            
                for project in affectedProjects:
                    stream.write('    - ' + project.getName())
                    
                    if project.hasDescription():
                        stream.write(' :  ')
                        stream.write(project.getLimitedDescription())
                        
                    stream.write('\n')
            
                stream.write('\n')      
                                
        # Link them back here...
        url=resolver.getUrl(self.entity)
        stream.write('\nFull details are available at:\n    ')
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
            stream.write('\nThat said, some information snippets are provided here.\n')            
      
        if isinstance(self.entity,Annotatable):
            self.resolveAnnotations(resolver,stream)
            
        if isinstance(self.entity,Workable):
            self.resolveWork(resolver,stream)
            
        if isinstance(self.entity,Statable):
            self.resolveStats(resolver,stream)

        self.resolveSyndication(resolver, stream)
        
        self.resolveFooter(resolver, id, stream)
    
        # If passed (or created) a StringIO, return String
        # containing contents.
        if isinstance(stream,io.StringIO):
            stream.seek(0)
            return stream.read()      
      
        return
        
        
    def resolveAnnotations(self, resolver, stream):
        """
        Resolve any annotations on the entity
        """
          
        #
        # Add an info/error/etc...
        #
        if self.entity.annotations:
            stream.write("\n")
            stream.write("The following annotations (debug/informational/warning/error messages) were provided:")
            stream.write("\n")
            for note in self.entity.annotations:      
                stream.write(' -%s- %s\n' % (levelName(note.level).upper(), note.text))
            stream.write("\n")
        
    def resolveWork(self, resolver, stream):
        """
        Resolve any work entries on the entity
        """
              
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
        """
        Resolve any stats on the entity
        """          
        stats=self.entity.getStats()
        # :TODO:
        # stream.write('\n\n')
        
    def resolveSyndication(self, resolver, stream): 
        """
        Resolve syndication links on the entity
        """
        stream.write('To subscribe to this information via syndicated feeds:')
        stream.write('\n')
            
        # Link them back here...
        rssurl=resolver.getUrl(self.entity,'rss','.xml')
        atomurl=resolver.getUrl(self.entity,'atom','.xml')
            
        stream.write('- RSS: ' + rssurl + '\n')
        stream.write('- Atom: ' + atomurl + '\n')
        
    def resolveFooter(self, resolver, id, stream):        
        """
        Resolve footer (Gump identification information)
        """
        stream.write('\n============================== Gump Tracking Only ===\n')
        stream.write('Produced by Apache Gump(TM) version %s.\n' % setting.VERSION)
        stream.write('Gump Run %s, %s\n' %    \
                        (   default.datetime_s, self.run.getRunGuid() ))
        if id:
            stream.write('Gump E-mail Identifier (unique within run) #%s.\n' % id )
         
        #topurl=resolver.getUrl(self.run)
        #opturl=resolver.getUrl(self.run,'options')
        #stream.write(topurl)
        #stream.write('\n')
        #stream.write(opturl)
        #stream.write('\n')
        
class SuccessNotification(Notification):
    """
    	Congrats
    """
    def __init__(self,run,entity,intro=' *no longer* has an issue'):
        Notification.__init__(self,run,entity,Notification.SUCCESS_TYPE,intro)
        
class FailureNotification(Notification):
    """
        Opps...
    """
    def __init__(self,run,entity,intro=' has an issue affecting its community integration'):
        Notification.__init__(self,run,entity,Notification.FAILURE_TYPE,intro)

class WarningNotification(Notification):
    """
    	Hmmm....
    """
    def __init__(self,run,entity,intro=' has some issues'):
        Notification.__init__(self,run,entity,Notification.WARNING_TYPE,intro)
        
