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
import os.path
from stat import *
import shutil
from gump import log
from gump.utils.work import *
from gump.utils.file import *
from gump.utils.launcher import *
from gump.utils.note import *

class Sync(Annotatable):
    """
    this class can be used to sync two directories
    x = Sync(sourcedir, targetdir) # construct
    x.execute() #run
    if targetdir does not exist, it will be created
    if sourcedir does not exist, the class will raise an IOError
    the class can be also used to copy from one directory to another
    x = Sync(sourcedir, targetdir, 1)
    """
    def __init__(self, sourcedir, targetdir, copyflag = 0):
        Annotatable.__init__(self)
        self.sourcedir = sourcedir
        self.targetdir = targetdir
        self.copyflag = copyflag
        
    def execute(self):
        if self.copyflag:
            action = 'copy'
        else:
            action = 'sync'
        log.debug('Starting %s from [%s]' % (action,self.sourcedir))
        log.debug('          target dir [' + self.targetdir + ']')
        if not os.path.exists(self.sourcedir):
            log.error('Exiting sync, source directory does not exist [' + self.sourcedir + ']')
            raise IOError, 'source directory does not exist [' + self.sourcedir + ']'
            return
        if not os.path.isdir(self.sourcedir):
            log.error('Exiting sync, source is not a directory [' + self.sourcedir + ']')
            raise IOError, 'source is not a directory [' + self.sourcedir + ']'
            return
        if not os.path.exists(self.targetdir):
            try:
                os.makedirs(self.targetdir)
            except Exception, details:
                log.exception('failed on ' + str(details))
                raise IOError, 'could not create directory [' + self.targetdir + ']'
        self.copytree(self.sourcedir, self.targetdir, 1)    
            
    def copytree(self, src, dst, symlinks=0):
        names = os.listdir(src)
        try:
            result = os.stat(dst)
        except Exception:
            result = None
        # handle case where result exists but is not a directory    
        if result and not S_ISDIR(result[ST_MODE]):
            os.remove(dst)
            result = None
        if not result:    
            os.makedirs(dst)
        if result:
            names2 = os.listdir(dst)            
            if not self.copyflag:    
                self.removenonmatching(src, dst, names, names2)
                self.epurate(src, dst, names, names2)    
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if symlinks and os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    if not name in ['CVS','.svn']:
                        self.copytree(srcname, dstname, symlinks)
                    #else:
                    #    log.debug('Skip SVN or CVS directory ' + str(srcname))
                else:
                    self.maybecopy(srcname, dstname)
            except (IOError, os.error), why:
                message = "Can't copy [%s] to [%s]: [%s]" % (`srcname`, `dstname`, str(why))
                log.exception(message)
                raise IOError, message
                
    def epurate(self, sourcedir, destdir, acceptablefiles, existingfiles):        
        """
        this routine will delete from a set of existing files
        in a directory the one which are not part of an 
        array of acceptablefiles
        sourcedir = directory from which the copy is taking place
        destdir = directory where the epuration is to take place 
        acceptablefiles = array of filenames of files which are accepted at destination
        existingfiles = array of filenames which exist at destination                                     
        """
        for afile in existingfiles:
            fullsourcefile = os.path.join(sourcedir, afile)
            fulldestfile = os.path.join(destdir, afile)
            if not afile in acceptablefiles:
                tobedeleted = os.path.join(destdir, afile)
                result = os.stat(tobedeleted)
                if S_ISDIR(result[ST_MODE]):
                    log.debug('attempting to remove directory [%s]' % (`tobedeleted`))
                    shutil.rmtree(tobedeleted)
                else:    
                    log.debug('attempting to remove file [%s]' % (`tobedeleted`))
                    os.remove(tobedeleted)
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
            fullsourcefile = os.path.join(sourcedir, afile)
            fulldestfile = os.path.join(destdir, afile)
            if afile in acceptablefiles:
                if os.path.isdir(fullsourcefile) and not os.path.isdir(fulldestfile):
                    log.debug('removing file [%s] to be replaced by directory' 
                    %(`fulldestfile`))
                    os.remove(fulldestfile)
                    removed.append(afile)
                elif os.path.isfile(fullsourcefile) and os.path.isdir(fulldestfile):              
                    log.debug('removing directory [%s] to be replaced by file' 
                    %(`fulldestfile`))
                    shutil.rmtree(fulldestfile)
                    removed.append(afile)
        for afile in removed:
            existingfiles.remove(afile)             
                
    def maybecopy(self, srcname, dstname):
        """
        copy a file from srcname to dstname if 
        dstname does not exist
        or srcname and dstname have different dates
        or srcname and dstname have different sizes
        """
        result = os.stat(srcname)
        try:
            result2 = os.stat(dstname)
        except (Exception), details:
            result2 = None
        okcopy = 0
        if not result2:
            okcopy = 1
        elif S_ISDIR(result2[ST_MODE]):
            shutil.rmtree(dstname)
            okcopy = 1
        elif result[ST_SIZE] != result2[ST_SIZE]:
            okcopy = 1
        elif result[ST_MTIME] != result2[ST_MTIME]:
            okcopy = 1
        if okcopy:
            log.debug("Attempting copy from [%s] to [%s]" %(`srcname`, `dstname`))    
            shutil.copy2(srcname, dstname)        

class Copy(Sync):
    """
    A Sync without the epurate
    """
    def __init__(self, sourcedir, targetdir):
        Sync.__init__(self, sourcedir, targetdir, 1)
                    
            
