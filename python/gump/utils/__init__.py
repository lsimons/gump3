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
    Helper Stuff
"""

import logging
import os
import sys
import types, StringIO
import time
import urllib

from gump  import log
from gump.core.config import default, setting


def gumpSafeName(name):
  """returns a file system safe name"""  
  #
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
        if type(var) == types.NoneType: continue
        if isinstance(var,types.TypeType): continue
        if isinstance(var,types.MethodType): continue

        if isinstance(var,list): 
          print indent+"  List Name:" + str(name) + ' len:' + str(len(var))
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

def banner():
    printSeparator()
    print
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "Apache Python Gump (" + setting.version + "), a multi-project builder."
    print  
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print
    print "Copyright (C) 2003/2004 Apache Software Foundation. All rights reserved."
    print "See the Apache Software License 1.1 for more details."
    print "http://www.apache.org/"
    print
    
def printSeparator(indent=''):
    printSeparatorToFile(None,indent)
    
def printSeparatorToFile(f=None,indent=''):    
    if not f: f=sys.stdout
    f.write( '%s\n' % (indent + ' ---------------------------------------------------- Gump'))

def secsToElapsedTimeTriple(secs):   
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
    
def secsToElapsedTimeString(secs):
    return elapsedTimeTripleToString(secsToElapsedTimeTriple(secs))           
    
def elapsedTimeTripleToString(elapsed):
    elapsedString=''
    
    (hours,mins,secs) = elapsed
    
    if hours:
        if elapsedString: elapsedString += ' '
        elapsedString += str(hours)+' hour'
        if hours > 1: elapsedString += 's'
        
    if mins:
        if elapsedString: elapsedString += ' '    
        elapsedString += str(mins)+' min'
        if mins > 1: elapsedString += 's'
        
    if secs:
        if elapsedString: elapsedString += ' '    
        elapsedString += str(secs)+' sec'
        if secs > 1: elapsedString += 's'
    
    return elapsedString    
    
# Note: Should've defaulted values to -1, but (by accident)
# set some to 0, which then stuck in the DB. Leave this
# check in until fixed that (perhaps by looking for 0 in
# DB).
def secsToDate(secs):
    if -1 == secs or 0 == secs: return '-'    
    return time.strftime(setting.datetimeformat, \
                    time.localtime(secs))    
    
# See note on secsToDate               
def secsToTime(secs):
    if -1 == secs or 0 == secs: return '-'
    return time.strftime(setting.timeformat, \
                    time.localtime(secs))                    
                
def getGeneralSinceDescription(secs, since=None):
    if not since: since = default.time
    return getGeneralDifferenceDescription( since, secs )
            
def getGeneralDifferenceDescription(newerSecs,olderSecs):
    if not 0 >= olderSecs and not olderSecs >= newerSecs:
        diffString='~ '
        diffSecs=newerSecs - olderSecs
        
        diffSecs	=	int(diffSecs)
        diffMins	=	int(diffSecs / 60)
        diffHours	=	int(diffSecs / 3600)
        diffDays	=	int(diffHours / 24)
        diffWeeks	=	int(diffDays / 7)
        diffMonths	=	int(diffDays / 31)
        diffYears	=	int(diffDays / 365)
        
        if diffYears:
            diffString += str(diffYears) + ' year'
            if diffYears > 1: diffString += 's'
        elif diffMonths:
            diffString += str(diffMonths) + ' month'
            if diffMonths > 1: diffString += 's'
        elif diffWeeks:
            diffString += str(diffWeeks) + ' week'
            if diffWeeks > 1: diffString += 's'
        elif diffDays:
            diffString += str(diffDays) + ' day'
            if diffDays > 1: diffString += 's'
        elif diffHours:
            diffString += str(diffHours) + ' hour'
            if diffHours > 1: diffString += 's'
        elif diffMins:
            diffString += str(diffMins) + ' min'
            if diffMins > 1: diffString += 's'
        elif diffSecs:
            diffString += str(diffSecs) + ' sec'
            if diffSecs > 1: diffString += 's'
        else:
            diffString = 'This run: ' + secsToTime(newerSecs)
    elif olderSecs == newerSecs:
        diffString = 'This run: ' + secsToTime(newerSecs)
    else:
        diffString = 'N/A'
    
    return diffString
    
def getBooleanString(bool):
    if bool: return 'True'
    return 'False'
    
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
        raise ValueError, 'Can\'t have a negative indent : ' + `depth`
    if depth > 0:
        while depth:
            indent = indent + '  '
            depth = depth -1
    return indent
                  
def formatException(ei):
    import traceback
    sio = StringIO.StringIO()
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
        if isinstance(accessor,types.TypeType): continue
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
    
        log.info('GC: Enabled %s : Tracked %s : Threshold %s' \
                % (`enabled`, `tracked`,`threshold`))
                
        # gc.set_debug(gc.DEBUG_LEAK)
    except:
        pass  
    return tracked    
           
def inspectGarbageCollection(marker=''):
    tracked = 0
    try:
        import gc
        tracked = len(gc.get_objects())
        message=''
        if marker:
            message=' @ '
            message+=marker
        log.debug('Objects Tracked by GC %s : %s' \
                % (message,  `tracked`))
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
            log.warn('Objects Unreachable by GC : ' + `unreachable`)
                        
        # See what GC thinks afterwards...
        # inspectGarbageCollection(marker)
    except:
        pass