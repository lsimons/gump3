#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/document/Attic/xdoc.py,v 1.11 2004/02/10 20:18:40 ajack Exp $
# $Revision: 1.11 $
# $Date: 2004/02/10 20:18:40 $
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
    xdoc generation, for forrest
"""

import socket
import time
import os
import sys
import logging
from types import NoneType
from xml.sax.saxutils import escape


from gump import log
from gump.utils import *
from gump.utils.xmlutils import xmlize
from gump.utils.owner import *

class XDocContext(Ownable):
    def __init__(self,stream=None,pretty=1,depth=0):
        
        Ownable.__init__(self)
        
        self.depth=depth
        self.pretty=pretty
        
        if stream:
            self.stream=stream
        else:
            log.debug('Create transient stream ['+`self.depth`+']...')
            self.stream=StringIO.StringIO()
                
    def createSubContext(self,transient=0):
        if not transient:
            sub = XDocContext(self.stream,self.pretty,self.depth+1)
        else:
            if not isinstance(transient,int):
                raise RuntimeError, 'Create transient w/ non-int flag ['+`transient`+']'               
            sub = XDocContext(None,self.pretty,self.depth+1)
        sub.setOwner(self)
        return sub
    
    def performIO(self,stuff):
        try:
            self.stream.write(stuff)
        except Exception, details:
            log.error('Failed to write [' + stuff + '] @ ['+`self.depth`+'] : ' + str(details))
            self.displayOwnership()
            raise
            
    def writeIndented(self,xdoc):
        if self.pretty:
            self.performIO(getIndent(self.depth))
        self.performIO(xdoc)
        
    def write(self,xdoc):
        self.performIO(xdoc)
        
    def writeLine(self,xdoc):
        self.performIO(xdoc)
        self.performIO('\n')
        
    def writeLineIndented(self,xdoc):
        if self.pretty:
            self.performIO(getIndent(self.depth))
        self.performIO(xdoc)
        self.performIO('\n')
        
    def writeRawLineIndented(self,raw):
        if self.pretty:
            self.performIO(getIndent(self.depth))    
        self.performIO(escape(raw))
        self.performIO('\n')
        
    def writeRawLine(self,raw):
        self.performIO(escape(raw))
        self.performIO('\n')
        
    def writeRawIndented(self,raw):
        if self.pretty:
            self.performIO(getIndent(self.depth))    
        self.performIO(escape(raw))
        
    def writeRaw(self,raw): 
        self.performIO(escape(raw))
    
    def isTransient(self):
        return isinstance(self.stream,StringIO.StringIO)
        
    def writeContext(self,otherContext):
        
        if otherContext.isTransient(): 
            #
            # Transfer that stream to ours...
            # ... if not ours
            #         
            stream=otherContext.stream
            if not stream == self.stream:
                stream.seek(0)
                self.performIO(stream.read())
                stream.close()
                    
    def close(self):
        #if isinstance(self.stream,StringIO.StringIO): 
        #    self.stream.seek(0)
        #    print(self.stream.read())
        #else:
        if not self.isTransient():
            try:
                self.stream.close()
            except: pass
            
class XDocPiece(Ownable):
    def __init__(self,context=XDocContext()):
        Ownable.__init__(self)    
        
        self.context=context
        self.subpieces=[]
        self.keeper=1
        self.emptyOk=0        
        
    def __repr__(self):
        return str(self.__class__)
        
    def __str__(self):
        return str(self.__class__)
        
    def createSubContext(self,transient=0):
        #
        # Create a new context
        #
        return self.context.createSubContext(transient)

    def storePiece(self,piece):
        #
        # Store it for later
        #
        self.subpieces.append(piece)
        
        # Capture Ownership
        piece.setOwner(self)
        
        return piece
  
        
    def serialize(self):
        self.callStart()        
        self.middle()
        self.callEnd()
        
    def callStart(self,piece=None):
        if not piece: piece = self
        if hasattr(piece,'start') and callable(piece.start):
            piece.start()
            
    def middle(self):
        if not self.subpieces and not self.isEmptyOk():
            log.warn('Empty [' + `self.__class__` + '] probably isn\'t good...')
            self.displayOwnership()
            
        for sub in self.subpieces:
            sub.serialize()
            
            # Gather 
            if sub.isTransient() and sub.isKeeper():
                self.context.writeContext(sub.context)

    def callEnd(self,piece=None):
        if not piece: piece = self
        if hasattr(piece,'end') and callable(piece.end):
            piece.end()    
                        
    def createRaw(self,raw=None):
        return self.storePiece(XDocRaw(self.createSubContext(),raw))     
                        
    def createComment(self,raw=None):
        return self.storePiece(XDocComment(self.createSubContext(),raw))                     
            
    def close(self):
        self.context.close()
              
    def isTransient(self):
        return self.context.isTransient()
        
    def isKeeper(self):
        return self.keeper
        
    def setEmptyOk(self, ok):
        self.emptyOk=ok
        
    def isEmptyOk(self):
        return self.emptyOk
                
class XDocSection(XDocPiece):
    def __init__(self,context,title):
        XDocPiece.__init__(self,context)
        self.title=title
        
    def __repr__(self):
        return str(self.__class__) + ':' + self.title
        
    def __str__(self):
        return str(self.__class__) + ':' + self.title
        
    def start(self):
        self.context.writeLineIndented('<section><title>%s</title>' % (self.title))
        
    def end(self):
        self.context.writeLineIndented('</section>')
        
    def createParagraph(self,text=None,transient=0):
        return self.storePiece(XDocParagraph(self.createSubContext(transient),text))
        
    def createTable(self,headings=None,transient=0):
        return self.storePiece(XDocTable(self.createSubContext(transient),headings))
        
    def createList(self,transient=0):
        return self.storePiece(XDocList(self.createSubContext(transient)))
            
    def createNote(self,text=None):
        return self.storePiece(XDocNote(self.createSubContext(),text))         
            
    def createWarning(self,text=None):
        return self.storePiece(XDocWarning(self.createSubContext(),text))         
            
    def createSource(self,text=None):
        return self.storePiece(XDocSource(self.createSubContext(),text))         
         
    def createSection(self,title,transient=0):
        return self.storePiece(XDocSection(self.createSubContext(transient),title))
                               
class XDocParagraph(XDocPiece):
    def __init__(self,context,text):
        XDocPiece.__init__(self,context)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.write('<p>')
        
    def end(self):
        self.context.writeLine('</p>')
        
    def createText(self,text=None,transient=0):
        return self.storePiece(XDocText(self.createSubContext(transient),text))
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext()))
        
    def createStrong(self,text=None,transient=0):
        return self.storePiece(XDocStrong(self.createSubContext(transient),text))

    def createLink(self,href,text=None):
        return self.storePiece(XDocLink(self.createSubContext(),href,text))              
        
      
class XDocComment(XDocPiece):
    def __init__(self,context,text):
        XDocPiece.__init__(self,context)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.writeIndented('<!-- ')
        
    def end(self):
        self.context.writeLine(' -->')
        
    def createText(self,text=None,transient=0):
        return self.storePiece(XDocText(self.createSubContext(transient),text))
                                
class XDocBreak(XDocPiece):
    def __init__(self,context):
        XDocPiece.__init__(self,context)
        
    def start(self):
        self.context.writeIndented('<br/>')
        
    def end(self):   pass
    def middle(self): pass      
                                
class XDocStrong(XDocPiece):
    def __init__(self,context,text):
        XDocPiece.__init__(self,context)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.write('<strong>')
        
    def end(self):
        self.context.write('</strong>')
        
    def createText(self,text=None,transient=0):
        return self.storePiece(XDocText(self.createSubContext(transient),text))
            
class XDocList(XDocPiece):
    def __init__(self,context):
        XDocPiece.__init__(self,context)
        
    def start(self):
        self.context.writeLineIndented('<ul>')
        
    def end(self):
        self.context.writeLineIndented('</ul>')
        
    def createItem(self,text=None):
        return self.storePiece(XDocItem(self.createSubContext(),text))  
                
    def createEntry(self,title,text=None):
        item=self.createItem()
        item.createStrong(title)
        if not isinstance(text,NoneType):
            item.createText(str(text))
        return item
                       
class XDocItem(XDocPiece):
    def __init__(self,context,text=None):
        XDocPiece.__init__(self,context)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.writeIndented('<li>')
        
    def end(self):
        self.context.writeLine('</li>')
        
    def createStrong(self,text=None):
        return self.storePiece(XDocStrong(self.createSubContext(),text))
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),text))  
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext()))        
        
    def createLink(self,href,text=None):
        return self.storePiece(XDocLink(self.createSubContext(),href,text))              
        
    def createFork(self,href,text=None):
        return self.storePiece(XDocFork(self.createSubContext(),href,text))    
                
    def createIcon(self,href,alt=None):
        return self.storePiece(XDocIcon(self.createSubContext(),href,alt))     
            
class XDocTable(XDocPiece):
    def __init__(self,context,headings=None):
        XDocPiece.__init__(self,context)        
        if headings:
            headerRow=self.createRow()
            for heading in headings:
                headerRow.createHeader(heading)
        
    def start(self):
        self.context.writeLineIndented('<table>')
        
    def end(self):
        self.context.writeLineIndented('</table>')
        
    def createRow(self,datum=None):
        if not datum:
            return self.storePiece(XDocRow(self.createSubContext()))
        else:
            row=self.createRow()
            if isinstance(datum,list):
                for data in datum:
                    row.createData(data)
            else:
                row.createData(datum)
            return row
                    
    def createEntry(self,title,data=None):
        row=self.createRow()
        titleData=row.createData(title)
        if not isinstance(data,NoneType):
            dataData=row.createData(str(data))
        return row
        
    def createLine(self,data=None):
        row=self.createRow()
        dataData=row.createData(data)
        return dataData
                       
class XDocRow(XDocPiece):
    def __init__(self,context):
        XDocPiece.__init__(self,context)
        
    def start(self):
        self.context.writeLineIndented('<tr>')
        
    def end(self):
        self.context.writeLineIndented('</tr>')
        
    def createHeader(self,text=None):
        return self.storePiece(XDocTableHeader(self.createSubContext(),text))
        
    def createData(self,text=None):
        return self.storePiece(XDocTableData(self.createSubContext(),text))
                          
class XDocTableHeader(XDocPiece):
    def __init__(self,context,text):
        XDocPiece.__init__(self,context)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.writeIndented('<th>')
        
    def end(self):
        self.context.writeLine('</th>')
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),text))
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext()))
                          
class XDocTableData(XDocPiece):
    def __init__(self,context,text):
        XDocPiece.__init__(self,context)
        if not isinstance(text,NoneType):
            self.createText(str(text))
        
        # Empty (no data) 'ok'
        # self.setEmptyOk(1)
        
    def start(self):
        self.context.writeIndented('<td>')
        
    def end(self):
        self.context.writeLine('</td>')
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),text))    
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext()))
        
    def createLink(self,href,text=None):
        return self.storePiece(XDocLink(self.createSubContext(),href,text))              
        
    def createFork(self,href,text=None):
        return self.storePiece(XDocFork(self.createSubContext(),href,text))            
        
    def createStrong(self,text=None):
        return self.storePiece(XDocStrong(self.createSubContext(),text))

class XDocNote(XDocPiece):
    def __init__(self,context,text):
        XDocPiece.__init__(self,context)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.writeLineIndented('<note>')
        
    def end(self):
        self.context.writeLine('</note>')
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),text))          
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext()))    

    def createStrong(self,text=None,transient=0):
        return self.storePiece(XDocStrong(self.createSubContext(transient),text))
        
    def createLink(self,href,text=None):
        return self.storePiece(XDocLink(self.createSubContext(),href,text))              
        
    def createFork(self,href,text=None):
        return self.storePiece(XDocFork(self.createSubContext(),href,text))
        
class XDocWarning(XDocPiece):
    def __init__(self,context,text):
        XDocPiece.__init__(self,context)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.writeLineIndented('<warning>')
        
    def end(self):
        self.context.writeLine('</warning>')
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),text))          
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext()))    

    def createStrong(self,text=None,transient=0):
        return self.storePiece(XDocStrong(self.createSubContext(transient),text))

            
class XDocSource(XDocPiece):
    def __init__(self,context,text=None):
        XDocPiece.__init__(self,context)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.writeIndented('<source>')
        
    def end(self):
        self.context.writeLine('</source>')
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),text))     
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext()))         
        
class XDocLink(XDocPiece):
    def __init__(self,context,href,text=None):
        XDocPiece.__init__(self,context)
        self.href=href
        if text: 
            self.createText(text)
        
    def start(self):
        self.context.write('<link href=\'' + escape(self.href) + '\'>')
        
    def end(self):
        self.context.write('</link>')
        
    def createText(self,text):
        return self.storePiece(XDocText(self.createSubContext(),text))     
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext()))    
        
    def createIcon(self,href,alt=None):
        return self.storePiece(XDocIcon(self.createSubContext(),href,alt))              
                
class XDocFork(XDocPiece):
    def __init__(self,context,href,text=None):
        XDocPiece.__init__(self,context)
        self.href=href
        if text:
            self.createText(text)
        
    def start(self):
        self.context.write('<fork href=\'' + escape(self.href) + '\'>')
        
    def end(self):
        self.context.write('</fork>')
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),text))    
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext()))          
        
class XDocIcon(XDocPiece):
    def __init__(self,context,href,alt):
        XDocPiece.__init__(self,context)
        self.href=href
        if alt:
            self.alt=alt
        else:
            self.alt=href
        
    def start(self):
        self.context.write('<icon src=\'' + escape(self.href) + 	\
                '\' alt=\'' + escape(self.alt) + '\' />')
                
    def middle(self): pass          
        
class XDocText(XDocPiece):
    def __init__(self,context,text):
        XDocPiece.__init__(self,context)
        self.text = text
        
    def middle(self):
        self.context.writeRaw(self.text)
 
#       
# Some raw xdocs (for when too lazy to create classes)
#
class XDocRaw(XDocPiece):
    def __init__(self,context,raw):
        XDocPiece.__init__(self,context)
        self.raw = raw
        
    def middle(self):
        self.context.writeLine(str(self.raw))
        
class XDocDocument(XDocPiece):
    def __init__(self,title,output=None):
        XDocPiece.__init__(self)  
        if isinstance(output,types.StringTypes):    
            self.xfile=output
            log.debug("Documenting to file : [" + self.xfile + "]")                    
            self.output=open(self.xfile, 'w')
        else:
            self.output=output        
        self.context=XDocContext(self.output)
        self.title=title
                
    def start(self):
            
        self.context.writeLine('<?xml version="1.0" encoding="ISO-8859-1"?>')
        self.context.writeLine('<!DOCTYPE document PUBLIC "-//APACHE//DTD Documentation V1.1//EN" "./dtd/document-v11.dtd">')
        self.context.writeLine('<!-- Automatically Generated by Python Gump: http://jakarta.apache.org/gump -->\n')
        self.context.writeLine('<document>')
        self.context.writeLine(' <header>')
        self.context.writeLine('  <title>%s</title>' % (self.title))
        self.context.writeLine('  <authors>')
        self.context.writeLine('   <person id="gump" name="Gump" email="gump@lists.apache.org"/>')
        self.context.writeLine('  </authors>')
        self.context.writeLine(' </header>')
        self.context.writeLine('<body>')    
        
    def end(self):
        self.context.writeLine('</body>')
        self.context.writeLine('</document>')            
        self.close()  

    def createSection(self,title,transient=0):
        return self.storePiece(XDocSection(self.createSubContext(transient),title))
                
    def createTable(self,headings=None,transient=0):
        return self.storePiece(XDocTable(self.createSubContext(transient),headings))

    def createSource(self,text=None):
        return self.storePiece(XDocSource(self.createSubContext(),text))         
    
    def createParagraph(self,text=None,transient=0):
        return self.storePiece(XDocParagraph(self.createSubContext(transient),text))
        
    def createNote(self,text=None):
        return self.storePiece(XDocNote(self.createSubContext(),text))  
        
    def createWarning(self,text=None):
        return self.storePiece(XDocWarning(self.createSubContext(),text))      
        
    
    