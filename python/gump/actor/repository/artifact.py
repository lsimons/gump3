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

    An Artifact Repository 
    
"""

import os

from gump.core.config import *
from gump import log
from gump.core.model import *

from shutil import copyfile

import re

class ArtifactRepository:
    
    # Match {id}-gump-{date}.{extn} id=1, date=2, extn=3
    ARTIFACT_RE=re.compile(r'^(.*)-gump-([0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]).(.*)$')
    
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
    
    def getGroupDir(self,group,rdir=None):
        """    
        	Repository format is:
    
    		.../{group}/jars/{output files}
        
        """
        if not rdir: rdir=self.getRepositoryDir()
        gdir=os.path.abspath(os.path.join(rdir,group))
        if not os.path.exists(gdir): os.makedirs(gdir)
        jdir=os.path.abspath(os.path.join(gdir,'jars'))
        if not os.path.exists(jdir): os.makedirs(jdir)
        return jdir  
        
    def getGroups(self):
        """
        Get all groups in the repository
        """
        return os.listdir(self.getRepositoryDir())
        
    def cleanRepository(self):
        for group in self.getGroups():
            try:
                self.cleanRepositoryGroup(group)
            except:
                pass
                
    def cleanRepositoryGroup(self,group):
        recent=self.extractMostRecentGroup(group)
        if recent:
            
            # Locate (and make if needed) group.
            gdir=self.getGroupDir(group)   
        
            for file in os.listdir(gdir):
                match=ArtifactRepository.ARTIFACT_RE.match(file)
                if match and not match.group(1) in list(recent.keys()):
                    print('remove : ' + file)
                    
    def publish(self,group,artifact,id=None):
        """
        Publish an artifact at the artifact repository.
        """
        
        # Locate (and make if needed) group.
        gdir=self.getGroupDir(group)
        
        # Extract name, to make relative to group
        artifactName=os.path.basename(artifact)
        
        # Publish under the format:
        #
        #	{id}-gump-@@DATE@@.{extension}
        #
        if id:
            (artifactRoot, artifactExtn) = os.path.splitext(artifactName)
            artifactName=id + '-gump-' + default.date_s + artifactExtn
        
        newArtifact=os.path.join(gdir,artifactName)
        
        # Do the file transfer..
        copyfile(artifact,newArtifact)
        
        log.info('Published %s to repository as %s at %s' % (artifact,artifactName, newArtifact))
        
        
    def extractGroup(self,group):
        """
        Get all the sets of identifiers in this group
        
        Returns a tuple:
        
        1) map of list of tuples (id,date,extn,full name), keyed by date (string).
        2) the latest date (most recent)
        
        """
        
        # Locate (and make if needed) group.
        gdir=self.getGroupDir(group)   
        
        # See what we have
        dates={}
        mostRecent=''
        for file in os.listdir(gdir):    
            match=ArtifactRepository.ARTIFACT_RE.match(file) 
            if match:
                # Extract the pieces....
                id=match.group(1)
                date=match.group(2)
                extn=match.group(3)
                
                # Group by date 
                if date not in dates:
                    dates[date]={}
                dates[date][id]=(id,date,extn,match.group(0))
                
                # Keep track of latest...
                if date > mostRecent:
                    mostRecent=date
                 
        return (dates, mostRecent)
        
    def extractMostRecentGroup(self,group):
         """
         Get the newest set
         
         Returns a list of tuples (id,date,extn,full name)
         """
         (dates,mostRecent)=self.extractGroup(group)
         if dates: return dates[mostRecent]
         
