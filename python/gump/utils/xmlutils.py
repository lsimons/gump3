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
    Simple Object to/from XML Utilities (for Gump)
"""

import os.path
import types, StringIO

from xml.sax import parse,parseString
from xml.sax.handler import ContentHandler, ErrorHandler
from xml.sax.saxutils import escape

from gump import log
from gump.utils.http import cacheHTTP
from gump.utils.note import *
from gump.core.config import gumpPath

###############################################################################
# SAX Dispatcher mechanism
###############################################################################
   
class SAXDispatcher(ContentHandler,ErrorHandler,Annotatable):
    """a stack of active xml elements"""

    def __init__(self,name,cls,basedir=None):
            
        Annotatable.__init__(self)
        
        #print '.',        
        """        
            Creates a DocRoot and parses the specified file into a GOM tree.
            The GOM tree is stored in the self.docElement attribute.
        """        
        self.basedir=basedir

        self.topOfStack=DocRoot(name,cls)
        self.elementStack=[self.topOfStack]
        
    def parse(self,file_or_stream):
        resetBasedir=0        
        if not self.basedir and isinstance(file_or_stream,types.StringTypes):
            resetBasedir=1
            self.basedir=os.path.dirname(file_or_stream)
                
        log.debug('Parse XML File/Stream: ' + str(file_or_stream) + ' with basedir of ' + str(self.basedir))                        
        parse(file_or_stream,self)                        
        if resetBasedir: 
            self.basedir=None
        # Stash the result
        self.docElement=self.topOfStack.element

    def parseString(self,s):
        log.debug('Parse XML String: ' + s)
        parseString(s,self)        
        # Stash the result
        self.docElement=self.topOfStack.element

    def startElement (self, name, attrs):
        """See ContentHandler class."""
        if self.topOfStack:         
        
            # Hack to pass this context about..
            attributes=dict(attrs)
            attributes['@basedir']=self.basedir
                
            # The newly loaded object moves to top of stack
            try:   
                #print 'At ' + `self.topOfStack` + ', process XML : <' + name + '...'     
                self.topOfStack=self.topOfStack.startElement(name,attributes) 
                        
            except Exception, detail:
                message=str(detail)
                        
                if self.topOfStack and isinstance(self.topOfStack,Annotatable):    
                    self.topOfStack.addError(message)                            
                else:
                    self.addError(message)
                                
                log.warn('Failed to parse XML : ' + message, exc_info=1)
                        
        #print 'Current Top: ' + `self.topOfStack`
        self.elementStack.append(self.topOfStack)

    def characters(self, s):
        """See ContentHandler class."""
        if not (None == self.topOfStack): 
            # Pass characters...
            #print 'At ' + `self.topOfStack` + ', process chars : \'' + s + '\''                                              
            self.topOfStack.characters(s)
        else:
            log.error('No top of stack for characters : ' + s)

    def endElement (self, name):
        """See ContentHandler class."""
        del self.elementStack[-1]
        self.topOfStack=self.elementStack[-1]
 
    def error(self, exception):
        self.addError('XML error : ' + str(exception))
        #log.error("Handle a recoverable error." + str(exception), exc_info=1)
        #raise exception
        
    def fatalError(self, exception):
        self.addError('XML error : ' + str(exception))
        #log.error("Handle a non-recoverable error." + str(exception), exc_info=1)
        #raise exception

    def warning(self, exception):
        self.addWarning('XML warning' + str(exception))
        #log.warn("Handle a warning." + str(exception), exc_info=1)
        
        
###############################################################################
# Base classes for the Gump object model
#
# This is actually where most of the logic and complexity is handled,
# allowing the actual model to be rather simple and compact. All
# elements of the GOM should extend GumpXMLObject or a subclass of GumpXMLObject.
###############################################################################
# :TODO:#1: class GumpXMLObject(Annotatable,object):
class GumpXMLObject(object):
    """
    
            Helper XML Object.

        Attributes become properties.    Characters become the string value
        of the element. An internal attribute with name '@text' is used
        for storing all the characters (as opposed to xml elements and xml
        attributes).
        
    """

    def __init__(self,attrs):
        
        # Ensure we have an 'annotations' list
        #if not hasattr(self,'annotations') or not isinstance(self.annotations,list):
        #        Annotatable.__init__(self)        
        
        # Transfer attributes
        for (name,value) in attrs.items():
            if not name == '@basedir':
                self.__dict__[name]=value
                        
        # Setup internal character field
        if not self.__dict__.has_key('@text'): 
            self.__dict__['@text']=''
            self.init()
        
    def __len__(self):
        # Exclude internal '@text', so reduce by 1
        l=len(self.__dict__.keys())
        if l > 1: return (l - 1)
        return len(self.__dict__['@text'])
            
    def __nonzero__(self):
        if len(self) > 0: return 1
        return len(self.__dict__['@text']) > 0
        
    def hasString(self):
        return len(self.__dict__['@text']) > 0    
                
    def hasAttr(self,name):
        return hasattr(self,name)
        
    def transfer(self,name,default=None):
        result=default
        if hasattr(self,name):
            x=getattr(self,name)
            if isinstance(x,GumpXMLObject) and x.hasString():
                result=str(self)
            else:
                result=x
        return result
    
    def getTagName(self):
        return self.__class__.__name__.lower().replace('xml','')
 
    def startElement(self, name, attrs):
        """ 
        
            Handles XML events via a series of delegations based upon
            the tag, and the 'metadata' (typed member data) on this
            object (i.e. the sub-class additions)                
        
            See ContentHandler class.
                
        """
        try:
            #print "Try __getattribute__ on [" + self.__class__.__name__ + "] for [" + name + "]"
            
            # If we are dealing with a Single or Multiple,
            # return an instance.
            attr=self.__getattribute__(name)
            
            #print "Try __getattribute__ -> [" + `attr` + "]"
            
            # These are delegated to objects
            if isinstance(attr,Single): return attr(attrs)
            if isinstance(attr,Multiple): return attr(attrs)
            
            # Simple attributes            
            return attr # :TODO: Get this checked out
        
        except AttributeError:
            # It is OK if people extend the GOM...
            message="No metadata related to tag '%s' on %s" % \
                                (name, self.__class__.__name__)
            # :TODO:#1: self.addInfo(message)
            log.debug(message)

    #
    # Process characters...
    #
    def characters(self,string):
        """See ContentHandler class."""
        self.__dict__['@text'] += string

    def __setitem__(self,name,value):
        self.__dict__[name]=value

    def __getitem__(self,i):
        if self.__dict__.has_key(i): return self.__dict__[i]   
        raise IndexError, "GumpXMLObject: No such index: " + `i` 
        
    def __delitem__(self,name):
        del self.__dict__[name]

    def __getattr__(self,name):    
        raise AttributeError, "GumpXMLObject: No such attribute: " + name        

    def __str__(self):
        """String representation of the element is the element content."""
        return self.__dict__['@text'].strip()

    def __repr__(self):
        return self.__class__.__name__
        
    def init(self):
        pass

 
class DocRoot(GumpXMLObject):    
    """Document roots are workspaces or targets of hrefs."""

    def __init__(self,name,cls):
        GumpXMLObject.__init__(self,{})
        self.name=name
        self.cls=cls
        self.element=None

    def startElement(self, name, attrs):
        if name<>self.name:
            raise RuntimeError, "Incorrect element, expected %s, found %s" % (self.name,name)
            
        # Construct and capture first node...
        
        self.element=self.cls(attrs)
        
        return self.element

class Named(GumpXMLObject):
    """
    
            Named elements (e.g., project,module,repository).

        Supports href and maintains a list of elements. Duplicate
        names get merged. Classes declared of this type must declare
        a static list property."""

    def __new__(cls,attrs):
        """ A Named element """     
        
        element=None
        #
        # Note: The first time a named is imported it is probably
        # not 'named' but with an 'href' to the 'remote' metadata.
        #
        name=attrs.get('name')        
        
        #     
        # A 'named' element can also be 'downloaded' via an href
        # to the full metadata, as such we have an interesting
        # 'bootstrap' that
        #            
        href=attrs.get('href')
        
        #log.debug('New Named [' + cls.__name__ + '] name=[' + str(name) + '] href=[' + str(href) + ']')
        
        if href:
            #log.debug('Download metadata from : [' + href + ']')        
        
            # Stored by caller...
            basedir=attrs.get('@basedir')            
            del attrs['@basedir']
                
            # Download (relative to base)
            if not href.startswith('http://'):
                newHref=gumpPath(href,basedir);
            else:
                newHref=cacheHTTP(href)
                    
            if newHref:
                # Get a tag name from a classname
                tag =    cls.__name__.lower().replace('xml','')
                                                
                try:
                    parser=SAXDispatcher(tag, cls, basedir)                                                                            
                    parser.parse(newHref)                                                                
                    element=parser.docElement         
                                
                    # Copy over any XML errors/warnings
                    #transferAnnotations(parser, element)    
                                
                except Exception, detail:
                    message='Failed to parse XML @ [' + newHref + ']. Details: ' + str(detail)
                    log.error(message, exc_info=1)     
                    raise RuntimeError, message
            else:
                # :TODO: Set any object "invalid"?
                message='HREF ['+href+'] not loaded'
                #log.error(message, exc_info=1)
                raise RuntimeError, message
                
            #
            # Stash for general reference/interest
            #
            if element:
                element.href=href                                        
                
            # Return the downloaded element instead...
            return element                
        else:
            try:
                # We've this already?
                element=cls.map[name]
            except:
                if name: 
                    # Create it first time...
                    element=GumpXMLObject.__new__(cls,attrs)
                    # Store in class map
                    cls.map[name]=element
                else:
                    message='Neither downloaded nor named: [' + str(cls) + ' : ' + `attrs` + ']'
                    log.error(message)
                    raise RuntimeError, message
            
        return element
                                
        # Same if same type, and same name
        # i.e project context X is not equals to module context X
    def __eq__(self,other):
        return self.__class__ == other.__class__ and self.name == other.name
                
    def __cmp__(self,other):
        return cmp(self.name,other.name)
                 
    def __hash__(self):
        return hash(self.name)
                        
    def __repr__(self):
        return self.__class__.__name__+':'+self.name
                
    def __str__(self):
        return self.__class__.__name__+':'+self.name
                
    def getName(self):
        return self.name        
   
class Single(GumpXMLObject):
    """
  
      Properties which are only ever expected to hold a single value.
      
      This class provides attributes (e.g. getattr/setattr)
      
    """

    def __init__(self,cls=GumpXMLObject):
        GumpXMLObject.__init__(self,{})
        """The cls passed in determines what type the delegate instance will have."""
        self.delegate=None
        self.cls=cls

    def __call__(self,attrs):
        if self.delegate:
            # Update the attributes on the instance
            if attrs.get('@basedir'): del attrs['@basedir']
            self.delegate.__dict__.update(dict(attrs))
        else:
            # Construct and instance of this
            self.delegate=self.cls(attrs)
        return self.delegate

    def __getattr__(self,name):
        if self.delegate:
            try:
                return self.delegate.__getattribute__(name)
            except:
                return self.delegate[name] 
        raise AttributeError, "Single: No such attribute: " + name

    def __repr__(self):
        s=GumpXMLObject.__repr__(self)
        if self.delegate: 
            s+=':'
            s+=self.delegate.__repr__()
        return s
        
    def __str__(self):
        if self.delegate: return str(self.delegate)
        return ''
        
    def __nonzero__(self):
        if self.delegate: 
            return self.delegate.__nonzero__()
        return False

    def __setitem__(self,name,value):
        self.delegate[name]=value

    def __getitem__(self,i):
        if i in self.delegate.__dict__: 
            return self.delegate.__dict__[i]        
        raise IndexError, "Single: No such index: " + `i`
        
    def hasString(self):
        if self.delegate and isinstance(self.delegate,GumpXMLObject): 
            return self.delegate.hasString()
        return False 
                
    def hasAttr(self,name):
        return hasattr(self,name)
        if self.delegate and isinstance(self.delegate,GumpXMLObject): 
            return self.delegate.hasAttr(name)
        return False 
        
    def transfer(self,name,default=None):
        if self.delegate and isinstance(self.delegate,GumpXMLObject):
            return self.delegate.transfer(name,default)            
        return None            
        
class Multiple(list,GumpXMLObject):
    """
    
            Properties which can hold multiple instances.
            
            
            This class provides items (e.g. getitem/setitem)
    
    """

    def __init__(self,cls=GumpXMLObject):
        """The cls passed in determines what type the delegate instances will have."""
        list.__init__(self)        
        GumpXMLObject.__init__(self,{}) 
             
        # Store the type of class we are a multiple of..
        self.cls=cls

    def __call__(self,attrs):
        # Construct a new instance
        object=self.cls(attrs)
        # Stash it into the list
        self.append(object)
        # Return it (to handle more XML events)
        return object

def xmlize(nodeName,object,f=None,indent='',delta='    '):

    if f==None: f=StringIO.StringIO()

    # :TODO: Do hack for when content is bad and a parse fails
    # so the XML loader has to set element=None
    if not object: return
            
    attrs=[nodeName]
    elements=[]
    text=''
    encoding='latin-1'

    # iterate over the object properties
    for name in object.__dict__:
        if name.startswith('__') and name.endswith('__'): continue
        if name == 'annotations': continue
        
        var=getattr(object,name)

        # avoid nulls, metadata, and methods
        if not var: continue
        if isinstance(var,types.TypeType): continue
        if isinstance(var,types.MethodType): continue

        # determine if the property is text, attribute, or element
        if name=='@text':
            text=var
        elif isinstance(var,types.StringTypes):
            attrs.append('%s="%s"' % (name,escape(var)))
        else:
            elements.append((name,var))

    # format for display
    if not elements:
        # use compact form for elements without children
        if text.strip():
            f.write( '%s<%s>%s</%s>\n' % \
                    (indent,' '.join(attrs).encode(encoding),	\
                                text.strip().encode(encoding),nodeName))
        else:
            f.write( '%s<%s/>\n' % (indent,' '.join(attrs).encode(encoding)))
    else:
        # use full form for elements with children
        f.write( '%s<%s>\n' % (indent,' '.join(attrs).encode(encoding)))
        newindent=indent+delta
        for (name,var) in elements:
            if isinstance(var,list):
                # multiple valued elements
                for e in var: xmlize(name,e,f,newindent,delta)
            elif isinstance(var,Single):
                # single valued elements
                xmlize(name,var.delegate,f,newindent,delta)
        f.write( '%s</%s>\n' % (indent,nodeName.encode(encoding)))

    # if the file is a StringIO buffer, return the contents
    # as a stream (cool feature, especially for testing)
    if isinstance(f,StringIO.StringIO):
        f.seek(0)
        return f.read()            
            
#
# Serialize an object to XML (to a stream/file)
#            
def xmlwrite(filename,tag,obj):
    f=open( filename, 'w')
    try:
        xmlize(tag,obj,f)
        # print "Generated [" + filename + "] successfully."
    finally:
        # Since we may exit via an exception, close fp explicitly.
        f.close()        
 