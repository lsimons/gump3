#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/utils/note.py,v 1.3 2003/12/04 23:16:24 ajack Exp $
# $Revision: 1.3 $
# $Date: 2003/12/04 23:16:24 $
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

import sys

from gump.utils import *

LEVEL_UNSET=0
LEVEL_DEBUG=1
LEVEL_INFO=2
LEVEL_WARNING=3
LEVEL_ERROR=4
LEVEL_FATAL=5

levelDescriptions = { 	LEVEL_UNSET : "Not Set",
                    LEVEL_DEBUG : "Debug",
                    LEVEL_INFO : "Info",
                    LEVEL_WARNING : "Warning",
                    LEVEL_ERROR : "Error",
                    LEVEL_FATAL : "Fatal" }               

def levelName(level):
    return levelDescriptions.get(level,'Unknown Level:' + str(level))
    
class Annotation:
    """ An annotation ... a log entry on the object ..."""
    def __init__(self,level,text):
        self.level=level
        self.text=text
        
    def __str__(self):
        return levelName(self.level) + ":" + self.text      
        
    def getLevelName(self):
        return levelName(self.level) 
    
    def getText(self):
        return self.text
    
    def dump(self, indent=0, output=sys.stdout):        
        output.write(getIndent(indent)+str(self)+'\n')
        
class Annotatable:
    
    def __init__(self):
        self.annotations=[]

    def addDebug(self,text):
        self.addAnnotation(LEVEL_DEBUG, text)        

    def addInfo(self,text):
        self.addAnnotation(LEVEL_INFO, text)
        
    def addWarning(self,text):
        self.addAnnotation(LEVEL_WARNING, text)
        
    def addError(self,text):
        self.addAnnotation(LEVEL_ERROR, text)
        
    def addFatal(self,text):
        self.addAnnotation(LEVEL_FATAL, text)
        
    def addAnnotation(self,level,text):
        self.addAnnotationObject(Annotation(level,text))
        
    def addAnnotationObject(self,message):
        self.annotations.append(message)
        
    def getAnnotations(self):
        return self.annotations
        
    def containsNasties(self):
        return self.containsOrAbove(LEVEL_WARNING)
        
    def containsOrAbove(self,level):
        for note in self.annotations:
            if note.level >= level:
                return 1
        return 0
                
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """         
        if self.annotations:
            output.write(getIndent(indent)+'Annotations:\n')
       
            for note in self.annotations:
                note.dump(indent+1,output)
  
        