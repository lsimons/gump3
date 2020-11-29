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

    Manage CVS password file
    
"""
import os

from gump import log
from gump.core.config import *
 
# password encryption table used by cvs
shifts = [
    0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
   16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
  114,120, 53, 79, 96,109, 72,108, 70, 64, 76, 67,116, 74, 68, 87,
  111, 52, 75,119, 49, 34, 82, 81, 95, 65,112, 86,118,110,122,105,
   41, 57, 83, 43, 46,102, 40, 89, 38,103, 45, 50, 42,123, 91, 35,
  125, 55, 54, 66,124,126, 59, 47, 92, 71,115, 78, 88,107,106, 56,
   36,121,117,104,101,100, 69, 73, 99, 63, 94, 93, 39, 37, 61, 48,
   58,113, 32, 90, 44, 98, 60, 51, 33, 97, 62, 77, 84, 80, 85,223,
  225,216,187,166,229,189,222,188,141,249,148,200,184,136,248,190,
  199,170,181,204,138,232,218,183,255,234,220,247,213,203,226,193,
  174,172,228,252,217,201,131,230,197,211,145,238,161,179,160,212,
  207,221,254,173,202,146,224,151,140,196,205,130,135,133,143,246,
  192,159,244,239,185,168,215,144,139,165,180,157,147,186,214,176,
  227,231,219,169,175,156,206,198,129,164,150,210,154,177,134,127,
  182,128,158,208,162,132,167,209,149,241,153,251,237,236,171,195,
  243,233,253,240,194,250,191,155,142,137,245,235,163,242,178,152 ]

# encode a password in the same way that cvs does
def mangle(passwd):
  return 'A' + ''.join(map(chr,[shifts[ord(c)] for c in str(passwd or '')]))


def readLogins():
    # read the list of cvs repositories that the user is already logged into
    logins={}
    cvspassfile=os.path.expanduser(os.path.join('~','.cvspass'))
    # print 'CVS Password File : ' + cvspassfile
    if os.path.exists(cvspassfile):
        cvspass=open(cvspassfile)
        for line in cvspass.readlines():
            clean=line.strip()
            parts=clean.split(' ')
      
            # Cope with new format .cvspass 
            rootPart=0
            if '/1' == parts[0]:
                rootPart=1
            root=parts[rootPart]
        
            # Cope w/ spaces in mangles
            mangle=' '.join(parts[rootPart+1:])
        
            # Stash this mangle for this root               
            logins[root]=mangle
        cvspass.close()    
    return logins
 
def loginToRepositoryOnDemand(repository,root,logins):
    # log into the cvs repository
    if str(repository.getMethod())=='pserver':
        newpass=mangle(repository.getPassword())
        if not root in logins or logins[root]!=newpass:
            log.info('Provide login for CVS repository: ' + repository.getName() + ' @ ' + root)            
            # Open with append...
        
            cvspassfile=os.path.expanduser(os.path.join('~','.cvspass'))                
            log.info('Updating CVS logins: ' + cvspassfile)            
            # Save new password into file (for CVS tools to use)
            cvspass=open(cvspassfile,'a')
            cvspass.write('/1 '+root+' '+newpass+'\n')
            cvspass.close()
            # Save new password into memory
            logins[root]=newpass
                    
        else:
            pass
            #log.debug('Login already available for: ' + repository.getName() \
            #        + ' @ ' + root)            
    else:
        log.warn('Unable to provide login for CVS repository: ' + repository.getName() \
                + ' @ ' + root + ' method: ' + str(repository.getMethod()) )  
                   
