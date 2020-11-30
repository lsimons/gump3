#!/usr/bin/env python

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
    Simple Lock Utilities (for Gump)
"""

import os,sys

#-----------------------------------------------------------------------# 
        
def acquireLock(lockFile):
    """ Block to ge an exclusive lock on a file. """
    failed=0
    if 'posix'==os.name:
        import fcntl
                
        try:            
            lock=open(lockFile,'a+')
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        except:            
            failed=1
    else:
        if os.path.exists(lockFile):
            failed=1
        lock=open(lockFile,'w')
            
    if failed:
        raise RuntimeError("""The lock file [%s] could not be established.""" % lockFile)
    
    # Write this PID into a lock file
    lock.write(repr(os.getpid()))
    lock.flush()
        
    return lock

#-----------------------------------------------------------------------# 
        
def releaseLock(lock,lockFile):
      
    if 'posix'==os.name:
        import fcntl            
        try:
            fcntl.flock(lockFile.fileno(), fcntl.LOCK_UN)
        except:
            pass
    
    # Close it, so we can dispose of it
    lock.close()    
    
    # Others might be blocked on this
    try:
        os.remove(lockFile)
    except:
        # Somehow another could delete this, even if locked...
        # Or, could be in the process of locking it.
        pass
