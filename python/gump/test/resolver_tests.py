#!/usr/bin/env python
# $Header: /home/stefano/cvs/gump/python/gump/test/Attic/resolver_tests.py,v 1.2 2004/01/09 19:57:19 ajack Exp $
# $Revision: 1.2 $
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
from gump.test import *
from gump.document.resolver import *

def testRelativePath(path1,path2):
      
    rpath=gump.document.resolver.getRelativePath(path1,path2)
    
    print 'From ' + `path2` + ' to ' + `path1` + \
            ' -> ' + `rpath` + ', length ' + `len(rpath)`
    
def testLocation(object1):
    location=getLocationForObject(object1)
    printSeparator()
    print 'Location: ' + `location`
    print 'Location: ' + location.serialize()
    
def testRelativeLocation(object1,object2):
    
    location1=getLocationForObject(object1)    
    location2=getLocationForObject(object2)
    location=getRelativeLocation(object1,object2)
    printSeparator()
    print 'To       Location: ' + `location1`
    print 'From     Location: ' + `location2`
    print 'Relative Location: ' + `location`
    print 'Relative Location: ' + location.serialize()

def testResolve(object):
        
    printSeparator()
    print "Resolved Object: " + `object`
    print "Resolved Object: " + resolver.getDirectory(object)
    print "Resolved Object: " + resolver.getFile(object)
    print "Resolver Object: " + resolver.getDirectoryUrl(object)
    print "Resolver Object: " + resolver.getUrl(object)
    
    
if __name__=='__main__':

    # init logging
    logging.basicConfig()

    #set verbosity to show all messages of severity >= default.logLevel
    log.setLevel(gump.default.logLevel)

    path=Path()
    path1=path.getPostfixed('ABC')
    path2=path1.getPostfixed('DEF')
    path3=path2.getPostfixed(['GHI','JKL'])
    path4=path3.getPrefixed('789')
    path5=path4.getPrefixed(['123','456'])
    print "Sub-Path 1: " + path1.serialize()
    print "Sub-Path 2: " + path2.serialize()
    print "Sub-Path 3: " + path3.serialize()
    print "Sub-Path 4: " + path4.serialize()
    print "Sub-Path 5: " + path5.serialize()
    
    # Relative Tests
    
    testRelativePath(['A'],['A'])
    testRelativePath(['A'],['A','B'])
    testRelativePath(['A','B'],['A','B'])
    testRelativePath(['A'],['A','B'])
    testRelativePath(['A','B','C','D','E1'],['A','B','C','D','E2'])
    testRelativePath(['A','B1','C','D','E1'],['A','B2','C','D','E2'])
    
    
    workspace=getWorkedTestWorkspace() 
    
    module1=workspace.getModule('module1')
    module2=workspace.getModule('module2')    
    project1=workspace.getProject('project1')    
    project2=workspace.getProject('project2')    
    ant1=project1.getAnt()
    
    testLocation(workspace)
    testLocation(module1)
    testLocation(module2)    
    testLocation(project1)    
    
    testRelativeLocation(project1,project1)
    testRelativeLocation(project1,module1)
    testRelativeLocation(module1,module2)
    testRelativeLocation(module1,ant1)
    testRelativeLocation(ant1,module1)
    
    resolver=Resolver('.','http://somewhere/something')

    printSeparator()
    print "Resolved Module: " + resolver.getDirectory(module1)
    print "Resolved Module: " + resolver.getFile(module1)
    print "Resolver Module: " + resolver.getDirectoryUrl(module1)
    print "Resolver Module: " + resolver.getUrl(module1)
    
    for work in workspace.getWorkList():
        printSeparator()    
        print "Resolved Work: " + `work`
        print "Resolved Work: " + resolver.getDirectory(work)
        print "Resolved Work: " + resolver.getFile(work)
        print "Resolver Work: " + resolver.getDirectoryUrl(work)
        print "Resolver Work: " + resolver.getUrl(work)
    
    
    