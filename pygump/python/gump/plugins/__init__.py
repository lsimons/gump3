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

"""Contains several modules which can be plugged into the pygump engine."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

class BaseErrorHandler:
    """Base error handler for use with the MulticastPlugin.
    
    This handler just re-raises a caught error.
    """
    def handle(visitor, error, visited_model_object):
        """Override this method to be able to swallow exceptions."""
        raise error

class LoggingErrorHandler:
    """Logging error handler for use with the MulticastPlugin.
    
    This handler logs then just re-raises a caught error.
    """
    def __init__(self, log):
        self.log = log

    def handle(visitor, error, visited_model_object):
        """Override this method to be able to swallow exceptions."""
        self.log.exception("%s threw an exception while visiting %s!" % (visitor, visited_model_object))
        raise error

class AbstractPlugin:
    """Base class for all plugins.
    
    To create a concrete plugin, implement one or more of these methods:
        
        - visit_workspace(workspace)
        - visit_repository(repository)
        - visit_module(module)
        - visit_project(project)
    
    Each of these methods will be called in a "topologically sorted" order.
    Concretely, this means that:
        
        * visit_workspace will be called first;
        * visit_repository will be called before any contained module or
          project is visited;
        * visit_module will be called before any contained project is
          visited;
        * visit_project will be called only after all dependencies of that
          project have already been visited.
    
    More concretely, this means plugins usually do not have to worry about
    the correct ordering of events, since this is usually what you want.
    """
    def __init__(self, log):
        self.log = log
    
    def _visit_workspace(self, workspace):
        if not hasattr(self,'visit_workspace'): return        
        if not callable(self.visit_workspace): return        
        self.visit_workspace(workspace)
    
    def _visit_repository(self, repository):
        if not hasattr(self,'visit_repository'): return        
        if not callable(self.visit_repository): return        
        self.visit_repository(repository)
    
    def _visit_module(self, module):
        if not hasattr(self,'visit_module'): return        
        if not callable(self.visit_module): return        
        self.visit_module(module)
    
    def _visit_project(self, project):
        if not hasattr(self,'visit_project'): return        
        if not callable(self.visit_project): return        
        self.visit_project(project)

class MulticastPlugin(AbstractPlugin):
    """Core plugin that redirects visit_XXX calls to other plugins."""
    def __init__(self, plugin_list, error_handler=BaseErrorHandler()):
        self.list = plugin_list
        self.error_handler = error_handler
    
    def visit_workspace(self, workspace):
        for visitor in self.list:
            try: visitor._visit_workspace(workspace)
            except: self.error_handler.handle(visitor, error, workspace)

    def visit_repository(self, repository):
        for visitor in self.list:
            try: visitor._visit_repository(repository)
            except: self.error_handler.handle(visitor, error, repository)

    def visit_module(self, module):
        for visitor in self.list:
            try: visitor._visit_module(module)
            except: self.error_handler.handle(visitor, error, module)

    def visit_project(self, project):
        for visitor in self.list:
            try: visitor._visit_project(project)
            except: self.error_handler.handle(visitor, error, project)

class LoggingPlugin(AbstractPlugin):
    """Plugin that prints debug messages as it visits model objects."""
    def __init__(self, log):
        self.log = log
    
    def visit_workspace(self, workspace):
        self.log.debug("Visiting workspace.")
    
    def visit_repository(self, repository):
        self.log.debug("Visiting repository '%s'." % repository.name)
    
    def visit_module(self, module):
        self.log.debug("Visiting module '%s'." % module.name)
    
    def visit_project(self, project):
        self.log.debug("Visiting project '%s'." % project.name)
