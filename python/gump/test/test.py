#!/usr/bin/env python

# $Header: /home/cvspublic/jakarta-gump/python/gump/conf.py,v 1.7 2003/05/10 18:20:36 nicolaken Exp $
# $Revision: 1.7 $
# $Date: 2003/05/10 18:20:36 $
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
    This module contains information on unit testing
"""
        
class Testable():       
    def __init__(self):
        
    def raiseIssue(self, stuff):
        message=''
        for s in stuff:
            if message: message += ' '
            message += str(s)
            
        raise RuntimeError, message
        
    def assertNotNone(self,message,object):        
        if isinstance(object,NoneType):
            self.raiseIssue(['Ought NOT be None', message, object])
            
    def assertNonZero(self,message,object):
        self.assertNotNone(message,object)
        if not object:
            self.raiseIssue(['Ought evaluate to non-zero', message, object])
            
    def assertEqual(self,message,object1,object2):
        if not object1 == object2:
            self.raiseIssue(['Ought evaluate as equal', message, object1, object2])
            
    def assertIn(self,message,object1,sequence1):
        if not object1 in sequence1:
            self.raiseIssue(['Ought evaluate as in', message, object1, sequence1])
            
    
            
class UnitTestSuite(Testable):
    def __init__(self,name):
        Testable.__init__(self)
        self.name=name
        
    def performTests(self)
    
        if hasattr(self,'setUp'):
            sefl.setUp()
    
        # iterate over the object properties
        for name in object.__dict__:
            if name.startswith('__') and name.endswith('__'): continue
            test=getattr(object,name)

            # avoid nulls, metadata, and methods other than test*
            if not test: continue
            if isinstance(test,types.TypeType): continue
            if not isinstance(test,types.MethodType): continue
            if not iscallable(test): continue
            if not name.startswith('test'): continue
            
            # Call the test...
            test(self)
            
        if hasattr(self,'tearUp')
            sefl.tearUp()
        
        