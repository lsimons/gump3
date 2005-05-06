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
from gump.model import Module, Project, Dependency, Command
from gump.model.util import check_skip, check_failure, get_failure_causes, get_root_cause
from gump.engine.algorithm import ExceptionInfo
from gump.util import ansicolor

from StringIO import StringIO

hr = '------------------------------------------------------------------------'

class DebugLogReporterPlugin(AbstractPlugin):
    """Outputs debug messages as it visits model elements."""
    def __init__(self, log):
        self.log = log
    
    def visit_workspace(self, workspace):
        self.log.info("Processing %s%s%s" % (ansicolor.Bright_Blue, workspace, ansicolor.Black))
    
    def visit_repository(self, repository):
        self.log.info("  Processing %s%s%s" % (ansicolor.Blue, repository, ansicolor.Black))
    
    def visit_module(self, module):    
        self.log.info("    Processing %s%s%s" % (ansicolor.Blue, module, ansicolor.Black))
    
    def visit_project(self, project):    
        self.log.info("      Processing %s%s%s" % (ansicolor.Purple, project, ansicolor.Black))
            
class OutputLogReporterPlugin(AbstractPlugin):
    """Outputs all logs set on all log-style model annotations to the log."""
    def __init__(self, log):
        self.log = log
    
    def initialize(self):
        self.log.debug(hr)
        self.log.debug('  Outputting all log data (potentially a lot)...')
        self.log.debug(hr)

    def _do_log_printing_visit(self, object, container=None):
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
                traceback.print_tb(entry.traceback, file=target)
                trace = target.getvalue()
                target.close()
                self.log.error("---%s--exception--%s:%s------:\n%s" % (name, entry.type, entry.value, trace))
    
    def visit_workspace(self, workspace):
        self._do_log_printing_visit(workspace)
    
    def visit_module(self, module):    
        self._do_log_printing_visit(module)
    
    def visit_project(self, project):    
        self._do_log_printing_visit(project)
        for command in project.commands:
            self._do_log_printing_visit(command,project)
            
    def finalize(self):
        self.log.debug('  Finished outputting all log data.')
        self.log.debug(hr)

class ResultLogReporterPlugin(AbstractPlugin):
    """Outputs information about build results to the logs."""
    def __init__(self, log):
        self.log = log
        self.buffer = StringIO()
        self.buffer.write('\n')
    
    def wr(self,msg):
        self.buffer.write(msg)
        self.buffer.write('\n')
    
    def initialize(self):
        self.wr(hr)
        self.wr('                           %sBUILD RESULTS%s' % (ansicolor.Bright_Blue, ansicolor.Black))
        self.wr(hr)
    
    def visit_workspace(self, workspace):
        if hasattr(workspace, "run_start") and hasattr(workspace, "run_end"):
            self.wr('  Run started:  %s' % workspace.run_start)
            self.wr('  Run finished: %s' % workspace.run_end)
            self.wr('')
        
        failed        = 0
        prereq_failed = 0
        skipped       = 0
        success       = 0
        cycled        = 0
        total = len(workspace.projects)
        for project in workspace.projects.values():
            if check_failure(project):
                prereq_fail = False
                for cause in get_failure_causes(project):
                    if isinstance(cause, Dependency) or isinstance(cause, Project):
                        prereq_fail = True
                        prereq_failed += 1
                        break
                
                if not prereq_fail:
                    failed += 1
                continue
            if check_skip(project):
                skipped += 1
                continue
            if hasattr(workspace, "unvisited"):
                if project in workspace.unvisited:
                    cycled += 1
                    continue
            
            success += 1
        
        total_percent = 100.0
        failed_percent = (1.0 * failed / total) * total_percent
        prereq_failed_percent = (1.0 * prereq_failed / total) * total_percent
        skipped_percent = (1.0 * skipped / total) * total_percent
        success_percent = (1.0 * success / total) * total_percent
        cycled_percent = (1.0 * cycled / total) * total_percent
        
        self.wr('  Project build statistics:')
        self.wr('Total   %sFailed   %sPrereq Failed   Skipped   %sSuccess   %sCyclic Dependency%s' % \
                (ansicolor.Red, ansicolor.Yellow, ansicolor.Green, ansicolor.Bright_Red, ansicolor.Black))
        self.wr('%5u   %s%6u   %s%13u   %7u   %s%7u   %s%17u%s' % (total,
                 ansicolor.Red, failed,
                 ansicolor.Yellow, prereq_failed, skipped,
                 ansicolor.Green, success,
                 ansicolor.Bright_Red, cycled,
                 ansicolor.Black))
        self.wr('%5.0f%%  %s%6.1f%%  %s%13.1f%%  %7.1f%%  %s%7.1f%%  %s%17.1f%%%s' % (total_percent,
                 ansicolor.Red, failed_percent,
                 ansicolor.Yellow, prereq_failed_percent, skipped_percent,
                 ansicolor.Green, success_percent,
                 ansicolor.Bright_Red, cycled_percent,
                 ansicolor.Black))
        self.wr(hr)
        
        if hasattr(workspace, "unvisited"):
            for project in workspace.unvisited:
                self.wr('%s%s: CYCLIC DEPENDENCY%s' % (ansicolor.Bright_Red, project, ansicolor.Black))
 
    def visit_project(self, project):
        if check_skip(project):
            self.wr('%s%s: SKIPPED%s' % (ansicolor.Blue, project, ansicolor.Black))
            return
        
        if not check_failure(project):
            self.wr('%s%s: OK%s' % (ansicolor.Green, project, ansicolor.Black))
        else:
            self.wr('%s%s: FAIL%s' % (ansicolor.Red, project, ansicolor.Black+ansicolor.Black))

            causes = get_failure_causes(project)
            for cause in causes:
                if isinstance(cause, ExceptionInfo):
                    self.wr("    %sMETADATA FAILURE (%s)%s" % (ansicolor.Red, cause, ansicolor.Black))
                if isinstance(cause, Command):
                    self.wr("    %sBUILD FAILURE (%s)%s" % (ansicolor.Red, cause, ansicolor.Black))
                if isinstance(cause, Dependency):
                    self.wr("    %sPREREQ FAILURE (%s)%s" % (ansicolor.Red, cause.dependency, ansicolor.Black))
                if isinstance(cause, Project):
                    self.wr("    %sPREREQ FAILURE (%s)%s" % (ansicolor.Red, cause, ansicolor.Black))
                if isinstance(cause, Module):
                    self.wr("    %sUPDATE FAILURE (%s)%s" % (ansicolor.Red, cause, ansicolor.Black))
                
                indent =    "     "
                for trace_elem in get_root_cause(cause):
                    real_elem = trace_elem
                    if isinstance(trace_elem, Dependency):
                        real_elem = trace_elem.dependency
                        
                    if hasattr(real_elem, "name"):
                        self.wr("%s%s caused by %s%s" % (ansicolor.Yellow, indent, real_elem, ansicolor.Black))
                        
                    indent += "  "
                    
    def finalize(self):
        self.wr(hr)
        
        self.buffer.flush()
        self.log.info(self.buffer.getvalue())
        self.buffer.close()
