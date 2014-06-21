#!/usr/bin/env python

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

import sys
from gump.core.config import default
from gump.core.loader.loader import WorkspaceLoader
from gump.core.run.gumprun import GumpRun

def write_to_dot_file(gump_set, dot_file_name):
    """
    Writes a dependency graph for the given GumpSet to the named file
    using the DOT language.
    """
    hull = set(p.getName() for p in gump_set.getProjects())

    dot = open(dot_file_name, "w")
    dot.write("digraph {\n")
    for project in gump_set.getProjects():
        _write_edges_for_project(project, dot, hull)
    dot.write("}\n")

def _write_edges_for_project(project, dot, hull):
    """
    Writes all edges starting in project and may recurse into all
    dependencies unless they are already contained in the set of
    projects to visit/visited
    """
    for dep in project.getDirectDependencies():
        _write_edge_and_maybe_recurse(project, dep.getProject(), '', dot, hull)
    for dep in project.get_removed_dependencies():
        _write_edge_and_maybe_recurse(project, dep.getProject(),
                                      ' [color = red]', dot, hull)

def _write_edge_and_maybe_recurse(left, right, style, dot, hull):
    """
    Writes a single edgre from left to right and may recurse into
    right unless it is already contained in the set of projects to
    visit/visited
    """
    dot.write('\t"%s" -> "%s"%s\n' % (left.getName(), right.getName(), style))
    if not right.getName() in hull:
        hull.add(right.getName())
        _write_edges_for_project(right, dot, hull)

if __name__ == '__main__':
    if not len(sys.argv) in [3, 4]:
        print "requires two args: workspace and outputfile and has one " + \
            "optional: project"
        exit(1)
    default.date_s = default.datetime.strftime('YYYYMMDD')
    default.datetime_s = default.datetime.strftime('YYYYMMDD-hhmmss')
    WORKSPACE = WorkspaceLoader().load(sys.argv[1])
    write_to_dot_file(GumpRun(WORKSPACE,
                              len(sys.argv) == 4 and sys.argv[3] or None)
                      .getGumpSet(),
                      sys.argv[2])
