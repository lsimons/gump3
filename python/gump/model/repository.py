#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/repository.py,v 1.7 2004/01/09 19:57:18 ajack Exp $
# $Revision: 1.7 $
# $Date: 2004/01/09 19:57:18 $
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

from gump.model.state import *
from gump.model.stats import *

from gump.model.object import NamedModelObject

from gump.utils import getIndent

class Repository(NamedModelObject, Statable):
    """A named repository"""
    def __init__(self,xml,workspace):
    	NamedModelObject.__init__(self,xml.getName(),xml,workspace)
            
        if 'cvs'==xml.type:
            self.type='CVS'
            if xml.root:
                if xml.root.method: 
                    self.method=xml.root.method
                # :TODO: And if not? Default?            
            
                if xml.root.user: self.user=xml.root.user
                if xml.root.password: self.password=xml.root.password
                if xml.root.path: self.path=xml.root.path
                if xml.root.hostname: self.hostname=self.xml.root.hostname
            else:
                raise RuntimeError, 'No XML <root on repository: ' + self.getName()
        elif 'svn'==xml.type:  
            self.type='Subversion'
            if xml.url:
                self.url=str(xml.url)
            else:
                raise RuntimeError, 'No URL on SVN repository: ' + self.getName()
        elif 'jars'==xml.type:
            self.type='Java Arcvhives'
        else:
            raise RuntimeError, 'Invalid Repository Type'            
            
        # Modules referencing this repository
        self.modules=[]
            
    def complete(self,workspace):
        pass
                     
    def check(self,workspace):
        if not self.hasModules():
            self.addWarning('Unused Repository (not referenced by modules)')
    
    def hasModules(self):
        if self.modules: return 1
        return 0
    
    def hasType(self):
        if self.type: return 1
        return 0            
           
    def getType(self):
        return self.type
            
    def getModules(self):
        return self.modules
    
    def dump(self, indent=0, output=sys.stdout):
        output.write(getIndent(indent)+'Repository : ' + self.name + '\n')   
        NamedModelObject.dump(self,indent+1,output)
        
    def hasTitle(self): 
        return hasattr(self.xml,'title') and self.xml.title
        
    def hasHomePage(self): 
        return hasattr(self.xml,'home-page') and getattr(self.xml,'home-page')
        
    def hasCvsWeb(self): 
        return hasattr(self.xml,'cvsweb') and self.xml.cvsweb

    # :TODO: Redistributable...
        
    def hasUser(self): return hasattr(self,'user')
    def hasPassword(self): return hasattr(self,'password')
    def hasPath(self): return hasattr(self,'path')
    def hasMethod(self): return hasattr(self,'method')
    def hasHostname(self): return hasattr(self,'hostname')   
    
    
    def getTitle(self): return str(self.xml.title)
    def getHomePage(self): return str(getattr(self.xml,'home-page'))
    def getCvsWeb(self): return str(self.xml.cvsweb)
    
    def getUser(self): return str(self.user)
    def getPassword(self): return str(self.password)
    def getPath(self): return str(self.path)
    def getMethod(self): return str(self.method)
    def getHostname(self): return str(self.hostname)
    
    def hasUrl(self): return hasattr(self,'url')
    def getUrl(self): return str(self.url)
    
    def addModule(self,module):
        self.modules.append(module)
        
    def getModules(self): 
        return self.modules    
        
class RepositoryStatistics(Statistics):
    """Statistics Holder"""
    def __init__(self,repositoryName):
        Statistics.__init__(self,repositoryName)
        
    def getFOGFactor(self):
        return (self.successes / (self.failures - self.prereqs))

    def getKeyBase(self):
        return 'repository:'+ self.name        
        
    