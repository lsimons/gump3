#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/results/model.py,v 1.1 2004/02/17 21:54:21 ajack Exp $
# $Revision: 1.1 $
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

from time import localtime, strftime, tzname
from string import lower, capitalize

from gump.utils.note import *
from gump.utils.work import *
from gump.utils.owner import *
from gump.model.state import *
from gump.results.rawmodel import *

from gump.utils.xmlutils import xmlize

class ResultModelObject(Annotatable,Ownable,Stateful):
    """Base model object for a single entity"""
    def __init__(self,name,xml=None,owner=None):
                
        # Can scribble on this thing...
    	Annotatable.__init__(self)

        # Can be owned
        Ownable.__init__(self,owner)

        # Holds a state
        Stateful.__init__(self)
    	
    	# Named
    	self.name=name
    	
        # The XML model
        if xml:
        	self.xml=xml    
 
        # Internals...
    	self.completionPerformed=0
    	
    def isComplete(self):
        return self.completionPerformed
        
    def setComplete(self,complete):
       self.completionPerformed=complete
         
    #
    # Same if same type, and same name
    # i.e project context X is not equals to module context X
    def __eq__(self,other):
        return self.__class__ == other.__class__ and self.name == other.name
        
    def __cmp__(self,other):
        return cmp(self.name,other.name)
        
    def __hash__(self):
        return hash(self.name)
        
    def __repr__(self):
        return str(self.__class__)+':'+self.name
        
    def __str__(self):
        return str(self.__class__)+':'+self.name

    def getName(self):
        return self.name
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        output.write(getIndent(indent)+'Name: ' + self.name + '\n')
        Annotatable.dump(self,indent,output)
    
    def hasXML(self):
        if hasattr(self,'xml') and self.xml: return 1
        return 0
        
    def getXML(self):
        return self.xml
    
    def hasXMLData(self):
        if hasattr(self,'xmldata') and self.xmldata: return 1
        return 0
        
    def getXMLData(self):
        if not self.hasXMLData():
            stream=StringIO.StringIO() 
            
            # Create on demand (push object attributes
            # into XML form)
            if not self.hasXML():
                self.createXML()
                
            xmlize(self.xml.getTagName(),self.xml,stream)
            stream.seek(0)
            self.xmldata=stream.read()
            stream.close()
    
        return self.xmldata
        
    def writeXMLToFile(self, outputFile):
        """ Serialize to a file """
        try:            
            f=open(outputFile, 'w')
            f.write(self.getXMLData())
        finally:
            # Since we may exit via an exception, close explicitly.
            if f: f.close()            

# represents a <workspaceResult/> element
class WorkspaceResult(ResultModelObject):
    def __init__(self,name,xml=None,owner=None):
    	ResultModelObject.__init__(self,name,xml,owner)    
    	
    	#
    	# Results per module
    	#
    	self.moduleResults 	=	{}
    	self.projectResults 	=	{}

    def hasModuleResults(self):
        if self.moduleResults.values(): return 1
        return 0
        
    def getModuleResults(self):
        return self.moduleResults.values()
        
    def hasProjectResults(self):
        if self.projectResults.values(): return 1
        return 0    
        
    def getProjectResults(self):
        return self.projectResults.values()
    
    def hasProjectResult(self,name):
        if name in self.projectResults: return 1
        return 0
        
    def getProjectResult(self,name):
        return self.projectResults[name]
        
    def setModuleResult(self,moduleResult):
        self.moduleResults[moduleResult.getName()] = moduleResult
                
        for projectResult in self.getProjectResults():
            self.setProjectResult(projectResult)
        
    def setProjectResult(self,projectResult):
        self.projectResults[projectResult.getName()] = projectResult
        
    def createXML(self):
        if self.hasXML(): return
        
        """ Convert object attribitues into serializable XML """
        self.xml=XMLWorkspaceResult(	\
            {	\
                'name':self.getName(),	\
                'state':self.getStateName(),	\
                'reason':self.getReasonName()	\
            })
            
        for moduleResult in self.moduleResults.values():
            moduleResult.createXML(self.xml)        
                    
    def complete(self, xmlprofileresults, xmlmoduleresults,	\
                    xmlprojectresults): 
        if self.isComplete(): return
        
        #
        # Import all modules
        #  
        for xmlmoduleresult in xmlmoduleresults.values(): 
            moduleResult=ModuleResult(xmlmoduleresult.name,xmlmoduleresult,self)
            self.setModuleResult(moduleResult)
                
        #
        # Import all projects
        #  
        for xmlprojectresult in xmlprojectresults.values():             
            projectResult=ProjectResult(xmlprojectresult.name,xmlprojectresult,self)
            self.setProjectResult(projectResult)

        # Complete the modules
        for moduleResult in self.getModuleResults():
            moduleResult.complete(self)
                        
        # Complete the projects  
        for projectResult in self.getProjectResults():
            # Complete the project
            projectResult.complete(self)           
        
        self.setComplete(1)
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        ResultModelObject.dump(self,indent,output)
        
        for moduleResult in self.moduleResults.values():
            moduleResult.dump(indent+1, output)
        
# represents a <moduleResult/> element
class ModuleResult(ResultModelObject):
    def __init__(self,name,xml=None,owner=None):
    	ResultModelObject.__init__(self,name,xml,owner)    
    	
    	# 
    	# Results per project
    	#
    	self.projectResults 	=	{}    
    	
    def setProjectResult(self,projectResult):
        self.projectResults[projectResult.getName()] = projectResult
        # Attach oneself as owner...
        projectResult.setModuleResult(self)
                
    def hasProjectResults(self):
        if self.projectResults.values(): return 1
        return 0    
        
    def getProjectResults(self):
        return self.projectResults.values()
        
    def createXML(self, workspaceResultXML):
        if self.hasXML(): return
        
        # This call constructs a new one...
        self.xml=workspaceResultXML.moduleResult(	\
            {	\
                'name':self.getName(),	\
                'state':self.getStateName(),	\
                'reason':self.getReasonName()	\
            })
            
        for projectResult in self.getProjectResults():
            print "CREATE XML FOR :" + `projectResult`
            projectResult.createXML(self.xml)
            
    def complete(self, workspaceResult): 
        if self.isComplete(): return
        
        for xmlprojectresult in self.xml.projectResult:
            if workspaceResult.hasProjectResult(xmlprojectresult.name):
                
                #
                # The project pretty much better be in the
                # workspace, but avoid crashing...
                #
                projectResult=workspaceResult.getProjectResult(xmlprojectresult.name)
                
                #
                # Claim ownership
                #
                self.setProjectResult(projectResult)
                
        self.setComplete(1)
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        ResultModelObject.dump(self,indent,output)
        
        for projectResult in self.projectResults.values():
            projectResult.dump(indent+1, output)
            
# represents a <projectResult/> element
class ProjectResult(ResultModelObject):
    def __init__(self,name,xml=None,owner=None):
    	ResultModelObject.__init__(self,name,xml,owner)
    	
    	self.moduleResult = None

    def createXML(self, moduleResultXML):
        if self.hasXML(): return
        
        self.xml=moduleResultXML.projectResult(	\
            {	\
                'name':self.getName(),	\
                'state':self.getStateName(),	\
                'reason':self.getReasonName()	\
            })
                
    def setModuleResult(self,moduleResult):
        self.moduleResult=moduleResult
        
    def complete(self,workspaceResult): 
        if self.isComplete(): return
        
        self.setComplete(1)
        
