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

from string import lower, capitalize

from gump import log
from gump.core.config import *
from gump.core.gumprun import *
from gump.core.actor import AbstractRunActor
from gump.model.project import *
from gump.model.module import *
from gump.model.state import *
from gump.model.misc import AddressPair
from gump.utils.smtp import *
from gump.utils import *

from gump.notify.logic import NotificationLogic
from gump.notify.notification import Notification

LINE     ='--   --   --   --   --   --   --   --   --   --   --   --   G U M P'
SEPARATOR='*********************************************************** G U M P'

class Notifier(AbstractRunActor):
    
    def __init__(self,run,resolver=None):      
        
        AbstractRunActor.__init__(self,run)
        
        self.unsent=''
        self.unsentSubjects=''
        self.unsents=0
        
        self.unwanted=''
        self.unwantedSubjects=''
        self.unwanteds=0
        
        self.resolver=self.options.getResolver()
        self.logic=NotificationLogic(self.run)
        
        self.id=0
                                        
    def processWorkspace(self):
        """
        	Notify about the workspace (if it needs it)
       	"""
        notification = self.logic.notification(self.workspace)
        if notification:
            self.notifyWorkspace(notification)   
         
        # Workspace can override...
        (wsTo, wsFrom) = self.workspace.getNotifyOverrides()        
                
        # Belt and braces (notify to us if not notify to them)
        if self.hasUnwanted():
            log.info('We have some unwanted\'s to send to list...')
            
            self.sendEmail(wsTo or self.workspace.mailinglist,wsFrom or self.workspace.email,    \
                        'BATCH: All dressed up, with nowhere to go...',\
                        self.getUnwantedContent())
                        
            # A bit paranoid, ought just rely upon object being
            # destroyed,
            self.unwanted=''  
            self.unwantedSubjects=''
            self.unwanteds=0    
        else:
            log.debug('No unwanted notifys.')
                
        # Belt and braces (notify to us if not notify to them)
        if self.hasUnsent():
            log.info('We have some unsented\'s to send to list...')    
            self.sendEmail(wsTo or self.workspace.mailinglist,wsFrom or self.workspace.email,    \
                        'BATCH: Unable to send...',\
                         self.getUnsentContent())
                        
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
 
    def addUnwanted(self,subject,content):
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
    
    def addUnsent(self,subject,content):
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
        self.id += 1 
        return self.id
        
    def getUnwantedContent(self):
        return self.getBatchContent(self.unwanteds,self.unwantedSubjects,self.unwanted)
             
    def getUnsentContent(self):
        return self.getBatchContent(self.unsents,self.unsentSubjects,self.unsent)
             
    def getBatchContent(self,count,subjects,batch):
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
            
    def hasUnwanted(self):
        if self.unwanted: return 1
        return 0
    
    def hasUnsent(self):
        if self.unsent: return 1
        return 0
    
    def notifyWorkspace(self,notification):
        """ Notify for the workspace """
        
        content=notification.resolveContent(self.resolver, self.getNextIdentifier())
        
        subject=self.workspace.prefix+': Gump Workspace ' + self.workspace.getName()
        
        self.sendEmail(self.workspace.mailinglist,
                        self.workspace.email,
                        subject,content)
    
    def notifyModule(self,module,notification):
        """ Notify to a specific module's <notify entry """
        
        # Form the content...
        content=notification.resolveContent(self.resolver, self.getNextIdentifier())
                
        # Form the subject
        subject=self.workspace.prefix+	\
                ': '+module.getName()+' '+	\
                lower(stateDescription(module.getState()))
                    
        self.sendEmails(self.getAddressPairs(module),subject,content)
            
    
    def notifyProject(self,project,notification):
        """ Notify to a specific project's <notify entry """
        module=project.getModule()
    
        #
        # Form the content...
        #
        content=notification.resolveContent(self.resolver, self.getNextIdentifier())
                
        # Form the subject
        subject=self.workspace.prefix+': '	\
            + module.getName() + '/' +project.getName()	\
            +' '+lower(stateDescription(project.getState()))
                    
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
        	Try to send them (if any to send, or store)
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
            self.addUnwanted(subject,content)
                    
    def sendEmail(self, toaddr, fromaddr, subject, content):
        """
        	Perform the SMTP send.
        """
        
        #
        # We send to a list, but a list of one is fine..
        #
        toaddrs=[ toaddr ]
    
        sent=False
        try:
            log.info('Send Notify To: ' + str(toaddr) + 
                ' From: ' + str(fromaddr) + ' Subject: ' + str(subject))
           
            # Form the user visable part ...
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
            sent=mail(toaddrs,fromaddr,email,	\
                        self.workspace.mailserver,	\
                        self.workspace.mailport)  
                   
        except Exception, details:
            sent=False
            log.error('Failed to send notify e-mail: ' + str(details), \
                        exc_info=1)
                        
            # Add why unset along with content stored (and e-mailed) below.            
            content = 'Failed to send notify e-mail: ' + str(details) + '\n' + content
                  
        if not sent:
            content = 'Failed with to: ['+str(toaddr)+'] from: ['+str(fromaddr)+']\n' + content
            
            self.addUnsent(subject,content)                                        
            log.error('Failed with to: ['+str(toaddr)+'] from: ['+str(fromaddr)+']' )
            
        return sent
