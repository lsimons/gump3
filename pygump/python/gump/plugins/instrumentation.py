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

class TimerPlugin(AbstractPlugin):
    """Set a date property on each model object as it is visited."""
    def __init__(self, propertyname, format='%d %b %Y %H:%M:%S'):
        self.format = format
        self.propertyname = propertyname
        
    def _do_visit(self, object):
        setattr(object, self.propertyname, self.gettime())
    
    def visit_workspace(self, workspace):
        self._do_visit(workspace)
    
    def visit_module(self, module):    
        self._do_visit(module)
    
    def visit_project(self, project):    
        self._do_visit(project)

    def gettime(self):
        import time
        return time.strftime(self.format, time.localtime())
