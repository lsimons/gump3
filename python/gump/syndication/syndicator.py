#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/syndication/syndicator.py,v 1.1 2003/12/05 00:51:49 ajack Exp $
# $Revision: 1.1 $
# $Date: 2003/12/05 00:51:49 $
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
  Highly experimental RSS feeds.
"""

import os
import time

from xml.sax.saxutils import escape

from gump import log
from gump.model.state import *
from gump.model.project import ProjectStatistics

# tell Python what modules make up the gump.syndication package
__all__ = ["rss","atom"]

class Syndicator:
    def __init__(self):     pass        
        
    #
    # Populate a method called 'document(run)'
    #
    def syndicate(self,run):
        if not hasattr(self,'syndicateRun'):
            raise RuntimeException, 'Complete [' + self.__class__ + '] with syndicateRun(self,run)'
        
        if not callable(self.syndicateRun):
            raise RuntimeException, 'Complete [' + self.__class__ + '] with a callable syndicateRun(self,run)'
        
        log.info('Syndicate run using [' + `self` + ']')
        
        self.syndicateRun(run)

    def getProjectContent(self,project,run):
        
        resolver=run.getOptions().getResolver()
        
        stats=project.getStats()
        
        content='Project ' + project.getName() \
                                + ' : ' \
                                + project.getStateDescription()
                            
        if not project.getStatePair().isReasonUnset():
           content += ' with reason ' \
                + project.getReasonDescription()
            
        content += '\n\n'
                        
        if not stats.previousState == STATE_NONE \
            and not stats.previousState == STATE_UNSET:
            content += 'Previous state: ' \
                                    + stateName(stats.previousState)  \
                                    + '\n\n'
    
        self.addSundries(project,content)
                
        return content

    

    def getModuletContent(self,module,run):
        
        resolver=self.run.getOptions().getResolver()
        
        stats=module.getStats()
        
        content='Module ' + module.getName() \
                                + ' : ' \
                                + module.getStateDescription()	
                            
        if not module.getStatePair().isReasonUnset():
           content += ' with reason ' \
                + module.getReasonDescription()
            
        content += '\n\n'
                        
        if not stats.previousState == STATE_NONE \
            and not stats.previousState == STATE_UNSET:
            content += 'Previous state: ' \
                                    + stateName(stats.previousState)  \
                                    + '\n\n'
    
        self.addSundries(module,content)
                
        return content

    def addSundries(self,object,content):
        
        resolver=self.run.getOptions().getResolver()    
        
        if object.annotations:
            content += '<table>'
            for note in object.annotations:
                    content += ('<tr><td>' \
                        + note.getLevelName() + '</td><td>' \
                        + note.getText() + '</td></tr>\n')                
            content += '<table>'
            
        if object.worklist:
            content += '<table>'    
            for work in object.worklist:
                url=resolver.getAbsoluteUrl(work)
                state=stateName(work.state)                 
                content += ('<tr><td><a href=\'' + 	\
                    url + '\'>' + work.getName() + 	\
                    '</a></td><td>' + state + 		\
                    '</td></tr>\n')                   
            content += '<table>'
            
        context += '\n\n\n<img alt=\'Brought to you by Jakarta Gump\' src=\'http://jakarta.apache.org/gump/images/bench.png\'/>'
              
def syndicate(run):
    
    from gump.syndication.rss import RSSSyndicator
    simple=RSSSyndicator()
    simple.syndicate(run)
    
    #atom=AtomSyndicator()
    #atom.syndicate(run)