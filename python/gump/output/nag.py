#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/output/Attic/nag.py,v 1.16 2004/02/23 21:55:35 ajack Exp $
# $Revision: 1.16 $
# $Date: 2004/02/23 21:55:35 $
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
    'Nag' (notification) e-mail generation...
"""

import socket
import time
import os
import sys
import logging

from string import lower, capitalize

from gump import log
from gump.config import *
from gump.model.project import *
from gump.model.module import *
from gump.model.state import *
from gump.net.mailer import *
from gump.utils import *

LINE='-  -  -  -  - -- -- ------------------------------------ G U M P'

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

class Nagger:
    
    def __init__(self,run):        
        self.run = run
        self.workspace=run.getWorkspace()
        self.gumpSet=run.getGumpSet()
    
        self.unsent=''
        self.unwanted=''
        
        
    def nag(self):
    
        #
        # Belt and braces...
        #
        if not self.workspace.isNag():
            return
    
        # A bit paranoid, ought just rely upon object being
        # destroyed,
        self.unsent=''
        self.unwanted=''
            
        #
        # Nag about the workspace (if it needs it)
        #
        if self.workspace.isFailed():
            self.nagWorkspace(run,self.workspace)
    
        # For all modules...
        for module in self.workspace.getModules():        
                if not self.gumpSet.inModules(module): continue

                if module.isFailed():
                    try:
                        log.info('Nag for module: ' + module.getName())                                        
                        self.nagModule(module)   
                    
                    except Exception, details:
                        log.error("Failed to send nag e-mails for module " + module.getName()\
                                    + " : " + str(details), exc_info=1)
                else:
                    for project in module.getProjects():
                        if project.isFailed() :
                            if not self.gumpSet.inSequence(project): continue                        
                        
                            try:                        
                                log.info('Nag for project: ' + project.getName())                                                        
                                self.nagProject(project)                        
                                
                            except Exception, details:
                                log.error("Failed to send nag e-mails for project " + project.getName()\
                                            + " : " + str(details), exc_info=1)
                
                
        # Belt and braces (nag to us if not nag to them)
        if self.hasUnwanted():
            log.info('We have some unwanted\'s to send to list...')
            
            self.sendEmail(self.workspace.mailinglist,self.workspace.email,	\
                        'All dressed up, with nowhere to go...',self.unwanted)
                        
            # A bit paranoid, ought just rely upon object being
            # destroyed,
            self.unwanted=''      
        else:
            log.info('No unwanted nags.')
                
        # Belt and braces (nag to us if not nag to them)
        if self.hasUnsent():
            log.info('We have some unsented\'s to send to list...')    
            self.sendEmail(self.workspace.mailinglist,self.workspace.email,	\
                        'Unable to send...',self.unsent)
                        
            # A bit paranoid, ought just rely upon object being
            # destroyed,
            self.unsent=''
        else:
            log.info('No unsent nags.')
                
    def addUnwanted(self,subject,content):
        if self.unwanted:
            self.unwanted += '-------------------------------------------------------------\n'
        self.unwanted += subject
        self.unwanted += '\n'
        self.unwanted += content
        self.unwanted += '\n'
    
    def addUnsent(self,subject,content):
        if self.unsent:
            self.unsent += '-------------------------------------------------------------\n'
        self.unsent += subject
        self.unsent += '\n'
        self.unsent += content
        self.unsent += '\n'
                    
    def hasUnwanted(self):
        if self.unwanted: return 1
        return 0
    
    def hasUnsent(self):
        if self.unsent: return 1
        return 0
    
    
    def nagWorkspace(self):
        """ Nag for the workspace """
        content=self.getGenericContent(self.workspace,'index',"There is a workspace problem... \n")
        
        self.sendEmail(self.workspace.mailinglist,	\
                        self.workspace.email,	\
                        self.workspace.prefix+': Gump Workspace Problem ',content)
    
    def nagModule(self,module):
        """ Nag to a specific module's <nag entry """
        
        #
        # Form the content...
        #
        content=self.getNamedTypedContent(module,'index')
                
        #
        # Form the subject
        #
        subject=self.workspace.prefix+	\
                ': '+module.getName()+' '+	\
                lower(stateDescription(module.getState()))
                    
        self.sendEmails(self.getAddressPairs(module),subject,content)
            
    
    def nagProject(self,project):
        """ Nag to a specific project's <nag entry """
        module=project.getModule()
    
        #
        # Form the content...
        #
        content=self.getNamedTypedContent(project, project.getName() )        
                
        #
        # Form the subject
        #
        subject=self.workspace.prefix+': '	\
            +module.getName()+'/'+project.getName()	\
            +' '+lower(stateDescription(project.getState()))
                    
        # Send those e-mails
        self.sendEmails(self.getAddressPairs(project),subject,content)
    
    def getAddressPairs(self, object):
        nags=[]
        
        for nagEntry in object.xml.nag:
            #
            # Determine where to send
            #
            toaddr=getattr(nagEntry,'to',self.workspace.mailinglist)
            fromaddr=getattr(nagEntry,'from',self.workspace.email)   
            
            # Somewhat bogus, but (I think) due to how the XML
            # objects never admit to not having something
            if not toaddr: toaddr =    self.workspace.mailinglist
            if not fromaddr : fromaddr =  self.workspace.email
                
            nags.append(AddressPair(getStringFromUnicode(toaddr),	\
                                    getStringFromUnicode(fromaddr)))  

        return nags
        
        
    def sendEmails(self, addressPairs, subject, content):
        if addressPairs:
            for pair in addressPairs:
                self.sendEmail(pair.getToAddress(), pair.getFromAddress(),	\
                                subject, content)
        else:
            #
            # This is a catch-all, for all project that
            # don't have <nag's assigned.
            #
            self.addUnwanted(subject,content)
                    
    def sendEmail(self, toaddr, fromaddr, subject, content):
        #
        # We send to a list, but a list of one is fine..
        #
        toaddrs=[ toaddr ]
    
        try:
               
            log.info('Send Nag e-mail to: ' + str(toaddr) + ' from: ' + str(fromaddr))
           
            #
            # Form the user visable part ...
            #
            email=EmailMessage( toaddrs, \
                                fromaddr, \
                                subject, \
                                content)       
              
            log.info('Subject: ' + str(subject))
                        
            #print '-------------------------------------------------------------------'
            #print 'To:' + `toaddr`
            #print 'From:' + `fromaddr`
            #print 'Subject:' + `subject`
            #print 'Server:' + `self.workspace.mailserver`
            #print 'e-mail:' + `email`    
            # Fire ...
            mail(toaddrs,fromaddr,email,	\
                self.workspace.mailserver,	\
                self.workspace.mailport) 
            
        except Exception, details:
            log.error('Failed to send nag e-mail: ' + str(details), \
                        exc_info=1)
                        
            self.addUnsent(subject,content)                
                        
            log.error('Failed with to: ['+str(toaddr)+'] from: ['+str(fromaddr)+']' )
            
    def getNamedTypedContent(self,object,feedPrefix=None,message=None):
        content="""To whom it may engage...
        
This is an automated request, but not an unsolicited one. For help understanding the request please visit http://jakarta.apache.org/gump/nagged.html, and/or contact gump@jakarta.apache.org.

"""
    
        # Get our facts straight.
        name=object.getName()
        type=object.__class__.__name__
        affected=object.determineAffected()
        duration=object.getStats().sequenceInState
        
        # Optional message
        if message:
            content+=message             
            
        content += type + ' ' + name + ' has an issue affecting it\'s community integration'
                
        if affected:
            content += '. This issue affects ' + `affected` + ' projects'
            
        if duration and duration > 1:
            content += ', and has been outstanding for ' + `duration` + ' runs'
        
        content += '. '
            
        content += self.getGenericContent(object,feedPrefix)
        
        return content
            
    def getGenericContent(self,object,feedPrefix=None,message=None):
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
        content += "\nFull details are available at: " + url 
        
        
        if object.annotations or object.worklist:
            content += ', however some snippets follow:\n'
            
        content += '\n'
        
        #
        # Add an info/error/etc...
        #
        if object.annotations:
            content += LINE
            content += "\n\nGump provided these annotations:\n\n"
            for note in object.annotations:      
                content += (' - %s - %s\n' % (levelName(note.level), note.text))
    
        #
        # Work
        #
        if object.worklist: 
            content+="\n\n"
            content += LINE   
            content += "\nGump performed this work:\n\n"
            for workitem in object.worklist:
                content+=workitem.overview()+'\n\n'   
                                
        if feedPrefix:
            content += '\n\nTo subscribe to this information via syndicated feeds:\n'      
            
            #
            # Link them back here...
            #
            rssurl=self.run.getOptions().getResolver().getUrl(object,feedPrefix,'.rss')
            atomurl=self.run.getOptions().getResolver().getUrl(object,feedPrefix,'.atom')
            
            content += "RSS: " + rssurl + " | "
            content += "Atom: " + atomurl + '\n'         
    
        return content
    
def nag(run):
    nagger=Nagger(run)
    nagger.nag()
    