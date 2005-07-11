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

"""This module provides a thin wrapper around the subprocess library.

On posix platforms, it does process group management to allow us to clean up
misbehaved processes.

To start using this module, simply replace all imports of the subprocess
module with imports of the gump.util.executor module. It defines a Popen
class that has the same behaviour as the Popen class in the subprocess
module.

Next, near the end of your application (right before you're calling
system.exit(), usually), add a call to the clean_up_processes() method. This
will attempt to clean up any leftover children created by this module. Note
that doing this can take some time depending on how well-behaved your children
are!"""

# The reason we aren't using a cleaner class-based setup here like we do with
# most of the other utility methods is that doing things this way (providing a
# Popen class) means this module can be used as a drop-in replacement for the
# subprocess module, which is, simply put, very convenient!

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import sys
from gump.util import ansicolor

# set this to a logging-module-compatible logger to make this module log all
# the commands it executes
_log = None

if sys.platform == "win32":
    from subprocess import PIPE
    from subprocess import STDOUT
    import subprocess
    
    class Popen(subprocess.Popen):
        """This is a thin wrapper around subprocess.Popen which does fancy logging."""
        def __init__(self, args, bufsize=0, executable=None,
                     stdin=None, stdout=None, stderr=None,
                     preexec_fn=None, close_fds=False, shell=False,
                     cwd=None, env=None, universal_newlines=False,
                     startupinfo=None, creationflags=0, no_cleanup=False):
            # a logger can be set for this module to make us log commands
            if _log:
                _log.info("        Executing command:\n      %s'%s'%s\n       in directory '%s'" % (ansicolor.Blue, " ".join(args), ansicolor.Black, os.path.abspath(cwd or os.curdir)))

            subprocess.Popen.__init__(self, args, bufsize=bufsize, executable=executable,
                         stdin=stdin, stdout=stdout, stderr=stderr,
                         preexec_fn=preexec_fn, close_fds=close_fds, shell=shell,
                         cwd=cwd, env=env, universal_newlines=universal_newlines,
                         startupinfo=startupinfo, creationflags=creationflags)

    def clean_up_processes(timeout):
        """This function can be called prior to program exit to attempt to
        kill all our running children that were created using this module.
        It does not work on windows!"""
        pass
else:
    # POSIX
    import os
    import time
    import subprocess
    import signal
    import errno
    import tempfile
    from subprocess import PIPE
    from subprocess import STDOUT

    temp_dir = tempfile.mkdtemp("gump_util_executor")
    process_list_filename = os.path.join(temp_dir, "processlist.pids")

    def savepgid(filename):
        """Function called from Popen child process to create new process groups."""
        os.setpgrp()
        f = None
        try:
            grp = os.getpgrp()
            f = open(filename,'a+')
            f.write("%d" % grp)
            f.write('\n')
        finally:
            if f:
                try: f.close()
                except: pass
            
    class Popen(subprocess.Popen):
        """This is a thin wrapper around subprocess.Popen which handles
        process group management. The gump.util.executor.clean_up_processes()
        method can be used to clean up the cruft left around by these Popen'ed
        processes."""
        def __init__(self, args, bufsize=0, executable=None,
                     stdin=None, stdout=None, stderr=None,
                     preexec_fn=None, close_fds=False, shell=False,
                     cwd=None, env=None, universal_newlines=False,
                     startupinfo=None, creationflags=0, no_cleanup=False):
            # see gump.plugins.java.builder.AntPlugin for information on the
            # no_cleanup flag

            # a logger can be set for this module to make us log commands
            if _log:
                _log.info("        Executing command:\n      %s'%s'%s\n       in directory '%s'" % (ansicolor.Blue, " ".join(args), ansicolor.Black, os.path.abspath(cwd or os.curdir)))

            if not no_cleanup:
                global process_list_filename
                """Create a new Popen instance that delegates to the
                subprocess Popen."""
                if not preexec_fn:
                    # setpgid to the gump process group inside the child
                    pre_exec_function = lambda: savepgid(process_list_filename)
                else:
                    # The below has a "stupid lambda trick" that makes the lambda
                    # evaluate a tuple of functions. This sticks our own function
                    # call in there while still supporting the originally provided
                    # function
                    pre_exec_function = lambda: (preexec_fn(),savepgid(process_list_filename))
                
                
                subprocess.Popen.__init__(self, args, bufsize=bufsize, executable=executable,
                         stdin=stdin, stdout=stdout, stderr=stderr,
                         # note our custom function in there...
                         preexec_fn=pre_exec_function, close_fds=close_fds, shell=shell,
                         cwd=cwd, env=env, universal_newlines=universal_newlines,
                         startupinfo=startupinfo, creationflags=creationflags)
            else:
                subprocess.Popen.__init__(self, args, bufsize=bufsize, executable=executable,
                         stdin=stdin, stdout=stdout, stderr=stderr,
                         # note our custom function is *not* in there...
                         preexec_fn=preexec_fn, close_fds=close_fds, shell=shell,
                         cwd=cwd, env=env, universal_newlines=universal_newlines,
                         startupinfo=startupinfo, creationflags=creationflags)
                

    def clean_up_processes(timeout=300):
        """This function can be called prior to program exit to attempt to
        kill all our running children that were created using this module."""
    
        global process_list_filename
        global temp_dir

        pgrp_list = []

        f = None
        try:
            f = open(process_list_filename, 'r')
            pgrp_list = [int(line) for line in f.read().splitlines()]
        except:
            if f: 
                try: f.close()
                except: pass
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass
        
        # send SIGTERM to everything, and update pgrp_list to just those
        # process groups which have processes in them.
        _kill_groups(pgrp_list, signal.SIGTERM)
       
        # pass a copy of the process groups. we want to remember every
        # group that we SIGTERM'd so that we can SIGKILL them later. it
        # is possible that a process in the pgrp was reparented to the
        # init process. those will be invisible to wait(), so we don't
        # want to mistakenly think we've killed all processes in the
        # group. thus, we preserve the list and SIGKILL it later.
        _reap_children(pgrp_list[:], timeout)
      
        # SIGKILL everything, editing pgrp_list again.
        _kill_groups(pgrp_list, signal.SIGKILL)
       
        # reap everything left, but don't really bother waiting on them.
        # if we exit, then init will reap them.
        _reap_children(pgrp_list, 60)

    def _kill_groups(pgrp_list, sig):
        # NOTE: this function edits pgrp_list
    
        for pgrp in pgrp_list[:]:
            try:
                os.killpg(pgrp, sig)
            except OSError, e:
                if e.errno == errno.ESRCH:
                    pgrp_list.remove(pgrp)

    def _reap_children(pgrp_list, timeout):
        # NOTE: this function edits pgrp_list
      
        # keep reaping until the timeout expires, or we finish
        end_time = time.time() + timeout
      
        # keep reaping until all pgrps are done, or we run out of time
        while pgrp_list and time.time() < end_time:
            # if there's no groups left, we're done, so let's
            # exit early!
            if len(pgrp_list) == 0:
                break
            
            # pause for a bit while processes work on exiting. this pause is
            # at the top, so we can also pause right after the killpg()
            time.sleep(1)
        
            # go through all pgrps to reap them
            for pgrp in pgrp_list[:]:
                # loop quickly to clean everything in this pgrp
                while 1:
                    try:
                        pid, status = os.waitpid(-pgrp, os.WNOHANG)
                    except OSError, e:
                        if e.errno == errno.ECHILD:
                            # no more children in this pgrp.
                            pgrp_list.remove(pgrp)
                            break
                        raise
                    if pid == 0:
                        # some stuff has not exited yet, and WNOHANG avoided
                        # blocking. go ahead and move to the next pgrp.
                        break
