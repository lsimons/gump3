#!/usr/bin/env python

# Copyright 2004-2005 The Apache Software Foundation
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

"""Contains several modules which can be plugged into the pygump engine.

A plugin is an instance of a class that extends AbstractPlugin. See the
documentation for AbstractPlugin to learn more about the contracts 
surrounding plugins.
"""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

from gump.model import ModelObject, CvsModule
from gump.model.util import mark_failure, check_failure, mark_skip, check_skip
from gump.model.util import mark_whether_module_was_updated

from gump.plugins import MulticastPlugin, OptimisticLoggingErrorHandler
from gump.plugins.updater import UPDATE_TYPE_CHECKOUT
from gump.plugins.updater import UPDATE_TYPE_UPDATE

class MoreEfficientMulticastPlugin(MulticastPlugin):
    """MulticastPlugin that implements a more efficient build algorithm.

    This plugin detects "failure" for a particular step in the build, and when
    it does, it sometimes skips a few steps.
    
    The following rules are implemented:
      - if a module fails to update, the projects it contains are not built
      - if there were no changes to the module since the previous run, the projects
        it contains are not built
      - if a project fails to build, none of its dependees are built
    
    If an element "fails", its "failed" property will be set to "True" and an
    array named "failure_cause" will be created pointing to the elements that
    "caused" them to fail.
    """
    #def __init__(self, plugin_list):
    #    MulticastPlugin.__init__(self, plugin_list, OptimisticLoggingErrorHandler())
    
    def visit_module(self, module):
        # run the delegates
        try:
            for visitor in self.list:
                visitor._visit_module(module)
        except:
            (type, value, traceback) = sys.exc_info()
            self.error_handler.handle(visitor, module, type, value, traceback)
            mark_failure(module, module.exceptions[len(module.exceptions)-1])
        
        # check for update errors
        if getattr(module, "update_exit_status", False):
            mark_failure(module, module)
            # if module update failed, don't try and attempt to build contained
            # projects either.
            for project in module.projects.values():
                mark_failure(project, module)
        
        # check for changes
        mark_whether_module_was_updated(module)
        if not getattr(module, "was_updated", False):
            for project in module.projects.values():
                mark_skip(project)
            
    def visit_project(self, project):
        # check for dependencies that failed to build
        for relationship in project.dependencies:
            if check_failure(relationship.dependency):
                mark_failure(project, relationship)

        # don't build if its not going to do any good
        if not check_failure(project) and not check_skip(project):
            try:
                for visitor in self.list:
                    visitor._visit_project(project)
            except:
                (type, value, traceback) = sys.exc_info()
                self.error_handler.handle(visitor, project, type, value, traceback)
                mark_failure(project, project.exceptions[len(project.exceptions)-1])
            
            # blame commands that went awry
            for command in project.commands:
                if getattr(command, "build_exit_status", False):
                    mark_failure(command, command)
                    mark_failure(project, command)
