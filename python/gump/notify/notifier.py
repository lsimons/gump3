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
from gump.model.project import *
from gump.model.module import *
from gump.model.state import *
from gump.net.smtp import *
from gump.utils import *

LINE     ='--   --   --   --   --   --   --   --   --   --   --   --   G U M P'
SEPARATOR='*********************************************************** G U M P'

class AddressPair:
    def __init__(self,toAddr,fromAddr):
        self.toAddr=toAddr
        self.fromAddr=fromAddr
        
    def __str__(self):
        return '[To:' + self.toAddr + ', From:' + self.fromAddr + ']'
        
    def getToAddress(self):
        return self.toAddr
        
    def getFromAddress(self):
        return self.fromAddr

class Notifier(RunActor):
    
    def __init__(self,run):      
        
        RunActor.__init__(self,run)
        
        self.workspace=run.getWorkspace()
        self.gumpSet=run.getGumpSet()
    
        self.unsent=''
        self.unsentSubjects=''
        self.unsents=0
        
        self.unwanted=''
        self.unwantedSubjects=''
        self.unwanteds=0
        
    def notify(self):
    
        #
        # Belt and braces...
        #
        if not self.workspace.isNotify():
            return
    
        # A bit paranoid, ought just rely upon object being
        # destroyed,
        self.unsent=''
        self.unwanted=''
            
        #
        # Nag about the workspace (if it needs it)
        #
        if self.workspace.isFailed():
            self.notifyWorkspace(run,self.workspace)
    
        # For all modules...
        for module in self.workspace.getModules():        
                if not self.gumpSet.inModuleSequence(module): continue

                if module.isFailed():
                    try:
                        log.info('Nag for module: ' + module.getName())
                        self.notifyModule(module)   
                    
                    except Exception, details:
                        log.error("Failed to send notify e-mails for module " + module.getName()\
                                    + " : " + str(details), exc_info=1)
                else:
                    for project in module.getProjects():
                        if project.isFailed() :
                            if not self.gumpSet.inProjectSequence(project): continue                        
                        
                            try:                        
                                log.info('Nag for project: ' + project.getName())                                                        
                                self.notifyProject(project)                        
                                
                            except Exception, details:
                                log.error("Failed to send notify e-mails for project " + project.getName()\
                                            + " : " + str(details), exc_info=1)
                
        
        # Workspace can override...
        (wsTo, wsFrom) = self.workspace.getNagOverrides()        
                
        # Belt and braces (notify to us if not notify to them)
        if self.hasUnwanted():
            log.info('We have some unwanted\'s to send to list...')
            
            self.sendEmail(wsTo or self.workspace.mailinglist,wsFrom or self.workspace.email,	\
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
            self.sendEmail(wsTo or self.workspace.mailinglist,wsFrom or self.workspace.email,	\
                        'BATCH: Unable to send...',\
                         self.getUnsentContent())
                        
            # A bit paranoid, ought just rely upon object being
            # destroyed,
            self.unsent=''
            self.unsentSubjects=''
            self.unsents=0
        else:
            log.debug('No unsent notifys.')
                
    def addUnwanted(self,subject,content):
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
        if self.unsent:
            self.unsent += SEPARATOR
            self.unsent += '\n'
        self.unsent += subject
        self.unsent += '\n'
        self.unsent += content
        self.unsent += '\n'
        
        self.unsentSubjects += subject + '\n'
        self.unsents += 1
        
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

""" % (`self.unwanteds`, plural)
            
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
    
    
    def notifyWorkspace(self):
        """ Nag for the workspace """
        content=self.getGenericContent(self.workspace,'There is a workspace problem... \n')
        
        self.sendEmail(self.workspace.mailinglist,	\
                        self.workspace.email,	\
                        self.workspace.prefix+': Gump Workspace Problem ',content)
    
    def notifyModule(self,module):
        """ Nag to a specific module's <notify entry """
        
        #
        # Form the content...
        #
        content=self.getNamedTypedContent(module)
                
        #
        # Form the subject
        #
        subject=self.workspace.prefix+	\
                ': '+module.getName()+' '+	\
                lower(stateDescription(module.getState()))
                    
        self.sendEmails(self.getAddressPairs(module),subject,content)
            
    
    def notifyProject(self,project):
        """ Nag to a specific project's <notify entry """
        module=project.getModule()
    
        #
        # Form the content...
        #
        content=self.getNamedTypedContent(project )        
                
        #
        # Form the subject
        #
        subject=self.workspace.prefix+': '	\
            +module.getName()+'/'+project.getName()	\
            +' '+lower(stateDescription(project.getState()))
                    
        # Send those e-mails
        self.sendEmails(self.getAddressPairs(project),subject,content)
    
    def getAddressPairs(self, object):
        notifys=[]
        
        # Workspace can override...
        (wsTo, wsFrom) = self.workspace.getNagOverrides()
        
        for notifyEntry in object.xml.notify:
            #
            # Determine where to send
            #
            toaddr=wsTo or getattr(notifyEntry,'to',self.workspace.mailinglist)
            fromaddr=wsFrom or getattr(notifyEntry,'from',self.workspace.email)   
            
            # Somewhat bogus, but (I think) due to how the XML
            # objects never admit to not having something
            if not toaddr: toaddr =    self.workspace.mailinglist
            if not fromaddr : fromaddr =  self.workspace.email
                
            notifys.append(AddressPair(getStringFromUnicode(toaddr),	\
                                    getStringFromUnicode(fromaddr)))  

        return notifys
        
        
    def sendEmails(self, addressPairs, subject, content):
        if addressPairs:
            for pair in addressPairs:
                self.sendEmail(pair.getToAddress(), pair.getFromAddress(),	\
                                subject, content)
        else:
            #
            # This is a catch-all, for all project that
            # don't have <notify's assigned.
            #
            self.addUnwanted(subject,content)
                    
    def sendEmail(self, toaddr, fromaddr, subject, content):
        #
        # We send to a list, but a list of one is fine..
        #
        toaddrs=[ toaddr ]
    
        sent=0
        try:
               
            log.info('Send Nag e-mail to: ' + str(toaddr) + \
                ' from: ' + str(fromaddr) + \
                'Subject: ' + str(subject))
           
            #
            # Form the user visable part ...
            #
            email=EmailMessage( toaddrs, \
                                fromaddr, \
                                subject, \
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
            sent=0
            log.error('Failed to send notify e-mail: ' + str(details), \
                        exc_info=1)
                  
        if not sent:
            self.addUnsent(subject,content)                
                        
            log.error('Failed with to: ['+str(toaddr)+'] from: ['+str(fromaddr)+']' )
            
        return sent
        
    def getNamedTypedContent(self,object,message=None):
        content="""To whom it may engage...
        
This is an automated request, but not an unsolicited one. For help 
understanding the request please visit 
http://gump.apache.org/nagged.html, 
and/or contact general@gump.apache.org.

"""
    
        # Get our facts straight.
        name=object.getName()
        type=object.__class__.__name__
        affected=object.determineAffected()
        duration=object.getStats().sequenceInState
        
        # Optional message
        if message:
            content+=message             
            
        content += type + ' ' + name + ' has an issue affecting its community integration'
                
        if affected:
            content += '.\nThis issue affects ' + `affected` + ' projects'
            
        if duration and duration > 1:
            content += ', and has been outstanding for ' + `duration` + ' runs'
        
        content += '.\n'
        
        if isinstance(object,Project) and affected:
            affectedProjects=object.determineAffectedProjects()
            if 1 or ((duration and duration > 3) and affectedProjects):
                #
                # Show those negatively affected
                #
                content += 'The following are affected:\n'
            
                for project in affectedProjects:
                    content += '    - ' + project.getName() 
                    
                    if project.hasDescription():
                        content += ' :  '
                        content += project.getLimitedDescription()
                        
                    content += '\n'
            
                content += '\n'            
            
        content += self.getGenericContent(object)
        
        return content
            
    def getGenericContent(self,object,message=None):
        content=''
    
        # Optional message
        if message:
            content=message             
    
        #
        # Add State (and reason)
        #
        content += 'The current state is \'' + object.getStateDescription() + '\''
    
        if object.hasReason():
            content +=  ', for reason \'' + object.getReasonDescription() + '\''
        
        content += '\n'
                                 
        #
        # Link them back here...
        #
        url=self.run.getOptions().getResolver().getUrl(object)
        content += "\nFull details are available at:\n    " 
        content += url 
        content += "\n"
                
        if object.annotations or object.worklist:
            content += 'That said, some snippets follow:\n'
            
        content += '\n'
        
        #
        # Add an info/error/etc...
        #
        if object.annotations:
            #content += LINE
            content += "\n"
            content += "Gump provided these annotations:\n"
            for note in object.annotations:      
                content += (' - %s - %s\n' % (levelName(note.level), note.text))
    
        #
        # Work
        #
        if object.worklist: 
            content+="\n\n"
            #content += LINE   
            content += "Gump performed this work:\n"
            for workitem in object.worklist:
                workurl=self.run.getOptions().getResolver().getUrl(workitem)
                content+=workurl+'\n'
                content+=workitem.overview()+'\n'   
                                
        content += '\n\nTo subscribe to this information via syndicated feeds:\n'      
            
        #
        # Link them back here...
        #
        rssurl=self.run.getOptions().getResolver().getUrl(object,'rss','.xml')
        atomurl=self.run.getOptions().getResolver().getUrl(object,'atom','.xml')
            
        content += "RSS: " + rssurl + '\n'
        content += "Atom: " + atomurl + '\n'         
    
        return content
    
def notify(run):
    notifier=Nagger(run)
    notifier.notify()
    
