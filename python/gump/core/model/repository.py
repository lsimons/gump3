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

import sys

from gump.core.model.object import NamedModelObject
from gump.core.model.stats import Statable, Statistics
from gump.util import getIndent
from gump.util.domutils import getDomChildValue

class ScmType:
    """
    enum-like class describing all supported SCMs
    """

    def __init__(self, name, displayName):
        self.name = name
        self.displayName = displayName

SCM_TYPE_CVS = ScmType('cvs', 'CVS')
SCM_TYPE_SVN = ScmType('svn', 'Subversion')
SCM_TYPE_ARTIFACTS = ScmType('artifacts', 'Artfifacts')
SCM_TYPE_P4 = ScmType('p4', 'Perforce')
SCM_TYPE_GIT = ScmType('git', 'Git')
SCM_TYPE_DARCS = ScmType('darcs', 'darcs')
SCM_TYPE_BZR = ScmType('bzr', 'Bazaar')
SCM_TYPE_HG = ScmType('hg', 'Mercurial')

# sorted by priority, the first matching SCM element inside a module wins
SUPPORTED_SCMS = [SCM_TYPE_CVS, SCM_TYPE_SVN, SCM_TYPE_P4,
                  SCM_TYPE_GIT, SCM_TYPE_DARCS, SCM_TYPE_BZR, SCM_TYPE_HG,
                  SCM_TYPE_ARTIFACTS]

def scm_type_for_name(name):
    """
    looks up a supported SCM by its name
    """
    for s in SUPPORTED_SCMS:
        if s.name == name:
            return s
    return None

class Repository(NamedModelObject, Statable):
    """ 

    A named repository (CVS|SVN|Perforce|Artifacts|GIT|darcs|bzr|hg)

    """
    def __init__(self, name, dom, workspace):
        NamedModelObject.__init__(self, name, dom, workspace)
        Statable.__init__(self)

        self.url = None

        typeAttribute = self.getDomAttributeValue('type')
        self.scmType = scm_type_for_name(typeAttribute)
        if not self.scmType:
            raise RuntimeError('Invalid Repository Type:' + str(typeAttribute))

        if SCM_TYPE_CVS == self.scmType:
            self.web = self.getDomChildValue('web') or \
                self.getDomChildValue('cvsweb')
            if self.hasDomChild('root'):
                root = self.getDomChild('root')
                self.method = getDomChildValue(root, 'method')
                self.user = getDomChildValue(root, 'user')
                self.password = getDomChildValue(root, 'password')
                self.path = getDomChildValue(root, 'path')
                self.hostname = getDomChildValue(root, 'hostname')
            else:
                raise RuntimeError('No XML <root on repository: ' \
                    + self.getName())
        elif SCM_TYPE_P4 == self.scmType:
            if self.hasDomChild('root'):
                root = self.getDomChild('root')
                self.p4port = getDomChildValue(root, 'hostname')
            else:
                raise RuntimeError('No Perforce server on P4 repository: ' \
                    + self.getName())
            self.web = self.getDomChildValue('web')
        else:
            if self.hasDomChild('url'):
                self.url = self.getDomChildValue('url')
            else:
                raise RuntimeError('No URL on ' + self.scmType.displayName + \
                    ' repository: ' + self.getName())
            self.web = self.getDomChildValue('web')
            self.user = self.getDomChildValue('user')
            self.password = self.getDomChildValue('password')

        # Modules referencing this repository
        self.modules = []

    def __lt__(self, other):
        return self.name < other.name # TEMPORARY


    def complete(self, workspace):
        pass

    def check(self, workspace):
        if not self.hasModules():
            self.addWarning('Unused Repository (not referenced by modules)')

    def hasModules(self):
        if self.modules:
            return True
        return False

    def hasScmType(self):
        if self.scmType:
            return True
        return False

    def getScmType(self):
        return self.scmType

    def getModules(self):
        return self.modules

    def dump(self, indent = 0, output = sys.stdout):
        output.write(getIndent(indent) + 'Repository : ' + self.name + '\n')
        NamedModelObject.dump(self, indent + 1, output)

    def hasTitle(self): 
        return self.hasDomAttribute('title')

    def hasHomePage(self): 
        return self.hasDomAttribute('home-page')

    def hasWeb(self): 
        return self.web

    def isRedistributable(self):
        # Existence means 'true'
        return self.hasDomChild('redistributable')

    def hasUser(self): 
        if hasattr(self, 'user'):
            if self.user:
                return True
        return False

    def hasPassword(self):
        if hasattr(self, 'password'):
            if self.password:
                return True
        return False

    def hasPath(self): 
        if hasattr(self, 'path'):
            if self.path:
                return True
        return False

    def hasMethod(self):
        if hasattr(self, 'method'):
            if self.method:
                return True
        return False

    def hasHostname(self): 
        if hasattr(self, 'hostname'):
            if self.hostname:
                return True
        return False

    def getTitle(self):
        return self.getDomAttributeValue('title')
    def getHomePage(self):
        return self.getDomAttributeValue('home-page')
    def getWeb(self):
        return self.web

    def getUser(self):
        return self.user
    def getPassword(self):
        return self.password
    def getPath(self):
        return self.path
    def getMethod(self):
        return self.method
    def getHostname(self):
        return self.hostname

    def hasUrl(self): 
        if self.url:
            return True
        return False

    def getUrl(self): 
        return self.url

    def addModule(self, module):
        self.modules.append(module)

class RepositoryStatistics(Statistics):
    """
        Statistics Holder
    """
    def __init__(self, repositoryName):
        Statistics.__init__(self, repositoryName)

    def getKeyBase(self):
        return 'repository:'+ self.name


