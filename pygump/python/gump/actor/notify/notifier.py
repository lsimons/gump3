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

    The 'Nag' (notification) e-mail generation Actor...
    
"""

import socket
import time
import os
import sys
import logging

from gump import log
from gump.core.config import *
from gump.core.run.gumprun import *
from gump.core.model.project import *
from gump.core.model.module import *
from gump.core.model.state import *
from gump.util import *

import gump.actor.notify.notification

class NotificationLogic(RunSpecific):
    
    def __init__(self,run):
        RunSpecific.__init__(self,run)
            
            # :TODO: First Ever?
            # :TODO What if M$ (i.e. not dbm) and/or no stats db
            
    def notification(self,entity):
        """
        Determine if a notification is appropriate, and
        generate it (the content)
        """
        
        notification=None
        
        # Stats had better have been set
        stats=entity.getStats()            
         
        #   
        # Determine if we want to notify, and if so
        # with what (Failure/Warning/Success)
        #
        if entity.isFailed():
            #
            # Notify on first failure, or each official
            # run.
            #
            if self.run.getOptions().isOfficial() \
                or (1 == stats.sequenceInState):                           
                notification=gump.actor.notify.notification.FailureNotification(self.run,entity)            
        elif entity.isSuccess():
            #
            # Notify on first success, after a failure.
            #
            #if (stats.sequenceInState == 1):            
            #    if not STATE_PREREQ_FAILED == stats.previousState:
            #        if stats.getTotalRuns() > 1:    
            #            notification=gump.actor.notify.notification.SuccessNotification(self.run,entity)
            #else:
                #
                # Notify on official if contains 'errors'.
                #
                if self.run.getOptions().isOfficial() and entity.containsRealNasties():
                    notification=gump.actor.notify.notification.WarningNotification(self.run,entity,' contains errors')   
                        
        #elif entity.isPrereqFailed():
        #    if (stats.sequenceInState == 1):            
        #        if not STATE_PREREQ_FAILED == stats.previousState:
        #            notification=PositiveNotification(self.run,entity)
                        
        return notification        

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
            stream=StringIO.StringIO()
   
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
        stream.write('The current state of this %s is \'%s\'' % (lower(type), self.entity.getStateDescription()))   
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
        if isinstance(stream,StringIO.StringIO):
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
                stream.write(' -%s- %s\n' % (upper(levelName(note.level)), note.text))
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
        stream.write('Produced by Gump version %s.\n' % setting.VERSION)
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
        
import socket
import time
import os
import sys
import logging

from string import lower, capitalize

from gump import log
from gump.core.config import *
from gump.core.run.gumprun import *
from gump.core.run.actor import AbstractRunActor
from gump.core.model.project import *
from gump.core.model.module import *
from gump.core.model.state import *
from gump.core.model.misc import AddressPair
from gump.util.smtp import *
from gump.util import *

from gump.actor.notify.logic import NotificationLogic
from gump.actor.notify.notification import Notification

LINE     ='--   --   --   --   --   --   --   --   --   --   --   --   G U M P'
SEPARATOR='*********************************************************** G U M P'

class Notifier(AbstractRunActor):
    
    def __init__(self,run,resolver=None):      
        
        AbstractRunActor.__init__(self,run)
        
        # Successful notifications
        self.sents=0
        
        # Unsuccesful
        self.unsent=''
        self.unsentSubjects=''
        self.unsents=0
        
        # Unwanted
        self.unwanted=''
        self.unwantedSubjects=''
        self.unwanteds=0
        
        self.resolver=self.options.getResolver()
        self.logic=NotificationLogic(self.run)
        
        self.id=0
                                  
    def processOtherEvent(self,event):    
        """
        
        At the end of the run...
        
        """
        if isinstance(event,FinalizeRunEvent):          
            self.processWorkspace()              
            
    def processWorkspace(self):
        """
        
        	Notify about the workspace (if it needs it)
        	
       	"""
        notification = self.logic.notification(self.workspace)
        if notification:
            self.notifyWorkspace(notification)   
         
        log.info('Notifications: Sent:%s Unsent:%s  Unwanted: %s' % \
                    (self.sents, self.unsents, self.unwanteds) )
         
        # Workspace can override...
        (wsTo, wsFrom) = self.workspace.getNotifyOverrides()        
                
        # Belt and braces (notify to us if not notify to them)
        if self._hasUnwanted():
            log.info('We have some unwanted\'s to send to list...')
            
            self.sendEmail(wsTo or self.workspace.administrator,wsFrom or self.workspace.email,
                        'BATCH: All dressed up, with nowhere to go...',
                        self._getUnwantedContent())
                        
            # A bit paranoid, ought just rely upon object being
            # destroyed,
            self.unwanted=''  
            self.unwantedSubjects=''
            self.unwanteds=0    
        else:
            log.debug('No unwanted notifys.')
                
        # Belt and braces (notify to us if not notify to them)
        if self._hasUnsent():
            log.info('We have some unsented\'s to send to list...')    
            self.sendEmail(wsTo or self.workspace.administrator,wsFrom or self.workspace.email,
                        'BATCH: Unable to send...',
                         self._getUnsentContent())
                        
            # A bit paranoid, ought just rely upon object being
            # destroyed,
            self.unsent=''
            self.unsentSubjects=''
            self.unsents=0
        else:
            log.debug('No unsent notifys.')
            
    def processModule(self,module):    
        """
            Notify about the module (if it needs it)
        """
        notification = self.logic.notification(module)
                
        if notification:
            try:
                log.info('Notify for module: ' + module.getName())
                         
                self.notifyModule(module,notification)   
                    
            except Exception, details:
                log.error("Failed to send notify e-mails for module " + module.getName()\
                                    + " : " + str(details), exc_info=1)
                                     
    def processProject(self,project):    
        """
            Notify about the project (if it needs it)
        """
        notification = self.logic.notification(project)
                
        if notification:
            try:
                log.info('Notify for project: ' + project.getName()) 
                self.notifyProject(project,notification)   
                    
            except Exception, details:
                log.error("Failed to send notify e-mails for project " + project.getName()\
                                    + " : " + str(details), exc_info=1)
 
    def _addUnwanted(self,subject,content):
        """
        	Add this notification to the 'unwanted' list, since
        	no addresses were found for it.
        """
        if self.unwanted:
            self.unwanted += SEPARATOR
            self.unwanted += '\n'
        self.unwanted += subject
        self.unwanted += '\n'
        self.unwanted += content
        self.unwanted += '\n'
        
        self.unwantedSubjects += subject + '\n'
        self.unwanteds += 1
    
    def _addUnsent(self,subject,content):
        """
            Add this notification to the 'unsent' list, since
            it failed to be sent.
        """    
        if self.unsent:
            self.unsent += SEPARATOR
            self.unsent += '\n'
        self.unsent += subject
        self.unsent += '\n'
        self.unsent += content
        self.unsent += '\n'
        
        self.unsentSubjects += subject + '\n'
        self.unsents += 1
        
    def getNextIdentifier(self):
        """
        Get's the next identifier.
        
        Note: Side effect, increments the identifier
        """
        self.id += 1 
        return self.id
        
    def _getUnwantedContent(self):
        """        
        Generate content for the batch of unwanted notifications.        
        """
        return self._getBatchContent(self.unwanteds,self.unwantedSubjects,self.unwanted)
             
    def _getUnsentContent(self):
        """        
        Generate content for the batch of unsent notifications.        
        """
        return self._getBatchContent(self.unsents,self.unsentSubjects,self.unsent)
             
    def _getBatchContent(self,count,subjects,batch):
        """
        Generate batch content
        """
        content = ''
        
        if count:
            plural=''
            if count > 0:
                plural='s'
                
            content = """Dear Gumpmeisters,
            
The following %s notify%s should have been sent

""" % (`count`, plural)
            
            content += SEPARATOR
            content += '\n'
            
            content += subjects
            
            content += SEPARATOR
            content += '\n'
            
            content += batch
            
        return content
            
    def _hasUnwanted(self):
        """
        Do we have any mails that should have been sent, but had nowhere to go?
        """
        if self.unwanted: return True
        return False
    
    def _hasUnsent(self):
        """
        Do we have any mails that failed to be sent?
        """
        if self.unsent: return True
        return False
    
    def notifyWorkspace(self,notification):
        """ Notify for the workspace """
        
        content=notification.resolveContent(self.resolver, self.getNextIdentifier())
        
        subject=self.workspace.prefix+': Gump Workspace ' + self.workspace.getName()
        
        self.sendEmail(self.workspace.administrator,
                        self.workspace.email,
                        subject,content)
    
    def notifyModule(self,module,notification):
        """ Notify to a specific module's <nag entries """
        
        # Form the content...
        content=notification.resolveContent(self.resolver, self.getNextIdentifier())
                
        # Form the subject
        subject=self.workspace.prefix+	\
                ': Module '+module.getName()+' '+	\
                lower(stateDescription(module.getState()))
                    
        if notification.isWarning():
            subject += ', but with warnings.'
            
        self.sendEmails(self.getAddressPairs(module),subject,content)
            
    
    def notifyProject(self,project,notification):
        """ Notify to a specific project's <nag entries """
        module=project.getModule()
    
        #
        # Form the content...
        #
        content=notification.resolveContent(self.resolver, self.getNextIdentifier())
                
        # Form the subject
        subject=self.workspace.prefix+': Project '+ project.getName()	\
            + ' (in module ' + module.getName() + ') ' \
            + lower(stateDescription(project.getState()))
            
        if notification.isWarning():
            subject += ', but with warnings.'
                    
        # Send those e-mails
        self.sendEmails(self.getAddressPairs(project),subject,content)
    
    def getAddressPairs(self, object):
        """
        	Get a list of notification to/from pair, overridding
        	them as needed (from the W/S).
        """
        notifys=[]
        
        # Workspace can override...
        (wsTo, wsFrom) = self.workspace.getNotifyOverrides()
        
        for pair in object.getNotifys():
            toaddr=wsTo or pair.getToAddress()
            fromaddr=wsFrom or pair.getFromAddress()
            notifys.append(AddressPair(toaddr,fromaddr))  

        return notifys
        
    def sendEmails(self, addressPairs, subject, content):
        """
        	Try to send them to interested parties
        	
        	Note: if nowhere to send, store them as 'unwanted'
        """
        if addressPairs:
            for pair in addressPairs:
                self.sendEmail(	pair.getToAddress(), 
                                pair.getFromAddress(),
                                subject, 
                                content)
        else:
            #
            # This is a catch-all, for all project that
            # don't have <notify's assigned.
            #
            self._addUnwanted(subject,content)
                    
    def sendEmail(self, toaddr, fromaddr, subject, content):
        """
        	Perform the SMTP send.	
        	If it fails, add the mail to the list of unsent
        """
        
        #
        # We send to a list, but a list of one is fine..
        #
        toaddrs=[ toaddr ]
    
        sent=False
        try:
            log.info('Send Notify To: ' + str(toaddr) + 
                ' From: ' + str(fromaddr) + ' Subject: ' + str(subject))
           
            # Form the user visible part ...
            email=EmailMessage( toaddrs, 
                                fromaddr, 
                                subject, 
                                content)       
                        
            #print '-------------------------------------------------------------------'
            #print 'To:' + `toaddr`
            #print 'From:' + `fromaddr`
            #print 'Subject:' + `subject`
            #print 'Server:' + `self.workspace.mailserver`
            #print 'e-mail:' + `email`    
            # Fire ...
            sent=mail(toaddrs,fromaddr,email,
                        self.workspace.mailserver,
                        self.workspace.mailport)  
                   
        except Exception, details:
            sent=False
            log.error('Failed to send notify e-mail: ' + str(details), exc_info=1)
                        
            # Add why unset along with content stored (and e-mailed) below.            
            content = 'Failed to send notify e-mail: ' + str(details) + '\n' + content
                  
        if not sent:
            content = 'Failed with to: ['+str(toaddr)+'] from: ['+str(fromaddr)+']\n' + content
            
            self._addUnsent(subject,content)                                        
            log.error('Failed with to: ['+str(toaddr)+'] from: ['+str(fromaddr)+']' )
        else:
            self.sents+=1                        
            
        return sent
