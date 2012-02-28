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
   Model for outputs of a Gump project
"""

from gump.core.model.object import NamedModelObject

OUTPUT_ASSEMBLY = 'assembly'
OUTPUT_BOOTCLASSPATH_JAR = 'boot'
OUTPUT_HOMEDIR = 'home'
OUTPUT_JAR = 'jar'
OUTPUT_LICENSE = 'license'
OUTPUT_POM = 'pom'
OUTPUT_TESTS_JAR = 'testsjar'

# represents an <output/> element
class Output(NamedModelObject):
    """ Generic output element """

    def __init__(self, name, dom, owner):
        NamedModelObject.__init__(self, name, dom, owner)
        self.id = ''
        self.type = ''
        self.path = None

    def setPath(self, path):
        """ home-dir relative paths of output """
        self.path = path

    def getPath(self):
        """ home-dir relative paths of output """
        return self.path

    def hasId(self):
        """ optional id of output """
        if self.id:
            return True
        return False

    def setId(self, id):
        """ optional id of output """
        self.id = id

    def getId(self):
        """ optional id of output """
        return self.id

    def getType(self):
        """ optional type of output """
        return self.type

    def setType(self, t):
        """ optional type of output """
        self.type = t

    def is_jar(self):
        """ is this some sort of jar output? """
        return self.type in [OUTPUT_BOOTCLASSPATH_JAR, \
                                 OUTPUT_JAR, \
                                 OUTPUT_TESTS_JAR]
