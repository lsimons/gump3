#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/output/Attic/nag.py,v 1.1 2003/11/17 22:10:54 ajack Exp $
# $Revision: 1.1 $
# $Date: 2003/11/17 22:10:54 $
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

from gump import log
from gump.config import *
from gump.model import *
from gump.net.mailer import *
from gump.utils import *

def nag(run):

    workspace=run.getWorkspace()
    gumpSet=run.getGumpSet()
    
    if not workspace.isNag():
        return

    #
    # Nag about the workspace (if it needs it)
    #
    if STATE_FAILED==workspace.getState():
        nagWorkspace(workspace)
    
    # For all modules...
    for modules in workspace.getModules():        
            if not gumpSet.inModules(module): continue
            
            for project in module.getProjects():
                if STATE_FAILED == project.getState() :
                    if not gumpSet.inSequence(project): continue    
                    
                    # :TODO: Something doesn't work w/ this.
                    # if projectFilterList and not pctxt.project in projectFilterList: continue
                    try:
                        nagProject(project,workspace)
                    except Exception, details:
                        log.error("Failed to send nag e-mails for project " + project.getName()\
                                            + " : " + str(details))
                
                
def nagWorkspace(workspace):
    """ Nag for the workspace """
    content=getContent(workspace, "There is a workspace problem... \n")
    sendEmail(workspace,workspace.mailinglist,workspace.email,workspace.prefix+': Gump Workspace Problem ',content)
    
def nagProject(workspace,project):
    """ Nag to a specific project's <nag entry """
    content=''
    
    module=project.getModule()
    
    #
    # Form the content...
    #
    displayedModule=0
    displayedProject=0
    if not STATE_SUCCESS == module.getState():
        displayedModule=1
        content+=getContent(workspace,module,"Module: " + module.getName() + "\n")
        
    if not STATE_SUCCESS == project.getState():
        displayedProject=1    
        content+=getContent(workspace,project,"Project: " + project.getName() + "\n"    )
        
    # No clue why this would happen, but fallback safe...
    if not displayedModule and not displayedProject:
        content+=getContent(workspace,module,"Module: " + module.getName() + "\n") 
        content+=getContent(workspace,project,"Project: " + project.getName() + "\n")
                
    #
    # Form the sujhect
    #
    subject=workspace.prefix+': '+module.getName()+'/'+project.getName()+' '+lower(stateName(project.getState()))
    
    nags=0
    for nagEntry in project.nag:
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
            log.error(content)
            
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
    # Fire ...
    mail(toaddrs,fromaddr,email,workspace.mailserver) 
            
def getContent(workspace,object,message=''):
    content=''
    
    # Optional message
    if message:
        content=message             
    
    #
    # Add State (and reason)
    #
    content += "State: " + object.getStateDescription() + "\n"
    
    if not object.reason == REASON_UNSET:
        content +=  "Reason: " + object.getReasonDescription() + "\n"
                                 
    #
    # Link them back here...
    #
    url=workspace.documenter.getObjectLink(object)
    content += "URL: " + url + "\n"
    
    #
    # Add an info/error/etc...
    #
    if object.annotations:
        content += "\n\nAnnotations:\n"
        for note in object.annotations:      
            content += (' - %s - %s\n' % (levelName(note.level), note.text))
    
    #
    # Work
    #
    if object.worklist:
        content+="\n\nWork Items:\n"
        for workitem in object.worklist:
            content+=workitem.overview()+"\n"            
    
    return content
    
    