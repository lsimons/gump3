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
    xdoc generation, for forrest
"""

import socket
import time
import os
import sys
import logging
import types

from types import NoneType
from xml.sax.saxutils import escape


from gump import log
from gump.utils import *
from gump.utils.owner import *

#
# MAP anything outside 32..128 to _
#
MAP=[]
UMAP=[]
i=0
while i<=255:
    # Allow TAB, LF, CR and 32 .. 128.
    if i == 9 or i == 10 or i==13 or (i >= 32 and i < 128):
        MAP.append(chr(i))
        UMAP.append(unicode(chr(i)))
    else:
        # Map others to underscore
        MAP.append(chr(95))
        UMAP.append(unicode(chr(95)))
    i+=1
STRING_MAP_TABLE=''.join(MAP)
UNICODE_MAP_TABLE=unicode('').join(UMAP)

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
                    	
    def __del__(self):  
        Ownable.__del__(self)
        self.stream=None  
        
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
        self.performIO(self.map(raw))
        self.performIO('\n')
        
    def writeRawLine(self,raw):   
        self.performIO(self.map(raw))
        self.performIO('\n')
        
    def writeRawIndented(self,raw):
        if self.pretty:
            self.performIO(getIndent(self.depth))    
        self.performIO(self.map(raw))
        
    def writeRaw(self,raw): 
        self.performIO(self.map(raw))
    
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
            self.stream.close()
            
    def map(self,raw):
        if isinstance(raw,types.UnicodeType):
            return escape(raw.translate(UNICODE_MAP_TABLE))
        return escape(raw.translate(STRING_MAP_TABLE))
        
class XDocPiece(Ownable):
    def __init__(self,context=None):
        Ownable.__init__(self)            
        if not context:
            context=XDocContext()
        self.context=context
        self.subpieces=[]
        self.keeper=1
        self.emptyOk=0        
        
    def __del__(self):
        Ownable.__del__(self)
        self.subpieces=None        
        self.context=None
                
    def __repr__(self):
        return self.__class__.__name__
        
    def __str__(self):
        return self.__class__.__name__
        
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
        
    def unlink(self):
        # Unlink subpieces...
        if self.subpieces:
            for subpiece in self.subpieces:
                subpiece.unlink()
        
        # Then destroy the list
        self.subpieces=None
        
        self.context=None
        
        # Unlink oneself
        self.setOwner(None)
                
class XDocSection(XDocPiece):
    def __init__(self,context,title):
        XDocPiece.__init__(self,context)
        self.title=title
        
    def __repr__(self):
        return self.__class__.__name__ + ':' + self.title
        
    def __str__(self):
        return self.__class__.__name__ + ':' + self.title
        
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

    def createEmphasis(self,text=None,transient=0):
        return self.storePiece(XDocEmphasis(self.createSubContext(transient),text))

    def createLink(self,href,text=None):
        return self.storePiece(XDocLink(self.createSubContext(),href,text))                    
        
    def createFork(self,href,text=None):
        return self.storePiece(XDocFork(self.createSubContext(),href,text))  
        
    def createIcon(self,href,alt=None):
        return self.storePiece(XDocIcon(self.createSubContext(),href,alt))             
      
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
            
class XDocEmphasis(XDocPiece):
    def __init__(self,context,text):
        XDocPiece.__init__(self,context)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.write('<em>')
        
    def end(self):
        self.context.write('</em>')
        
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

    def createEmphasis(self,text=None,transient=0):
        return self.storePiece(XDocEmphasis(self.createSubContext(transient),text))
        
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
        titleData=row.createData().createStrong(title)
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

    def createEmphasis(self,text=None,transient=0):
        return self.storePiece(XDocEmphasis(self.createSubContext(transient),text))
                
    def createIcon(self,href,alt=None):
        return self.storePiece(XDocIcon(self.createSubContext(),href,alt))   

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

    def createEmphasis(self,text=None,transient=0):
        return self.storePiece(XDocEmphasis(self.createSubContext(transient),text))
        
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

    def createEmphasis(self,text=None,transient=0):
        return self.storePiece(XDocEmphasis(self.createSubContext(transient),text))

            
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
        if not href: raise RuntimeError, 'Can not fork with nowhere to go.'
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
            
    def createIcon(self,href,alt=None):
        return self.storePiece(XDocIcon(self.createSubContext(),href,alt))               
        
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
        
    def unlink(self):
        XDocPiece.unlink(self)             
        self.text=None
        
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
        self.context.writeLine('<!-- Automatically Generated by Python Gump: http://gump.apache.org/ -->\n')
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
        
        # Probably ought do this higher up
        self.unlink()
        invokeGarbageCollection()
        

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
        
    
    