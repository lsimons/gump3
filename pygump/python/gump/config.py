#!/usr/bin/env python

# Copyright 2005 The Apache Software Foundation
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

"""This module provides the "component wiring" for the gump application."""

__copyright__ = "Copyright (c) 2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import os
import logging

def get_config(settings):
    """Convert the settings object into something more specific.

    The 'main' module uses the 'optparse' module to generate a Values instance,
    which is the argument provided to this method. The reason we put this
    function and the Config class in between those settings and the main
    engine is that we can change gump internals more easily while keeping the
    CLI interface the same, with the integration point being isolated to this
    config module.
    
    Nonetheless, if possible, it is preferable to set options through CLI
    rather than in this method. Modify the get_parser() method in the main
    module to support that.
    """
    config = Config(settings)
    
    if settings.debug:
        config.log_level       = logging.DEBUG
    else:
        config.log_level       = logging.INFO

    # TODO: change main.py to do it like this
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


def get_plugins(config):
    """This method returns an ordered list of plugins.
    
    These plugins work together to form "the meat" of the gump application.
    Changing what this method returns allows changing nearly everything but
    the core behaviour of the gump engine.
    
    The config argument provided is an instance of the _Config class that is
    returned from the get_config method below.
    """
    
    pre_process_plugins = []
    # TODO: append more plugins here...
    
    from gump.plugins.instrumentation import TimerPlugin
    pre_process_plugins.append(TimerPlugin("run_start"))
    
    plugins = []
    # TODO: append more plugins here...

    from gump.plugins import LoggingPlugin
    log = get_logger(config.log_level, "plugin-log")
    plugins.append(LoggingPlugin(log))
    
    post_process_plugins = []
    # TODO: append more plugins here...
    post_process_plugins.append(TimerPlugin("run_end"))

    from gump.plugins.dynagumper import Dynagumper
    db = get_db(config)
    log = get_logger(config.log_level, "plugin-dynagumper")
    post_process_plugins.append(Dynagumper(db, log, "run_start", "run_end"))
    
    return (pre_process_plugins, plugins, post_process_plugins)


def get_error_handler(config):
    """This method returns the error handler that deals with naughty plugins.
    
    Though every plugin is free to do proper error handling and recovery, the
    ones that do usually should not bring gump to a full stop. That is why a
    central error handler is defined that catches all exceptions thrown by
    all plugins and figures out what to do with it. This function provides
    that error handler.

    The config argument provided is an instance of the _Config class that is
    returned from the get_config method below.
    """

    # TODO: implement an error handler that does actual recovery...
    
    from gump.plugins import LoggingErrorHandler
    log = get_logger(config.log_level, "plugin-error-handler")
    return LoggingErrorHandler(log)

###
### Changing anything below this line is for advanced gump hackers only!
###

class Config:
    """Central class for configuring the gump engine.

    This class is mostly an empty "container" on which the get_config method
    above sets properties. The only bit of intelligence in this class is
    within the defined __getattr__ method that computes config values based
    on other config values.
    """
    def __init__(self, cli_provided_settings):
        self.settings = cli_provided_settings

    def __getattr__(self,name):
        """Calculate missing settings from other settings at runtime."""
        if hasattr(self.settings, name):
            return self.settings.name

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


def get_logger(level, name):
    """Provide a logging implementation for the given level and name."""
    logging.basicConfig()
    log = logging.getLogger(name)
    log.setLevel(level)
    return log


def get_db(config):
    """Provide a database implementation."""
    from gump.util.mysql import Database
    db = Database(config) #TODO!
    return db


def get_vfs(filesystem_root, cache_dir):
    """Provide a VFS implementation."""
    from gump.util.io import VFS
    return VFS(filesystem_root, cache_dir)


def get_modeller_loader(log, vfs=None, mergefile=None, dropfile=None):
    """Provide a Loader implementation."""
    from gump.engine.modeller import Loader
    return Loader(log, vfs, mergefile, dropfile)


def get_modeller_normalizer(log):
    """Provide a Normalizer implementation."""
    from gump.engine.modeller import Normalizer
    return Normalizer(log)


def get_modeller_objectifier(log):
    """Provide a Objectifier implementation."""
    from gump.engine.modeller import Objectifier
    return Objectifier(log)


def get_modeller_verifier():
    """Provide a Verifier implementation."""
    from gump.engine.modeller import Verifier
    return Verifier()


def get_walker(config):
    """Provide a Walker implementation."""
    from gump.engine.walker import Walker
    
    log = get_logger(config.log_level, "walker")
    return Walker(log)


def get_plugin(config):
    """Provide a Plugin implementation."""
    from gump.plugins import MulticastPlugin
    
    (pre_process_plugins, plugins, post_process_plugins) = get_plugins(config)
    error_handler = get_error_handler(config)
    
    return (MulticastPlugin(pre_process_plugins, error_handler),
            MulticastPlugin(plugins, error_handler),
            MulticastPlugin(post_process_plugins, error_handler))
