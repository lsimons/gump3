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
    Helper Stuff
"""

import logging
import os
import sys
import types, io
import time
import urllib.request, urllib.parse, urllib.error

from functools import cmp_to_key

from gump import log
from gump.core.config import default, setting

def banner():
    print("      _____")
    print("     |   __|_ Apache_ ___")
    print("     |  |  | | |     | . |")
    print("     |_____|___|_|_|_|  _|")
    print(("                     |_|     ~ v. " + setting.VERSION + " ~"))
    print()

def gumpSafeName(name):
  """returns a file system safe name"""  
  return urllib.parse.quote_plus(name)

def getModule(modulePath):
    try:
        aMod = sys.modules[modulePath]
        if not isinstance(aMod, types.ModuleType):
            raise KeyError
    except KeyError:
        # The last [''] is very important!
        aMod = __import__(modulePath, globals(), locals(), [''])
        sys.modules[modulePath] = aMod
    return aMod
    
def dump(obj,indent="",visited=None):
    
    print((indent+"Object: ["+str(obj.__class__)+"] "+str(obj)))
    
    if not visited:
        visited=[]
    if obj in visited: return
    visited.append(obj)
    
    if not obj: return
    if isinstance(obj,type): return
    if isinstance(obj,types.MethodType): return
    
      
    # iterate over the own properties
    try:
      for name in obj.__dict__:
        if name.startswith('__') and name.endswith('__'): continue
        var=obj.__dict__[name]

        # avoid nulls, metadata, and methods
        if type(var) == type(None): continue
        if isinstance(var,type): continue
        if isinstance(var,types.MethodType): continue

        if isinstance(var,list): 
          print((indent+"  List Name:" + str(name) + ' len:' + str(len(var))))
          i=0
          for v in var:
             i+=1
             print((indent+"  (" + str(i) + ") " + str(name)))
             dump(v, indent+"  ", visited)
        elif isinstance(var,dict): 
          print(("  Dictionary Name:" + str(name) + " " + str(var.__class__)))
          for (k,v) in list(var.items()):
             print((indent+"    Key:" + str(k) + " " + str(v.__class__)))
             dump(v,indent+"  ", visited)
        elif isinstance(var,object) and not isinstance(var,str): 
          print((indent+"  Object Name:" + str(name) + " " + str(var.__class__)))
          if not 'owner' == str(name):
              dump(var,indent+"  ", visited)
        else:
          try:
            print((indent+"  " + str(name) + " :-> " + str(var)))
          except:
            print((indent+"  " + str(name) + " :-> Unprintable (non-ASCII) Characters"))
    except:
        pass
   
def display(obj):
    print((str(obj.__class__)))
    # iterate over the own properties
    for name in obj.__dict__:
      if name.startswith('__') and name.endswith('__'): continue
      var=obj.__dict__[name]

      # avoid nulls, metadata, and methods
      if not var: continue
      if isinstance(var,type): continue
      if isinstance(var,types.MethodType): continue

      if isinstance(var,list): 
        print(("  List Name:" + str(name) + " " + str(var.__class__)))
        for v in var:
            display(v)
      elif isinstance(var,dict): 
        print(("  Dictionary Name:" + str(name) + " " + str(var.__class__)))
        for (k,v) in list(var.items()):
            display(v)
      else:
        try:
          print(("  " + str(name) + " :-> " + str(var)))
        except:
          print(("  " + str(name) + " :-> Unprintable (non-ASCII) Characters"))
                
class AlphabeticDictionaryIterator:
    """ Iterate over a dictionary in alphabetic key order """
    def __init__(self,dict):
        self.dict=dict
        self.keys=list(dict.keys())
        self.keys.sort()
        self.iter=iter(self.keys)
        
    def __iter__(self):
        return self
        
    def __next__(self):
        key=next(self.iter)
        return self.dict[key]      
        
def createOrderedList(disorderedList,sortfunc=None):
    # Is there a better way to clone a list?    
    cloned=list(disorderedList)    
    # Sort it
    if sortfunc:
        return sorted(cloned,key=cmp_to_key(sortfunc))
    return sorted(cloned)       
    
def printSeparator(indent=''):
    printSeparatorToFile(None,indent)
    
def printSeparatorToFile(f=None,indent=''):    
    if not f: f=sys.stdout
    f.write( '%s\n' % (indent + ' ---------------------------------------------------- Gump'))
    
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

def wrapLine(line,wrapLen=100, eol='\n', marker='[WRAPPED]'):
    
    wrappedLine=''       
    #
    # Provide some wrapping (at ~ 100)
    #
    if len(line) > wrapLen:      
        startPosn=0
        endPosn=wrapLen
        increment=wrapLen
        totalLen=len(line)                         
        while increment > 0:
            #print `startPosn` + " : " + `endPosn` + " : (" + `totalLen` + ') : ' + `increment`
            
            # Add the piece
            wrappedLine+=line[startPosn:endPosn+1]
            
            # We have more wrappign to do
            if (totalLen - endPosn) > wrapLen:
                increment=wrapLen
            else:
                increment=(totalLen - endPosn)
                
            # We aren't at end
            if increment:
                wrappedLine+=eol+marker
                
            startPosn=endPosn+1
            endPosn+=increment
            #print `startPosn` + " : " + `endPosn` + " : (" + `totalLen` + ') : ' + `increment`
    else:
        wrappedLine=line
            
    return wrappedLine
    
def getIndent(depth=0):
    indent=''
    if depth < 0:
        raise ValueError('Can\'t have a negative indent : ' + repr(depth))
    if depth > 0:
        while depth:
            indent = indent + '  '
            depth = depth -1
    return indent
                  
def formatException(ei):
    import traceback
    sio = io.StringIO()
    traceback.print_exception(ei[0], ei[1], ei[2], None, sio)
    s = sio.getvalue()
    sio.close()
    if s[-1] == "\n":
        s = s[:-1]
    return s

def getBeanAttributes(bean):
    attributes={}
    for name in bean.__class__.__dict__:
        if name.startswith('__') and name.endswith('__'): continue
        accessor=getattr(bean,name)            
        # avoid metadata, non-methods, methods other than (is|get)*
        if isinstance(accessor,type): continue
        # Ignore non-methods
        if not isinstance(accessor,types.MethodType): continue        
        # Ignore non-callable methods (????)
        if not callable(accessor): continue
        
        # Ignore methods not isX or getX
        # :TODO: Ought check that the X is upper case...
        if name.startswith('get'):
            attrName=name[3:]
        elif name.startswith('is'):
            attrName=name[2:]
        else:
            continue
            
        # Get value and stash it
        attributes[attrName]=accessor()   
            
    return attributes
    
def logResourceUtilization(message=None): pass

# This doesn't appear fully implemented in Python (2.2/2.3) so
# is simply a waste of cycles to call/display

#    try:
        #import resource
        #
        #if not message:
        #    message=''
        #    
        #myresources=resource.getrusage(resource.RUSAGE_SELF)
        #
        ## Extract the pieces
        #(my_ru_utime, my_ru_stime, my_ru_maxrss, \
        #    my_ru_ixrss, my_ru_idrss, my_ru_isrss, 	\
        #    my_ru_minflt, my_ru_majflt, my_ru_nswap, \
        #    my_ru_inblock, my_ru_oublock, my_ru_msgsnd, \
        #    my_ru_msgrcv, my_ru_nsignals, my_ru_nvcsw, 	\
        #    my_ru_nivcsw)=myresources
#    
#        kidresources=resource.getrusage(resource.RUSAGE_CHILDREN)
#        
#        # Extract the pieces
#        (kid_ru_utime, kid_ru_stime, kid_ru_maxrss, \
#            kid_ru_ixrss, kid_ru_idrss, kid_ru_isrss, 	\
#            kid_ru_minflt, kid_ru_majflt, kid_ru_nswap, \
#            kid_ru_inblock, kid_ru_oublock, kid_ru_msgsnd, \
#            kid_ru_msgrcv, kid_ru_nsignals, kid_ru_nvcsw, 	\
#            kid_ru_nivcsw)=kidresources
#            
#        log.debug('My Memory ' + message + ' ' + `my_ru_maxrss`)
#        log.debug('My Resources ' + message + ' ' + `myresources`)
#        log.debug('Child Memory ' + message + ' ' + `kid_ru_maxrss`)
#        log.debug('Child Resources ' + message + ' ' + `kidresources`)        
#    
        #resources=resource.getrusage(resource.RUSAGE_BOTH)
        #log.debug('All Resources ' + message  + ' ' + `resources`)
        
#    except Exception, details:        
#        if not os.name == 'dos' and not os.name == 'nt':
#            log.error("Failed get resource utilization." \
#        
           
def initializeGarbageCollection():
    tracked = 0
    try:
        import gc
        enabled = gc.isenabled()
        threshold = gc.get_threshold()
        tracked = len(gc.get_objects())        
    
        log.debug('GC: Enabled %s : Tracked %s : Threshold %s' \
                % (repr(enabled), repr(tracked),repr(threshold)))
                
        gc.enable()
        gc.set_threshold(10,10,10)
                
        # gc.set_debug(gc.DEBUG_LEAK)
    except:
        pass  
    return tracked    
           
def inspectGarbageCollection(marker=''):
    tracked = 0
    try:
        import gc
        tracked = len(gc.get_objects())
        #message=''
        #if marker:
        #    message=' @ '
        #    message+=marker
        #log.debug('Objects Tracked by GC %s : %s' \
        #        % (message,  `tracked`))
    except:
        pass  
    return tracked
                    
def invokeGarbageCollection(marker=''):
    try:
        # See what GC thinks
        inspectGarbageCollection(marker)
        
        # Perform GC
        import gc        
        unreachable = gc.collect()
        
        # Curiousity..
        if unreachable:
            message='Objects Unreachable by GC : ' + repr(unreachable)
            if marker:
                message+=' @ '
                message+=marker
            log.warn(message)
                        
        # See what GC thinks afterwards...
        # inspectGarbageCollection(marker)
    except:
        pass
   
def getRefCounts():
    pass
    #d = {}
    #sys.modules
    ## collect all classes
    #for m in sys.modules.values():
    #    for sym in dir(m):
    #        o = getattr (m, sym)
    #        if type(o) is types.ClassType:
    #            d[o] = sys.getrefcount (o)
    ## sort by refcount
    #pairs = map (lambda x: (x[1],x[0]), d.items())
    #pairs.sort()
    #pairs.reverse()
    #return pairs

def printTopRefs(count,message=None):
    pass
    #if message: print 'References @ ', message
    #for n, c in getRefCounts()[:count]:
    #    print '%10d %s - %s' % (n, c.__name__, `c`)
