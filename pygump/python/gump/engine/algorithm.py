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

"""Contains several algorithms which can be plugged into the Walker.

Algorithms are a sort of "super-plugins" which are responsible for

 a) actually firing up other plugins
 b) implementing the "build algorithm"

The walker handles dependency ordering and a depth-first traversal,
after that its up to the algorithm implementation to provide all other
build intelligence.

The algorithm code is very similar to that of a plugin; make sure to
read the plugin documentation for some additional details.
"""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import sys
import re

from gump.util import ansicolor
from gump.model import ModelObject, CvsModule, ExceptionInfo, Jar
from gump.model.util import mark_failure, check_failure, mark_skip, check_skip
from gump.model.util import mark_whether_module_was_updated
from gump.model.util import mark_stale_prereq
from gump.model.util import check_module_update_failure
from gump.model.util import store_exception

from gump.model.util import UPDATE_TYPE_CHECKOUT, UPDATE_TYPE_UPDATE

class BaseErrorHandler:
    """Base error handler for use with the various algorithms.
    
    This handler just re-raises a caught error.
    """
    def handle(self, visitor, visited_model_object, type, value, traceback):
        """Override this method to be able to swallow exceptions."""
        # TODO this is not properly saving the traceback stack. Highly annoying. Fix it!
        raise type, value

class LoggingErrorHandler:
    """Logging error handler for use with the various algorithms.
    
    This handler logs then just re-raises a caught error.
    """
    def __init__(self, log):
        assert hasattr(log, "exception")
        assert callable(log.exception)
        
        self.log = log

    def handle(self, visitor, visited_model_object, type, value, traceback):
        """Log the exception, then re-raise it."""
        self.log.exception("%s threw an exception while visiting %s!" % \
                           (visitor, visited_model_object))
        raise type, value

class OptimisticLoggingErrorHandler:
    """Logging error handler for use with the various algorithms.
    
    This handler logs a caught error then stores it on the model.
    """
    def __init__(self, log):
        assert hasattr(log, "exception")
        assert callable(log.exception)
        
        self.log = log

    def handle(self, visitor, visited_model_object, type, value, traceback):
        """Swallow the exception, storing it with the model."""
        self.log.exception("%s%s threw an exception while visiting %s!%s" % \
                (ansicolor.Bright_Red, visitor, visited_model_object, ansicolor.Black))
        if isinstance(visited_model_object, ModelObject):
            store_exception(visited_model_object, type, value, traceback)

class DumbAlgorithm:
    """"Core" algorithm that simply redirects all visit_XXX calls to other plugins."""
    def __init__(self, plugin_list, error_handler=BaseErrorHandler()):
        assert isinstance(plugin_list, list)
        for visitor in plugin_list:
            assert hasattr(visitor, "_initialize")
            assert callable(visitor._initialize)
            assert hasattr(visitor, "_visit_workspace")
            assert callable(visitor._visit_workspace)
            assert hasattr(visitor, "_visit_repository")
            assert callable(visitor._visit_repository)
            assert hasattr(visitor, "_visit_module")
            assert callable(visitor._visit_module)
            assert hasattr(visitor, "_visit_project")
            assert callable(visitor._visit_project)
            
        self.list = plugin_list
        self.error_handler = error_handler
    
    def _initialize(self):
        for visitor in self.list:
            try: visitor._initialize()
            except:
                (type, value, traceback) = sys.exc_info()
                self.error_handler.handle(visitor, \
                        "{{{initialization stage}}}", type, value, traceback)

    def _visit_workspace(self, workspace):
        # DEBUG TIP: This is a good function to monitor if you want to figure
        #   out flow control
        for visitor in self.list:
            try: visitor._visit_workspace(workspace)
            except:
                (type, value, traceback) = sys.exc_info()
                self.error_handler.handle(visitor, workspace, type, value, traceback)

    def _visit_repository(self, repository):
        # DEBUG TIP: This is a good function to monitor if you want to figure
        #   out flow control
        for visitor in self.list:
            try: visitor._visit_repository(repository)
            except:
                (type, value, traceback) = sys.exc_info()
                self.error_handler.handle(visitor, repository, type, value, traceback)

    def _visit_module(self, module):
        # DEBUG TIP: This is a good function to monitor if you want to figure
        #   out flow control
        for visitor in self.list:
            try: visitor._visit_module(module)
            except:
                (type, value, traceback) = sys.exc_info()
                self.error_handler.handle(visitor, module, type, value, traceback)

    def _visit_project(self, project):
        # DEBUG TIP: This is a good function to monitor if you want to figure
        #   out flow control
        for visitor in self.list:
            try: visitor._visit_project(project)
            except:
                (type, value, traceback) = sys.exc_info()
                self.error_handler.handle(visitor, project, type, value, traceback)

    def _finalize(self, workspace):
        # DEBUG TIP: This is a good function to monitor if you want to figure
        #   out flow control
        for visitor in self.list:
            try:
                visitor._finalize(workspace)
            except:
                (type, value, traceback) = sys.exc_info()
                self.error_handler.handle(visitor, \
                        "{{{finalization stage}}}", type, value, traceback)

class NoopPersistenceHelper:
    def store_previous_builds(self, *args):
        pass
    
    def use_previous_build(self, *args):
        pass
    
    def has_previous_build(self, *args):
        return False
    
    def stop_using_previous_build(self, *args):
        pass
    
    def save_workspace(self, *args):
        pass

DEFAULT_PROJECT_REGEX = ".*"
DEFAULT_PROJECT_LIST = []
DEFAULT_PROJECT_LIST.append(DEFAULT_PROJECT_REGEX)

class MoreEfficientAlgorithm(DumbAlgorithm):
    """Algorithm that implements a more efficient build algorithm.

    This algorithm detects "failure" for a particular step in the build, and when
    it does, it sometimes skips a few steps.
    
    The following rules are implemented:
      - if a module fails to update, the projects it contains are not built
      - if there were no changes to the module since the previous run, the projects
        it contains are not built
      - if a project fails to build
        - if there is a "previous build"
          - its dependees are flagged "failed prereq" and built against that
        - otherwise none of its dependees are built
    
    If an element "fails", its "failed" property will be set to "True" and an
    array named "failure_cause" will be created pointing to the elements that
    "caused" them to fail.
    """
    def __init__(self, plugin_list, error_handler=BaseErrorHandler(),
                 persistence_helper=NoopPersistenceHelper(), project_list=DEFAULT_PROJECT_LIST):
        DumbAlgorithm.__init__(self, plugin_list, error_handler)
        
        assert hasattr(persistence_helper, "use_previous_build")
        assert callable(persistence_helper.use_previous_build)
        self.persistence_helper = persistence_helper
          
        assert isinstance(project_list, list)
        for p in project_list:
            assert isinstance(p, basestring)

        self.project_list = project_list
        self.project_match_list = [re.compile(p) for p in project_list]
        self.project_model_list = []
        self.module_model_list = []
        
    def _visit_workspace(self, workspace):
        for k,v in workspace.projects.iteritems():
            for x in self.project_match_list:
                if x.match(k):
                    self.project_model_list.append(v)
                    break
        
        for p in self.project_model_list:
            if not p.module in self.module_model_list:
                self.module_model_list.append(p.module)
        
    def _visit_module(self, module):
        # DEBUG TIP: This is a good function to monitor if you want to figure
        #   out flow control
        # run the delegates
        try:
            if not module in self.module_model_list:
                mark_skip(module)
                return
            
            for visitor in self.list:
                visitor._visit_module(module)
        except:
            (type, value, traceback) = sys.exc_info()
            self.error_handler.handle(visitor, module, type, value, traceback)
            mark_failure(module, module.exceptions[len(module.exceptions)-1])
        
        # check for update errors
        if check_module_update_failure(module):
            # if module update failed, don't try and attempt to build contained
            # projects either.
            for project in module.projects.values():
                mark_failure(project, module)
        
        # check for changes
        mark_whether_module_was_updated(module)
        #TODO enable
        #if not getattr(module, "was_updated", False):
        #    for project in module.projects.values():
        #        print "Line 170: %s was not updated!" % module.name
        #        mark_skip(project)
            
    def _visit_project(self, project):
        # DEBUG TIP: This is a good function to monitor if you want to figure
        #   out flow control
        # check for dependencies that failed to build
        
        if not project in self.project_model_list:
            mark_skip(project)
            return
        
        for relationship in project.dependencies:
            if check_failure(relationship.dependency):
                # if there is a "last successful build", we'll use that
                if self.persistence_helper.has_previous_build(project):
                    self.persistence_helper.use_previous_build(relationship.dependency)
                    mark_stale_prereq(project, relationship.dependency)
                else:
                    # otherwise, we're doomed!
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
                    mark_failure(project, command)
    
    def _finalize(self, workspace):
        DumbAlgorithm._finalize(self, workspace)
        for project in workspace.projects:
            self.persistence_helper.stop_using_previous_build(project)
        self.persistence_helper.store_previous_builds(workspace)
        self.persistence_helper.save_workspace(workspace)
        self.project_model_list = []
        self.module_model_list = []
