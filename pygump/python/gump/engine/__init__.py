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

"""This module contains the main controller that runs pygump.

The function main() is called from the main.main() function, which construcs
the neccessary helpers for an Engine instance that is then told to perform a
run.

The engine utilizes several submodules that provide pieces of its
functionality. Each of these modules usually exports a single class which has
a clearly defined responsibility. A single instance of such a class is used
for performing a specific task. In pygump we call such a beast a "component".

All required settings, as well as any other components a component may depend
on are passed into the constructor when first creating the instance. This is
all handled by the main() function. Doing things this way greatly decreases
the amount of coupling between the different modules. For example, the
gump.engine module is the only module that actually has an "import logging".
It creates all the log instances to pass into its helpers. This means that
completely rewiring or disabling logging is a simple as modifying the
_get_logger() function in this module.
"""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import os
import logging

from xml import dom
from xml.dom import minidom

def main(settings):
    """
    Controls the big pygump beast. This function is called from the main.main()
    method once the environment has been analyzed, parsed, fully set
    up, and checked for correctness. In other words, once the beastie is
    ready to roll.
    
    It creates an Engine and starts it.
    
    Arguments:
      - settings -- everything the engine needs to know about the environment.
    """
    
    # ooh...ah...fancy :-D
    _banner(settings.version)
    
    # get engine config
    config = get_config(settings)
    
    # get engine dependencies
    log = get_logger(config.log_level, "engine")
    db  = get_db(config)
    
    vfsdir = os.path.join(config.paths_work, "vfs-cache")
    if not os.path.isdir(vfsdir):
        os.mkdir(vfsdir);
    vfs = get_vfs(config.paths_metadata, vfsdir)
    
    modeller_log = get_logger(config.log_level, "modeller")
    mergefile = os.path.join(config.paths_work, "merge.xml")
    dropfile = os.path.join(config.paths_work, "dropped.xml")
    modeller_loader = get_modeller_loader(modeller_log, vfs, mergefile, dropfile)
    modeller_objectifier = get_modeller_objectifier(modeller_log)
    
    # create engine
    engine = Engine(config, log, db, modeller_loader, modeller_objectifier)
    
    # run it
    engine.initialize()
    engine.run()
    engine.dispose()


def _banner(version):
    """Print a fancy ASCII-art gump logo."""
    print
    print
    print "      _____"
    print "     |   __|_ Apache_ ___"
    print "     |  |  | | |     | . |"
    print "     |_____|___|_|_|_|  _|"
    print "                     |_|     ~ v. " + version + " ~"
    print
    print

###
### FACTORY METHODS
###

def get_config(settings):
    """
    Convert the settings object (the Values retrieved from the OptionsParser)
    into something more specific. The reason we put this function and the Config
    class in between is that we can change gump internals while keeping the CLI
    interface the same more easily, with the integration point being isolated to
    this method and the Config class definition.
    """
    config = Config()
    
    if settings.debug:
        config.log_level       = logging.DEBUG
    else:
        config.log_level       = logging.INFO

    config.hostname        = settings.hostname
    config.projects        = settings.projects
    config.paths_home      = settings.homedir
    config.paths_work      = settings.workdir
    config.paths_logs      = settings.logdir
    config.paths_workspace = settings.workspace
    config.do_update       = not settings.no_updates
    config.start_time      = settings.starttimeutc
    
    config.projects        = settings.projects
    
    config.mail_server     = settings.mailserver
    config.mail_server_port = settings.mailport
    config.mail_to         = settings.mailto
    config.mail_from       = settings.mailfrom
    
    # TODO: set defaults in main.py instead
    config.database_server = "localhost"
    if hasattr(settings,"databaseserver"): config.database_server = settings.databaseserver
    config.database_port   = 3306
    if hasattr(settings,"databaseport"): config.database_port = settings.databaseport
    config.database_name   = "gump"
    if hasattr(settings,"databasename"): config.database_name = settings.databasename
    config.database_user   = "gump"
    if hasattr(settings,"databaseuser"): config.database_user = settings.databaseuser
    config.database_password   = "gump"
    if hasattr(settings,"databasepassword"): config.database_password = settings.databasepassword
    
    return config

def get_logger(level, name):
    logging.basicConfig()
    log = logging.getLogger(name)
    log.setLevel(level)
    return log

def get_db(config):
    from gump.util.mysql import Database
    db = Database(config) #TODO!
    return db

def get_vfs(filesystem_root, cache_dir):
    from gump.engine.vfs import VFS
    return VFS(filesystem_root, cache_dir)

def get_modeller_loader(log, vfs=None, mergefile=None, dropfile=None):
    from gump.engine.modeller import Loader
    return Loader(log, vfs, mergefile, dropfile)

def get_modeller_objectifier(log):
    from gump.engine.modeller import Objectifier
    return Objectifier(log)

###
### Classes
###

class Config:
    def __getattr__(self,name):
        """
        Some config values are calculated at runtime from other values
        if they're not especially set.
        """
        if name == 'debug':
            return self.loglevel >= logging.DEBUG
        if name == 'paths_pygump':
            return os.path.jion(self.paths_home, "pygump")
        if name == 'paths_metadata':
            return os.path.join(self.paths_home, "metadata")
        if name == 'do_mail':
            return self.mail_server and self.mail_server_port and self.mail_to and self.mail_from
        
        # unknown, raise error
        raise AttributeError, name

class Engine:
    """
    This is the core of the pygump application.
    """
    
    def __init__(self, config, log, db, workspace_loader, workspace_objectifier):
        """
        Store all config and dependencies as properties.
        """
        self.config = config
        self.log = log
        self.db = db
        self.workspace_loader = workspace_loader
        self.workspace_objectifier = workspace_objectifier
    
    def initialize(self):
        """
        Perform pre-run initialization.
        """
        pass
    
    def run(self):
        """
        Perform a run.
        """
        try:
            # 1) merge workspace into big DOM tree
            (dom, dropped_nodes) = self.workspace_loader.get_workspace_tree(self.config.paths_workspace)
            # 2) convert that DOM tree into python objects
            workspace = self.workspace_objectifier.get_workspace(dom)
            # 3) store those objects in the database
            self.store_workspace(self.workspace) #TODO
            # 4) determine the tasks to perform
            self.tasks = self.create_ordered_tasklist() #TODO
            
            # 5) now make the workers perform those tasks
            self.create_workers() #TODO
            self.start_workers() #TODO
            self.wait_for_workers() #TODO
        except:
            self.log.exception("Fatal error during run!")
    
    def dispose(self):
        """
        End a run.
        """
        pass
