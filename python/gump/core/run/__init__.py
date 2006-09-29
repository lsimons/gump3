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

#
# $Header: /home/stefano/cvs/gump/python/gump.core.run/__init__.py,v 1.1 2004/07/19 16:07:54 ajack Exp $
# 

"""
Gump works in a batch mode. Doing one iteration of cvs and svn updates
and then building all the different projects is called a single "gump
run". Such a run is modelled by gump.core.run.gumprun.GumpRun.

A run is split into several stages:

    1) setup work (parsing commands, merging xml files, etc)
    2) general build work (initializing and setting up helpers,
       performing per-run tasks)
    3) per-module and per-project work (ie updates and builds
       and whatever different "actors" do on a per-module or
       per-project basis)
    3) post-build work (cleaning up, sending out e-mail, etc)

Each of these stages is handled by the gump.core.runner package. The
gump.core.run package defines what should happen during any such run,
and is the place where the runner and actors keep track of what is
going on.
"""

# tell Python what modules make up the gump.run package
__all__ = ["actor","gumpenv","gumprun","options", "gumpset"]
