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
the neccessary helpers for an _Engine instance that is then told to perform a
run().

The engine utilizes several submodules that provide pieces of its
functionality. Each of these modules usually exports a single class which has
a clearly defined responsibility. A single instance of such a class is used
for performing a specific task. In pygump we call such a beast a "component".

All required settings, as well as any other components a component may depend
on are passed into the constructor when first creating the instance. This is
all handled by the main() function. Doing things this way greatly decreases
the amount of coupling between the different modules. For example, the
gump.config module is the only module that actually has an "import logging".
It creates all the log instances to pass into its helpers. This means that
completely rewiring or disabling logging is a simple as modifying the
get_logger() function in the gump.config module.
"""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import logging
import os
from xml import dom
from xml.dom import minidom

from gump.config import get_config
from gump.config import get_logger
from gump.config import get_vfs
from gump.config import get_engine_walker
from gump.config import get_engine_loader
from gump.config import get_engine_normalizer
from gump.config import get_engine_objectifier
from gump.config import get_engine_verifier
from gump.config import get_dom_implementation
from gump.config import get_plugin
from gump.config import shutdown_logging

from gump.util.io import open_file_or_stream
from gump.util import ansicolor

_ENGINE_LOGGER_NAME = "engine"
_ENGINE_HELPER_LOGGER_NAME = "modeller"
_MERGE_FILE_NAME = "merge.xml"
_DROPPED_FILE_NAME = "dropped.xml"

def main(settings):
    """Controls the big pygump beast.

    This function is called from the main.main()
    method once the environment has been analyzed, parsed, fully set
    up, and checked for correctness. In other words, once the beastie is
    ready to roll.
    
    It creates an Engine and starts it.
    
    Arguments:
      - settings -- everything the engine needs to know about the environment.
    """
    # For those familiar with "inversion of control" containers; this is
    # method is basically the "container". Since we're not doing any kind
    # of "autowiring", this method and the config file must work together
    # to get all the components wired up properly. However, that wiring
    # responsibility really is isolated right there. If neccessary we can
    # introduce some magic if we need to, but I do like that it is so very
    # visible what is going on here.
    #
    # The downside is that config.py and this method are very hard to unit
    # tests, since it all interacts in an ugly fashion. Oh well, this code
    # gets exercised more than enough on any integration test since there
    # is no if/else branching of any kind, no looping, etc.
    
    # ooh...ah...fancy :-D
    if settings.enable_colors:
        from gump.util import ansicolor
        ansicolor.enable_colors()

    if not settings.quiet:
        _banner(settings.version)
    
    # get engine config
    config = get_config(settings)
    
    # get engine dependencies
    log = get_logger(config, _ENGINE_LOGGER_NAME)
    
    vfs = get_vfs(config)
    engine_walker = get_engine_walker(config)
    engine_log = get_logger(config, _ENGINE_HELPER_LOGGER_NAME)
    engine_loader = get_engine_loader(engine_log, vfs)
    engine_normalizer = get_engine_normalizer(engine_log)
    engine_objectifier = get_engine_objectifier(config, engine_log)
    engine_verifier = get_engine_verifier(config, engine_walker)
    
    mergefile = os.path.join(config.paths_work, _MERGE_FILE_NAME)
    dropfile = os.path.join(config.paths_work, _DROPPED_FILE_NAME)
    
    dom_implementation = get_dom_implementation()
    (pre_process_visitor, visitor, post_process_visitor) = get_plugin(config)
    
    # create engine
    engine = _Engine(log, engine_loader, engine_normalizer,
                     engine_objectifier, engine_verifier, engine_walker,
                     dom_implementation,
                     pre_process_visitor, visitor, post_process_visitor,
                     config.paths_workspace, mergefile, dropfile)

    # Debugging sessions start right here
    if settings.attach_wing:
        print "=" * 78
        print """
!!!ENABLING WING IDE DEBUGGER!!!

You are entering a WING IDE debug session. If you set up Wing correctly and
specified the WINGHOME environment variable, wing should attach to gump in
a moment.

An overview of debugging external processes with Wing is at

  http://wingware.com/doc/debug/debugging-externally-launched-code

With the complete documentation for the Wing debugger at

  http://wingware.com/doc/debug/index

Note that you can get a free copy of the Wing IDE for open source development.
Details are at

  http://wingware.com/store/prices#discounts
        """
        print "=" * 78
        import wingdbstub
        wingdbstub.debugger.StartDebug(1)

    if settings.attach_pdb:
        print "=" * 78
        print """
!!!ENABLING COMMANDLINE DEBUGGER!!!

You are entering a PDB debug session. If you didn't want this, simply type
'continue' at the prompt that follows, then enter, then 'quit' when the
prompt returns.

Python's debugger is completely commmand-line based. An overview of
the available commands is at

  http://www.python.org/doc/current/lib/debugger-commands.html

You get basic information on these commands by typing 'help'. It's a good
idea to set some breakpoints within the run() method of the Engine class and
some breakpoints within for example the Walker class and/or the Algorithm
classes. Throughout the code, some useful spots to start debugging have been
marked with "# DEBUG TIP". For example, the following sequence of commands may
be useful for getting your feed wet (though note the line numbers are probably
out-of-sync with the current layout of the sourcefiles):

(Pdb) break gump/engine/__init__.py:235
(Pdb) break gump/engine/__init__.py:259
(Pdb) break gump/engine/algorithm.py:203
(Pdb) break gump/engine/algorithm.py:230
(Pdb) break gump/engine/walker.py:52
(Pdb) break
(Pdb) where
(Pdb) continue
(Pdb) where
(Pdb) continue
(Pdb) where
(Pdb) continue
(Pdb) where
       ... (until you're bored)
(Pdb) clear 1 2 3 4 5
(Pdb) continue
        """
        print "=" * 78
        import pdb
        pdb.set_trace()

    # run it
    engine.run()
    
    shutdown_logging()


def _banner(version):
    """Print a fancy ASCII-art gump logo."""
    print ansicolor.Bright_Blue
    print "                  _____"
    print "                 |   __|_ " + ansicolor.Red + "Apache" + ansicolor.Bright_Blue + "_ ___"
    print "                 |  |  | | |     | . |"
    print "                 |_____|___|_|_|_|  _|"
    print "                                 |_|     " + ansicolor.Blue + "~ v. " + version + " ~"
    print ansicolor.Black


class EngineError(Exception):
    """Generic error thrown for all internal Engine module exceptions."""
    pass


class _Engine:
    """This is the core of the core of the pygump application. It interacts
    with the other parts of the gump.engine package to transform the model
    xml into an object model and let loose plugins on that model."""
    
    def __init__(self, log, workspace_loader, workspace_normalizer,
                 workspace_objectifier, workspace_verifier, walker,
                 dom_implementation,
                 pre_process_visitor, visitor, post_process_visitor,
                 workspace, merge_to=None, drop_to=None):
        """Store all config and dependencies as properties.
        
        Arguments:
            
            - log -- the log to write debug and error messages to.
            - workspace_loader -- the component providing the dom tree.
            - workspace_normalizer -- the component transforming the dom tree
                into a standard format
            - workspace_objectifier -- the component transforming the dom into
                object form
            - workspace_verifier -- the component making sure the object model
                is correct
            - walker -- the component that knows how to traverse the gump
                model in dependency order
            - pre_process_visitor -- the component that gets called by the
                walker while visiting parts of the model during the
                pre-processing stage
            - visitor -- the component that gets called by the walker while
                visiting parts of the model during the build stage
            - post_process_visitor -- the component that gets called by the
                walker while visiting parts of the model during the
                pre-processing stage
            - dom_implementation -- a python dom implementation (for example
                the one returned by xml.dom.getDOMImplementation())

            - workspace -- the resource containing the workspace xml.
            - merge_to -- the resource to write the merged workspace xml to.
            - drop_to -- the resource to write the dropped projects xml to.
        """
        assert hasattr(log, "exception")
        assert callable(log.exception)
        assert hasattr(workspace_loader, "get_workspace_tree")
        assert callable(workspace_loader.get_workspace_tree)
        assert hasattr(workspace_normalizer, "normalize")
        assert callable(workspace_normalizer.normalize)
        assert hasattr(workspace_objectifier, "get_workspace")
        assert callable(workspace_objectifier.get_workspace)
        assert hasattr(workspace_verifier, "verify")
        assert callable(workspace_verifier.verify)
        assert hasattr(walker, "walk")
        assert callable(walker.walk)
        assert hasattr(dom_implementation, "createDocument")
        assert callable(dom_implementation.createDocument)
        assert workspace != None
        
        self.log = log
        self.workspace_loader = workspace_loader
        self.workspace_normalizer = workspace_normalizer
        self.workspace_objectifier = workspace_objectifier
        self.workspace_verifier = workspace_verifier
        self.walker = walker
        self.dom_implementation = dom_implementation

        self.pre_process_visitor = pre_process_visitor
        self.visitor = visitor
        self.post_process_visitor = post_process_visitor

        self.workspace = open_file_or_stream(workspace,'r')
        self.merge_to = open_file_or_stream(merge_to,'w')
        self.drop_to = open_file_or_stream(drop_to,'w')

    def run(self):
        """Perform a gump run. What actually goes on during a gump run is
        largely determined by the components we're using."""
        # DEBUG TIP: good place to start debugging :-)
        try:
            # * merge workspace into big DOM tree
            (domtree, dropped_nodes) = self.workspace_loader.get_workspace_tree(self.workspace)
            
            # * clean it up and structure it properly
            domtree = self.workspace_normalizer.normalize(domtree)
            
            # * write the merged, normalized tree out to a new xml file
            self._write_merge_files(domtree, dropped_nodes)
            
            # * convert that DOM tree into python objects
            workspace = self.workspace_objectifier.get_workspace(domtree)
            
            # * we're done with the xml stuff, allow GC
            domtree.unlink()
            for node in dropped_nodes:
                node.unlink()
                
            # * verify that our model is correct (for example, that it has
            #   no circular dependencies)
            self.workspace_verifier.verify(workspace)
            
            # DEBUG TIP: good place to look at the plugin flow control
            # * Pfew! All done. Now actually start *doing* stuff.
            self.walker.walk(workspace, self.pre_process_visitor, 'pre_process')
            # (visited_repositories, visited_modules, visited_projects) = \
            self.walker.walk(workspace, self.visitor, 'process')
            self.walker.walk(workspace, self.post_process_visitor, 'post_process')
            
            # That's it? Yeah! All other functionality is in the visitors :-D
        except:
            self.log.exception("Fatal error during run!")
    
    def _write_merge_files(self, domtree, dropped_nodes):
        """Write the fully resolved DOM tree to a file.
        
        Also writes an XML file detailing any projects and modules that were
        dropped because of a HREF resolution issue.
        """
        if self.merge_to:
            self.merge_to.write( domtree.toxml() )
            self.merge_to.close()
        
        if self.drop_to and len(dropped_nodes) > 0:
            dropdoc = self.dom_implementation.createDocument(None, "dropped-projects-and-modules", None)
            dropdocroot = dropdoc.documentElement
            for node in dropped_nodes:
                dropdocroot.appendChild(node)
            self.drop_to.write( dropdoc.toxml() )
            self.drop_to.close()
