#!/usr/bin/env python
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
    Notification Testing
"""

import os
import logging
import types, StringIO

from gump import log
import gump.core.config
from gump.core.gumprun import GumpRun
from gump.test import getWorkedTestWorkspace
from gump.test.pyunit import UnitTestSuite
from gump.output.notify import notify,Notifier
from gump.net.smtp import *

class NotificationTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        #
        # Load a decent Workspace
        #
        self.workspace=getWorkedTestWorkspace()          
        self.assertNotNone('Needed a workspace', self.workspace)
        self.run=GumpRun(self.workspace)
        
    def testNotificationContents(self):
    
        nagger=Notifier(self.run)
        
        # For all modules...
        for module in self.workspace.getModules():                    
            #print 'Get Content For Module : ' + module.getName()
            nagger.getNamedTypedContent(module,'test')
            for project in module.getProjects():
                #print 'Get Content For Project : ' + project.getName()
                # print 
                nagger.getNamedTypedContent(project,'test')
                
    def testNotifyUnwantedUnsent(self):
    
        nagger=Notifier(self.run)
        
        self.assertFalse( 'No Unwanted', nagger.hasUnwanted() )
        self.assertFalse( 'No Unsent', nagger.hasUnsent() )
        
        nagger.addUnwanted('test subject','test content')
        nagger.addUnsent('test subject','test content')
        
        self.assertTrue( 'Has Unwanted', nagger.hasUnwanted() )
        self.assertTrue( 'Has Unsent', nagger.hasUnsent() )
                
    def testNagAddresses(self):
    
        notifier=Notifier(self.run)
           
        # For all modules...
        for module in self.workspace.getModules():                    
            #print 'Get Addresses For Module : ' + module.getName()
            addresses=notifier.getAddressPairs(module)
            for addr in addresses:
                #print 'AddressPair : ' + str(addr)
                pass
            for project in module.getProjects():
                #print 'Get Addresses For Project : ' + project.getName()
                addresses=nagger.getAddressPairs(project)
                for addr in addresses:
                    #print 'AddressPair : ' + str(addr)      
                    pass   
                             
    def testNagEmails(self):
    
        notifier=Notifier(self.run)
           
        # For all modules...
        for module in self.workspace.getModules(): 
            for project in module.getProjects():
                #print 'Get E-mail For Project : ' + project.getName()
                addresses=nagger.getAddressPairs(project)
                for addr in addresses:   
                    toAddrs=[ addr.getToAddress() ]
                    email=EmailMessage( toAddrs, \
                            addr.getFromAddress(), \
                            'Test Subject', \
                            'Test Content')       
                    #print str(email)
                    
        notifier.getUnwantedContent()
        notifier.getUnsentContent()
                
    def testNotify(self):  
        notify(self.run)
        