#!/usr/bin/env python
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
    Notification Testing
"""

import os
import logging
import types, io

from gump import log
import gump.core.config
from gump.core.run.gumprun import GumpRun
from gump.actor.stats.statistician import Statistician

from gump.test import getWorkedTestRun
from gump.test.pyunit import UnitTestSuite

from gump.actor.notify.notifier import Notifier
from gump.actor.notify.notification import SuccessNotification,FailureNotification,WarningNotification
from gump.util.smtp import *

class NotificationTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        #
        # Load a decent Run/Workspace
        #
        self.run=getWorkedTestRun()  
        self.assertNotNone('Needed a run', self.run)
        self.workspace=self.run.getWorkspace()          
        self.assertNotNone('Needed a workspace', self.workspace)
        
        # Prime the information..
        stats=Statistician(self.run)
        stats.updateStatistics()
        
    def testNotificationContents(self):
        
        resolver=self.run.getOptions().getResolver()
        content1=SuccessNotification(self.run, self.workspace).resolveContent(resolver)
        content2=FailureNotification(self.run, self.workspace).resolveContent(resolver)   
        content3=WarningNotification(self.run, self.workspace).resolveContent(resolver)    
        #print content1
        #print content2
        #print content3
    
        # For all modules...
        for module in self.workspace.getModules():                    
            #print 'Get Content For Module : ' + module.getName()
            content1=SuccessNotification(self.run, module).resolveContent(resolver)
            content2=FailureNotification(self.run, module).resolveContent(resolver) 
            content3=WarningNotification(self.run, module).resolveContent(resolver) 
            #print content1
            #print content2
            #print content3
            for project in module.getProjects():
                #print 'Get Content For Project : ' + project.getName()
                # print 
                content1=SuccessNotification(self.run, project).resolveContent(resolver)
                content2=FailureNotification(self.run, project).resolveContent(resolver)
                content3=WarningNotification(self.run, project).resolveContent(resolver)
                #print content1
                #print content2
                #print content3
                
    def testNotifyUnwantedUnsent(self):
    
        notifier=Notifier(self.run)
        
        self.assertFalse( 'No Unwanted', notifier._hasUnwanted() )
        self.assertFalse( 'No Unsent', notifier._hasUnsent() )
        
        notifier._addUnwanted('test subject','test content')
        notifier._addUnsent('test subject','test content')
        
        self.assertTrue( 'Has Unwanted', notifier._hasUnwanted() )
        self.assertTrue( 'Has Unsent', notifier._hasUnsent() )
                
    def testNotifyAddresses(self):
    
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
                addresses=notifier.getAddressPairs(project)
                for addr in addresses:
                    #print 'AddressPair : ' + str(addr)      
                    pass   
                             
    def testNotifyEmails(self):
    
        notifier=Notifier(self.run)
           
        # For all modules...
        for module in self.workspace.getModules(): 
            for project in module.getProjects():
                #print 'Get E-mail For Project : ' + project.getName()
                addresses=notifier.getAddressPairs(project)
                for addr in addresses:   
                    toAddrs=[ addr.getToAddress() ]
                    email=EmailMessage( toAddrs, \
                            addr.getFromAddress(), \
                            'Test Subject', \
                            'Test Content')       
                    #print str(email)
                    
        notifier._getUnwantedContent()
        notifier._getUnsentContent()
        
