#!/usr/bin/python

# Copyright 2003-2004 The Apache Software Foundation
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

"""	
    Works on the Gump Repository
"""

import os.path
import sys
import pprint

from gump import log
from gump.core.gumpinit import gumpinit

import gump.repository.artifact

# static void main()
if __name__=='__main__':
    gumpinit()

    result = 1
    
    if not len(sys.argv) >= 1:
        raise RuntimeError, 'Usage: repo.py \'repo directory\' [\'clean\']'
        
    dir   = sys.argv[1]
    clean = len(sys.argv) == 2
    
    if not os.path.exists(dir): raise RuntimeError, 'No such directory : ' + `dir`    
    if not os.path.isdir(dir): raise RuntimeError, 'Not a directory : ' + `dir`  
           
    repo=gump.repository.artifact.ArtifactRepository(dir)

    for group in repo.getGroups():
        print '---------------------------------------------------------'
        print 'Group : ' + group
        pprint.pprint(repo.extractGroup(group))
    
    log.info('Gump Repository Tool Complete. Exit code:' + str(result))
          
    # bye!
    sys.exit(result)