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

"""
  Gump XML model.

  It contains a sax dispatcher tool, a dependency
  walker, and an object model (GOM) which is built from an xmlfile using
  the sax dispatcher.

  The idea is that a subclass of GumpModelObject is used for each of the various
  xml tags which can appear in a gump profile, with a saxdispatcher
  generating a tree of GumpModelObject objects from the profile, dynamically
  merging as it finds href references.

  You can then use the dependencies() method to get an ordered, flat vector
  of the projects in the profile.

  Then there's some basic procedures to work with the GOM, like load().

  For basic usage patterns, look at the gump.view module or the gump.core.build
  module.
"""

###############################################################################
# Initialize
###############################################################################

# tell Python what modules make up the gump.core.model package
__all__ = ["misc","state", "output", \
    "object","project","module","workspace","repository", \
    "builder","profile",]

