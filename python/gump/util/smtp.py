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

    SMTP interface
    
"""
from gump import log
from gump.core.config import *
from gump.util import *
from email.header import Header

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
        self.toaddrs = toaddrs
        #self.fromaddr = Header(fromaddr, 'iso-8859-1')
        self.fromaddr = fromaddr
        #self.subject = Header(subject, 'iso-8859-1')
        self.subject = subject
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
           	% (	time.strftime('%a, %d %b %Y %H:%M:%S %Z', time.localtime()),
                        #self.fromaddr.encode(),
                        self.fromaddr, 
           		string.join(self.toaddrs, ", "),
                        #self.subject.encode(),
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
    
    sent=False
    try:
        #
        # Attach to the SMTP server to send....
        #
        server = smtplib.SMTP(server,port)
        #server.set_debuglevel(1)
        failures = server.sendmail(sane_fromaddr, sane_toaddrs, data)
        server.quit()
        
        # Note: w/o an exception it was accepted to some folk...
        # Failures is a list of tuples of error code plus recipient
        # that was refused.
        
        if not failures: 
            sent=True
        else:
            for failure in failures:
                log.error('Failed to send e-mail to : ' + repr(failure))
        
    except Exception as details:
        sent=False
        
        log.error('Failed to send e-mail: ' + str(details))
        log.error(data, exc_info=1)
        log.error('Server :' + str(server) + ' From   :' + str(fromaddr) + ' To     :' + str(toaddrs))
        
        # Keep it going...
        raise
    
    return sent
    
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
   
    email=EmailMessage(['Adam Jack <ajack@trysybase.com>'],\
                    'Adam Jack <ajack@trysybase.com>', \
                    'Hi','There')
  
    #mail([default.email],default.email,email,default.mailserver)
  
    mail(['ajack@trysybase.com'],default.email,email,default.mailserver)
  
    print((sanitizeAddress('Adam Jack <ajack@trysybase.com>'))) 
  
  
