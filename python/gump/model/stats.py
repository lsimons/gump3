#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/stats.py,v 1.2 2004/01/09 19:57:18 ajack Exp $
# $Revision: 1.2 $
# $Date: 2004/01/09 19:57:18 $
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
    Statistics gathering/manipulation
"""

import time
import os
import sys
import logging
import anydbm

import gump
from gump.config import *
from gump.model.state import *

class Statistics:
    """Statistics Holder"""
    def __init__(self,name):
        self.name=name
        self.successes=0
        self.failures=0
        self.prereqs=0
        self.first=0
        self.last=0
        self.currentState=STATE_UNSET
        self.previousState=STATE_UNSET
        self.startOfState=0        
        self.sequenceInState=0
        
        
    def getFOGFactor(self):
        return (self.successes / (self.failures - self.prereqs))
        
    def getLastUpdated(self):
        return (self.lastUpdated)
        
    def nameKey(self):
        return self.getKeyBase() + '-name'
        
    def successesKey(self):
        return self.getKeyBase() + '-successes'
        
    def failuresKey(self):
        return self.getKeyBase() + '-failures'
        
    def prereqsKey(self):
        return self.getKeyBase() + '-prereqs'
        
    def firstKey(self):
        return self.getKeyBase() + '-first'
        
    def lastKey(self):
        return self.getKeyBase() + '-last'
        
    def lastUpdatededKey(self):
        return self.getKeyBase() + '-last-updated'
        
    def currentStateKey(self):
        return self.getKeyBase() + '-current-state'
        
    def previousStateKey(self):
        return self.getKeyBase() + '-previous-state'
        
    def startOfStateKey(self):
        return self.getKeyBase() + '-start-state' 
               
    def sequenceInStateKey(self):
        return  self.getKeyBase() + '-seq-state'
        
        
    def update(self,project):        
        #
        # Update based off current run
        #
        if project.isSuccess():
            self.successes += 1
            self.last = gump.default.time
            
            # A big event...
            if not self.first:
                self.first=self.last
            elif project.isFailed():
                s.failures += 1    
            elif project.isPrereqFailed():                        
                s.prereqs  += 1
            
        #
        # Deal with states & changes...
        #
        lastCurrentState=self.currentState
        self.currentState=project.getState()
        
        if lastCurrentState==self.currentState:
            self.startOfState = default.time            
            self.sequenceInState += 1            
        else:
            self.previousState=lastCurrentState            
            self.sequenceInState = 1
            
            
    def dump(self, indent=0, output=sys.stdout):
        gump.utils.dump(self)
        
    
 
            
class Statable:
    def __init__(self): pass
    
    # Stats are loaded separately and cached on here,
    # hence they may exist on an object at all times.
    def hasStats(self):
        return hasattr(self,'stats')
        
    def setStats(self,stats):
        self.stats=stats
        
    def getStats(self):
        if not self.hasStats():
            raise RuntimeError, "Statistics not calculated/updated/available [yet]: " \
                    + self.getName()
        return self.stats
        
    