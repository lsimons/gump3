#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/net/Attic/mailer.py,v 1.6 2004/02/13 22:12:37 ajack Exp $
# $Revision: 1.6 $
# $Date: 2004/02/13 22:12:37 $
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
    Nag Users...
"""
from gump import log
from gump.config import *
from gump.utils import *

import smtplib, string
        
class EmailMessage:
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return self.getSerialized()
        
	# A *list* if recipients
	# A single sender
	# The subject
    # The text of the message (the main bodypart)
    def __init__(self,toaddrs,fromaddr,subject,text,signature=None):
        self.toaddrs=toaddrs
        self.fromaddr=fromaddr
        self.subject=subject
        self.text=text
		
		# The signature
        self.signature=signature
		
		# Defaults
        if not self.signature:
            self.signature=default.signature

    #
    # Serialize for sending
    #
    def getSerialized(self):
        """E-mail"""
        # Add the From: and To: headers at the start!
        data = ("Date: %s\r\nFrom: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s%s"
           	% (	time.strftime('%d %b %y %H:%M:%S', time.gmtime()),
           	    self.fromaddr, 
           		string.join(self.toaddrs, ", "),
                self.subject,
           		self.text,
           		default.signature))
           		
        return data;
     
#
#	Send an e-mail to a list of addresses, from an address, with content.
#	Use the specified server/port.
#   
def mail(toaddrs,fromaddr,message,server='localhost',port=25):
    #
    # Sanitize e-mail addresses
    #
    sane_toaddrs=[]
    for toaddr in toaddrs:
        sane_toaddrs.append(sanitizeAddress(toaddr))
        
    sane_fromaddr = sanitizeAddress(fromaddr)
    
    #
    # Get servialized data for e-mail bodyparts...
    #
    if isinstance(message,EmailMessage):
        data = message.getSerialized()
    else:
        data = EmailMessage(toaddrs,fromaddr,'',str(message)).getSerialized()
    
    try:
        #
        # Attach to the SMTP server to send....
        #
        server = smtplib.SMTP(server,port)
        # server.set_debuglevel(1)
        server.sendmail(sane_fromaddr, sane_toaddrs, data)
        server.quit()
        
    except Exception, details:
        log.error('Failed to send e-mail: ' + str(details))
        log.error(data, exc_info=1)
        log.error('Server :' + str(server) + ' From   :' + str(fromaddr) + ' To     :' + str(toaddrs))
    
def sanitizeAddress(addr):
    parts=addr.split('<')
    if len(parts) > 1:
        addr=parts[1]
    parts=addr.split('>')
    addr=parts[0]
    return addr
    
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)
   
  # email=EmailMessage('There','Hi')
  
  # mail([default.email],default.email,email,default.mailserver)
  
  # mail([ 'ajack@trysybase.com' ],default.email,email,default.mailserver)
  
  print sanitizeAddress('Adam Jack <ajack@trysybase.com>')
  
  
