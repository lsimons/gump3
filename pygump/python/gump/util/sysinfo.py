#!/usr/bin/env python

# Copyright 2005 The Apache Software Foundation
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

"""This module provides system introspection tools based on all sorts of ugly
shell-based stuff."""

__copyright__ = "Copyright (c) 2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import os
from tempfile import mkstemp

# This is what _system returns if os.system() for some very strange
# reason would throw an exception.
RESULT_IF_SYSTEM_CALL_FAILS = 10000

def _safe_close(fd):
    """Closes both file descriptors and python "files" properly
    without throwing an exception."""
    try:
        if isinstance(fd,int):
            os.close(fd)
        else:
            fd.close()
    except:
        pass

def _safe_rm(filename):
    """Deletes a file without throwing an exception."""
    try:
        os.remove(filename)
    except:
        pass
    
#TODO solidify and move elsewhere
def _system(command):
    """This is a utility method that can be used to execute arbitrary
    commands sent to other programs, capturing standard out and standard
    error. Note that this is a horribly inefficient way to execute
    commands, so avoid it if you can.

    Returns a tuple containing the exit code for the command, the standard
    out log, and the standard error log."""
    (f, scriptname) = mkstemp()
    os.write(f,command)
    _safe_close(f)
    (f, soutname) = mkstemp()
    _safe_close(f)
    (f, serrname) = mkstemp()
    _safe_close(f)
    
    try:
        cmd = "sh -e '%s' >%s 2>%s" % (scriptname, soutname, serrname)
    
        result = RESULT_IF_SYSTEM_CALL_FAILS
        try:
            result = os.system(cmd)
        except:
            pass
        if not os.name == 'dos' and not os.name == 'nt':
            result = (((result & 0xFF00) >> 8) & 0xFF)
        
        f = open(soutname)
        output = f.read()
        _safe_close(f)
        f = open(serrname)
        error = f.read()
        _safe_close(f)
    
        return (result, output, error)
    finally:
        _safe_rm(scriptname)
        _safe_rm(soutname)
        _safe_rm(serrname)

def amount_of_memory():
    """Returning an integer giving the amount of RAM memory in the system,
    in megabytes. Returns 0 if the amount of RAM cannot be determined."""
    amount = 0 # i.e., we don't know
    cmd = 'cat /proc/meminfo | grep MemTotal | sed -e "s/[^0-9]//g"'
    (result, output, error) = _system(cmd)
    if not result: # exit status 0 is good!
        try:
            amount = int(output)
        except:
            pass
    
    return amount
    
def amount_of_cpu_mhz():
    """Returning an integer giving the processor speed for this system,
    in MHz. Returns 0 if the processor speed cannot be determined."""
    amount = 0 # i.e., we don't know
    cmd = "cat /proc/cpuinfo | grep MHz | sed -e 's/[^0-9]//g' | awk '!x[$0]++'"
    (result, output, error) = _system(cmd)
    if not result: # exit status 0 is good!
        try:
            amount = int(output)
        except:
            pass
    
    return amount

def number_of_cpus():
    """Returning an integer giving the number of CPUs in the system.
    Returns 0 if the number of CPUs cannot be determined."""
    amount = 0 # i.e., we don't know
    cmd = 'cat /proc/cpuinfo | grep "^processor" | sed -e "s/[^0-9]//g" | grep -c ".*"'
    (result, output, error) = _system(cmd)
    if not result: # exit status 0 is good!
        try:
            amount = int(output)
        except:
            pass
    
    return amount
