#!/usr/bin/env python

# $Header: /home/cvs/jakarta-gump/python/gump/utils/work.py,v 1.9 2004/02/17 21:54:21 ajack Exp $
# $Revision: 1.9 $
# $Date: 2004/02/17 21:54:21 $
#
# ====================================================================
#
# The Apache Software License, Version 1.1
#
# Copyright (c) 2003 The Apache Software Foundation.  All rights
# reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. The end-user documentation included with the redistribution, if
#    any, must include the following acknowlegement:
#       "This product includes software developed by the
#        Apache Software Foundation (http://www.apache.org/)."
#    Alternately, this acknowlegement may appear in the software itself,
#    if and wherever such third-party acknowlegements normally appear.
#
# 4. The names "The Jakarta Project", "Alexandria", and "Apache Software
#    Foundation" must not be used to endorse or promote products derived
#    from this software without prior written permission. For written
#    permission, please contact apache@apache.org.
#
# 5. Products derived from this software may not be called "Apache"
#    nor may "Apache" appear in their names without prior written
#    permission of the Apache Group.
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
# ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# ====================================================================
#
# This software consists of voluntary contributions made by many
# individuals on behalf of the Apache Software Foundation.  For more
# information on the Apache Software Foundation, please see
# <http://www.apache.org/>.

"""
    This module contains information on
"""

import os
import os.path
from time import localtime, strftime, tzname
from string import lower, capitalize

from gump.utils.note import *
from gump.utils.owner import *
               
FILE_TYPE_MISC=1
FILE_TYPE_CONFIG=2
FILE_TYPE_OUTPUT=3

fileTypeDescriptions = { 	FILE_TYPE_MISC : "Miscellaneous",
                FILE_TYPE_CONFIG : "Config",
                FILE_TYPE_OUTPUT : "Output", }    
    
def fileTypeName(type):
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
            
    def overview(self, lines=50):
        overview='File Name: ' + self.name +' (Type: ' + fileTypeName(self.type)+')\n'
        
        #
        # :TODO: Annotations....
        #
        
        if self.path and os.path.exists(self.path):
            overview += "---------------------------------------------\n" 
            from gump.utils.tools import tailFileToString            
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

    def getTypeName(self):
        return fileTypeName(self.type)
        
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
        
    def add(self,reference):
        
        if reference.hasOwner():
            # :TODO: Clone ...... ????????
            raise RuntimeError, 'FileReference already owned, can\'t add to list'
        
        # Keep unique within the scope of this list
        name=reference.getName()
        uniquifier=1
        while self.nameIndex.has_key(name):
            name=reference.getName()+str(uniquifier)
            uniquifier+=1
        reference.setName(name)
        
        # Store by name
        self.nameIndex[name]=reference
        
        # Store in the list
        self.append(reference)
        
        # Let this reference know it's owner
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
    
