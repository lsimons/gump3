#!/usr/bin/env python

# Copyright 2005 The Apache Software Foundation
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

"""This module provides facilities for walking a gump model."""

__copyright__ = "Copyright (c) 2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

class Walker:
    """Walks a gump tree using topsort.

    Visits projects in dependency order, and just-in-time visits the modules
    that contain those projects, and just-in-time visits the repositories
    that contain those projects. Before all that, it visits the workspace
    itself.
    
    Note that the walker will fail to visit all projects that are part of a
    cyclic dependency chain or that depend on projects in such a cyclic
    dependency chain.
    """
    def __init__(self, log):
        assert hasattr(log,"debug")
        assert callable(log.debug)
        
        self.log = log
    
    def walk(self, workspace, visitor):
        """Walks a gump tree using inverted topsort.
        
        Arguments:
            - workspace -- the workspace to walk
            - visitor -- the core plugin to send messages to

        Returns a tuple containing the repositories visited, the modules
        visited, and the projects visited, in the order they were visited.
        """
        visited_repositories = []
        visited_modules = []
        visited_projects = []

        visitor._initialize()
        visitor._visit_workspace(workspace)
        list = self._topsort_projects(workspace)
        
        for project in list:
            if not project.module in visited_modules:
                if not project.module.repository in visited_repositories:
                    visitor._visit_repository(project.module.repository)
                    visited_repositories.append(project.module.repository)
                visitor._visit_module(project.module)
                visited_modules.append(project.module)
            
            visitor._visit_project(project)
            visited_projects.append(project)
        
        visitor._finalize()
        return (visited_repositories, visited_modules, visited_projects)
    
    def _topsort_projects(self, workspace):
        """Does a topological sort of the projects in a workspace.
        
        The vertices are of course the projects, and the edges are the
        dependencies between those projects.
        """
        self._set_indegrees(workspace)
        # using a stack *should* ensure depth-first
        stack = self._get_initial_stack(workspace)
        
        list = []

        while len(stack) > 0:
            project = stack.pop()
            list.append(project)
            
            for dependee in project.dependees:
                dependee.dependee.indegree -= 1
                if dependee.dependee.indegree == 0:
                    stack.append(dependee.dependee)
    
        self._clear_indegrees(workspace)
        return list

    def _set_indegrees(self, workspace):
        """Set the number of in-degrees for each project.
        
        The number of in-degrees is a measure of how many
        dependecies a project has. The key bit is that the
        walker decreases the number of in-degrees for each
        project as a dependee is handled.
        """
        for project in workspace.projects.values():
            project.indegree = 0
        
        for dependency in workspace.dependencies:
            dependency.dependee.indegree += 1
    
    def _clear_indegrees(self, workspace):
        """Removes the in-degrees property from each project."""
        
        for project in workspace.projects.values():
            del project.indegree

    def _get_initial_stack(self, workspace):
        """Get the projects with an in-degree of 0.
        
        In other words, get the projects without dependecies.
        """
        stack = []
        for project in workspace.projects.values():
            if project.indegree == 0:
                stack.append(project) 
        
        return stack    
