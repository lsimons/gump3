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

def _needs_support(obj):
    try:
        import cPickle as pickle
    except:
        import pickle
    
    try:
        pickle.dumps(obj)
        return False
    except TypeError:
        return True

def add_pickle_support(klass):
    if not _needs_support(klass):
        return
    
    def getstate(self):
        newdict = self.__dict__.copy()
        for k,v in self.__dict__.iteritems():
            if _needs_support(v):
                del newdict[k]
        return newdict
    
    klass.__getstate__ = getstate
