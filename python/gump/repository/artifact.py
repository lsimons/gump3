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

    An Artifact Repository 
    
"""

import os

from gump.core.config import *
from gump import log
from gump.model import *

from shutil import copyfile


class ArtifactRepository:
    """
    	Represents a local (Gump produced) Artifacts Repository
    """
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
        """
        Returns the root directory.
        
        Note: Side effects, makes the directory
        """
        rdir=os.path.abspath(self.root)
        if not os.path.exists(rdir): os.makedirs(rdir)
        return rdir  
    
    #
    # Repository format is:
    #
    #	../{group}/jars/{output files}
    #    
    def getGroupDir(self,group,rdir=None):
        if not rdir: rdir=self.getRepositoryDir()
        gdir=os.path.abspath(os.path.join(rdir,group))
        if not os.path.exists(gdir): os.makedirs(gdir)
        jdir=os.path.abspath(os.path.join(gdir,'jars'))
        if not os.path.exists(jdir): os.makedirs(jdir)
        return jdir  
        
    def publish(self,group,artifact,id=None):
        
        # Locate (and make if needed) group.
        cdir=self.getGroupDir(group)
        
        # Extract name, to make relative to group
        artifactName=os.path.basename(artifact)
        
        # Publish under the format:
        #
        #	{id}-gump-@@DATE@@.{extension}
        #
        if id:
            (artifactRoot, artifactExtn) = os.path.splitext(artifactName)
            artifactName=id + '-gump-' + default.date.strftime(setting.DATE_FORMAT) + artifactExtn
        
        newArtifact=os.path.join(cdir,artifactName)
        
        # Do the file transfer..
        copyfile(artifact,newArtifact)
        
        log.info('Published %s to repository as %s at %s' % (artifact,artifactName, newArtifact))
        