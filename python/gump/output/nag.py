#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/output/Attic/nag.py,v 1.6 2004/01/28 00:13:39 ajack Exp $
# $Revision: 1.6 $
# $Date: 2004/01/28 00:13:39 $
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

def nag(run):

    workspace=run.getWorkspace()
    gumpSet=run.getGumpSet()
    
    #
    # Belt and braces...
    #
    if not workspace.isNag():
        return

    #
    # Nag about the workspace (if it needs it)
    #
    if workspace.isFailed():
        nagWorkspace(run,workspace)
    
    # For all modules...
    for module in workspace.getModules():        
            if not gumpSet.inModules(module): continue

            if module.isFailed():
                try:
                    log.info('Nag for module: ' + module.getName())                        
                    
                    nagModule(run,workspace,module)   
                                         
                except Exception, details:
                    log.error("Failed to send nag e-mails for module " + module.getName()\
                                + " : " + str(details), exc_info=1)
            else:
                for project in module.getProjects():
                    if project.isFailed() :
                        if not gumpSet.inSequence(project): continue                        
                        
                        try:
                        
                            log.info('Nag for project: ' + project.getName())                        
                            nagProject(run,workspace,project)                        
                        except Exception, details:
                            log.error("Failed to send nag e-mails for project " + project.getName()\
                                            + " : " + str(details), exc_info=1)
                
                
def nagWorkspace(run,workspace):
    """ Nag for the workspace """
    content=getContent(workspace, "There is a workspace problem... \n")
    sendEmail(workspace,workspace.mailinglist,workspace.email,workspace.prefix+': Gump Workspace Problem ',content)
    
def nagModule(run,workspace,module):
    """ Nag to a specific module's <nag entry """
    content=''
    
    #
    # Form the content...
    #
    content+=getContent(run,workspace,module,"Module: " + module.getName() + "\n")
                
    #
    # Form the sujhect
    #
    subject=workspace.prefix+': '+module.getName()+' '+lower(stateName(module.getState()))
    
    nags=0
    for nagEntry in module.xml.nag:
        try:
            #
            # Form and send the e-mail...
            #
            toaddr=getattr(nagEntry,'to',workspace.mailinglist)
            fromaddr=getattr(nagEntry,'from',workspace.mailinglist)
            
            sendEmail(workspace,toaddr,fromaddr,subject,content)
            
            nags+=1
        except Exception, details:
            log.error("Failed to send nag e-mail for module " + module.name \
                    + " : " + str(details))
            log.error(content, exc_info=1)
            
    # Belt and braces (nag to us if not nag to them)
    if not nags:
        sendEmail(workspace,workspace.mailinglist,workspace.mailinglist,subject,content)
    
    
def nagProject(run,workspace,project):
    """ Nag to a specific project's <nag entry """
    content=''
    
    module=project.getModule()
    
    #
    # Form the content...
    #
    displayedModule=0
    displayedProject=0
    if not module.isSuccess():
        displayedModule=1
        content+=getContent(run,workspace,module,"Module: " + module.getName() + "\n")
        
    if not project.isSuccess():
        displayedProject=1    
        content+=getContent(run,workspace,project,"Project: " + project.getName() + "\n"    )
        
    # No clue why this would happen, but fallback safe...
    if not displayedModule and not displayedProject:
        content+=getContent(run,workspace,module,"Module: " + module.getName() + "\n") 
        content+=getContent(run,workspace,project,"Project: " + project.getName() + "\n")
                
    #
    # Form the sujhect
    #
    subject=workspace.prefix+': '+module.getName()+'/'+project.getName()+' '+lower(stateName(project.getState()))
    
    nags=0
    for nagEntry in project.xml.nag:
        try:
            #
            # Form and send the e-mail...
            #
            toaddr=getattr(nagEntry,'to',workspace.mailinglist)
            fromaddr=getattr(nagEntry,'from',workspace.mailinglist)
            
            sendEmail(workspace,toaddr,fromaddr,subject,content)
            
            nags+=1
        except Exception, details:
            log.error("Failed to send nag e-mail for project " + project.name \
                    + " : " + str(details))
            log.error(content, exc_info=1)
            
    # Belt and braces (nag to us if not nag to them)
    if not nags:
        sendEmail(workspace,workspace.mailinglist,workspace.mailinglist,subject,content)
            
def sendEmail(workspace, toaddr, fromaddr, subject, content):
    #
    # We send to a list, but a list of one is fine..
    #
    toaddrs=[ toaddr ]
            
    #
    # Form the user visable part ...
    #
    email=EmailMessage( toaddrs, \
                        fromaddr, \
                        subject, \
                        content)       
                        
    print 'To:' + `toaddrs`
    print 'From:' + `toaddrs`
    print 'Subject:' + `toaddrs`
    print 'Server:' + `workspace.mailserver`
    print 'e-mail:' + `email`
    
    # Fire ...
    #mail(toaddrs,fromaddr,email,workspace.mailserver) 
            
def getContent(run,workspace,object,message=''):
    content=''
    
    # Optional message
    if message:
        content=message             
    
    #
    # Add State (and reason)
    #
    content += "State: " + object.getStateDescription() + "\n"
    
    if not object.hasReason():
        content +=  "Reason: " + object.getReasonDescription() + "\n"
                                 
    #
    # Link them back here...
    #
    url=run.getOptions().getResolver().getUrl(object)
    content += "URL: " + url + "\n"
    
    #
    # Add an info/error/etc...
    #
    #if object.annotations:
    #    content += "\n\nAnnotations:\n"
    #    for note in object.annotations:      
    #        content += (' - %s - %s\n' % (levelName(note.level), note.text))
    
    #
    # Work
    #
    #if object.worklist:
    #    content+="\n\nWork Items:\n"
    #    for workitem in object.worklist:
    #        content+=workitem.overview()+"\n"            
    
    return content
    
    