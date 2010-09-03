#!/usr/bin/python


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

 A gump.core.run (not 'run gump')
 
"""

###############################################################################
# Init
###############################################################################

# Overall objectives
OBJECTIVE_UNSET = 0
OBJECTIVE_UPDATE = 0x01
OBJECTIVE_BUILD = 0x02
OBJECTIVE_CHECK = 0x04
OBJECTIVE_DOCUMENT = 0x08

OBJECTIVE_REDO = OBJECTIVE_UPDATE | OBJECTIVE_BUILD
OBJECTIVE_INTEGRATE = OBJECTIVE_UPDATE | OBJECTIVE_BUILD | \
                        OBJECTIVE_DOCUMENT
OBJECTIVE_OFFLINE = OBJECTIVE_BUILD | OBJECTIVE_DOCUMENT

# Features
FEATURE_UNSET = 0
FEATURE_STATISTICS = 0x01
FEATURE_RESULTS = 0x02
FEATURE_NOTIFY = 0x04
FEATURE_DIAGRAM = 0x08
FEATURE_SYNDICATE = 0x10
FEATURE_DESCRIBE = 0x20
FEATURE_PUBLISH = 0x40
FEATURE_DOCUMENT = 0x80
FEATURE_HISTORICAL = 0x100

FEATURE_DEFAULT = FEATURE_STATISTICS \
    | FEATURE_SYNDICATE \
    | FEATURE_DESCRIBE \
    | FEATURE_DOCUMENT \
    | FEATURE_NOTIFY

FEATURE_ALL = FEATURE_STATISTICS \
    | FEATURE_RESULTS \
    | FEATURE_NOTIFY \
    | FEATURE_DIAGRAM \
    | FEATURE_SYNDICATE \
    | FEATURE_DESCRIBE \
    | FEATURE_PUBLISH \
    | FEATURE_DOCUMENT

FEATURE_OFFICIAL = FEATURE_ALL


###############################################################################
# Classes
###############################################################################

class GumpRunOptions:
    """

    GumpRunOptions are the 'switches' that dictate the code path

    """
    def __init__(self):
 
        self.debug = False
        self.verbose = False
        self.cache = True # Defaults to CACHE
        self.quick = True # Defaults to QUICK
        self.dated = False        # Defaults to NOT dated.
        self.optimize = False     # Do the least ammount of work...
        self.official = False     # Do a full run (with publishing e-mail)

        # Default is XDOCS/XHTML, but can also force text with --text 
        self.text = False

        # Defautl for XDOCS is XHTML
        self.xdocs = False

        self.objectives = OBJECTIVE_INTEGRATE
        self.features = FEATURE_DEFAULT

        self.resolver = None

    def isDated(self):
        return self.dated

    def setDated(self, dated):
        self.dated = dated

    def setHistorical(self, historical):
        if historical:
            self.enableFeature(FEATURE_HISTORICAL)
        else:
            self.disableFeature(FEATURE_HISTORICAL)

    def isOfficial(self):
        """
        Is an official run requested?
        """
        return self.official

    def setOfficial(self, official):
        """
        An official run
        """
        self.official = official
        self.features = FEATURE_OFFICIAL

    def isQuick(self):
        """
        Is a 'quick' (not complete, i.e. list not sequence) run requested?
        """
        return self.quick

    def setQuick(self, quick):
        """
        Set a 'quick' (not complete, i.e. list not sequence) run request
        """
        self.quick = quick

    def isText(self):
        """
        Is Text documentation generation requested?
        """
        return self.text

    def setText(self, text):
        self.text = text

    def isXDocs(self):
        """
        Is XDOC documentation generation requested?
        """
        return self.xdocs

    def setXDocs(self, xdocs):
        """
        Set XDOC documentation generation
        """
        self.xdocs = xdocs

    def isCache(self):
        """
        Is metadata caching requested?
        """
        return self.cache

    def setCache(self, cache):
        """
        Perform metadata caching
        """
        self.cache = cache

    def isDebug(self):
        """
        Is a debug run requested?
        """
        return self.debug

    def setDebug(self, debug):
        self.debug = debug

    def isVerbose(self):
        return self.verbose

    def setVerbose(self, verbose):
        """
        A verbose run
        """
        self.verbose = verbose

    def setResolver(self, resolver):
        """
        The File/URL resolver (from Gump objects)
        """
        self.resolver = resolver

    def getResolver(self):
        return self.resolver

    # Objectives...
    def setObjectives(self, objectives):
        """
        Set the objectives
        """
        self.objectives = objectives

    def getObjectives(self):
        return self.objectives

    def _testObjectiveIsSet(self, objective):
        """
        Helper to test a single objective
        """
        if (self.objectives & objective):
            return True
        return False

    # Features...
    def setFeatures(self, features):
        """
        Set the features
        """
        self.features = features

    def getFeatures(self):
        return self.features

    def disableFeature(self, feature):
        """
        Disable a specific feature (or bitwise or of features)
        """
        self.features = (self.features ^ feature)

    def enableFeature(self, feature):
        """
        Enable a specific feature (or bitwise or of features)
        """
        self.features = (self.features | feature)

    def _testFeatureIsSet(self, feature):
        """
        A utility method to see if a feature is set.
        """
        if (self.features & feature):
            return True
        return False

    def isUpdate(self):
        """
        Are Updates (CVS|SVN|...) to be performed?
        """
        return self._testObjectiveIsSet(OBJECTIVE_UPDATE)

    def isBuild(self):
        """
        Are Builds (Ant|...) to be performed?
        """
        return self._testObjectiveIsSet(OBJECTIVE_BUILD)

    def isCheck(self): 
        """
        Is this really jsut a 'check' or things?
        """
        return self._testObjectiveIsSet(OBJECTIVE_CHECK) 

    def isNotify(self):
        """
        Are notifications (nag e-mails) to be produced?
        """
        return self._testFeatureIsSet(FEATURE_NOTIFY)

    def isResults(self):
        """
        Are results to be downloaded/produced for this run?
        """
        return self._testFeatureIsSet(FEATURE_RESULTS)

    def isStatistics(self):
        return self._testFeatureIsSet(FEATURE_STATISTICS)

    def isHistorical(self):
        return self._testFeatureIsSet(FEATURE_HISTORICAL)

    def isDocument(self):
        """
        Is documentation to be created for this run?
        """
        return  self._testObjectiveIsSet(OBJECTIVE_DOCUMENT) and \
            self._testFeatureIsSet(FEATURE_DOCUMENT)

    def isSyndicate(self):
        """
        Is syndication (RSS|Atom) to be performed for this run?
        """
        return self._testFeatureIsSet(FEATURE_SYNDICATE)

    def isDescribe(self):
        """
        Is describer (RDF) to be performed for this run?
        """
        return self._testFeatureIsSet(FEATURE_DESCRIBE)

    def isPublish(self):
        """
        Is publish (artifact repository) to be performed for this run?
        """
        return self._testFeatureIsSet(FEATURE_PUBLISH)

    def isDiagram(self):
        """
        Are SVG dependency diagrams to be generated for this run?
        """
        return self._testFeatureIsSet(FEATURE_DIAGRAM)
