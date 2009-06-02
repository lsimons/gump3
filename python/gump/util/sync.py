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
import os.path
from stat import *
import shutil

from gump import log
from gump.util import getStringFromUnicode
from gump.util.work import *
from gump.util.file import *
from gump.util.note import *

SYNC_ACTION=1
COPY_ACTION=2

class PathWalker(Annotatable):

    def __init__(self, sourcedir, targetdir, action = SYNC_ACTION, output=None, debug=0):
        Annotatable.__init__(self)
        self.sourcedir = getStringFromUnicode(sourcedir)
        self.targetdir = getStringFromUnicode(targetdir)
        self.action = action
        
        if SYNC_ACTION==action:
            self.actionString='Sync'
        elif COPY_ACTION==action:
            self.actionString='Copy'
            
        self.debug=debug
        
        # A place to 'log' actions        
        self.output=output
        self.outputStream=None
        
        # Notice that actions occured        
        self.actionsOccured=False
        self.inboundActions=False
        self.cleanupActions=False
        
    def execute(self):
        #log.debug('Starting %s from [%s]' % (self.actionString,self.sourcedir))
        #log.debug('        target dir [' + self.targetdir + ']')
        
        # Allow user to pass an open stream, or a filename
        # In later case control open/close.
        doClose=0
        if self.output:
            if isinstance(self.output,types.StringTypes):
                doClose=1
                #log.debug('       changes to  [' + self.output + ']')
                self.outputStream=open(self.output,'w')
            else:
                self.outputStream=self.output
                
        try:
            
            if not os.path.exists(self.sourcedir):
                log.error('Exiting sync, source directory does not exist [' + self.sourcedir + ']')
                raise IOError, 'source directory does not exist [' + self.sourcedir + ']'

            if not os.path.isdir(self.sourcedir):
                log.error('Exiting sync, source is not a directory [' + self.sourcedir + ']')
                raise IOError, 'source is not a directory [' + self.sourcedir + ']'

            if not os.path.exists(self.targetdir):
                try:
                    os.makedirs(self.targetdir)
                except Exception, details:
                    log.exception('failed on ' + str(details))
                    raise IOError, 'could not create directory [' + self.targetdir + ']'
                
            self.copytree(self.sourcedir, self.targetdir, 1)   
             
        finally:
            if doClose and self.outputStream:
                #
                # We opened it, we close it...
                #
                self.outputStream.close()
                
                #
                # Clean Up Empty Output Files
                #
                if os.path.exists(self.output):
                    if not os.path.getsize(self.output) > 0:
                        try:
                            os.remove(self.output)
                            #log.debug('No changes, removed  [' + self.output + ']')
                        except: pass
                
        return (self.actionsOccured, self.inboundActions, self.cleanupActions)
        
    def displayAction(self,inbound,type,file,reason=''):
        
        # Mark something happened..
        self.actionsOccured=True
        
        if inbound:
            self.inboundActions=True
        else:
            self.cleanupActions=True
        
        # Log it (if requested)
        if self.outputStream:
            reasonSep=''
            if reason: reasonSep=' - '
            self.outputStream.write('%s : %s%s%s\n' % ( type , str(file), reasonSep, reason ))
        
    def isCopy(self): return (COPY_ACTION == self.action)
    def isSync(self): return (SYNC_ACTION == self.action)
    def isDiff(self): return (DIFF_ACTION == self.action)
    
    def setDebug(self, debug): self.sebug = debug
    def isDebug(self): return self.debug
        
    def copytree(self, src, dst, symlinks=0):
        
        # Only supported on some platforms.
        if 'posix'<>os.name: symlinks=0
        
        #
        # List all the files in the source location
        #
        names = os.listdir(src)
        
        #
        # Determine information about the destination (existence/type)
        #
        try:
            destinationStat = os.stat(dst)
        except Exception:
            destinationStat = None
         
        #   
        # handle case where destinationStat exists but is not a directory    
        #
        if destinationStat and not S_ISDIR(destinationStat[ST_MODE]):
            self.displayAction(True,' -F ', dst, 'Need a directory here, not a file.')        
            os.remove(dst)
            destinationStat = None
         
        #
        # Generate the target location (even if it means making
        # a path of directories.)
        #   
        if not destinationStat:     
            self.displayAction(True,' +D ', dst)    
            os.makedirs(dst)
            
        if destinationStat:
            names2 = os.listdir(dst)            
            if not self.isCopy():    
                self.removenonmatching(src, dst, names, names2)
                self.epurate(src, dst, names, names2)    
                
        #
        #
        #
        for name in names:
            
            try:    
                srcname = os.path.join(src, name)
                dstname = os.path.join(dst, name)
            
            except UnicodeDecodeError, why:
                message = 'Unicode Error. Can\'t copy [%s] in [%s] to [%s]: [%s]' % (`name`, `src`, `dst`, str(why))
                log.exception(message)
                raise RuntimeError, message
                
            try:
                if symlinks and os.path.islink(srcname):
                    if os.path.exists(dstname):
                        if os.path.islink(dstname) or os.path.isfile(dstname):
                            os.remove(dstname)
                        else:
                            shutil.rmtree(dstname, True)
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    # Copy directories, but not CVS/SVN/GIT etc. stuff
                    if not name in ['CVS','.svn','.git', '_darcs', '.bzr',
                                    '.hg']:
                        self.copytree(srcname, dstname, symlinks)
                else:
                    # Selectively copy file
                    self.maybecopy(srcname, dstname)
                    
            except (IOError, os.error), why:
                message = "Can't copy [%s] to [%s]: [%s]" % (`srcname`, `dstname`, str(why))
                log.exception(message)
                raise IOError, message
                
    def epurate(self, sourcedir, destdir, acceptablefiles, existingfiles):        
        """
        this routine will delete from a set of existing files
        in a directory [the ones which are not part of an 
        array of acceptablefiles]
        
        sourcedir = directory from which the copy is taking place
        destdir = directory where the epuration is to take place 
        acceptablefiles = array of filenames of files which are accepted at destination
        existingfiles = array of filenames which exist at destination                                     
        
        None
        """
        for afile in existingfiles:
            
            fullsourcefile = os.path.join(sourcedir, afile)
            fulldestfile = os.path.join(destdir, afile)
            if not afile in acceptablefiles:
                tobedeleted = os.path.join(destdir, afile)
                try:
                    destinationStat = os.stat(tobedeleted)
                    if S_ISDIR(destinationStat[ST_MODE]):
                        if self.isDebug(): log.debug('Attempting to remove directory [%s]' % (`tobedeleted`))
                        self.displayAction(False,' -D ', tobedeleted)    
                        shutil.rmtree(tobedeleted)
                    else:    
                        if self.isDebug(): log.debug('Attempting to remove file [%s]' % (`tobedeleted`))   
                        self.displayAction(False,' -F ', tobedeleted)    
                        os.remove(tobedeleted)
                except (IOError, os.error), why:
                    log.warning('Error removing [%s] - %s. Try again.' % (`tobedeleted`, why))
                    self.displayAction(False,' -X ', tobedeleted)    
                    shutil.rmtree(tobedeleted, True)
                    
    def removenonmatching(self, sourcedir, destdir, acceptablefiles, existingfiles):
        """
            this routine will remove from destination
            the entries which are files at destination and directory at source
            the entries which are directory at destination and files at source
            leaves untouched entries which exist both at source and at destination
            sourcedir = directory from which the copy is taking place
            destdir = directory where the epuration is to take place 
            acceptablefiles = array of filenames of files which are accepted at destination
            existingfiles = array of filenames which exist at destination                                     
        """
        removed = []
        for afile in existingfiles:
            
            if afile in acceptablefiles:
                                
                fullsourcefile = os.path.join(sourcedir, afile)
                fulldestfile = os.path.join(destdir, afile)
            
                if os.path.isdir(fullsourcefile) and not os.path.isdir(fulldestfile):
                    if self.isDebug(): 
                        log.debug('Removing file [%s] to be replaced by directory' 
                                %(`fulldestfile`))
                    os.remove(fulldestfile)
                    self.displayAction(True,' -F ', fulldestfile, 'Need a directory.')
                    removed.append(afile)
                elif os.path.isfile(fullsourcefile) and os.path.isdir(fulldestfile):              
                    if self.isDebug(): 
                        log.debug('Removing directory [%s] to be replaced by file' 
                                %(`fulldestfile`))
                    self.displayAction(True,' -D ', fulldestfile, 'Need a file.')
                    shutil.rmtree(fulldestfile)
                    removed.append(afile)
                    
        # Do the work
        for afile in removed:
            existingfiles.remove(afile)             
                
    def maybecopy(self, srcname, dstname):
        """
            copy a file from srcname to dstname if 
            dstname does not exist
            or srcname and dstname have different dates
            or srcname and dstname have different sizes
        """
        sourceStat = os.stat(srcname)
        try:
            destinationStat = os.stat(dstname)
        except:
            destinationStat = None
            
        reason=''
        # Determine if copy is appropriate.
        performCopy = 0
        if not destinationStat:
            performCopy = 1
            reason='Did not exist.'
        elif S_ISDIR(destinationStat[ST_MODE]):
            self.displayAction(True,' -D ', dstname, 'Need a file.')    
            shutil.rmtree(dstname)
            performCopy = 1
        elif sourceStat[ST_SIZE] != destinationStat[ST_SIZE]:
            performCopy = 1
            reason='Size difference.'
        elif sourceStat[ST_MTIME] != destinationStat[ST_MTIME]:
            performCopy = 1
            reason='Stat difference.'
            
        if performCopy:
            if self.isDebug(): log.debug("Attempting copy from [%s] to [%s]" %(`srcname`, `dstname`))    
            self.displayAction(True,' U> ', dstname, reason)    
            shutil.copy2(srcname, dstname)    
        #else:
        #    log.debug("Do not copy from [%s:%s] to [%s:%s]" \
        #                %(`srcname`, `sourceStat`, `dstname`,`destinationStat`))
        #        

class Copy(PathWalker):
    """
    A Sync without the epurate
    """
    def __init__(self, sourcedir, targetdir, output=None, debug=0):
        PathWalker.__init__(self, sourcedir, targetdir, COPY_ACTION, output, debug)
                    
class Sync(PathWalker):
    """
        This class can be used to sync two directories
            x = Sync(sourcedir, targetdir) # construct
            x.execute() #run
            if targetdir does not exist, it will be created
            if sourcedir does not exist, the class will raise an IOError
            the class can be also used to copy from one directory to another
        x = Sync(sourcedir, targetdir, )
    """
    def __init__(self, sourcedir, targetdir, output=None, debug=0):
        PathWalker.__init__(self, sourcedir, targetdir, SYNC_ACTION, output, debug)
        
