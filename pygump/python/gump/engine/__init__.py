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

from xml import dom
from xml.dom import minidom

from gump.config import *
from gump.util.io import open_file_or_stream

_ENGINE_LOGGER_NAME = "engine"
_MODELLER_LOGGER_NAME = "modeller"
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
    _banner(settings.version)
    
    # get engine config
    config = get_config(settings)
    
    # get engine dependencies
    log = get_logger(config, _ENGINE_LOGGER_NAME)
    
    vfs = get_vfs(config)
    walker = get_walker(config)
    modeller_log = get_logger(config, _MODELLER_LOGGER_NAME)
    modeller_loader = get_modeller_loader(modeller_log, vfs)
    modeller_normalizer = get_modeller_normalizer(modeller_log)
    modeller_objectifier = get_modeller_objectifier(modeller_log)
    modeller_verifier = get_modeller_verifier(walker)
    
    mergefile = os.path.join(config.paths_work, _MERGE_FILE_NAME)
    dropfile = os.path.join(config.paths_work, _DROPPED_FILE_NAME)
    
    dom_implementation = get_dom_implementation()
    (pre_process_visitor, visitor, post_process_visitor) = get_plugin(config)
    
    # create engine
    engine = _Engine(log, modeller_loader, modeller_normalizer,
                     modeller_objectifier, modeller_verifier, walker,
                     dom_implementation,
                     pre_process_visitor, visitor, post_process_visitor,
                     config.paths_workspace, mergefile, dropfile)
    
    # run it
    engine.run()


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
            
            # * Pfew! All done. Now actually start *doing* stuff.
            self.walker.walk(workspace, self.pre_process_visitor)
            # (visited_repositories, visited_modules, visited_projects) = \
            self.walker.walk(workspace, self.visitor)
            self.walker.walk(workspace, self.post_process_visitor)
            
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
