#!/usr/bin/python


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

from gump import log
from gump.core.model.workspace import Cmd
from gump.core.update.scmupdater import ScmUpdater

###############################################################################
# Classes
###############################################################################

class SvnUpdater(ScmUpdater):
    """
    Updater for Subversion
    """
    
    def __init__(self, run):
        ScmUpdater.__init__(self, run)


    def getCheckoutCommand(self, module):
        """
            Build the appropriate SVN command for checkout
        """
        return self.getCommand(module, False)

    def getUpdateCommand(self, module):
        """
            Build the appropriate SVN command for update
        """
        return self.getCommand(module, True)

    def getCommand(self, module, forUpdate):
        """
            Build the appropriate SVN command for checkout or update
        """
        repository = module.repository
        url = module.getScm().getRootUrl()
      
        log.debug("SVN URL: [" + url + "] on Repository: "\
                      + repository.getName())
     
        #
        # Prepare SVN checkout/update command...
        # 
        cmd = Cmd('svn', 'update_'+module.getName(), 
                  module.getWorkspace().getSourceControlStagingDirectory())
       
        #
        # Be 'quiet' (but not silent) unless requested otherwise.
        #
        if self.shouldBeQuiet(module):    
            cmd.addParameter('--quiet')
                  
        if forUpdate:
            cmd.addParameter('update')
        else:
            cmd.addParameter('checkout', url)
       
        #
        # Request non-interactive
        #
        cmd.addParameter('--non-interactive')

        # Optional username/password
        if repository.hasUser():
            cmd.addParameter('--username', repository.getUser())    
        if repository.hasPassword():
            cmd.addParameter('--password', repository.getPassword())
            
        #
        # If module name != SVN directory, tell SVN to put it into
        # a directory named after our module
        #
        if not module.getScm().hasDir() or \
           not module.getScm().getDir() == module.getName():
                cmd.addParameter(module.getName())
        
        return cmd
