#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/utils/sync.py,v 1.1 2004/03/04 21:38:47 antoine Exp $
# $Revision: 1.1 $
# $Date: 2004/03/04 21:38:47 $
#
# ====================================================================
#
# The Apache Software License, Version 1.1
#
# Copyright (c) 2004 The Apache Software Foundation.  All rights
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
import os.path
from stat import *
import shutil
from gump import log
from gump.utils.work import *
from gump.utils.file import *
from gump.utils.launcher import *
class Sync:
    """
    this class can be used to sync two directories
    x = Sync(sourcedir, targetdir) # construct
    x.execute() #run
    if targetdir does not exist, it will be created
    if sourcedir does not exist, the class will raise an IOError
    """
    def __init__(self, sourcedir, targetdir):
        self.sourcedir = sourcedir
        self.targetdir = targetdir
    def execute(self):
        log.info('Starting sync from [' + self.sourcedir + ']')
        log.info('        target dir [' + self.targetdir + ']')
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
                return
        copytree(self.sourcedir, self.targetdir, 1)    
            
def copytree(src, dst, symlinks=0):
    names = os.listdir(src)
    try:
        result = os.stat(dst)
    except Exception, details:
        result = None
    # handle case where result exists but is not a directory    
    if result and not S_ISDIR(result[ST_MODE]):
        remove(dst)
        result = None
    if not result:    
        os.makedirs(dst)
    if result:
        names2 = os.listdir(dst)
        epurate(src, dst, names, names2)    
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                maybecopy(srcname, dstname)
        except (IOError, os.error), why:
            message = "Can't copy [%s] to [%s]: [%s]" % (`srcname`, `dstname`, str(why))
            log.exception(message)
            raise IOError, message
def epurate(sourcedir, destdir, acceptablefiles, existingfiles):
    """
    this routine will delete from a set of existing files
    in a directory the one which are not part of an 
    array of acceptablefiles
    somedir = directory where the epuration is to take place                                      
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
        elif os.path.isdir(fullsourcefile) and not os.path.isdir(fulldestfile):
            log.debug('removing file [%s] to be replaced by directory' 
            %(`fulldestfile`))
            os.remove(fulldestfile)
        elif os.path.isfile(fullsourcefile) and os.path.isdir(fulldestfile):              
            log.debug('removing directory [%s] to be replaced by file' 
            %(`fulldestfile`))
            shutil.rmtree(fulldestfile)
            
def maybecopy(srcname, dstname):
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
        
            
            
