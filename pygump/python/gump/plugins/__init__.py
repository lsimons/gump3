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

import sys

class BaseErrorHandler:
    """Base error handler for use with the MulticastPlugin.
    
    This handler just re-raises a caught error.
    """
    def handle(self, visitor, visited_model_object, type, value, traceback):
        """Override this method to be able to swallow exceptions."""
        # TODO this is not properly saving the traceback stack. Highly annoying. Fix it!
        raise type, value

class LoggingErrorHandler:
    """Logging error handler for use with the MulticastPlugin.
    
    This handler logs then just re-raises a caught error.
    """
    def __init__(self, log):
        self.log = log

    def handle(self, visitor, visited_model_object, type, value, traceback):
        """Override this method to be able to swallow exceptions."""
        self.log.exception("%s threw an exception while visiting %s!" % (visitor, visited_model_object))
        raise type, value

class AbstractPlugin:
    """Base class for all plugins.
    
    To create a concrete plugin, implement one or more of these methods:
        
        - initialize()
        - visit_workspace(workspace)
        - visit_repository(repository)
        - visit_module(module)
        - visit_project(project)
        - finalize()
    
    Ordering
    --------
    Each of these methods will be called in a "topologically sorted" order.
    Concretely, this means that:
        
        * initialize will be called first;
        * visit_workspace will be called first;
        * visit_repository will be called before any contained module or
          project is visited;
        * visit_module will be called before any contained project is
          visited;
        * visit_project will be called only after all dependencies of that
          project have already been visited;
        * finalize will be called last.
    
    More concretely, this means plugins usually do not have to worry about
    the correct ordering of events, since this is usually what you want.
    
    Error handling
    --------------
    Plugins are expected to raise an exception (usually gump.model.Error)
    if there is a problem with the model that prevents them from functioning
    as intended. If they are able to proceed but their execution results in
    a failure (which is not uncommon in the gump world at all), the plugin
    should *not* raise an exception but rather annotate the model with the
    information about that exception.
    
    Model annotation
    ----------------
    Plugins are expected to communicate with their environment through reading
    properties from the gump object model or setting properties on that model.
    
    In general, plugins that execute commands are expected to set the return
    code for that command as a "$action_exit_status" property on whatever part
    of the model makes most sense, for example a plugin that executes a Script
    model element should set the "build_exit_status" property on that element.
    
    Also in general, plugins that execute commands are expected to place the
    output (both stdout and stderr) of their commands as a "$action_log"
    property on the relevant part of the model, where "$action" is the
    conceptual task they are performing (update,build,...).
    """
    def __init__(self, log):
        self.log = log
    
    def _initialize(self):
        if not hasattr(self,'initialize'): return        
        if not callable(self.initialize): return        
        self.initialize()
    
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

    def _finalize(self):
        if not hasattr(self,'finalize'): return        
        if not callable(self.finalize): return        
        self.finalize()
    
class MulticastPlugin(AbstractPlugin):
    """Core plugin that redirects visit_XXX calls to other plugins."""
    def __init__(self, plugin_list, error_handler=BaseErrorHandler()):
        self.list = plugin_list
        self.error_handler = error_handler
    
    def initialize(self):
        for visitor in self.list:
            try: visitor._initialize()
            except:
                (type, value, traceback) = sys.exc_info()
                self.error_handler.handle(visitor, "{{{initialization stage}}}", type, value, traceback)

    def visit_workspace(self, workspace):
        for visitor in self.list:
            try: visitor._visit_workspace(workspace)
            except:
                (type, value, traceback) = sys.exc_info()
                self.error_handler.handle(visitor, workspace, type, value, traceback)

    def visit_repository(self, repository):
        for visitor in self.list:
            try: visitor._visit_repository(repository)
            except:
                (type, value, traceback) = sys.exc_info()
                self.error_handler.handle(visitor, repository, type, value, traceback)

    def visit_module(self, module):
        for visitor in self.list:
            try: visitor._visit_module(module)
            except:
                (type, value, traceback) = sys.exc_info()
                self.error_handler.handle(visitor, module, type, value, traceback)

    def visit_project(self, project):
        for visitor in self.list:
            try: visitor._visit_project(project)
            except:
                (type, value, traceback) = sys.exc_info()
                self.error_handler.handle(visitor, project, type, value, traceback)

    def finalize(self):
        for visitor in self.list:
            try: visitor._finalize()
            except:
                (type, value, traceback) = sys.exc_info()
                self.error_handler.handle(visitor, "{{{finalization stage}}}", type, value, traceback)

class LoggingPlugin(AbstractPlugin):
    """Plugin that prints debug messages as it visits model objects."""
    def __init__(self, log):
        self.log = log
    
    def initialize(self):
        self.log.debug("Initializing...")
    
    def visit_workspace(self, workspace):
        self.log.debug("Visiting workspace.")
    
    def visit_repository(self, repository):
        self.log.debug("Visiting repository '%s'." % repository.name)
    
    def visit_module(self, module):
        self.log.debug("Visiting module '%s'." % module.name)
    
    def visit_project(self, project):
        self.log.debug("Visiting project '%s'." % project.name)

    def finalize(self):
        self.log.debug("Finishing up...")
    
