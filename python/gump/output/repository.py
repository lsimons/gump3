#!/usr/bin/env python
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
    A Repository 
"""

import os

from gump.config import *
from gump import log
from gump.model import *

from shutil import copyfile


class JarRepository:
    """Contains Repository Contents"""
    def __init__(self,root):
        self.root=root
        
    def __repr__(self):
        return str(self.root)
        
    def __str__(self):
        return 'Repository:' + str(self.root)
        
    def __eq__(self,other):
        return self.root == other.root
                
    def __cmp__(self,other):
        return cmp(self.root,other.root)
            
    def getRepositoryDir(self):
        rdir=os.path.abspath(self.root)
        if not os.path.exists(rdir): os.mkdir(rdir)
        return rdir  
    
    #
    # Repository format is:
    #
    #	../{group}/jars/{output files}
    #    
    def getGroupDir(self,group,rdir=None):
        if not rdir: rdir=self.getRepositoryDir()
        gdir=os.path.abspath(os.path.join(rdir,group))
        if not os.path.exists(gdir): os.mkdir(gdir)
        jdir=os.path.abspath(os.path.join(gdir,'jars'))
        if not os.path.exists(jdir): os.mkdir(jdir)
        return jdir  
        
    def publish(self,group,artefact):
        
        # Locate (and make if needed) group.
        cdir=self.getGroupDir(group)
        
        # Extract name, to make relative to group
        artefactName=os.path.basename(artefact)
        newArtefact=os.path.join(cdir,artefactName)
        
        # Do the transfer..
        copyfile(artefact,newArtefact)
        
  
