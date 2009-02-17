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

from gump.core.model.workspace import Cmd
from gump.core.update.scmupdater import ScmUpdater
from gump.tool.integration.cvs import readLogins, loginToRepositoryOnDemand

def maybe_add_tag(module, cmd):
    # Determine if a tag is set, on <cvs or on <module
    tag = None
    if module.getScm().hasTag():
        tag = module.getScm().getTag()
    elif module.hasTag():
        tag = module.getTag()
    if tag:
        cmd.addParameter('-r', tag, ' ')

###############################################################################
# Classes
###############################################################################

class CvsUpdater(ScmUpdater):
    """
    Updater for CVS
    """
    
    def __init__(self, run):
        ScmUpdater.__init__(self, run)

        #
        # A stash of known logins.
        #
        self.logins = readLogins()

    def getCheckoutCommand(self, module):
        """
            Build the appropriate CVS command for checkout
        """
        self.maybeLogin(module)
    
        cmd = Cmd('cvs', 'update_' + module.getName(),
                  module.getWorkspace().getSourceControlStagingDirectory())
        self.setupCommonParameters(module, cmd)
          
        # do a cvs checkout
        cmd.addParameter('checkout')
        cmd.addParameter('-P')
        maybe_add_tag(module, cmd)

        if not module.getScm().hasModule() or \
           not module.getScm().getModule() == module.getName(): 
            cmd.addParameter('-d', module.getName(), ' ')

        if module.getScm().hasModule():
            cmd.addParameter(module.getScm().getModule())
        else:
            cmd.addParameter(module.getName())            

        return cmd

    def getUpdateCommand(self, module):
        """
            Build the appropriate CVS command for update
        """

        self.maybeLogin(module)
    
        cmd = Cmd('cvs', 'update_' + module.getName(),
                  module.getSourceControlStagingDirectory())
        self.setupCommonParameters(module, cmd)
          
        # Do a cvs update
        cmd.addParameter('update')
        cmd.addParameter('-P')
        cmd.addParameter('-d')
        maybe_add_tag(module, cmd)

        return cmd
    
    def setupCommonParameters(self, module, cmd):
        if self.shouldBeQuiet(module):    
            cmd.addParameter('-q')
        elif module.isDebug():
            cmd.addParameter('-t')
        # Request compression
        cmd.addParameter('-z3')
          
        # Set the CVS root
        cmd.addParameter('-d', module.getScm().getCvsRoot())    

    def maybeLogin(self, module):
        repository = module.repository
        root = module.getScm().getCvsRoot()

        # Provide CVS logins, if not already there
        loginToRepositoryOnDemand(repository, root, self.logins)

