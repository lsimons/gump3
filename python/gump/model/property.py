#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/property.py,v 1.2 2003/11/18 17:29:17 ajack Exp $
# $Revision: 1.2 $
# $Date: 2003/11/18 17:29:17 $
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

from gump.model.object import *

# represents a <property/> element
class Property(NamedModelObject):
    
    def __init__(self,xml,parent):
    	NamedModelObject.__init__(self,xml.getName(),xml,parent)
    	self.value=xml.value or '*Unset*' 
    	
    def setValue(self,value):
        self.value = value
        
    def getValue(self):
        return self.value
        
    # provide default elements when not defined in xml
    def complete(self,parent,workspace):
        if self.isComplete(): return
                 
        if self.xml.reference=='home':
            try:
                targetProject=workspace.getProject(self.xml.project)
                self.setValue(targetProject.getHomeDirectory())
            except Exception, details:
                log.warn( "Cannot resolve homedir of " + self.xml.project + " for " + `parent` + ' : ' + `details`,exc_info=1)                
        elif self.xml.reference=='srcdir':
            try:
                targetProject=workspace.getProject(self.xml.project)
                
                self.setValue(targetProject.getModule().getSourceDirectory())
            except Exception, details:
                log.warn( "Cannot resolve srcdir of " + self.xml.project + " for " + `parent` + ' : ' + `details`,exc_info=1)
        elif self.xml.reference=='jarpath' or self.xml.reference=='jar':
            try:
                targetProject=workspace.getProject(self.xml.project)
                
                if self.xml.id:
                    for jar in targetProject.getJars():
                        if jar.id==self.xml.id:
                            if self.xml.reference=='jarpath':
                                self.setValue(jar.path)
                            else:
                                self.setValue(jar.name)
                            break
                    else:
                        self.value=("jar with id %s was not found in project %s " +
                                  "referenced by %s") % (self.xml.id, targetProject.getName(), project.getName())
                        log.error(self.value)
                elif targetProject.getJarCount()==1:
                    self.value=targetProject.getJars()[0].path
                elif  targetProject.getJarCount()>1:
                    self.value=("Multiple jars defined by project %s referenced by %s; " + \
                        "an id attribute is required to select the one you want") % \
                          (targetProject.getName(), project.getName())
                    log.error(self.value)
                else:
                    self.value=("Project %s referenced by %s defines no jars as output") % \
                        (targetProject.getName(), project.getName())
                    log.error(self.value)
            except Exception, details:
                log.warn( "Cannot resolve jar/jarpath of " + self.xml.project + \
                  " for " + `parent` + ". Details: " + str(details),exc_info=1)
        elif self.xml.path:
            #
            # Path relative to module's srcdir 
            #        
            self.value=os.path.abspath(os.path.join(	\
                    parent.getOwner().getModule().getSourceDirectory(),	\
                    self.xml.path))
        
        if not hasattr(self,'value'):
            log.error('Unhandled Property: ' + self.getName() + ' on: ' + \
                    str(parent))
                
        self.setComplete(1)
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the property """
        output.write(getIndent(indent)+'Property: ' + self.getName() + ' ' + self.getValue()+ '\n')

class PropertyContainer(object):
    """ Can hold properties """
    def __init__(self,properties=None):
        self.properties={}
        
        # Any starting properties..
        if properties:
            self.properties=properties
            
    def addProperty(self,property):
        self.properties[property.getName()]=property
        
    def setProperty(self,name,value):
        self.properties[name]=Property(name,value)
        
    def getPropertyValue(self,name):
        return self.properties[name].getValue()
        
    def getProperty(self,name):
        return self.properties[name]
        
    def getProperties(self):
        return self.properties.values()
        
    def importProperties(self,xml):
        for xmlproperty in xml.property:
            self.addProperty(Property(xmlproperty,self))
            
    def completeProperties(self,workspace=None):        
        if not workspace: workspace=self
        for property in self.getProperties(): 
            property.complete(self,workspace)
                        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the properties """
        for property in self.getProperties():
            property.dump(indent+1,output)
        
