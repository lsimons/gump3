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

    The logic for 'Nag' (notification) e-mail generation, i.e. do it
    when official or when first changes state (failed to success or
    succes to failed).
    
"""

import socket
import time
import os
import sys
import logging

from gump import log
from gump.core.config import *
from gump.core.run.gumprun import *
from gump.core.model.project import *
from gump.core.model.module import *
from gump.core.model.state import *
from gump.util import *

import gump.notify.notification

class NotificationLogic(RunSpecific):
    
    def __init__(self,run):
        RunSpecific.__init__(self,run)
            
            # :TODO: First Ever?
            # :TODO What if M$ (i.e. not dbm) and/or no stats db
            
    def notification(self,entity):
        """
        Determine if a notification is appropriate, and
        generate it (the content)
        """
        
        notification=None
        
        # Stats had better have been set
        stats=entity.getStats()            
         
        #   
        # Determine if we want to notify, and if so
        # with what (Failure/Warning/Success)
        #
        if entity.isFailed():
            #
            # Notify on first failure, or each official
            # run.
            #
            if self.run.getOptions().isOfficial() \
                or (1 == stats.sequenceInState):                           
                notification=gump.notify.notification.FailureNotification(self.run,entity)            
        elif entity.isSuccess():
            #
            # Notify on first success, after a failure.
            #
            if (stats.sequenceInState == 1):            
                if not STATE_PREREQ_FAILED == stats.previousState:
                    if stats.getTotalRuns() > 1:    
                        notification=gump.notify.notification.SuccessNotification(self.run,entity)
            else:
                #
                # Notify on official if contains 'errors'.
                #
                if self.run.getOptions().isOfficial() and entity.containsRealNasties():
                    notification=gump.notify.notification.WarningNotification(self.run,entity,' contains errors')   
                        
        #elif entity.isPrereqFailed():
        #    if (stats.sequenceInState == 1):            
        #        if not STATE_PREREQ_FAILED == stats.previousState:
        #            notification=PositiveNotification(self.run,entity)
                        
        return notification        
