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

    Actor to publish artifacts to a repository 
    
"""

import os

from gump import log

import gump.core.run.gumprun
import gump.core.run.actor

import gump.util.file
from gump.util.tools import listDirectoryToFileHolder


class RepositoryPublisher(gump.core.run.actor.AbstractRunActor):
    def __init__(self,run):
        """
            Publish Jars to a Repository
        """
        gump.core.run.actor.AbstractRunActor.__init__(self,run)
        
        self.repository=run.getOutputsRepository()
        
    def processProject(self,project):
        """
        
        Process a project (i.e. publish it's artifacts to the repository)
        
        """
        
        if project.okToPerformWork() and project.hasOutputs() and project.isRedistributable():      
            groupName = project.getArtifactGroup() 
            
            # If we have a <license name='...
            if project.hasLicense():
                licensePath=os.path.abspath(
                                        os.path.join( project.getModule().getWorkingDirectory(),
                                                project.getLicense() ) )
                                          
                try:
                    # Publish licenses
                    self.repository.publish( groupName, licensePath )            
                except Exception as details:
                    message='Failed to publish license [' + licensePath + '] to repository : ' + str(details)
                    project.addError(message)
                    log.error(message)                     
                                    
            # For all output artifacts (outputs)
            for output in project.getOutputs():
                # :TODO: Relative to module source?
                outputPath=os.path.abspath(output.getPath())
                try:
                    # Publish under artifact identifier...
                    self.repository.publish( groupName, outputPath, output.getId())
                except Exception as details:
                    message='Failed to publish [' + outputPath + '] to repository : ' + str(details)
                    project.addError(message)
                    log.error(message)
            
            # For 'fun' list repository
            listDirectoryToFileHolder( project,
                                   self.repository.getGroupDir(groupName),
                                   gump.util.file.FILE_TYPE_REPO, 
                                   'list_repo_'+project.getName())
                                   
        else:
            ok = project.okToPerformWork()
            has = project.hasOutputs()
            redist = project.isRedistributable()
        
            log.debug('Not publishing because [ok=%s,has outputs=%s,redistributable=%s]' \
                        % (ok,has,redist))
        
  
