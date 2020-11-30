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
    This module contains information on an object's owner
"""
from gump import log
from gump.util import getIndent

class Ownable:
    """Contains ownership """
    def __init__(self,owner=None):
        if self == owner:
            raise RuntimeError("Can set owner to self on " + repr(self))
        self.owner=owner
    
    def __del__(self):
        self.owner=None

    def hasOwner(self):
        return self.owner
        
    def setOwner(self,owner):
        if self == owner:
            raise RuntimeError("Can set owner to self on " + repr(self))
        self.owner=owner
        
    def getOwner(self):
        return self.owner or self
        
    def displayOwnership(self,visited=None):
        if not visited: visited=[]
        if self in visited: 
            log.error('Circular path @ ' + repr(self))
            return
        visited.append(self)
        log.info(getIndent(len(visited))+repr(self))
        if self.hasOwner():
            self.getOwner().displayOwnership(visited)
        return         
