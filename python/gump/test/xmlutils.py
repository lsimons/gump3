#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/test/Attic/xmlutils.py,v 1.1.2.1 2004/06/08 21:36:37 ajack Exp $
# $Revision: 1.1.2.1 $
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
    XML Testing
"""

from gump.test.pyunit import UnitTestSuite
from gump.utils import *
from gump.utils.xmlutils import *


class Xml1(GumpXMLObject): pass
class Xml2(GumpXMLObject): pass
class Xml3(GumpXMLObject):     
  map={}
  
class Xml4(Named):     
  map={}
  def init(self):
    self.y=Single(Xml2)
    

class XmlTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        
    def suiteSetUp(self):
        pass
    
    def emptyTests(self,o):
        """
            Helper to test an object is empty
        """
        self.assertFalse('Empty __nonzero__',	o )
        self.assertEqual('Empty __len__',	0, len(o) )
        
    def nonEmptyTests(self,o):
        """
            Helper to test an object is nonEmpty
        """
        self.assertTrue('NonEmpty __nonzero__',	o )
        self.assertNotEqual('NonEmpty __len__',	0, len(o) )
        
    def testGumpXMLObjectConstructEmpty1(self):
        o = GumpXMLObject({})
        self.emptyTests(o)
        
    def testGumpXMLObjectConstructEmpty2(self):
        o = GumpXMLObject({'@text':''})
        self.emptyTests(o)
        
    def testGumpXMLObjectConstructNonEmpty1(self):
        o = GumpXMLObject({'@text':'X'})
        self.nonEmptyTests(o)
        
    def testGumpXMLObjectConstructNonEmpty2(self):
        o = GumpXMLObject({'fred':'X'})
        self.nonEmptyTests(o)
        
    def testParse1(self):
        data="<x></x>"
        parser=SAXDispatcher('x',Xml1)
        parser.parseString(data)
        self.assertNotNone('Ought have doc element', parser.docElement)
        #dump(parser.docElement)
        
    def testParse2(self):
        data="<x a='1'></x>"
        parser=SAXDispatcher('x',Xml1)
        parser.parseString(data)
        self.assertNotNone('Ought have doc element', parser.docElement)
        #dump(parser.docElement)
        
    def testParse3(self):
        data="<x a='1'></x>"
        parser=SAXDispatcher('x',Xml2)
        parser.parseString(data)
        self.assertNotNone('Ought have doc element', parser.docElement)
        #dump(parser.docElement)
        
    def testParse4(self):
        data="<x name='test' a='1'><y/></x>"
        parser=SAXDispatcher('x',Xml3)
        parser.parseString(data)
        self.assertNotNone('Ought have doc element', parser.docElement)
        self.assertEqual('Named', parser.docElement.name, 'test')
        #dump(parser.docElement)
        
    def testParse5(self):
        data="<x name='test' a='1'><y/></x>"
        parser=SAXDispatcher('x',Xml4)
        parser.parseString(data)
        self.assertNotNone('Ought have doc element', parser.docElement)
        self.assertEqual('Named', parser.docElement.getName(), 'test')
        #dump(parser.docElement)
        
    def testParse6(self):
        data="<x name='test' a='1'><y>Y</y></x>"
        parser=SAXDispatcher('x',Xml4)
        parser.parseString(data)
        self.assertNotNone('Ought have doc element', parser.docElement)
        self.assertEqual('Named', parser.docElement.getName(), 'test')
        x4=parser.docElement
        x2=x4.y
        d=x2.delegate
        self.assertTrue('The Xml2 object has a value',str(d))  
        self.assertTrue('The Xml2 object has a value',str(x2))   
        self.assertTrue('The Xml2 object has a value',x4.transfer('y')) 
        self.assertString('The Xml2 object has a String value',x4.transfer('y'))   
        self.assertTrue('The Xml2 object has a value',x2.hasString())  
        
    def testSingle1(self):
        s = Single(Xml1)
        s({'X':'X'})
        
        self.assertNotNone('Existence',s) 
        
        self.assertTrue('Has X attr',hasattr(s,'X'))         
        self.assertFalse('No Y attr',hasattr(s,'Y')) 
        
        self.assertFalse('No X item','X' in s) 
        self.assertFalse('No Y item','Y' in s) 
        
        self.assertNotNone('X attribute #1', getattr(s,'X')) 
        self.assertNotNone('X attribute #2', s.X) 
        self.assertTrue('X attribute #3', s.X) 
        
        self.assertFalse('X member NOT callable',callable(s.X)) 
        
        self.assertNonZeroString('String',str(s.X))
        self.assertEqual('String X','X',str(s.X))
        
    def testMultiple1(self):
        s = Multiple(Xml1)
        s({'X':'X'})
        
        self.assertNotNone('Existence',s) 
        
        self.assertFalse('No X attr',hasattr(s,'X'))         
        self.assertFalse('No Y attr',hasattr(s,'Y')) 
        
        self.assertFalse('No X item','X' in s) 
        self.assertFalse('No Y item','Y' in s) 
        
        self.assertNotNone('0th item',s[0]) 
        
    def testNamed1(self):
        s = Xml4({'name':'X'})
        
        self.assertNotNone('Existence',s) 
        
        self.assertFalse('No X attr',hasattr(s,'X'))         
        self.assertFalse('No Y attr',hasattr(s,'Y')) 
        
        self.assertFalse('No X item','X' in s) 
        self.assertFalse('No Y item','Y' in s) 
        
        self.assertNotNone('X item',Xml4.map['X']) 
        