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

from gump import log

from gump.core.model.workspace import CommandWorkItem, execute, \
    REASON_UPDATE_FAILED, STATE_FAILED, STATE_SUCCESS, WORK_TYPE_UPDATE
from gump.core.run.gumprun import RunSpecific

###############################################################################
# Classes
###############################################################################
class ScmUpdater(RunSpecific):
    """
    Base class for a SCM specific updaters.
    
    Provides helpers and template method implementations.
    """
    
    def __init__(self, run):
        RunSpecific.__init__(self, run)

    #
    # "public" interface of ScmUpdater
    #

    def preview(self, module):
        """
        Supposed to preview what needs to be done.

        For most SCMs it doesn't say much and this method is never
        called during a normal Gump run.
        """
        (cmd, isUpdate) = self.getCommandAndType(module)
        if cmd:
            cmd.dump()

    def updateModule(self, module):
        """
        Performs a fresh check-out or an update of an existing wrokspace.
        """

        log.info('Perform ' + module.getScm().getScmName() + \
                     ' Checkout/Update on #[' + `module.getPosition()` + \
                     '] : ' + module.getName())
    
        (cmd, isUpdate) = self.getCommandAndType(module)

        if cmd:
            if isUpdate:
                log.debug(module.getScm().getScmName() + " Module Update : " + \
                              module.getName() + ", Repository Name: " + \
                              module.repository.getName())
            else:
                log.debug(module.getScm().getScmName() + \
                              " Module Checkout : " + module.getName() + \
                              ", Repository Name: " + \
                              module.repository.getName())

            # Execute the command and capture results        
            cmdResult = execute(cmd, module.getWorkspace().tmpdir)
      
            # Store this as work, on both the module and (cloned) on the repo
            work = CommandWorkItem(WORK_TYPE_UPDATE, cmd, cmdResult)
            module.performedWork(work)
            module.repository.performedWork(work.clone())
      
            # Update Context w/ Results  
            if not cmdResult.isOk():              
                log.error('Failed to checkout/update module: ' + module.name)   

                #
                # Here the live branch differs from trunk: while live
                # will mark the module as failed (and not build any
                # projects contained in it), live will go on if the
                # directory exists and assume it is a transient error
                #
                if not isUpdate:     
                    module.changeState(STATE_FAILED, REASON_UPDATE_FAILED)
                else:
                    module.addError('*** Failed to update from source control.' \
                                        + 'Stale contents ***')
                        
                    # Black mark for this repository
                    repository = module.getRepository()
                    repository.addError('*** Failed to update %s from source' + \
                                            ' control. Stale contents ***' \
                                            % module.getName())
                                        
                    # Kinda bogus, but better than nowt (for now)
                    module.changeState(STATE_SUCCESS, REASON_UPDATE_FAILED)

            else:
                module.changeState(STATE_SUCCESS)       

            return module.okToPerformWork()

        log.error("Don't know how to to checkout/update module: " + \
                      module.name)   
        module.changeState(STATE_FAILED, REASON_UPDATE_FAILED)
        return False

    #
    # helpers
    #

    def shouldBeQuiet(self, module):
        """
        Whether the configuration asks for a quiet update
        (it does so by default)
        """
        return not module.isDebug() \
            and not module.isVerbose() \
            and not module.getScm().isDebug() \
            and not module.getScm().isVerbose()


    def getCommandAndType(self, module):
        """
        Checks whether an update or a fresh checkout is needed and
        returns a command to perform the required action.
        
        Returns a tuple (command, isUpdate)
        """
        exists = os.path.exists(module.getSourceControlStagingDirectory())

        cmd = None
        if exists:
            cmd = self.getUpdateCommand(module)
        else:
            cmd = self.getCheckoutCommand(module)
        return (cmd, exists)


    #
    # methods that should be overridden in subclasses
    #

    def getCheckoutCommand(self, module):
        """
        Create the command needed to obtain a fresh working copy.
        """
        return None

    def getUpdateCommand(self, module):
        """
        Create the command needed to update an existing working copy.
        """
        return None

