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

    Actor to publish artifacts to a repository 
    
"""

import os

from gump import log

import gump.core.gumprun
import gump.core.actor

import gump.utils.file
from gump.utils.tools import listDirectoryToFileHolder


class RepositoryPublisher(gump.core.actor.AbstractRunActor):
    def __init__(self,run):
        """
            Publish Jars to a Repository
        """
        gump.core.actor.AbstractRunActor.__init__(self,run)
        
        self.repository=run.getOutputsRepository()
        
    def processProject(self,project):
        """
        
        Process a project (i.e. publish it's artifacts to the repository)
        
        """
        
        if project.okToPerformWork() and project.hasOutputs() and project.isRedistributable():      
            groupName = project.getModule().getName()
            
            # If we have a <license name='...
            if project.hasLicense():
                licensePath=os.path.abspath(
                                        os.path.join( project.getModule().getWorkingDirectory(),
                                                project.getLicense() ) )
                                          
                try:
                    # Publish licenses
                    self.repository.publish( groupName, licensePath )            
                except Exception, details:
                    message='Failed to publish license [' + licensePath + '] to repository : ' + str(details)
                    project.addError(message)
                    log.error(message)                     
                                    
            # For all output artifacts (jars)
            for jar in project.getJars():
                # :TODO: Relative to module source?
                jarPath=os.path.abspath(jar.getPath())
                try:
                    # Publish under artifact identifier...
                    self.repository.publish( groupName, jarPath, jar.getId())
                except Exception, details:
                    message='Failed to publish [' + jarPath + '] to repository : ' + str(details)
                    project.addError(message)
                    log.error(message)
            
            # For 'fun' list repository
            listDirectoryToFileHolder( project,
                                   self.repository.getGroupDir(groupName),
                                   gump.utils.file.FILE_TYPE_REPO, 
                                   'list_repo_'+project.getName())
        
  
