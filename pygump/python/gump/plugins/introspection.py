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

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import platform

from gump.plugins import AbstractPlugin

class IntrospectionPlugin(AbstractPlugin):
    """Print out a what the workspace looks like. Useful for debugging."""
    def __init__(self, log):
        self.log = log
        
    def finalize(self, workspace):
        msg = "Workspace properties:\n   "
        properties = [prop for prop in dir(workspace) if not prop.startswith("__")]
        properties.sort()
        msg += "\n   ".join(properties)

        allproperties = []
        for v in workspace.repositories.values():
            properties = [prop for prop in dir(v) if not prop.startswith("__") and not prop in allproperties]
            allproperties.extend(properties)
        allproperties.sort()
        msg += "\n\nAll possible repository properties:\n   "
        msg += "\n   ".join(allproperties)

        allproperties = []
        for v in workspace.modules.values():
            properties = [prop for prop in dir(v) if not prop.startswith("__") and not prop in allproperties]
            allproperties.extend(properties)
        allproperties.sort()
        msg += "\n\nAll possible module properties:\n   "
        msg += "\n   ".join(allproperties)

        allproperties = []
        for v in workspace.projects.values():
            properties = [prop for prop in dir(v) if not prop.startswith("__") and not prop in allproperties]
            allproperties.extend(properties)
        allproperties.sort()
        msg += "\n\nAll possible project properties:\n   "
        msg += "\n   ".join(allproperties)

        msg += "\n\nAll known repositories:\n"
        for k in workspace.repositories.keys():
            msg += "   %s\n" % k

        msg += "\nAll known modules:\n"
        for k in workspace.modules.keys():
            msg += "   %s\n" % k

        msg += "\nAll known projects:\n"
        for k in workspace.modules.keys():
            msg += "   %s\n" % k
        
        self.log.debug("=" * 78)
        self.log.debug(msg)
        self.log.debug("=" * 78)
        
        # Example of how you can "probe" into specific parts of the model
        # if you want...
        #
        #xmlapis = workspace.projects["xml-apis"]
        #for prop in dir(xmlapis):
        #    att = getattr(xmlapis, prop)
        #    if callable(att):
        #        continue
        #    self.log.debug("XML-APIS attribute %s has value %s" % (prop, att))
        