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
    Checks that the Gump definitions are ok.
    
    The workspace is loaded into memory, rudimentary
    checks occur, and the output tree is documented
    (e.g. via forrest).
    
"""

import os.path
import sys

from gump import log
from gump.core.gumpinit import gumpinit
from gump.test import getWorkedTestRun
from gump.document.xdocs.documenter import XDocDocumenter

def document(runs=1):

    run=getWorkedTestRun()
    
    test='test'
    if not os.path.exists(test): os.mkdir(test)
    
    gtest=os.path.join(test,'gump')
    if not os.path.exists(gtest): os.mkdir(gtest)
    
    xwork=os.path.join(gtest,'xdocs-work')
    if not os.path.exists(xwork): os.mkdir(xwork)
        
    documenter=XDocDocumenter(run,gtest,'http://someplace')
        
    for r in range(runs):   
        print 'Perform run # ' + `r`
        documenter.document()
        
def xrun():
    gumpinit()
  
    document(100) 
    
    # bye!
    sys.exit(0)
    
# static void main()
if __name__=='__main__':

    print 'Profiling....'
    import profile
    profile.run('xrun()', 'iprof')
    # xrun()
     