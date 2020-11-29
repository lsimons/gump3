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
import types, io
import shutil

from gump import log
from gump.util.note import *
from gump.util.work import *
from gump.util.file import *
from gump.util.sync import *
from gump.util.process.command import *
from gump.util.process.launcher import *
    
def listDirectoryAsWork(workable,directory,name=None):
    ok=0
    if not name: name='list_'+directory
    cmd=getCmdFromString("ls -l "+directory,name)
    try:
        result=execute(cmd)
        ok=result.state==gump.util.process.command.CMD_STATE_SUCCESS 
        if not ok:
            log.error('Failed to list [' + directory + ']')     
    except Exception as details:
        ok=0
        log.error('Failed to list [' + directory + '] : ' + str(details))
       
    # Update workable
    workable.performedWork(CommandWorkItem(WORK_TYPE_DOCUMENT,cmd,result))
    
    return ok
    
def catDirectoryContentsAsWork(workable,directory,name=None):
    
    # Chances are a workable is also annotatable...
    annotatable=None
    if isinstance(workable,Annotatable):
        annotatable=workable
        
    try:
        if os.path.exists(directory) and os.path.isdir(directory):
            for fileName in os.listdir(directory):
                baseName=name    
                file=os.path.abspath(os.path.join(directory,fileName))                
                if os.path.exists(file) and os.path.isfile(file):
                    if baseName: 
                        workName=baseName+'_'+fileName
                    else:
                        workName=fileName
                    catFileAsWork(workable,	file, workName)
        elif annotatable:
                annotatable.addWarning('No directory [' + str(directory) + ']')
    except:
        if annotatable:
            annotatable.addWarning('Failed to display directory contents [' + str(directory) + ']')    
        
def catFileAsWork(workable,file,name=None):
    ok=0
    if not name: name='cat_'+os.path.basename(file)
    cmd=getCmdFromString('cat '+str(file),'display_file_'+name)
    try:
        result=execute(cmd)
        ok=result.isOk() 
        if not ok:
            log.error('Failed to cat [' + str(file) + ']')     
    except Exception as details:
        ok=0
        log.error('Failed to cat [' + str(file) + '] : ' + str(details))
       
    # Update workable
    workable.performedWork(CommandWorkItem(WORK_TYPE_DOCUMENT,cmd,result))    
    
    return ok

def listDirectoryToFileHolder(holder,directory,type=FILE_TYPE_MISC,name=None):
       
    # Create a reference to the directory
    reference=FileReference(directory,type,name)
    
    #
    # Update holder w/ reference to directory, 'listing'
    # is implied (from it being a directory)
    #
    holder.addFileReference(reference)
    
    #
    # This is 'ok', if it exists, and is a directory
    #
    return reference.exists() and reference.isDirectory()
    
def catDirectoryContentsToFileHolder(holder,directory,type=FILE_TYPE_MISC,name=None):
    
    # Chances are a holder is also annotatable...
    annotatable=None
    if isinstance(holder,Annotatable):
        annotatable=holder
        
    try:
        listDirectoryToFileHolder(holder,directory,type,name)
        
        if os.path.exists(directory) and  os.path.isdir(directory):
            for fileName in os.listdir(directory):
                baseName=name    
                file=os.path.abspath(os.path.join(directory,fileName))                
                if baseName: 
                    workName=baseName+'_'+fileName
                else:
                    workName=fileName
                catFileToFileHolder(holder,	file, type, workName)
        elif annotatable:
                annotatable.addWarning('No directory [' + str(directory) + ']')
    except:
        if annotatable:
            annotatable.addError('Failed to display directory [' + str(directory) + ']')
    
        
def catFileToFileHolder(holder,file,type=FILE_TYPE_MISC,name=None):
       
    # Create a reference to the file
    reference=FileReference(file,type,name)
    
    #
    # Update holder w/ reference to directory, 'cat'
    # is implied (from it being a file)
    #
    holder.addFileReference(reference)
    
    #
    # This is 'ok', if it exists, and is not a directory
    #
    return reference.exists() and reference.isNotDirectory()

   
def copyDirectories(sourcedir,destdir,annotatable=None,output=None):   
    """    
        Copy any changed files, report if work done        
    """
    changes=0
    try:
        copy=Copy(sourcedir,destdir,output)        
        changes=copy.execute()    
    finally:
        if annotatable:
            transferAnnotations(copy, annotatable)     
                      
    return changes
       
def syncDirectories(sourcedir,destdir,annotatable=None,output=None):                
    """
        Sync two directories, report if difference
        [and hence changes] occured.
    """
    changes=0
    try:
        sync=Sync(sourcedir,destdir,output)        
        changes=sync.execute()    
    finally:
        if annotatable:
            transferAnnotations(sync, annotatable)                
    return changes
            
def wipeDirectoryTree(dir, recreateDir = True):
    log.info('Wipe Directory [' + repr(dir) + ']') 
    if os.path.exists(dir):
        try:
            shutil.rmtree(dir)            
        except: pass
    if recreateDir and not os.path.exists(dir):
        os.makedirs(dir)
                
def tailFile(file,lines,wrapLen=0,eol=None,marker=None):
    """ Return the last N lines of a file as a list """
    taillines=[]
    try:
        o=None
        try:
            # Read lines from the file...
            o=open(file, 'r')
            line=o.readline()
            
            size=0
            while line:      
                #
                # Wrap if requested
                #
                if wrapLen:
                    wline=wrapLine(line,wrapLen,eol,marker)
                else:
                    wline=line
                
                # Store the lines
                taillines.append(wline)
            
                # But dump any before 'lines'
                size=len(taillines)
                if size > lines:
                    del taillines[0:(size-lines)]
                    size=len(taillines)
                    
                # Read next...
                line=o.readline()
                
        finally:
            if o: o.close()
    except Exception as details:
        log.error('Failed to tail :' + file + ' : ' + str(details), exc_info=1)    
                            
    return taillines

def tailFileToString(file,lines,wrapLen=0,eol=None,marker=None):
    return "".join(tailFile(file,lines,wrapLen,eol,marker))

SEPARATOR='---------------------------------------------------------------- GUMP\n'
def catFile(output,file,title=None):
    """ Cat a file to a stream... """
    if title:
        output.write(SEPARATOR)    
        output.write(title + '\n\n')
        
    input=open(file,'r')
    line = input.readline()
    while line:
        output.write(line)
        # Next...
        line = input.readline()
        
    if title:
        output.write(SEPARATOR)    
        
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)
  
  # dump(log)
  
  if len(sys.argv) > 0:
    print((tailFileToString(sys.argv[1], 5  )))
