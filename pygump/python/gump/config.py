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

# Note that there aren't any unit tests for this module. That's a
# concious decision. Most of this code has a "glue" function, and
# is either really trivial or by definition required for a good
# operation of the entire application. The latter makes it an
# important candidate for good unit testing. However, this file is
# one of the places that is expected to change most often, and hence,
# that would lead to a rather intensive maintainance burden with
# regard to the unit tests.

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
    if settings.quiet:
        config.debug = False
        config.log_level = logging.WARN
    
    # set up other stuff
    run_config_hooks(config)
    
    return config


def get_plugins(config):
    """This method returns an ordered list of plugins.
    
    These plugins work together to form "the meat" of the gump application.
    Changing what this method returns allows changing nearly everything but
    the core behaviour of the gump engine.
    
    The config argument provided is an instance of the _Config class that is
    returned from the get_config method below.
    """
    #
    # Note that in general, the ordering of these plugins is vital to ensuring
    # correct functionality!
    #
    log = get_logger(config, "plugin")

    pre_process_plugins = []
    # TODO: append more plugins here...
    
    from gump.plugins.instrumentation import TimerPlugin
    pre_process_plugins.append(TimerPlugin("run_start"))
    
    plugins = []

    # TODO: append more plugins here...

    plugins.append(TimerPlugin("work_start"))
        
    from gump.plugins import LoggingPlugin

    debuglog = get_logger(config, "plugin.logger.debug")
    from gump.plugins.logreporter import DebugLogReporterPlugin
    plugins.append(DebugLogReporterPlugin(debuglog))
        
    if config.do_update:    
        plugins.append(TimerPlugin("update_start"))
        from gump.plugins.updater import CvsUpdater, SvnUpdater
        plugins.append(CvsUpdater())
        plugins.append(SvnUpdater())
        plugins.append(TimerPlugin("update_end"))
    else:
        log.info("Not running updates! (pass --do-updates to enable them)")
        
    if config.do_build:
        from gump.model import Ant
        from gump.model import Script

        # by contract, rmdir always needs to go before mkdir!
        from gump.plugins.dirbuilder import RmdirBuilderPlugin
        plugins.append(RmdirBuilderPlugin())
        from gump.plugins.dirbuilder import MkdirBuilderPlugin
        plugins.append(MkdirBuilderPlugin())
    
        buildlog = get_logger(config, "plugin.builder")
    
        from gump.plugins.builder import PathPlugin
        plugins.append(PathPlugin(buildlog, Ant))
        plugins.append(PathPlugin(buildlog, Script))
        from gump.plugins.builder import ScriptBuilderPlugin
        plugins.append(ScriptBuilderPlugin(buildlog))
        from gump.plugins.java.builder import ClasspathPlugin
        plugins.append(ClasspathPlugin(buildlog,Ant))
        from gump.plugins.java.builder import AntPlugin
        plugins.append(AntPlugin(buildlog))
        #plugins.append(AntPlugin(buildlog, debug=True))
    else:
        log.info("Not running builds! (pass --do-builds to enable them)")
     
           
    if config.irc:        
        # Since one does not need to put --irc onto the command line,
        # bew pretty strict. Fail if there config is in error, or if
        # IRCLIB is not available.
        from gump.plugins.irc import parseAddressInfo, IrcBotPlugin
        
        # Parse the input format to extract addressing
        (channel,nickname,server,port)=parseAddressInfo(config.irc)
        
        # Add the plugin, based upon this configuration information.
        plugins.append(IrcBotPlugin(log,config.debug,channel,nickname,server,port))
    else:
        log.info("Not talking on irc! (pass --irc to enable)")
        
    plugins.append(TimerPlugin("work_end"))

    post_process_plugins = []
    # TODO: append more plugins here...
    post_process_plugins.append(TimerPlugin("run_end"))
    
    if config.do_fill_database:
        from gump.plugins.dynagumper import Dynagumper
        dblog = get_logger(config, "util.db")
        db = get_db(dblog,config)
        dynagumplog = get_logger(config, "plugin.dynagumper")
        post_process_plugins.append(Dynagumper(db, dynagumplog))
    else:
        log.info("Not filling database! (pass --fill-database to enable)")
    
    reportlog = get_logger(config, "plugin.logger")
    from gump.plugins.logreporter import OutputLogReporterPlugin
    post_process_plugins.append(OutputLogReporterPlugin(reportlog))

    from gump.plugins.logreporter import ResultLogReporterPlugin
    post_process_plugins.append(ResultLogReporterPlugin(reportlog))
    
    #if config.debug:
    #    from gump.plugins.introspection import IntrospectionPlugin
    #    post_process_plugins.append(IntrospectionPlugin(reportlog))
    
    # Give us an insight to what we have cooking...
    for plugin in pre_process_plugins: log.debug("Preprocessor : %s " % `plugin`)
    for plugin in plugins: log.debug("Processor    : %s " % `plugin`)
    for plugin in post_process_plugins: log.debug("Postprocessor: %s " % `plugin`)

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
    #from gump.plugins import LoggingErrorHandler
    from gump.engine.algorithm import OptimisticLoggingErrorHandler
    log = get_logger(config, "plugin.error-handler")
    return OptimisticLoggingErrorHandler(log)


def get_at_variable_dictionary(config):
    import time
    
    dictionary = {}
    dictionary["GUMP_VERSION"] = config.version
    dictionary["DATE"] = time.strftime("%Y%m%d%H%M")
    
    return dictionary

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
            return getattr(self.settings, name)

        if name == 'paths_pygump':
            return os.path.join(self.paths_home, "pygump")
        if name == 'paths_metadata':
            return os.path.join(self.paths_home, "metadata")
        if name == 'do_mail':
            return self.mail_server and self.mail_server_port and self.mail_to and self.mail_from
        
        # unknown, raise error
        raise AttributeError, name


def get_logger(config, name):
    """Provide a logging implementation for the given level and name."""
    logging.basicConfig()
    log = logging.getLogger(name)
    # Let the file decide ... log.setLevel(config.log_level)
    return log

def shutdown_logging():
    """Perform orderly logging shutdown"""
    logging.shutdown()
    

def get_db(log,config):
    """Provide a database implementation."""
    from gump.util.mysql import Database

    db = Database(log,
                  config.database_server,
                  config.database_user,
                  config.database_password,
                  config.database_name)
    return db


_VFS_CACHE_DIR_NAME="vfs-cache"

def get_vfs(config):
    """Provide a VFS implementation."""
    from gump.util.io import VFS

    cache_dir = os.path.join(config.paths_work, _VFS_CACHE_DIR_NAME)
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir);
    return VFS(config.paths_metadata, cache_dir)


def get_engine_loader(log, vfs=None):
    """Provide a Loader implementation."""
    from gump.engine.loader import Loader
    return Loader(log, vfs)


def get_engine_normalizer(log):
    """Provide a Normalizer implementation."""
    from gump.engine.normalizer import Normalizer
    return Normalizer(log)


def get_engine_at_parser(config):
    """Provide a AtParser implementation."""
    from gump.engine.at_parser import AtParser
    
    return AtParser(get_at_variable_dictionary(config))


def get_engine_objectifier(config, log):
    """Provide a Objectifier implementation."""
    from gump.engine.objectifier import Objectifier
    return Objectifier(log, config.paths_work)


def get_engine_verifier(config, walker):
    """Provide a Verifier implementation."""
    from gump.engine.verifier import Verifier, LoggingErrorHandler
    log = get_logger(config, "verifier")
    return Verifier(walker, LoggingErrorHandler(log))


def get_engine_walker(config):
    """Provide a Walker implementation."""
    from gump.engine.walker import Walker
    
    log = get_logger(config, "walker")
    return Walker(log)


def get_dom_implementation():
    """Provide a DOM implementation."""
    from xml import dom
    impl = dom.getDOMImplementation()
    return impl


def get_plugin(config):
    """Provide a Plugin implementation."""
    from gump.engine.algorithm import DumbAlgorithm
    from gump.engine.algorithm import MoreEfficientAlgorithm
    
    (pre_process_plugins, plugins, post_process_plugins) = get_plugins(config)
    error_handler = get_error_handler(config)
    
    if getattr(config, "project_name", False):
        mainalgorithm = MoreEfficientAlgorithm(plugins, error_handler, project_list=config.project_name)
    else:
        mainalgorithm = MoreEfficientAlgorithm(plugins, error_handler)
    
    return (DumbAlgorithm(pre_process_plugins, error_handler),
            mainalgorithm, #DumbAlgorithm(plugins, error_handler)
            DumbAlgorithm(post_process_plugins, error_handler))

#
# Miscellaneous configuration bits
#
def run_config_hooks(config):
    """This function is the place to configure all things that aren't cleanly
    "class-based", for example per-module configuration."""

    # set up logging module
    from logging.config import fileConfig
    if config.debug:
        fileConfig('gump.log.config.debug')
    else:
        if config.quiet:
            fileConfig('gump.log.config.quiet')
        else:
            fileConfig('gump.log.config')
    
    # set up gump.util.executor module
    # this will make Popen log all invocations
    import gump.util.executor
    gump.util.executor._log = get_logger(config, "util.executor")
    
    # set up gump.engine.objectifier module
    # this will change where we look for installed packages
    import gump.engine.objectifier
    if config.local_repository_name:
        gump.engine.objectifier.DEFAULT_GUMP_LOCAL_REPOSITORY_NAME = config.local_repository_name
    if config.local_module_name:
        gump.engine.objectifier.DEFAULT_GUMP_LOCAL_MODULE_NAME = config.local_module_name
