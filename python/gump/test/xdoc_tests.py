#!/usr/bin/env python
# $Header: /home/stefano/cvs/gump/python/gump/test/Attic/xdoc_tests.py,v 1.3 2004/01/09 19:57:19 ajack Exp $
# $Revision: 1.3 $
# $Date: 2004/01/09 19:57:19 $
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
    Model Testing
"""

import os
import logging
import types, StringIO

from gump import log
import gump.config
from gump.document.xdoc import *


if __name__=='__main__':

    # init logging
    logging.basicConfig()

    #set verbosity to show all messages of severity >= default.logLevel
    log.setLevel(gump.default.logLevel)

    stream=StringIO.StringIO() 
      
    doc1=XDocDocument('Test 1', stream)
    section1=doc1.createSection('Test Section 1')
    para1=section1.createParagraph('Test Text 1')
    
    table1=section1.createTable()
    comment1=table1.createComment('Test Comment 1')
    table1.createEntry('Title1:','Data1')
    
    list1=section1.createList()
    list1.createEntry('Title1:','Item1')    
    list1.createItem('Item2').createLink('http://somewhere','Link')
    list1.createItem('Item3').createLink('http://somewhere').createIcon('http://somewhere','Alt')
    list1.createItem('Item4').createIcon('http://somewhere','Alt')
    list1.createEntry('Title1:','Item1').createBreak()
    list1.createEntry('Item5').createLink('http://somewhere','Link')
    
    table1=section1.createTable(['H1','H2'])
    
    #dump(doc1)
    doc1.serialize()
    
    stream.seek(0)
    print stream.read()
