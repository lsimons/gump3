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

import os.path

from gump.core.model.workspace import Cmd
from gump.core.update.scmupdater import ScmUpdater, should_be_quiet
from gump.tool.integration.cvs import readLogins, loginToRepositoryOnDemand
from gump.util.tools import tailFileToString

def maybe_add_tag(module, cmd):
    # Determine if a tag is set, on <cvs or on <module
    tag = None
    if module.getScm().hasTag():
        tag = module.getScm().getTag()
    elif module.hasTag():
        tag = module.getTag()
    if tag:
        cmd.addParameter('-r', tag, ' ')

def setup_common_parameters(module, cmd):
    if should_be_quiet(module):    
        cmd.addParameter('-q')
    elif module.isDebug():
        cmd.addParameter('-t')
    # Request compression
    cmd.addParameter('-z3')
          
    # Set the CVS root
    cmd.addParameter('-d', module.getScm().getCvsRoot())    

def error_unless_file_content_matches(cvsdir, filename, expected_content,
                                      prop):
    f = os.path.join(cvsdir, filename)
    if not os.path.exists(f):
        return (False, 'workspace doesn\'t contain a ' + filename + ' file')
    actual = tailFileToString(f, 1).rstrip()
    if actual != expected_content:
        return (False, 'expected ' + prop + ' to be \'' + \
                        expected_content + '\' but is \'' + actual + '\'')
    return None

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
        setup_common_parameters(module, cmd)
          
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
        setup_common_parameters(module, cmd)
          
        # Do a cvs update
        cmd.addParameter('update')
        cmd.addParameter('-P')
        cmd.addParameter('-d')
        maybe_add_tag(module, cmd)

        return cmd
    
    def workspaceMatchesModule(self, module):
        """
        look for a CVS directory and the files contained therein, try to match
        the contents of said files
        """
        cvsdir = os.path.join(module.getSourceControlStagingDirectory(),
                               'CVS')
        if not os.path.exists(cvsdir):
            return (False, 'workspace doesn\'t contain a CVS directory')

        root = error_unless_file_content_matches(cvsdir, 'Root',
                                                 module.getScm().getCvsRoot(),
                                                 'CVSROOT')
        if root:
            return root

        expected_module = module.getName()
        if module.getScm().hasModule():
            expected_module = module.getScm().getModule()
        rep = error_unless_file_content_matches(cvsdir, 'Repository',
                                                expected_module, 'Module')
        if rep:
            return rep

        if module.getScm().hasTag() or module.hasTag():
            expected_tag = 'T'
            if module.getScm().hasTag():
                expected_tag += module.getScm().getTag()
            elif module.hasTag():
                expected_tag += module.getTag()
            tag = error_unless_file_content_matches(cvsdir, 'Tag',
                                                    expected_tag, 'Tag')
            if tag:
                return tag

        elif os.path.exists(os.path.join(cvsdir, 'Tag')):
            return (False, 'workspace is tagged with \'' + \
                        tailFileToString(os.path.join(cvsdir, 'Tag'),
                                         1).rstrip() + \
                        '\' but shouldn\'t have a tag at all.')

        return (True, '')

    def maybeLogin(self, module):
        repository = module.repository
        root = module.getScm().getCvsRoot()

        # Provide CVS logins, if not already there
        loginToRepositoryOnDemand(repository, root, self.logins)

