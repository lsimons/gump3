#!/usr/bin/env python

# $Header: /home/cvspublic/jakarta-gump/python/gump/conf.py,v 1.7 2003/05/10 18:20:36 nicolaken Exp $
# $Revision: 1.7 $
# $Date: 2003/05/10 18:20:36 $
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
    xdoc generation, for forrest
"""

import socket
import time
import os
import sys
import logging

from gump import log, gumpSafeName
from gump.conf import *
from gump.context import *
from gump.model import *
from gump.mailer import *

def nag(workspace,context,moduleFilterList=None,projectFilterList=None):
    if STATUS_FAILED==context.status:
        nagWorkspace(workspace,context)
    
    for (mname,mctxt) in context.subcontexts.iteritems():
        if not STATUS_SUCCESS == mctxt.status:
            if Module.list.has_key(mname):
                # :TODO: Something doesn't work w/ this.
                # if moduleFilterList and not mname in moduleFilterList: continue    
                module=Module.list[mname]
                for (pname,pctxt) in mctxt.subcontexts.iteritems():
                    if STATUS_FAILED == pctxt.status:
                        # :TODO: Something doesn't work w/ this.
                        # if projectFilterList and not pctxt.project in projectFilterList: continue
                        project=Project.list[pname]
                        if project.nag:
                            nagProject(workspace,context,module,mctxt,project,pctxt)
                        else:
                            log.error("Project naggable w/ nowhere to nag")
                
def nagWorkspace(workspace,context):
    """ Nag for the workspace """
    content=getContext(context, "Workspace ... \n")
    email=EmailMessage(workspace.prefix+': Gump Workspace Problem ',content)
    mail([ workspace.email ],workspace.email,email,workspace.mailserver)
  
def nagProject(workspace,context,module,mctxt,project,pctxt):
    """ Nag to a specific project's <nag entry """
    content=''
    
    #
    # Form the content...
    #
    content+="----------------------------------------------------\n"
    content+=getContent(mctxt,"Module: " + module.name + "\n")
    content+=getContent(pctxt,"Project: " + project.name + "\n"    )
    content+="----------------------------------------------------\n"
        
    #
    # Form and send the e-mail...
    #
    email=EmailMessage(workspace.prefix+':'+module.name+'/'+project.name+' '+stateName(pctxt.status),content)
    toaddr=project.nag.toaddr or workspace.email
    fromaddr=project.nag.fromaddr or workspace.email
    toaddrs=[ toaddr or workspace.email ]
    mail(toaddrs,fromaddr,email,workspace.mailserver) 
    
def getContent(context,message=''):
    content=''
    
    # Optional message
    if message:
        content=message
    
    #
    # Add status (and reason)
    #
    content += "Status: " + stateName(context.status)
    
    if not context.reason == REASON_UNSET:
        content +=  "Reason: " + reasonString(context.reason)
    #
    # Add an info/error/etc...
    #
    for note in context.annotations:      
        content += (' - %s - %s' % (levelName(note.level), note.text))
    
    #
    # Work
    #
    if context.worklist:
        content+="\n"
        for workitem in context.worklist:
            content+=workitem.overview()+"\n"
            
    return content