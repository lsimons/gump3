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

import sys
from subprocess import Popen
from subprocess import PIPE

def amount_of_memory():
    """Returning an integer giving the amount of RAM memory in the system,
    in megabytes. Returns 0 if the amount of RAM cannot be determined."""
    if sys.platform == "win32":
        return 0
    amount = 0 # i.e., we don't know
    cat = Popen(["cat", "/proc/meminfo"], stdout=PIPE)
    if cat.wait():
        return amount
    grep = Popen(["grep", "MemTotal"], stdin=cat.stdout, stdout=PIPE)
    if grep.wait():
        return amount
    sed = Popen(["sed", "-e", "s/[^0-9]//g"], stdin=grep.stdout, stdout=PIPE)
    result = sed.wait()
    if not result:
        amount = int(sed.communicate()[0])
    return amount
    
def amount_of_cpu_mhz():
    """Returning an integer giving the processor speed for this system,
    in MHz. Returns 0 if the processor speed cannot be determined."""
    if sys.platform == "win32":
        return 0
    amount = 0 # i.e., we don't know
    cat = Popen(["cat", "/proc/cpuinfo"], stdout=PIPE)
    if cat.wait():
        return amount
    grep = Popen(["grep", "MHz"], stdin=cat.stdout, stdout=PIPE)
    if grep.wait():
        return amount
    sed = Popen(["sed", "-e", "s/[^0-9]//g"], stdin=grep.stdout, stdout=PIPE)
    if sed.wait():
        return amount
    awk = Popen(["awk", "!x[$0]++"], stdin=sed.stdout, stdout=PIPE)
    result = awk.wait()
    if not result:
        amount = int(awk.communicate()[0])
    return amount

def number_of_cpus():
    """Returning an integer giving the number of CPUs in the system.
    Returns 0 if the number of CPUs cannot be determined."""
    if sys.platform == "win32":
        return 0
    amount = 0 # i.e., we don't know
    cat = Popen(["cat", "/proc/cpuinfo"], stdout=PIPE)
    if cat.wait():
        return amount
    grep = Popen(["grep", "^processor"], stdin=cat.stdout, stdout=PIPE)
    if grep.wait():
        return amount
    sed = Popen(["sed", "-e", "s/[^0-9]//g"], stdin=grep.stdout, stdout=PIPE)
    if sed.wait():
        return amount
    grep2 = Popen(["grep", "-c", ".*"], stdin=sed.stdout, stdout=PIPE)
    result = grep2.wait()
    if not result:
        amount = int(grep2.communicate()[0])
    return amount
