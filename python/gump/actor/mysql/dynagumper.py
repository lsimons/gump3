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

__copyright__ = "Copyright (c) 2004 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import platform

from gump.core.run.gumprun import *
import gump.core.run.actor

class Dynagumper(gump.core.run.actor.AbstractRunActor):
    """
    Populate the DynaGump run metadata database.
    """
    
    def __init__(self,run,db, log = None):
        """
        Set up the Dynagumper:
            Dynagumper(run,database)
        
        Run is an instance of GumpRun, db is an instance of Database.
        Optional argument: log, instance of logging.logger or similar.
        Will use log from gump.logging if not provided.
        """
        gump.core.run.actor.AbstractRunActor.__init__(self,run)    
        self.db = db
        
        if not log: from gump import log
        self.log = log
    
    def ensureThisHostIsInDatabase(self):
        """
        Adds information about this server to the hosts table.
        """
        (system, host, release, version, machine, processor) = platform.uname()
        tablename = "hosts"
        description = "%s (%s,%s,%s,%s,%s)" % (host, system, release, version, machine, processor)
        cmd = "INSERT INTO %s (address, name, cpu_arch, description) VALUES ('%s', '%s', '%s', '%s')" \
                % (tablename, host, host, processor, description)
        
        self.db.execute(cmd)
        
    def processOtherEvent(self,event):
        #TODO do the actual work right here...
        #self.log.warning('dynagumper.py processOtherEvent: need to implement event processing')
        pass
              
    def processWorkspace(self):
        """
        Add information about the workspace to the database.
        """
        #TODO do the actual work right here...
        #self.ensureThisHostIsInDatabase()
        #self.log.warning('dynagumper.py processWorkspace: need to implement workspace event processing')
        pass

    def processModule(self,module):    
        """
        Add information about a module to the database.
        """
        #TODO do the actual work
        #self.log.warning('dynagumper.py processModule: need to implement module event processing')
        pass

    def processProject(self,project):    
        """
        Add information about a project to the database.
        """
        #TODO do the actual work right here...
        #self.log.warning('dynagumper.py processProject: need to implement project event processing')
        pass
