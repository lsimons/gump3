#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/utils/tools.py,v 1.11 2004/02/24 19:32:28 ajack Exp $
# $Revision: 1.11 $
# $Date: 2004/02/24 19:32:28 $
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
import types, StringIO

from gump import log
from gump.utils.work import *
from gump.utils.file import *
from gump.utils.launcher import *
    
def listDirectoryAsWork(workable,directory,name=None):
    ok=0
    if not name: name='list_'+directory
    cmd=getCmdFromString("ls -l "+directory,name)
    try:
        result=execute(cmd)
        ok=result.state==CMD_STATE_SUCCESS 
        if not ok:
            log.error('Failed to list [' + directory + ']')     
    except Exception, details:
        ok=0
        log.error('Failed to list [' + directory + '] : ' + str(details))
       
    # Update workable
    workable.performedWork(CommandWorkItem(WORK_TYPE_DOCUMENT,cmd,result))
    
    return ok
    
def catDirectoryContentsAsWork(workable,directory,name=None):
    try:
        if os.path.exists(directory) and  os.path.isdir(directory):
            for fileName in os.listdir(directory):
                baseName=name    
                file=os.path.abspath(os.path.join(directory,fileName))                
                if os.path.exists(file) and os.path.isfile(file):
                    if baseName: 
                        workName=baseName+'_'+fileName
                    else:
                        workName=fileName
                    catFileAsWork(workable,	file, workName)
    except:
        try:
            workable.addWarning('No such directory [' + str(directory) + ']')
        except:
            pass
    
        
def catFileAsWork(workable,file,name=None):
    ok=0
    if not name: name='cat_'+os.path.basename(file)
    cmd=getCmdFromString('cat '+str(file),'display_file_'+name)
    try:
        result=execute(cmd)
        ok=result.state==CMD_STATE_SUCCESS 
        if not ok:
            log.error('Failed to cat [' + str(file) + ']')     
    except Exception, details:
        ok=0
        log.error('Failed to cat [' + str(file) + '] : ' + str(details))
       
    # Update workable
    workable.performedWork(CommandWorkItem(WORK_TYPE_DOCUMENT,cmd,result))    
    
    return ok

def listDirectoryToFileHolder(holder,directory,type=FILE_TYPE_MISC):
       
    # Create a reference to the directory
    reference=FileReference(directory,type)
    
    #
    # Update holder w/ reference to directory, 'listing'
    # is implied (from it being a directory)
    #
    holder.addFileReference(reference)
    
    #
    # This is 'ok', if it exists, and is a directory
    #
    return reference.exists() and reference.isDirectory()
    
def catDirectoryContentsToFileHolder(holder,directory,name=None):
    try:
        if os.path.exists(directory) and  os.path.isdir(directory):
            for fileName in os.listdir(directory):
                baseName=name    
                file=os.path.abspath(os.path.join(directory,fileName))                
                if os.path.exists(file) and os.path.isfile(file):
                    if baseName: 
                        workName=baseName+'_'+fileName
                    else:
                        workName=fileName
                    catFileToFileHolder(holder,	file, workName)
    except:
        try:
            holder.addWarning('No such directory [' + str(directory) + ']')
        except:
            pass
    
        
def catFileToFileHolder(holder,file,name=None):
       
    # Create a reference to the file
    reference=FileReference(file,type)
    
    #
    # Update holder w/ reference to directory, 'cat'
    # is implied (from it being a file)
    #
    holder.addFileReference(reference)
    
    #
    # This is 'ok', if it exists, and is not a directory
    #
    return reference.exists() and reference.isNotDirectory()

   
def syncDirectories(noRSync,type,cwddir,tmpdir,sourcedir,destdir,name=None):                
    # :TODO: Make this configurable (once again)
    #if not workspace.sync:
    #  workspace.sync = default.syncCommand
    
    if noRSync:
        cmd=Cmd('cp','sync_'+name,cwddir)
        cmd.addParameter('-Rfv')
        cmd.addParameter(sourcedir)
        cmd.addParameter(destdir)
    else:
        cmd=Cmd('rsync','rsync_'+name,cwddir)            
        cmd.addParameter('-r')
        cmd.addParameter('-a')
        # Keep it quiet...
        # cmd.addParameter('-v')
        # cmd.addParameter('-v')
        # cmd.addParameter('--stats')        
        cmd.addParameter('--delete')
        cmd.addParameter(sourcedir)
        cmd.addParameter(destdir)

    log.debug(' ------ Sync\'ing : '+ name)
    
    # Perform the Sync
    cmdResult=execute(cmd,tmpdir)

    work=CommandWorkItem(type,cmd,cmdResult)
    
    return work        
    
def tailFile(file,lines):
    """ Return the last N lines of a file as a list """
    taillines=[]
    try:
        o=None
        try:
            # Read lines from the file...
            o=open(file, 'r')
            line=o.readline()
            
            while line:
                # Store the lines
                taillines.append(line)
            
                # But dump any before 'lines'
                size=len(taillines)
                if size > lines:
                    del taillines[0:(size-lines)]
                    
                # Read next...
                line=o.readline()
                
        finally:
            if o: o.close()
    except Exception, details:
        log.error('Failed to tail :' + file + ' : ' + str(details), exc_info=1)    
                            
    return taillines

def tailFileToString(file,lines):
    return "".join(tailFile(file,lines))
    
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)
  
  # dump(log)
  
  if len(sys.argv) > 0:
    print tailFileToString(sys.argv[1], 5  )
  
