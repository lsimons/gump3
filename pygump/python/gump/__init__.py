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

"""Pygump downloads and compiles source code and interprets the results.

See http://gump.apache.org/ for more information.

Pygump is split into several submodules. The gump.engine module contains
the main() function that creates a gump.engine.Engine instance that is in
control of running the application.

The gump.engine module has several submodules which help with specific
tasks. For example, it has utilities for processing the gump xml metadata
into a DOM tree and into an object-oriented gump.model-based representation.

The gump.util module contains several submodules of its own which are not
tied to the rest of gump. For example, it has utilities for interacting with
a mysql database, for sending and formatting e-mail, etc.

The gump.model module provides an object-oriented way to represent all the
gump metadata.

The gump.plugin module provides several utilities which can be plugged into
the gump engine for additional functionality. Plugins are responsible for all
"side effects" of a gump run. For example, there are plugins to push data into
database, plugins to send e-mails, etc.
"""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"
