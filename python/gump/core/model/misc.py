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

    This module contains miscellaneous model objects

"""

import os

from gump.core.model.object import NamedModelObject, ModelObject

class Positioned:
    def __init__(self): 
        self.posn = -1
        self.total = -1

    def setPosition(self, posn):
        """ Set this object's position (within some sequence) """
        self.posn = posn

    def setTotal(self, total):
        """ Set the total length of sequence """
        self.total = total

    def getPosition(self):
        """ Return either a tuple or a position, dependent upon if
        total is set. Mainly for presentation in ``. """
        if -1 != self.total:
            return (self.posn, self.total)
        if -1 != self.posn:
            return self.posn

    def getPositionIndex(self):
        """ Get index in sequence """
        return self.posn

class Resultable:
    def __init__(self): 
        pass

    # Stats are loaded separately and cached on here, 
    # hence they may exist on an object at all times.
    def hasServerResults(self):
        return hasattr(self, 'serverResults')

    def setServerResults(self, serverResults):
        self.serverResults = serverResults

    def getServerResults(self):
        if not self.hasServerResults():
            raise RuntimeError, "ServerResults not available [yet]: " \
                    + self.getName()
        return self.serverResults


    # Stats are loaded separately and cached on here, 
    # hence they may exist on an object at all times.
    def hasResults(self):
        return hasattr(self, 'results')

    def setResults(self, results):
        self.results = results

    def getResults(self):
        if not self.hasResults():
            raise RuntimeError, "Results not available [yet]: " \
                    + self.getName()
        return self.results

class Resolvable(ModelObject):
    """
    A ModelObject that can be resolved relative to it's owning model
    or workspace e.g. JUnitReport or Work
    """
    def __init__(self, dom, owner):
        ModelObject.__init__(self, dom, owner)
        self.path = None

    def complete(self):
        if self.isComplete():
            return


        if self.hasDomAttribute('nested'):
            self.path = os.path.abspath(
                os.path.join(self.owner.getModule().getWorkingDirectory(), 
                             self.getDomAttributeValue('nested')))
        elif self.hasDomAttribute('parent'):
            self.path = os.path.abspath(
                os.path.join(self.owner.getWorkspace().getBaseDirectory(), 
                             self.getDomAttributeValue('parent')))

        # Done, don't redo
        self.setComplete(True)

    def getResolvedPath(self):
        return self.path

# represents a <junitreport/> element
class JunitReport(Resolvable):
    def __init__(self, dom, owner):
        Resolvable.__init__(self, dom, owner)

 
# represents a <work/> element
class Work(Resolvable): 
    def __init__(self, dom, owner):
        Resolvable.__init__(self, dom, owner)

class DirResolvable(ModelObject):
    """
        Common code for getting a directory (attribute) and
        returning that as a path relative to the 
    """
    def __init__(self, dom, owner):
        ModelObject.__init__(self, dom, owner)
        self.dir = None

    def complete(self):
        if self.isComplete():
            return

        if self.hasDomAttribute('dir'):
            dirString = self.getDomAttributeValue('dir')

            # Security attempt
            # :TODO: Move to a one-time check
            if '..' in dirString:
                self.owner.addError('Bad directory attribute %s on <%s' % \
                                    dirString, self.__class__.__name__)
                dirString = 'bogus'

            self.dir = os.path.abspath(
                os.path.join(self.owner.getModule().getWorkingDirectory(), 
                              dirString))

        # Done, don't redo
        self.setComplete(True)

    def hasDirectory(self):
        """
        Does it have a directory?
        """
        if self.dir:
            return True
        return False

    def getDirectory(self):
        """ 
        Get the directory. 
        """
        return self.dir


# represents a <mkdir/> element
class Mkdir(DirResolvable):
    def __init__(self, dom, owner):
        DirResolvable.__init__(self, dom, owner) 

# represents a <delete/> element
class Delete(DirResolvable): 
    def __init__(self, dom, owner):
        DirResolvable.__init__(self, dom, owner)
        self.file = None

    def complete(self):
        if self.isComplete():
            return

        DirResolvable.complete(self)

        if self.hasDomAttribute('file'):
            file = self.getDomAttributeValue('file')

            # Security attempt
            # :TODO: Move to a one-time check
            if '..' in file:
                self.owner.addError('Bad file attribute %s on <%s' % \
                                    file, self.__class__.__name__)
                file = 'bogus'

            self.file = os.path.abspath(
                os.path.join(self.owner.getModule().getWorkingDirectory(), 
                             file))

        # Done, don't redo
        self.setComplete(True)

    def hasFile(self):
        if self.file:
            return True
        return False

    def getFile(self):
        return self.file 

class AddressPair:
    def __init__(self, toAddr, fromAddr):
        self.toAddr = toAddr
        self.fromAddr = fromAddr

    def __str__(self):
        return '[To:' + self.toAddr + ', From:' + self.fromAddr + ']'

    def getToAddress(self):
        return self.toAddr

    def getFromAddress(self):
        return self.fromAddr


