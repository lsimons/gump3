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

"""This module verifies a gump object model."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import logging
import os
import sys

from xml import dom
from xml.dom import minidom

from gump.model import *

from gump.engine import EngineError
from gump.util import ansicolor

class VerificationError(EngineError):
    """Error raised by the verifier if the model is not valid."""
    pass

class CyclicDependencyError(VerificationError):
    """Error raised by the verifier if the model contains one or more cyclic
    dependencies. The cycles property will contain an array of cycles, where
    a cycle again is an array of projects that together make up a cycle."""
    #TODO think about error hierarchies in gump and decide if this is the way
    #     we want to implement them
    pass

def print_cyclic_trace(cycles, handler):
    for cycle in cycles: # isn't there a level of nesting too much here???
        for chain in cycle:
            msg = "  "
            for project in chain:
                msg += "%s --> " % project.name
            msg = ansicolor.Bright_Red + msg[:-5] + ansicolor.Black
            handler(msg)
    
class AbstractErrorHandler:
    """Base class for supporting configurable error recovery. Instead of
    raising exceptions, supportive classes will pass the error to an instance
    of this class. This allows clients to recover from errors more gracefully.
    This default implementation tries to call a handleError() method on
    itself, and raises the error if that is not possible.
    
    Subclasses should implement a handleError(error) method, where the
    provided error argument is normally an instance of Exception.
    
    This setup is similar to that used by the SAX libraries."""
    #TODO maybe move this elsewhere?
    def _handleError(self):
        if not hasattr(self, 'handleError'): raise
        if not callable(self.handleError): raise
        self.handleError()

class LoggingErrorHandler(AbstractErrorHandler):
    """Naive error handler which logs all errors and then swallows them."""
    def __init__(self, log):
        self.log = log

    def handleError(self):
        errorType = sys.exc_info()[0]
        if errorType is CyclicDependencyError:
            errorValue = sys.exc_info()[1]
            self.log.error("The following cyclic dependencies were found:")
            print_cyclic_trace(errorValue, self.log.error)
            self.log.error("The projects involved will not be built!")
        else:
            raise

class Verifier:
    """Determines whether a finished gump model conforms to certain contracts.
    
    Those contracts are not currently completely specified, but it is somewhat
    possible to digest them from the model documentation. However, the
    verifier itself together with its unit tests is probably the only "hard"
    specification of those contracts."""
    def __init__(self, walker, errorHandler=AbstractErrorHandler()):
        assert hasattr(walker, "walk")
        assert callable(walker.walk)
        
        self.walker = walker
        self.errorHandler = errorHandler
        
    def verify(self, workspace):
        """Sends VerificationError objects to the errorHandler argument if the
        provided model contains errors. If no errorHandler is provided, the
        exceptions are 'raise'd."""
        from gump.plugins import AbstractPlugin
        visitor = AbstractPlugin(None)
        (visited_repositories, visited_modules, visited_projects) = self.walker.walk(workspace, visitor)
        
        if len(visited_projects) != len(workspace.projects):
            # some projects weren't visited! Those indicate cycles...
            unvisited = []
            
            for p in workspace.projects.values():
                if not p in visited_projects:
                    unvisited.append(p)
            
            cycles = self._find_cycles(unvisited[:])
            workspace.cycles = cycles
            workspace.unvisited = unvisited
            
            try:
                raise CyclicDependencyError, cycles
            except:
                self.errorHandler._handleError()
    
    def _find_cycles(self,projects):
        """Brute-force find all cycles.
        
        1) depth-first traverse all paths extending from each project
           (the "needle")
        2) use a stack for documenting the current path traversal
        2) look for cycles in those paths involving the needle
           2.a) avoid traversing cycles not involving the needle
                by coloring nodes on visit, making sure to visit
                them only once
           2.b) store a cycle when its found
        3) return an array containing an array of cycles"""
        cycles = []
        for project in projects:
            needle = project
            visited = []
            stack = [project]
            self._visit(project,visited,stack,needle,cycles)
        
        return cycles
    
    def _visit(self,project,visited,stack,needle,cycles):
        # debuggging statements...
        #msg = "Visiting: %s, stack=[" % project.name
        #for p in stack:
        #    msg += p.name + ","
        #msg = msg[:-1] + "]"
        #print msg
        
        visited.append(project)
        for relationship in project.dependencies:
            dependency = relationship.dependency
            stack.append(dependency)
            if dependency == needle: # cycle involving needle!
                cycles.append(stack[:])
                visited.append(dependency)
            else:
                if not dependency in visited:
                    self._visit(dependency,visited,stack,needle,cycles)

            stack.pop() # get rid of this dependency, we'll be looking
                        # at the next dependency in the next iteration of
                        # the for loop
