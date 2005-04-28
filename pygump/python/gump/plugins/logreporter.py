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

from gump.plugins import AbstractPlugin

hr = '------------------------------------------------------------------------'

class LogReporterPlugin(AbstractPlugin):
    """Outputs all logs set on all log-style model annotations to the log."""
    def __init__(self, log):
        self.log = log
    
    def initialize(self):
        self.log.debug(hr)
        self.log.debug('  Outputting all log data (a lot)...')
        self.log.debug(hr)

    def _do_visit(self, object, container=None):
        name = getattr(object, "name", "unnamed %s" % type(object))
        if container:
            if hasattr(container, "name"):
                name = "%s:%s" % (container.name, name)
                
        #self.log.debug(name)
        for attribute in dir(object):
            if attribute.endswith("_log"):
                logmsg = getattr(object,attribute)
                self.log.debug("---%s.%s----------------------------------:\n%s" % (name, attribute, logmsg))
                self.log.debug(hr)
            #else:
            #    self.log.debug(' %s -> %s' % (attribute,getattr(object,attribute)))

        if hasattr(object, 'exceptions'):
            import StringIO
            import traceback
            for entry in object.exceptions:
                target = StringIO.StringIO()
                traceback.print_tb(entry[2], file=target)
                trace = target.getvalue()
                target.close()
                self.log.error("---%s--exception--%s:%s------:\n%s" % (name, entry[0], entry[1], trace))
    
    def visit_workspace(self, workspace):
        self._do_visit(workspace)
    
    def visit_module(self, module):    
        self._do_visit(module)
    
    def visit_project(self, project):    
        self._do_visit(project)
        for command in project.commands:
            self._do_visit(command,project)
            
    def finalize(self):
        self.log.debug('  Finished Outputting all log data (a lot)...')
        self.log.debug(hr)
