#!/usr/bin/env python
#
# Copyright 2005 The Apache Software Foundation
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

# being picky about the imports since any '.' in python code slows things down
from gump.util.executor import Popen
from gump.util.executor import PIPE
from os import name as osname
from os.path import isdir
from os.path import join
from os.path import exists
from os.path import abspath
from os.path import normcase
from os import makedirs
from os import mkdir
from os import walk
from os import link
from os import unlink
from os import stat

from re import search
from shutil import copyfile
from shutil import copystat
from shutil import rmtree

"""
This module provides a very efficient implementation of the specific rsync-like functionality
that gump needs. The basic idea is that gump needs three copies of roughly the same directory
tree:

  work/checkouts/mymodule/myproject
  work/builds/mymodule/myproject
  work/builds/mymodule/myproject/.gump-persistence

the steps that gump takes are as follows:

  - if possible, "revert" the checkout location
    (eg svn revert -R work/checkouts/mymodule/myproject)
  - update the checkout location (eg svn up work/checkouts/mymodule/myproject)
  - take a big sledgehammer and make the build location have exactly the same
    content as the checkout location, *except* for the .gump-persistence directory,
    which is left intact
    (eg rsync -a --delete work/checkouts/mymodule/myproject \
          work/builds/mymodule/myproject \
          --delete-excludes=.gump-persistence)
  - when a build is successful, take a big sledgehammer and make the persistence location
    have exactly the same content as the build location, *except* for the .gump-persistence
    directory, which we don't want to "recursively keep around"
    (eg rsync -a --delete work/builds/mymodule/myproject \
          work/builds/mymodule/myproject/.gump-persistence \
          --excludes=.gump-persistence)

The associated calls into this module look roughly like

  sync('work/checkouts/mymodule/myproject', 'work/builds/mymodule/myproject',
       excludes=[".gump-persist"])
  sync('ant/ant', 'ant/ant/.gump-persist', excludes=[".gump-persist"])

On mac and linux, this module makes use of hardlinks for files, which saves a considerable
amount of space, avoids a lot of copying stuff around, and is faster than native rsync if
the target to copy to is not yet around or way-out-of-date.

Native rsync is still about 10 times faster on updates of existing stuff. A good tradeoff
between disk space use and performance is the smart_sync command, which picks the rsync
mode to use based on this speed/disk space difference, periodically cleaning out and
re-doing everything using hard links. WARNING: native_sync assumes shell patterns, sync
assumes regular expressions for the exclude filtering. Use only a sensible subset of the two!

Also note that memory usage briefly grows sharply, as we have to keep arond a hash in memory
with all the file and directory entries inside the source location so we can figure out what
bits to delete later. Rsync probably does this a little differently, visiting source and
target directories at the same time and deleting whatever is in the target location as it
lists the source directory and sees what "should go". The reason for not doing things like
that is that it feels a little safer.

I've tested subversion 1.2.3 on the mac and when it updates a file it really does replace it,
meaning hardlinks can probably also be safely used here without nasty side effects when we
have multiple gumps running concurrently using the same checkout base. This may not be true
for CVS or other versioning systems; I don't know.

Finally, the use of hard links means that all three 'copies' of the different files need to
be on the same physical filesystem. That means partitioning of the gump working copies will
have to be a per-module or per-repository basis, eg you can't split the work dir in two
partitions (eg one for checkouts and one for builds).
"""

def __should_update(src, dst):
    """Compare file attributes and decide whether an update is needed."""
    sstat = stat(src)
    dstat = stat(dst)

    # compare file size
    ss = sstat.st_size
    ds = dstat.st_size
    if ss != ds: return True
    
    # compare modification time
    st = sstat.st_mtime
    dt = dstat.st_mtime
    if abs(st - dt) > 5: return True
    
    # same same
    return False
    

# figure out how to do the file copies. No symlinks, they may break
# some builds...
__hardlinks = osname == "posix" or osname == "mac"
if __hardlinks:
    def __copy_file(src, dst):
        """Get rid of dst if it is weird, or create new hard link if update is needed."""
        if isdir(dst):
            rmtree(dst)
        elif exists(dst):
            if __should_update(src,dst):
                unlink(dst)
            else:
                return
        link(src, dst)
else:
    def __copy_file(src, dst):
        """Get rid of dst if its a directory, then copy over file if update is needed."""
        if isdir(dst):
            rmtree(dst)
        elif exists(dst) and __should_update(src, dst):
            return
        copyfile(src, dst)


def __strip_slash_prefix(path):
    if len(path) == 0:
        return path
    
    if path[0] == "/" or path[0] == "\\":
        return path[1:]
    

def sync(source, target, excludes=[], onerror=None):
    """Big sledgehammer to sync source and target locations. See module documentation."""
    assert isinstance(source, basestring)
    assert isinstance(target, basestring)
    assert isdir(source)
    assert hasattr(excludes, "__iter__")
    for i in excludes:
        assert isinstance(i, basestring)
    
    source = normcase(abspath(source))
    target = normcase(abspath(target))

    if not isdir(target):
        makedirs(target)
        
    # this is where the memory usage grows -- we keep a rather big array in memory here...
    # ...do_delete does modify it in-place, but still, executing on the 'smallest subset
    # possible' (and not a whole source tree at a time) seems prudent
    keep = __do_copy(source, target, excludes, onerror)
    __do_delete(target, keep, excludes, onerror)


def __do_copy(source, target, excludes, onerror):
    """Recursive directory copy using os.walk."""
    plen = len(source)
    keep = {}
    for (root, dirs, files) in walk(source, topdown=True, onerror=onerror):
        __filter_walk_stack(root, dirs, excludes)
        __filter_walk_stack(root, files, excludes)
        relative_root = __strip_slash_prefix(root[plen:])
        
        for idir in dirs:
            spath = join(root, idir)
            tpath = join(target, relative_root, idir)
            if not isdir(tpath):
                mkdir(tpath)
            copystat(spath, tpath)
        
        for ifile in files:
            spath = join(root, ifile)
            tpath = join(target, relative_root, ifile)
            __copy_file(spath, tpath)
        
        keep[relative_root] = (dirs, files)
    return keep


def __do_delete(target, dontdel, excludes, onerror):
    """Recursive deletes of unknown files using os.walk."""
    plen = len(target)
    for (root, dirs, files) in walk(target, topdown=True, onerror=onerror):
        relative_root = __strip_slash_prefix(root[plen:])

        if not dontdel.has_key(relative_root):
            rmtree(normcase(abspath(root)), onerror=onerror)
            continue
        
        # note we modify the dontdel hash so its starts shrinking as we
        # go through it...
        (dontdel_dirs, dontdel_files) = dontdel.pop(relative_root)
        
        dontwalkdirs = []
        for idir in dirs:
            if not idir in dontdel_dirs:
                dontwalkdirs.append(idir)
                rmtree(join(root, idir), onerror=onerror)
        for x in dontwalkdirs:
            dirs.remove(x)
        
        for ifile in files:
            if not ifile in dontdel_files:
                unlink(join(root, ifile))


def __filter_walk_stack(root, paths, excludes):
    """Apply regexps to a bunch of paths and modify the array in place if there's a match."""
    if len(excludes) == 0:
        return
    
    ignore_paths = []
    for ipath in paths:
        iabspath = abspath(join(root, ipath))
        for x in excludes:
            if search(x, iabspath):
                ignore_paths.append(ipath)
                break
    for ipath in ignore_paths:
        paths.remove(ipath)


from tempfile import mkdtemp
have_native = not Popen(["rsync", "--version"], stdout=PIPE, shell=True).wait()
from time import localtime

if have_native:
    def native_sync(source, target, excludes):
        assert isinstance(source, basestring)
        assert isinstance(target, basestring)
        assert isdir(source)
        assert hasattr(excludes, "__iter__")
        for i in excludes:
            assert isinstance(i, basestring)
        
        source = normcase(abspath(source))
        target = normcase(abspath(target))
        if not source[-1] == "/" and not source[-1] == "\\":
            source = source + "/"
        if not target[-1] == "/" and not target[-1] == "\\":
            target = target + "/"

        if not isdir(target):
            makedirs(target)

        cmd = ["rsync", "-a", "--delete"]
        for x in excludes:
            cmd.append("--exclude='" + x + "'")
        cmd.append(source)
        cmd.append(target)
        
        result = Popen(cmd, shell=True).wait()
        if result:
            raise "rsync command %s failed with exit status %s!" % (" ".join(cmd), result)

if __hardlinks and have_native:
    def smart_sync(source, target, excludes=[], onerror=None, cleanup=None):
        if not exists(target):
            sync(source, target, excludes=excludes, onerror=onerror)
        else:
            if cleanup == None:
                currtime = localtime()
                currday = currtime.tm_mday
                docleanup = currday in [1, 14]
            else:
                docleanup = cleanup
            
            if docleanup:
                # periodically clean out completely to start with new hard links and save space
                emptydir = mkdtemp()
                sync(emptydir, target, excludes=excludes, onerror=onerror)
                rmtree(emptydir)
                sync(source, target, excludes=excludes, onerror=onerror)
            else:
                native_sync(source, target, excludes)
elif have_native:
    def smart_sync(source, target, excludes=[], onerror=None, cleanup="ignored"):
        native_sync(source, target, excludes)
else:
    def smart_sync(source, target, excludes=[], onerror=None, cleanup="ignored"):
        sync(source, target, excludes, onerror=onerror)

