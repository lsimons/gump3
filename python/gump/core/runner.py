#!/usr/bin/python


# Copyright 2003-2004 The Apache Software Foundation
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

"""

"""

import os.path
import sys

from gump import log



from gump.core.misc import *
from gump.update.updater import *
from gump.build.builder import *




###############################################################################
# Classes
###############################################################################


class GumpRunner(Runnable):

    def __init__(self, run):
        
        #
        Runnable.__init__(self, run)
        
        self.misc=GumpMiscellaneous(run)    
        self.updater=GumpUpdater(run)
        self.builder=GumpBuilder(run)
        

def getRunner(run):
    from gump.core.tasks import SequentialTaskRunner
    return SequentialTaskRunner(run)
    
    #from gump.core.demand import OnDemandRunner
    #return OnDemandRunner(run)
