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

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

class VFS:
    """
    Provides homogenized access to local files, as well as files residing
    on remote servers (HTTP or FTP or ...).
    """
    def __init__(filesystem_root = None, cachedir = None):
        self.filesystem_root = filesystem_root
        self.cachedir = cachedir
    
    def get_as_stream(self, url_or_path):
        """
        Get access to a file as a stream. Files that live remotely are cached
        locally.
        """
        raise RuntimeError, "not implemented!" # TODO
