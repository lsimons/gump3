#!/usr/bin/env python

# Copyright 2004-2005 The Apache Software Foundation
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

"""This module is used by the gump engine for all interaction with files.

It handles access to both local and remote files (like files retrieved over
HTTP). Note that some of the gump engine helpers run external programs which
in turn interact with the filesystem directly rather than through this really
thin Virtual Filesystem Layer.
"""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import os
import string
import urllib
import urlparse


class Error(Exception):
    """Generic error thrown for all internal VFS module exceptions."""
    pass


class VFS:
    """Component for retrieving local and remote files as streams.
    
    Provides homogenized access to local files, as well as files residing
    on remote servers (HTTP or FTP or ...). Remote files are cached
    efficiently.
    
    Currently only provides operations for reading:
        
        - get_as_stream(url_or_path) -- determines whether the argument is an
            actual url or a reference to a local file, then fetches the file
            identified by the argument and returns it as a file-like object.
            Note that the returned file must be closed as normal!
    """
    def __init__(self, filesystem_root = None, cachedir = None):
        """
        Create a new VFS. Arguments:
            
            - filesystem_root -- path to the directory on this machine that
                                 should be used as the virtual root for
                                 the VFS. Basic care is taken to ensure that
                                 it is not possible to "escape" from this
                                 root.
            - cachedir -- path to the directory on this machine that should
                          be used as the 
        """
        if filesystem_root:
            self.filesystem_root = os.path.abspath(filesystem_root)
        else:
            self.filesystem_root = None
            
        if cachedir:
            self.cachedir = os.path.abspath(cachedir)
        else:
            self.cachedir = None
    
    def get_as_stream(self, url_or_path):
        """
        Get access to a file or url as a stream for reading.
        
        A stream is a file-like object that supports basic methods such as
        readline().
        
        Note that if the VFS does not have a cache directory available,
        operations such as seeking are not available. Also note that if the
        VFS does not have a local filesystem root, a Error will be thrown
        if a local file is requested.
        """
        
        if not url_or_path:
            raise Error, "Bad url or path requested: %s" % url_or_path
        
        if string.find(url_or_path, ':') != -1:
            return self._get_url_as_stream(url_or_path)
        else:
            return self._get_file_as_stream(url_or_path)
        
    def _get_url_as_stream(self, url):
        """Get access to a remote file as a stream for reading.
        
        Note that if the VFS does not have a cache directory available,
        operations such as seeking are not available.
        """
        if self.cachedir:
            path = self._get_cache_path_for_url_and_mkdirs(url)
            urllib.urlretrieve(url, path)
            return open(path)
        else:
            return urllib.urlopen(path)

    def _get_file_as_stream(self, path):
        """Get access to a local file as a stream for reading.
        
        Note that if the VFS does not have a local filesystem root,
        a Error will be thrown.
        """
        if not self.filesystem_root:
            raise Error, "This VFS does not support retrieving local files (%s was requested)!" % path
        
        relpath = path.lstrip('/') # transform absolute paths into paths
                                   # relative to the VFS filesystem "root"
        fullpath = os.path.abspath(os.path.join( self.filesystem_root, relpath ))
        
        if not fullpath.startswith(self.filesystem_root):
            raise Error, "The requested resource %s is not part of the VFS!" % path
        
        if not os.path.exists(fullpath):
            raise Error, "No resource %s found in VFS!" % path
        if not os.path.isfile(fullpath):
            raise Error, "Requested resource %s is not a stream!" % path
        
        return open(fullpath)

    def _get_cache_path_for_url_and_mkdirs(self, url):
        """Helper for _get_url_as_stream().
        
        Determine the local path within the VFS cache to store the results of
        getting a particular url at, creating neccessary immediate directories
        as neccessary.
        """
        (addressing_scheme, network_location, path, parameters, query, fragment_identifier) = urlparse.urlparse(url)
        
        schemedir = os.path.join(self.cachedir, addressing_scheme)
        if not os.path.exists(schemedir): os.mkdir(schemedir)

        serverdir = os.path.join(schemedir, network_location)
        if not os.path.exists(serverdir): os.mkdir(serverdir)

        filebase = string.replace(path, '/', '_')
        filename = self._safe_filename(filebase + '___' + query + '___' + fragment_idenfitier)
        
        # we can be *reasonably* sure there's no two urls that result in
        # this same path...
        return os.path.join(serverdir, filename)

    def _safe_filename(self, filename):
        """Replaces all the "special characters" in a string with '-'."""
        newpath = filename
        for unsafe in [' ',
                       '`',
                       '~',
                       '!',
                       '#',
                       '$',
                       '%',
                       '^',
                       '&',
                       '*',
                       '(',
                       ')',
                       '=',
                       '+',
                       '{',
                       '}',
                       '[',
                       ']',
                       '|',
                       '\\',
                       ':',
                       ';',
                       '"',
                       "'",
                       '<',
                       '>',
                       ',',
                       '?',
                       '/']:
            newpath = string.replace(newpath, unsafe, '-')
            return newpath
