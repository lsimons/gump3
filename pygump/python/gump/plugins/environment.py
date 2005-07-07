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

import os
from gump.model import Project
from gump.plugins import AbstractPlugin

def __get_env(self):
    # start copying the existing environment from the OS
    if not hasattr(self, "__env"):
        self.__env = dict(os.environ)
        
    return self.__env

def __set_env(self, env):
        self.__env = env

def __del_env(self):
    del self.__env

class EnvironmentPlugin(AbstractPlugin):
    """Set up lazily-initialized environment dictionary for use with executed commands."""
    
    def __init__(self):
        pass
    
    def initialize(self):
        Project.env = property(__get_env, __set_env, __del_env,
            "Environment dictionary for use with command execution")
