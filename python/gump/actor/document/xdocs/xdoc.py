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
    XDOC generation, for Forrest.
    XHTML generation
"""

import socket
import time
import os
import sys
import logging
import types

from xml.sax.saxutils import escape

from gump import log
from gump.util import *

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
        UMAP.append(str(chr(i)))
    else:
        # Map others to underscore
        MAP.append(chr(95))
        UMAP.append(str(chr(95)))
    i+=1
STRING_MAP_TABLE=''.join(MAP)
UNICODE_MAP_TABLE=str('').join(UMAP)

class XDocContext:
    def __init__(self,stream=None,pretty=False,depth=0):  
        self.depth=depth
        self.pretty=pretty
        
        if stream:
            self.stream=stream
        else:
            log.debug('Create transient stream ['+repr(self.depth)+']...')
            self.stream=io.StringIO()
                
    def createSubContext(self,transient=False):
        if not transient:
            sub = self
        else:              
            sub = XDocContext(None,self.pretty,self.depth+1)
        return sub
    
    def performIO(self,stuff):
        try:
            self.stream.write(stuff)
        except Exception as details:
            log.error('Failed to write [' + stuff + '] @ ['+repr(self.depth)+'] : ' + str(details))
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
        return isinstance(self.stream,io.StringIO)
        
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
        #if isinstance(self.stream,io.StringIO): 
        #    self.stream.seek(0)
        #    print(self.stream.read())
        #else:
        if not self.isTransient():     
            self.stream.close()
            
    def map(self,raw):
        if isinstance(raw,str):
            return escape(raw.translate(UNICODE_MAP_TABLE))
        return escape(raw.translate(STRING_MAP_TABLE))
        
class XDocPiece:
    """
    A piece of an XDOC (a node)
    """
    def __init__(self,context=None,config=None,style=None):
        if not context: context=XDocContext()
        self.context=context
        self.config=config
        self.subpieces=None
        self.style=style
        self.keeper=True      
        
    def __repr__(self):
        return self.__class__.__name__
        
    def __str__(self):
        return self.__class__.__name__
        
    def createSubContext(self,transient=False):
        # Create a new context
        return self.context.createSubContext(transient)

    def storePiece(self,piece):
        #
        # Store it for later
        #
        if not self.subpieces:
            self.subpieces=[]
            
        self.subpieces.append(piece)
        
        return piece

    def serialize(self):
        if self.keeper: 
            self.callStart()        
            self.middle()
            self.callEnd()
        
    def callStart(self,piece=None):
        if not piece: piece = self
        if hasattr(piece,'start') and callable(piece.start):
            piece.start()
            
    def middle(self):
        if not self.subpieces:
            log.warn('Empty [' + repr(self) + '] probably isn\'t good...')
        else:
            for sub in self.subpieces:
                sub.serialize()
            
                # Gather 
                if sub.isTransient() and sub.keeper:
                    self.context.writeContext(sub.context)

    def callEnd(self,piece=None):
        if not piece: piece = self
        if hasattr(piece,'end') and callable(piece.end):
            piece.end()    
                        
    def createRaw(self,raw=None):
        return self.storePiece(XDocRaw(self.createSubContext(),self.config,raw))     
                        
    def createComment(self,raw=None):
        return self.storePiece(XDocComment(self.createSubContext(),self.config,raw))                     
            
    def close(self):
        self.context.close()
              
    def isTransient(self):
        return self.context.isTransient()
        
    def isKeeper(self):
        return self.keeper
        
    def setStyle(self,style):
        # Force Style to be upper case
        self.style=style
        
    def getStyle(self,style):
        return self.style
    
    def getStyleAttribute(self):
        if self.style:
            return ' class="' + self.style + '"' 
        return ''
                
class XDocSection(XDocPiece):
    def __init__(self,context,config,title):
        XDocPiece.__init__(self,context,config)
        self.title=title
        
    def __repr__(self):
        return self.__class__.__name__ + ':' + self.title
        
    def __str__(self):
        return self.__class__.__name__ + ':' + self.title
        
    def start(self):
        if not self.config.isXhtml():    
            self.context.writeLineIndented('<section><title>%s</title>' % (self.title))
        else:
            self.context.writeLineIndented('<h3>%s</h3>' % (self.title))    
        
    def end(self):
        if not self.config.isXhtml():      
            self.context.writeLineIndented('</section>')
        # Not pretty.
        #else:
        #    self.context.writeLineIndented('<hr/>')    
        
    def createParagraph(self,text=None,transient=False):
        return self.storePiece(XDocParagraph(self.createSubContext(transient),self.config,text))
        
    def createTable(self,headings=None,transient=False):
        return self.storePiece(XDocTable(self.createSubContext(transient),self.config,headings))
        
    def createList(self,transient=False):
        return self.storePiece(XDocList(self.createSubContext(transient),self.config))
            
    def createNote(self,text=None):
        return self.storePiece(XDocNote(self.createSubContext(),self.config,text))         
            
    def createWarning(self,text=None):
        return self.storePiece(XDocWarning(self.createSubContext(),self.config,text))         
            
    def createSource(self,text=None):
        return self.storePiece(XDocSource(self.createSubContext(),self.config,text))         
         
    def createSection(self,title,transient=False):
        return self.storePiece(XDocSection(self.createSubContext(transient),self.config,title))
                               
class XDocParagraph(XDocPiece):
    def __init__(self,context,config,text):
        XDocPiece.__init__(self,context,config)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.write('<p>')
        
    def end(self):
        self.context.writeLine('</p>')
        
    def createText(self,text=None,transient=False):
        return self.storePiece(XDocText(self.createSubContext(transient),self.config,text))
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext()))
        
    def createStrong(self,text=None,transient=False):
        return self.storePiece(XDocStrong(self.createSubContext(transient),self.config,text))

    def createEmphasis(self,text=None,transient=False):
        return self.storePiece(XDocEmphasis(self.createSubContext(transient),self.config,text))

    def createLink(self,href,text=None):
        return self.storePiece(XDocLink(self.createSubContext(),self.config,href,text))                    
        
    def createFork(self,href,text=None):
        return self.storePiece(XDocFork(self.createSubContext(),self.config,href,text))  
        
    def createIcon(self,href,alt=None):
        return self.storePiece(XDocIcon(self.createSubContext(),self.config,href,alt))             
      
class XDocComment(XDocPiece):
    def __init__(self,context,config,text):
        XDocPiece.__init__(self,context,config)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.writeIndented('<!-- ')
        
    def end(self):
        self.context.writeLine(' -->')
        
    def createText(self,text=None,transient=False):
        return self.storePiece(XDocText(self.createSubContext(transient),self.config,text))
                                
class XDocBreak(XDocPiece):
    def __init__(self,context,config):
        XDocPiece.__init__(self,context,config)
        
    def start(self):
        self.context.writeIndented('<br/>')
        
    def end(self):   pass
    def middle(self): pass      
                                
class XDocStrong(XDocPiece):
    def __init__(self,context,config,text):
        XDocPiece.__init__(self,context,config)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.write('<strong>')
        
    def end(self):
        self.context.write('</strong>')
        
    def createText(self,text=None,transient=False):
        return self.storePiece(XDocText(self.createSubContext(transient),self.config,text))
            
class XDocEmphasis(XDocPiece):
    def __init__(self,context,config,text):
        XDocPiece.__init__(self,context,config)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.write('<em>')
        
    def end(self):
        self.context.write('</em>')
        
    def createText(self,text=None,transient=False):
        return self.storePiece(XDocText(self.createSubContext(transient),self.config,text))
            
class XDocList(XDocPiece):
    def __init__(self,context,config):
        XDocPiece.__init__(self,context,config)
        
    def start(self):
        self.context.writeLineIndented('<ul>')
        
    def end(self):
        self.context.writeLineIndented('</ul>')
        
    def createItem(self,text=None):
        return self.storePiece(XDocItem(self.createSubContext(),self.config,text))  
                
    def createEntry(self,title,text=None):
        item=self.createItem()
        item.createStrong(title)
        if text is not None:
            item.createText(str(text))
        return item
                       
class XDocItem(XDocPiece):
    def __init__(self,context,config,text=None):
        XDocPiece.__init__(self,context,config)
        if text:
            self.createText(text)
            
    def start(self):
        self.context.writeIndented('<li>')
        
    def end(self):
        self.context.writeLine('</li>')
        
    def createStrong(self,text=None):
        return self.storePiece(XDocStrong(self.createSubContext(),self.config,text))

    def createEmphasis(self,text=None,transient=False):
        return self.storePiece(XDocEmphasis(self.createSubContext(transient),self.config,text))
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),self.config,text))  
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext(),self.config))        
        
    def createLink(self,href,text=None):
        return self.storePiece(XDocLink(self.createSubContext(),self.config,href,text))              
        
    def createFork(self,href,text=None):
        return self.storePiece(XDocFork(self.createSubContext(),self.config,href,text))    
                
    def createIcon(self,href,alt=None):
        return self.storePiece(XDocIcon(self.createSubContext(),self.config,href,alt))     
            
class XDocTable(XDocPiece):
    def __init__(self,context,config,headings=None):
        XDocPiece.__init__(self,context,config)        
        if headings:
            headerRow=self.createRow()
            for heading in headings:
                if isinstance(heading,tuple):
                    (title,style)=heading
                    headerRow.createHeader(title).setStyle(style)
                else:
                    headerRow.createHeader(heading)    
        
    def start(self):
        self.context.writeLineIndented('<table>')
        
    def end(self):
        self.context.writeLineIndented('</table>')
        
    def createRow(self,datum=None):
        if not datum:
            return self.storePiece(XDocRow(self.createSubContext(),self.config))
        else:
            row=self.createRow()
            if isinstance(datum,list):
                for data in datum:
                    if isinstance(data,tuple):
                        (value,style)=data
                        row.createData(value).setStyle(style)
                    else:
                        row.createData(data)
                        
            else:
                row.createData(datum)
            return row
                    
    def createEntry(self,title,data=None):
        row=self.createRow()
        titleData=row.createData().createStrong(title)
        if data is not None:
            dataData=row.createData(str(data))
        return row
        
    def createLine(self,data=None):
        row=self.createRow()
        dataData=row.createData(data)
        return dataData
                       
class XDocRow(XDocPiece):
    def __init__(self,context,config):
        XDocPiece.__init__(self,context,config)
        
    def start(self):
        self.context.writeLineIndented('<tr' + self.getStyleAttribute() + '>')
        
    def end(self):
        self.context.writeLineIndented('</tr>')
        
    def createHeader(self,text=None):
        return self.storePiece(XDocTableHeader(self.createSubContext(),self.config,text))
        
    def createData(self,text=None):
        return self.storePiece(XDocTableData(self.createSubContext(),self.config,text))
                          
class XDocTableHeader(XDocPiece):
    def __init__(self,context,config,text):
        XDocPiece.__init__(self,context,config)
        if text:
            self.createText(text)
        
    def start(self):
        self.context.writeIndented('<th' + self.getStyleAttribute() + '>')
        
    def end(self):
        self.context.writeLine('</th>')
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),self.config,text))
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext(),self.config))
                          
class XDocTableData(XDocPiece):
    def __init__(self,context,config,text):
        XDocPiece.__init__(self,context,config)
        if text is not None:
            self.createText(str(text))
            
    def start(self):
        self.context.writeIndented('<td' + self.getStyleAttribute() + '>')
        
    def end(self):
        self.context.writeLine('</td>')
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),self.config,text))    
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext(),self.config))
        
    def createLink(self,href,text=None):
        return self.storePiece(XDocLink(self.createSubContext(),self.config,href,text))              
        
    def createFork(self,href,text=None):
        return self.storePiece(XDocFork(self.createSubContext(),self.config,href,text))            
        
    def createStrong(self,text=None):
        return self.storePiece(XDocStrong(self.createSubContext(),self.config,text))  

    def createEmphasis(self,text=None,transient=False):
        return self.storePiece(XDocEmphasis(self.createSubContext(transient),self.config,text))
                
    def createIcon(self,href,alt=None):
        return self.storePiece(XDocIcon(self.createSubContext(),self.config,href,alt))   

class XDocNote(XDocPiece):
    def __init__(self,context,config,text):
        XDocPiece.__init__(self,context,config)
        if text:
            self.createText(text)
            
    def start(self):
        if self.config.isXhtml():    
            self.context.writeLineIndented('<p><table><tr><td class="NOTE">')
        else:
            self.context.writeLineIndented('<note>')    
        
    def end(self):
        if self.config.isXhtml():    
            self.context.writeLine('</td></tr></table></p>')
        else:
            self.context.writeLine('</note>')
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),self.config,text))          
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext(),self.config))    

    def createStrong(self,text=None,transient=False):
        return self.storePiece(XDocStrong(self.createSubContext(transient),self.config,text))

    def createEmphasis(self,text=None,transient=False):
        return self.storePiece(XDocEmphasis(self.createSubContext(transient),self.config,text))
        
    def createLink(self,href,text=None):
        return self.storePiece(XDocLink(self.createSubContext(),self.config,href,text))              
        
    def createFork(self,href,text=None):
        return self.storePiece(XDocFork(self.createSubContext(),self.config,href,text))
        
class XDocWarning(XDocPiece):
    def __init__(self,context,config,text):
        XDocPiece.__init__(self,context,config)
        if text:
            self.createText(text)
        
    def start(self):
        if self.config.isXhtml():    
            self.context.writeLineIndented('<p><table><tr><td class="WARN">')
        else:
            self.context.writeLineIndented('<warning>')    
        
    def end(self):
        if self.config.isXhtml():    
            self.context.writeLine('</td></tr></table></p>')
        else:
            self.context.writeLine('</warning>')
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),self.config,text))          
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext(),self.config))    

    def createStrong(self,text=None,transient=False):
        return self.storePiece(XDocStrong(self.createSubContext(transient),self.config,text))

    def createEmphasis(self,text=None,transient=False):
        return self.storePiece(XDocEmphasis(self.createSubContext(transient),self.config,text))

            
class XDocSource(XDocPiece):
    def __init__(self,context,config,text=None):
        XDocPiece.__init__(self,context,config)
        if text:
            self.createText(text)
        
    def start(self):
        if self.config.isXhtml():    
            self.context.writeIndented('<p><pre clas="CODE">')
        else:
            self.context.writeIndented('<source>')
        
    def end(self):
        if self.config.isXhtml():    
            self.context.writeIndented('</pre></p>')
        else:
            self.context.writeIndented('</source>')
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),self.config,text))     
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext(),self.config))         
        
class XDocLink(XDocPiece):
    def __init__(self,context,config,href,text=None):
        XDocPiece.__init__(self,context,config)
        self.href=href
        if text: 
            self.createText(text)
            
    def start(self):
        if not self.config.isXhtml():    
            self.context.write('<link href=\'' + escape(self.href) + '\'>')
        else:
            self.context.write('<a href=\'' + escape(self.href) + '\'>')
        
    def end(self):
        if not self.config.isXhtml():    
            self.context.write('</link>')
        else:
            self.context.write('</a>')
        
    def createText(self,text):
        return self.storePiece(XDocText(self.createSubContext(),self.config,text))     
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext(),self.config))    
        
    def createIcon(self,href,alt=None):
        return self.storePiece(XDocIcon(self.createSubContext(),self.config,href,alt))              
        
                
class XDocFork(XDocPiece):
    def __init__(self,context,config,href,text=None):
        XDocPiece.__init__(self,context,config)
        if not href: raise RuntimeError('Can not fork with nowhere to go.')
        self.href=href
        if text:
            self.createText(text) 
        
    def start(self):
        if not self.config.isXhtml():    
            self.context.write('<fork href=\'' + escape(self.href) + '\'>')
        else:
            self.context.write('<a target=\'_new\' href=\'' + escape(self.href) + '\'>')
        
    def end(self): 
        if not self.config.isXhtml():    
            self.context.write('</fork>')
        else:
            self.context.write('</a>')
        
    def createText(self,text=None):
        return self.storePiece(XDocText(self.createSubContext(),self.config,text))    
        
    def createBreak(self):
        return self.storePiece(XDocBreak(self.createSubContext(),self.config))          
            
    def createIcon(self,href,alt=None):
        return self.storePiece(XDocIcon(self.createSubContext(),self.config,href,alt))               
        
class XDocIcon(XDocPiece):
    
    def __init__(self,context,config,href,alt):
        XDocPiece.__init__(self,context,config)
        self.href=href
        if alt:
            self.alt=alt
        else:
            self.alt=href
        
    def start(self):
        if not self.config.isXhtml():       
            tag='icon'
        else:
            tag='img'
        self.context.write('<' + tag + ' src=\'' + escape(self.href) + 	\
                    '\' alt=\'' + escape(self.alt) + '\' />')
                
    def middle(self): pass          
        
class XDocText(XDocPiece):
    def __init__(self,context,config,text):
        XDocPiece.__init__(self,context,config)
        self.text = text      
        
    def middle(self):
        self.context.writeRaw(self.text)
        
#       
# Some raw xdocs (for when too lazy to create classes)
#
class XDocRaw(XDocPiece):
    def __init__(self,context,config,raw):
        XDocPiece.__init__(self,context,config)
        self.raw = raw
        
    def middle(self):
        self.context.writeLine(str(self.raw))
        
class XDocDocument(XDocPiece):
    
    def __init__(self,title,output=None,config=None,rootpath='.'):
        if isinstance(output,str):    
            self.xfile=output
            #log.debug('Documenting to file : [' + self.xfile + ']')                    
            # Open for writing with a decent sized buffer.
            self.output=open(self.xfile, 'w', 4096)
        else:
            self.output=output        
        XDocPiece.__init__(self,XDocContext(self.output),config)  
        
        self.title=title
        self.rootpath=rootpath
        # :DEV: if not self.rootpath: raise RuntimeError, 'Bad rootpath'
        
    def start(self):
        
        if self.config.isXhtml():
            self.context.writeLine('<?xml version="1.0" encoding="ISO-8859-1"?>')
            self.context.writeLine('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">')
            self.context.writeLine('<!-- Automatically Generated by Apache  Gump(TM): http://gump.apache.org/ -->')
            self.context.writeLine('<html>')
            self.context.writeLine(' <head>')
            self.context.writeLine('  <title>%s</title>' % (self.title))
            self.context.writeLine('  <meta name="author" content="general@gump.apache.org"/>')
            self.context.writeLine('  <meta name="copyright" content="Apache Software Foundation"/>')
            
            self.context.writeLine('  <link rel="stylesheet" type="text/css" href="%s/css/style.css" title="Style"/>' % self.rootpath)
            
            self.context.writeLine(' </head>')
            self.context.writeLine('<body>')    
            self.context.writeLine('<table class="TRANSPARENT">')  
            self.context.writeLine(' <tr>')  
            self.context.writeLine(' <td><a href="%s/index.html">Run</a></td><td>|</td>' % self.rootpath) 
            self.context.writeLine(' <td><a href="%s/workspace.html">Workspace</a></td><td>|</td>' % self.rootpath) 
            self.context.writeLine(' <td><a href="%s/buildLog.html">Log</a></td><td>|</td>' % self.rootpath)  
            self.context.writeLine(' <td><a href="%s/project_todos.html">Issues</a></td><td>|</td>' % self.rootpath)  
            self.context.writeLine(' <td><a href="%s/project_fixes.html">Fixes</a></td><td>|</td>' % self.rootpath)  
            self.context.writeLine(' <td><a href="%s/project_prereqs.html">Pre-reqs</a></td><td>|</td>' % self.rootpath)  
            self.context.writeLine(' <td><a href="%s/gump_stats/index.html">Stats</a></td><td>|</td>' % self.rootpath)  
            self.context.writeLine(' <td><a href="%s/gump_xref/index.html">XRef</a></td><td>|</td>' % self.rootpath) 
            self.context.writeLine(' <td><a href="%s/proxyLog.html">Maven Repository Proxy Log</a></td>' % self.rootpath) 
            
            self.context.writeLine(' <td colspan="3"><img align="right" src="%s/images/gump-logo.png" alt="Gump Logo"/></td>' % self.rootpath)  
            self.context.writeLine(' </tr>')  
            self.context.writeLine('</table>')  
        else: 
            self.context.writeLine('<?xml version="1.0" encoding="ISO-8859-1"?>')
            self.context.writeLine('<!DOCTYPE document PUBLIC "-//APACHE//DTD Documentation V1.1//EN" "./dtd/document-v11.dtd">')
            self.context.writeLine('<!-- Automatically Generated by Apache  Gump(TM): http://gump.apache.org/ -->')
            self.context.writeLine('<document>')
            self.context.writeLine(' <header>')
            self.context.writeLine('  <title>%s</title>' % (self.title))
            self.context.writeLine('  <authors>')
            self.context.writeLine('   <person id="gump" name="Apache Gump" email="gump@lists.apache.org"/>')
            self.context.writeLine('  </authors>')
            self.context.writeLine(' </header>')
            self.context.writeLine('<body>')     
            
        
    def end(self):
        self.context.writeLine('</body>')
        if not self.config.isXhtml():
            self.context.writeLine('</document>')            
        else:
            from gump.core.config import default
            self.context.writeLine('<p align="left" style="font-size:smaller">Apache Gump, Gump, Apache, the Apache feather logo, and the Apache Gump project logos are trademarks of The Apache Software Foundation.')
            self.context.writeLine('<p align="right">Last Updated: %s.<A TARGET="_new" HREF="http://python.org"><img border ="0" align="right" src="%s/images/PythonPowered.gif" alt="Python Logo"/></A></p>' \
                                    % (default.datetime_sp, self.rootpath)) 
            self.context.writeLine('</html>')            
        self.close()                  
            
    def createSection(self,title,transient=False):
        return self.storePiece(XDocSection(self.createSubContext(transient),self.config,title))
                
    def createTable(self,headings=None,transient=False):
        return self.storePiece(XDocTable(self.createSubContext(transient),self.config,headings))

    def createSource(self,text=None):
        return self.storePiece(XDocSource(self.createSubContext(),self.config,text))         
    
    def createParagraph(self,text=None,transient=False):
        return self.storePiece(XDocParagraph(self.createSubContext(transient),self.config,text))
        
    def createNote(self,text=None):
        return self.storePiece(XDocNote(self.createSubContext(),self.config,text))  
        
    def createWarning(self,text=None):
        return self.storePiece(XDocWarning(self.createSubContext(),self.config,text))      
