#!/usr/bin/python


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
  Highly experimental RSS feeds.
"""

import os
import time

from xml.sax.saxutils import escape

from gump import log
from gump.core.gumprun import *
from gump.model.state import *
from gump.model.project import ProjectStatistics


class AbstractSyndicator(RunSpecific):
    def __init__(self,run):
        RunSpecific.__init__(self,run)
        
    #
    # Populate a method called 'syndicateRun(run)'
    #
    def syndicate(self):
        if not hasattr(self,'syndicateRun'):
            raise RuntimeError, 'Complete [' + `self.__class__` + '] with syndicateRun(self)'
        
        if not callable(self.syndicateRun):
            raise RuntimeException, 'Complete [' + `self.__class__` + '] with a callable syndicateRun(self)'
        
        log.info('Syndicate run using [' + `self` + ']')
        
        self.syndicateRun()

    def getProjectContent(self,project,run):
        
        resolver=run.getOptions().getResolver()
        
        stats=project.getStats()
        
        content='<p>Project ' + project.getName()  + ', '
                                
        content += self.getStateContent(project.getStatePair())
                        
        content += 'Duration in state: <b>' + `stats.sequenceInState` + '</b> (runs) '
        
        if not stats.previousState == STATE_NONE \
            and not stats.previousState == STATE_UNSET:
            content += ', Previous state: <b>' \
                                    + stateDescription(stats.previousState)  \
                                    + '</b>'
    
        content += '</p>'
        
        if project.hasDescription():
            content+='<p>'           
            content+=project.getDescription()
            content+='<p>'
            
        content += self.getSundries(project)
                
        return content

    

    def getModuleContent(self,module,run):
        
        resolver=self.run.getOptions().getResolver()
        
        stats=module.getStats()
        
        content='<p>Module ' + module.getName() + ', '
                                    
        content += self.getStateContent(module.getStatePair())
        
        content += 'Duration in state: <b>' + `stats.sequenceInState`  + '</b> (runs)'
                        
        if not stats.previousState == STATE_NONE \
            and not stats.previousState == STATE_UNSET:
            content += ', Previous state: <b>' \
                                    + stateDescription(stats.previousState) \
                                    + '</b>'
                                    
        content += '</p>'
    
        if module.hasDescription():
            content+='<p>'            
            content+=module.getDescription()
            content+='</p>'
            
        content += self.getSundries(module)
                
        return content

    def getStateContent(self,statePair):
        
        resolver=self.run.getOptions().getResolver()    
        
        content = 'Gump State: ' + statePair.getStateDescription()	
                            
        if not statePair.isReasonUnset():
           content += ' with reason ' \
                + statePair.getReasonDescription()
        
        content += ( '&nbsp;<img src=\'%s\' alt=\'%s\'/>' ) % \
            resolver.getStateIconInformation(statePair)
            
        content += '<br/><br/>'
        
        return content
        
    def getSundries(self,object):
        
        content = ''
        
        resolver=self.run.getOptions().getResolver()    
        
        if object.annotations:
            content += '<p><table>'
            for note in object.annotations:
                    content += ('<tr><td>' \
                        + note.getLevelName() + '</td><td>' \
                        + note.getText() + '</td></tr>\n')                
            content += '<table></p>'
         
        #
        # They can come visit for this...
        #
           
        #if object.worklist:
        #    content += '<p><table>'    
        #    for work in object.worklist:
        #        url=resolver.getUrl(work)
        #        state=stateDescription(work.state)                 
        #        content += ('<tr><td><a href=\'' + 	\
        #            url + '\'>' + work.getName() + 	\
        #            '</a></td><td>' + state + 		\
        #            '</td></tr>\n')                   
        #    content += '</table></p>'
        
        return content

    #
    # Only report once per state change
    # Don't report on prereq failed, or if just came from that
    # Don't report on packages
    # Don't report on bogus states (testing)
    #
    def moduleOughtBeWidelySyndicated(self, module):
        
        stats=module.getStats()
        
        return stats.sequenceInState == 1	\
            and not stats.currentState == STATE_PREREQ_FAILED \
            and not stats.currentState == STATE_UNSET \
            and not stats.currentState == STATE_NONE \
            and not stats.currentState == STATE_COMPLETE  \
            and not ( \
                stats.currentState == STATE_SUCCESS and	\
                stats.previousState == STATE_PREREQ_FAILED ) \
            and not module.isPackaged()       
              
              
    #
    # Only report once per state change
    # Don't report on prereq failed, or if just came from that
    # Don't report on packages
    # Don't report on bogus states (testing)
    #
    def projectOughtBeWidelySyndicated(self, project):
        
        stats=project.getStats()
        
        return stats.sequenceInState == 1	\
            and not stats.currentState == STATE_PREREQ_FAILED \
            and not stats.currentState == STATE_UNSET \
            and not stats.currentState == STATE_NONE \
            and not stats.currentState == STATE_COMPLETE 	\
            and not ( \
                stats.currentState == STATE_SUCCESS and	\
                stats.previousState == STATE_PREREQ_FAILED ) \
            and not project.isPackaged()    
