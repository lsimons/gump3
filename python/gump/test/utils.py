#!/usr/bin/env python
#
# $Header: /home/stefano/cvs/gump/python/gump/test/utils.py,v 1.5 2004/02/17 21:54:21 ajack Exp $
# $Revision: 1.5 $
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
    Utils Testing
"""

from gump.utils import *
from gump.utils.launcher import Parameters
from gump.test.pyunit import UnitTestSuite

class UtilsTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        self.now=default.time
        
    def testDateTimeUtils(self):
        oneHourBefore=self.now - (60*60)
        twoHoursBefore=self.now - (60*60*2)
        oneDayBefore=self.now - (60*60*24)
        twoDaysBefore=self.now - (60*60*24*2)
        oneWeekBefore=self.now - (60*60*24*7)
        twoWeeksBefore=self.now - (60*60*24*7*2)
        oneMonthBefore=self.now - (60*60*24*31)
        twoMonthsBefore=self.now - (60*60*24*31*2)
        oneYearBefore=self.now - (60*60*24*365)
        twoYearsBefore=self.now - (60*60*24*365*2)
        
        rough=getGeneralDifferenceDescription(self.now, oneHourBefore)
        self.assertInString('Date Diff String', '1 hour', rough)
        
        rough=getGeneralDifferenceDescription(self.now, twoHoursBefore)
        self.assertInString('Date Diff String', '2 hours', rough)
      
        rough=getGeneralDifferenceDescription(self.now, oneDayBefore)
        self.assertInString('Date Diff String', '1 day', rough)
        
        rough=getGeneralDifferenceDescription(self.now, twoDaysBefore)
        self.assertInString('Date Diff String', '2 days', rough)
      
        rough=getGeneralDifferenceDescription(self.now, oneWeekBefore)
        self.assertInString('Date Diff String', '1 week', rough)
        
        rough=getGeneralDifferenceDescription(self.now, twoWeeksBefore)
        self.assertInString('Date Diff String', '2 weeks', rough)
      
        rough=getGeneralDifferenceDescription(self.now, oneMonthBefore)
        self.assertInString('Date Diff String', '1 month', rough)
        
        rough=getGeneralDifferenceDescription(self.now, twoMonthsBefore)
        self.assertInString('Date Diff String', '2 months', rough)        
        
        rough=getGeneralDifferenceDescription(self.now, oneYearBefore)
        self.assertInString('Date Diff String', '1 year', rough)
        
        rough=getGeneralDifferenceDescription(self.now, twoYearsBefore)
        self.assertInString('Date Diff String', '2 years', rough)
        
    def testSpacesInCommandLines(self):
        params=Parameters()
        params.addParameter('NoSpaces', 'aaaaa','=')
        params.addParameter('WithValueSpaces', 'aa aa a','=')
        params.addParameter('With Name Spaces', 'aaaaa','=')
        params.addParameter('WithQuotesAndSpaces', 'aa \' \" aa a','=')
        params.addParameter('WithEscapes', 'aa\\a','=')
        
        #print params.formatCommandLine()
        
        params=Parameters()
        params.addPrefixedParameter('-D','X', 'aaaaa','=')
        params.addPrefixedParameter('-D','Y', 'aa aa a','=')
        params.addPrefixedParameter('-D','Z', 'aa \' aa a','=')
        params.addPrefixedParameter('-D','Z', 'aa \" aa a','=')
        
        #print params.formatCommandLine()
        
    def testWrap(self):
        line='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        #print wrapLine(line)
        line='1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
        #print wrapLine(line)
        