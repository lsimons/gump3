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
    from subprocess import Popen
    
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
    from subprocess import PIPE
    from subprocess import STDOUT

    def _get_new_process_group():
        """Get us an unused (or so we hope) process group."""
        pid = os.fork()
        gid = pid # that *should* be correct. However, let's actually
                  # create something in that group.
        if pid == 0:
            # Child
            
            # ensure a process group is created
            os.setpgrp()
            
            # sleep for ten days to keep the process group around
            # for "a while"
            import time
            time.sleep(10*24*60*60)
            os._exit(0)
        else:
            # Parent
    
            # wait for child a little so it can set its group
            import time
            time.sleep(1)
            
            # get the gid for the child
            gid = os.getpgid(pid)
        
        return gid

    # This is the group we chuck our children in. We don't just want to
    # use our own group since we don't want to kill ourselves prematurely!
    _our_process_group = _get_new_process_group()

    class Popen(subprocess.Popen):
        """This is a thin wrapper around subprocess.Popen which handles
        process group management. The gump.util.executor.clean_up_processes()
        method can be used to clean up the cruft left around by these Popen'ed
        processes."""
        def __init__(self, args, bufsize=0, executable=None,
                     stdin=None, stdout=None, stderr=None,
                     preexec_fn=None, close_fds=False, shell=False,
                     cwd=None, env=None, universal_newlines=False,
                     startupinfo=None, creationflags=0):
            """Create a new Popen instance that delegates to the
            subprocess Popen."""
            if not preexec_fn:
                # setpgid to the gump process group inside the child
                pre_exec_function = lambda: os.setpgid(0, _our_process_group)
            else:
                # The below has a "stupid lambda trick" that makes the lambda
                # evaluate a tuple of functions. This sticks our own function
                # call in there while still supporting the originally provided
                # function
                pre_exec_function = lambda: (preexec_fn(),os.setpgid(0, _our_process_group))
            
            # a logger can be set for this module to make us log commands
            if _log:
                _log.info("Executing command: %s'%s'%s in directory '%s'" % (ansicolor.Blue, " ".join(args), ansicolor.Black, os.path.abspath(cwd or os.curdir)))
            
            subprocess.Popen.__init__(self, args, bufsize=bufsize, executable=executable,
                     stdin=stdin, stdout=stdout, stderr=stderr,
                     # note our custom function in there...
                     preexec_fn=pre_exec_function, close_fds=close_fds, shell=shell,
                     cwd=cwd, env=env, universal_newlines=universal_newlines,
                     startupinfo=startupinfo, creationflags=creationflags)

    def clean_up_processes(timeout=300):
        """This function can be called prior to program exit to attempt to
        kill all our running children that were created using this module."""
    
        pgrp_list = [_our_process_group]
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
