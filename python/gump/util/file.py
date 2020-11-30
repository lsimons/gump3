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
    This module contains file (dir/plain) references
"""

import os
import os.path
from time import localtime, strftime, tzname

from gump.util.note import *
from gump.util.owner import *
               
FILE_TYPE_MISC=1
FILE_TYPE_CONFIG=2
FILE_TYPE_SOURCE=3
FILE_TYPE_PACKAGE=4
FILE_TYPE_OUTPUT=5
FILE_TYPE_REPORT=6
FILE_TYPE_REPO=7
FILE_TYPE_LOG=8

fileTypeDescriptions = { 	FILE_TYPE_MISC : "Miscellaneous",
                FILE_TYPE_CONFIG : "Config",
                FILE_TYPE_SOURCE : "Source",
                FILE_TYPE_PACKAGE : "Package",
                FILE_TYPE_OUTPUT : "Output",
                FILE_TYPE_REPORT : "Report",
                FILE_TYPE_REPO : "Repository",
                FILE_TYPE_LOG : "Log" }    
    
def fileTypeDescription(type):
    return fileTypeDescriptions.get(type,'Unknown File Type:' + str(type))
                   
class FileReference(Ownable,Annotatable):
    """ Unit of File"""
    def __init__(self,path,type=FILE_TYPE_MISC,name=None,message=''):
        Ownable.__init__(self)
        Annotatable.__init__(self)
        
        self.path=path
        self.type=type
        
        # Extract a name, or basename
        if name:
            self.name=name
        else:
            self.name=os.path.basename(path)
            
        if message:
            self.addInfo(message)
    
    def __del__(self):
        Ownable.__del__(self)
        Annotatable.__del__(self)
        
    def overview(self, lines=50):
        overview='File Name: ' + self.name +' (Type: ' + fileTypeDescription(self.type)+')\n'
        
        #
        # :TODO: Annotations....
        #
        
        if self.path and os.path.exists(self.path):
            overview += "---------------------------------------------\n" 
            from gump.util.tools import tailFileToString            
            overview += tailFileToString(self.path,lines)
            overview += "---------------------------------------------\n"
            
        return overview
        
    def exists(self):
        return os.path.exists(self.path)
        
    def isDirectory(self):
        return os.path.isdir(self.path)
        
    def isNotDirectory(self):
        return not os.path.isdir(self.path)
        
    def getType(self):
        return self.type

    def getTypeDescription(self):
        return fileTypeDescription(self.type)
        
    def getPath(self):
        return self.path
        
    def getName(self):
        return self.name
        
    def setName(self,name):
        self.name=name
        
    def clone(self):
        cloned=FileReference(self.path,self.type,self.name)
        # :TODO: Transfer annotations?
        return cloned

class FileList(list,Ownable):
    
    """List of file (in order)"""
    def __init__(self,owner=None):
        list.__init__(self)
        Ownable.__init__(self,owner)            
        
        # Organize by name
        self.nameIndex={}
        
    def __del__(self):
        Ownable.__del__(self)
        
    def add(self,reference):
        
        if reference.hasOwner():
            # :TODO: Clone ...... ????????
            raise RuntimeError('FileReference already owned, can\'t add to list')
        
        # Keep unique within the scope of this list
        name=reference.getName()
        uniquifier=1
        while name in self.nameIndex:
            name=reference.getName()+str(uniquifier)
            uniquifier+=1
        reference.setName(name)
        
        # Store by name
        self.nameIndex[name]=reference
        
        # Store in the list
        self.append(reference)
        
        # Let this reference know its owner
        reference.setOwner(self.getOwner())
                
    def clone(self):
        cloned=FileList()
        for reference in self:
            cloned.add(reference.clone())
        return cloned
        
class FileHolder:       
    def __init__(self):
        self.filelist=FileList(self)
        
    def getFileList(self):
        return self.filelist
        
    def addFileReference(self,fileReference):
    	self.filelist.add(fileReference)
    	
    def addFile(self,path):
    	self.filelist.add(FileReference(path))
    
