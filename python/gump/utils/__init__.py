#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/utils/__init__.py,v 1.1 2003/11/17 22:10:55 ajack Exp $
# $Revision: 1.1 $
# $Date: 2003/11/17 22:10:55 $
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
    Helper Stuff
"""

import logging
import sys
import types, StringIO
import time
import urllib

from gump  import log
from gump.config import default, setting

def gumpSafeName(name):
  """returns a file system safe name"""
  return urllib.quote_plus(name)

###############################################################################
# Dump an object (as best possible generically)
###############################################################################
def dump(obj,indent=""):
    print indent+"Object: ["+str(obj.__class__)+"] "+str(obj)
    if not obj: return
    if isinstance(obj,types.TypeType): return
    if isinstance(obj,types.MethodType): return
      
    # iterate over the own properties
    try:
      for name in obj.__dict__:
        if name.startswith('__') and name.endswith('__'): continue
        var=obj.__dict__[name]

        # avoid nulls, metadata, and methods
        if not var: continue
        if isinstance(var,types.TypeType): continue
        if isinstance(var,types.MethodType): continue

        if isinstance(var,list): 
          print indent+"  List Name:" + str(name)
          i=0
          for v in var:
             i+=1
             print indent+"  (" + str(i) + ") " + str(name)
             dump(v, indent+"  ")
        elif isinstance(var,dict): 
          print "  Dictionary Name:" + str(name) + " " + str(var.__class__)
          for (k,v) in var.iteritems():
             print indent+"    Key:" + str(k) + " " + str(v.__class__)
             dump(v,indent+"  ")
        elif isinstance(var,object) and not isinstance(var,str): 
          print indent+"  Object Name:" + str(name) + " " + str(var.__class__)
          dump(var,indent+"  ")
        else:
          try:
            print indent+"  " + str(name) + " :-> " + str(var)
          except:
            print indent+"  " + str(name) + " :-> Unprintable (non-ASCII) Characters"
    except:
        pass
   
def display(obj):
    print str(obj.__class__)
    # iterate over the own properties
    for name in obj.__dict__:
      if name.startswith('__') and name.endswith('__'): continue
      var=obj.__dict__[name]

      # avoid nulls, metadata, and methods
      if not var: continue
      if isinstance(var,types.TypeType): continue
      if isinstance(var,types.MethodType): continue

      if isinstance(var,list): 
        print "  List Name:" + str(name) + " " + str(var.__class__)
        for v in var:
            display(v)
      elif isinstance(var,dict): 
        print "  Dictionary Name:" + str(name) + " " + str(var.__class__)
        for (k,v) in var.iteritems():
            display(v)
      else:
        try:
          print "  " + str(name) + " :-> " + str(var)
        except:
          print "  " + str(name) + " :-> Unprintable (non-ASCII) Characters"
                
class AlphabeticDictionaryIterator:
    """ Iterate over a dictionary in alphabetic key order """
    def __init__(self,dict):
        self.dict=dict
        self.keys=dict.keys()
        self.keys.sort()
        self.iter=iter(self.keys)
        
    def __iter__(self):
        return self
        
    def next(self):
        key=self.iter.next()
        return self.dict[key]      
        
def createOrderedList(disorderedList,sortfunc=None):
    # Is there a better way to clone a list?    
    sorted=list(disorderedList)    
    # Sort it
    if sortfunc:
        sorted.sort(sortfunc)
    else:
        sorted.sort()        
    # Return it sorted
    return sorted   

# :TODO: Go find the one I lost...
def banner():
    printSeparator()
    print
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "Apache Python Gump (" + setting.version + "), a multi-project builder."
    print  
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print
    print "Copyright (C) 2003 Apache Software Foundation. All rights reserved."
    print "See the Apache Software License 1.1 for more details."
    print "http://www.apache.org/"
    print
    
def printSeparator(indent=''):
    printSeparatorToFile(None,indent)
    
def printSeparatorToFile(f=None,indent=''):    
    if not f: f = sys.stdout
    f.write( '%s\n' % (indent + ' ---------------------------------------------------- Gump'))

def secsToElapsedTime(secs):   
    # Extract Hours
    if secs > 3600:
        hours	=	int(secs / 3600)
        secs	%=	3600
    else:
        hours	=	0
          
    # Extract Minutes  
    if secs > 60:
        mins	=	int(secs / 60)
        secs	%=	60
    else:
        mins 	= 	0
            
    # Seconds
    secs 	=	int(round(secs,0))
        
    return (hours, mins, secs)
    
def secsToString(secs):
    return elapsedTimeToString(secsToElapsedTime(secs))           
    
def elapsedTimeToString(elapsed):
    #:TODO: Don't show hours if 0, show mins/secs words
    return ('%02d:%02d:%02d' % elapsed)        
    
def secsToDate(secs):
    return time.strftime(setting.datetimeformat, \
                    time.localtime(secs))
    
#
# Get into ASCII, but make an attempt at coping with
# non-ASCII
#
def getStringFromUnicode(u):
    try:
        s = str(u)
    except UnicodeError:
        s = ''
        for uc in u:
            try:
                sc = uc.encode('latin-1')            
            except UnicodeError:
                sc = '_'
            # Add character by character
            s += sc
            
    return s
    
def getIndent(depth=0):
    indent=''
    if depth < 0:
        raise ValueError, 'Can\'t have a negative indent : ' + `depth`
    if depth > 0:
        while depth:
            indent = indent + '  '
            depth = depth -1
    return indent
    
         
def getTerseClassName(object):
    return object.__class__.__name__
        
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)
  
  #dump(log)

  print "secsToElapsedTime(1340) : " + str(secsToElapsedTime(1340))
  print "secsToString(1340) : " + secsToString(1340)
  print "elapsedTimeToString(secsToElapsedTime(1340)) : " + elapsedTimeToString(secsToElapsedTime(1340))
  
  print "str = " + getStringFromUnicode("Ceki Gülcü")
  
  print "indent = [" + getIndent(5) + "]"
  
