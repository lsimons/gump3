#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/model/object.py,v 1.9 2003/11/26 20:01:16 ajack Exp $
# $Revision: 1.9 $
# $Date: 2003/11/26 20:01:16 $
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
from gump.utils.xmlutils import xmlize

from gump.model.state import *


INHERIT_NONE=1
INHERIT_ALL=2
INHERIT_JARS=3
INHERIT_HARD=4
INHERIT_RUNTIME=5
        
class Propogatable(Stateful):
    
    def __init__(self):     
        # Problems        
        self.cause=None	# Primary Cause
        self.causes=[]
            
    def changeState(self,state,reason=REASON_UNSET,cause=None,message=None):  
          
        #
        # Do NOT over-write a pre-determined condition
        #            
        if self.isUnsetOrOk():

            # Store it...        
            newState=StatePair(state,reason)
            Stateful.setStatePair(self,newState)        
                
            # If we are having something bad going on...
            if not newState.isOk(): 
                #
                # If no-one else to point the finger at ...
                # ... step up.
                #
                if not cause: cause = self
                
                # List of things that caused issues...
                self.addCause(cause)
                                   
                #
                # Describe the problem
                #
                if not message:
                    message = lower(stateName(state))
                    if not REASON_UNSET == reason:
                        message += " with reason " + lower(reasonString(reason))            
                self.addError(capitalize(message))
        
                # Send on the changes...
                self.propagateErrorStateChange(state,reason,cause,message)
    

    def propagateErrorStateChange(self,state,reason,cause,message):
               
        # .. then push this error down
        if hasattr(self,'getChildren'):
            for object in self.getChildren():
                object.changeState(state,reason,cause,message)        
                            
    def setCause(self,cause):
        if not self.cause: self.cause=cause
        
    def hasCause(self):
        return self.cause
        
    def getCause(self):
        return self.cause
        
    def addCause(self,cause):
        if not self.cause: self.setCause(cause)
        self.causes.append(cause)
        
    def getCauses(self):
        return self.causes
        

class ModelObject(Annotatable,Workable,Propogatable,Ownable):
    """Base model object for a single entity"""
    def __init__(self,xml,owner=None):
                
        # Can scribble on this thing...
    	Annotatable.__init__(self)
    	
    	# Holds work (with state)
    	Workable.__init__(self)
    	
    	# Can propogate states
        Propogatable.__init__(self)

        # Can propogate states
        Ownable.__init__(self,owner)

        # The XML model
    	self.xml=xml
    	
    	self.completionPerformed=0
    	
    def isComplete(self):
        return self.completionPerformed
        
    def setComplete(self,complete):
       self.completionPerformed=complete
       
    def isDebug(self):
        return self.xml.debug
        
    def isVerbose(self):
        return self.xml.verbose      
        
    def dump(self, indent=0, output=sys.stdout):
        """ Display the contents of this object """
        Annotatable.dump(self,indent,output)
    
    def hasViewData(self):
        return hasattr(self,'viewdata')
        
    def getViewData(self):
        if not self.hasViewData():
            stream=StringIO.StringIO() 
            xmlize(self.xml.getTagName(),self.xml,stream)
            stream.seek(0)
            self.viewdata=stream.read()
            stream.close()
    
        return self.viewdata
        
    # Somewhat bogus...
    
    def elapsedSecs(self):
        elapsedSecs=self.worklist.elapsedSecs()
        if hasattr(self,'getChildren'):
            for object in self.getChildren():
                elapsedSecs += object.elapsedSecs()
        return int(round(elapsedSecs,0))
    
    def aggregateStates(self, states=None):
        if not states: states=[]
        
        pair=self.getStatePair()
        # Add state, if not already there
        if not pair.isUnset() and not pair in states: \
            states.append(pair)
        
        return self.getSubbordinateStates(states);
        
    def getSubbordinateStates(self, states=None):
        if not states: states=[]
        
        # Subbordinates
        if hasattr(self,'getChildren'):
            for object in self.getChildren():
                object.aggregateStates(states)
            
        return states;                
                                
class NamedModelObject(ModelObject):
    """Context for a single entity"""
    def __init__(self,name,xml,owner=None):
                
    	ModelObject.__init__(self,xml,owner)
    	
    	# Named
    	self.name=name
      
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
        ModelObject.dump(self,indent,output)

# represents a <nag/> element
class Nag(ModelObject):
    def __init__(self,toaddr,fromaddr):
    	ModelObject.__init__(self,xml,workspace)

# represents a <javadoc/> element
class Javadoc(ModelObject): pass
      
# represents a <description/> element
class Description(ModelObject): pass

# represents a <home/> element
class Home(ModelObject): pass

# represents a <jar/> element
class Jar(NamedModelObject):
    def __init__(self,xml,owner):
    	NamedModelObject.__init__(self,xml.getName(),xml,owner)
    	
    def setPath(self,path):
        self.path=path
    
    def getPath(self):
        return self.path;
        
    def getId(self):
        return self.xml.id
        
    def getType(self):
        return self.xml.type

# represents a <junitreport/> element
class JunitReport(ModelObject): pass

# represents a <mkdir/> element
class Mkdir(ModelObject): pass

# represents a <delete/> element
class Delete(ModelObject): pass

# represents a <work/> element
class Work(ModelObject): pass
        
        
