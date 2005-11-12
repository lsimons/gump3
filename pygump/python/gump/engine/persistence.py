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

"""Extreme gump model hacking wizardry which uses the python shelve module to keep 
around the "last successful build". This is an experimental module only!

Why no unit tests? No good reason. There really ought to be some. Since this code has
*loads* of side effects, the unit test should actually be quite big. Secondly, since
basically we're subverting all the 'cleanness' of our model there should be extensive
integration testing. Oh well. Testing in isolation *should* be relatively feasible just
by passing in a mock shelf.

Basically what happens is that when the algorithm.py detects a dependency on a failed
build, it will ask this helper to get it a "previous one". In order to make the rest of
the gump system work kind-of transparently, that means we need to realistically store
"everything" about a particular project build. "Everything" is potentially pretty much
a snapshot of the entire harddrive of the system, the entire gump codebase itself, the
load-up of that codebase in memory, etc. That's a bit too much.

What we do save is a mungled, minimized, small snapshot of a part of the project and
the stuff it refers to within the gump model. And then we make a snapshot of the project
directory (eg all of the checkout including subdirectories, so that should include all
build outputs too) which we save too.

Then when we want to use a previous build, we get the mangled project definition from
the shelf and force-feed it into the new gump tree. We update it to reference the new
module (though we don't update the module to reference the new project), update it to
have dependencies on the new projects (though the algorithm.py doesn't make sure that
those have already been built, which can introduce subtle problems if the dependencies
for a project changed, but little we can do about that), then update the project path
to reference the snapshot of its files, and then finally we actually "replace" the
"current" (failed) project with the "previous" one in the project tree.

This replacement project definition stays in force for the rest of the run (though
algorithm.py could change that behaviour) so that if many projects depend on this failed
one, we don't have to go through the process of loading the project every time.

Why not implemented as a plugin? Well, this module is one of the core bits of the
algorithm.py functionality, and otherwise pretty much hacks into lots of bits in the
gump system. While the parts of this plugin that don't interact with the algorithm.py
code very closely could be split off, keeping it "out" as a special case hopefully keeps
the program flow a little more understandable.

Note that the file-copying code is not very efficient. Ideally we can do something using
hard links, falling back to efficient rsync. What we're doing here is doubling disk space
usage. When using SVN and doing a 'keep local copy checked out and duplicate before build'
(which gump2 does but gump3 does not at the moment), that means we have 3 checkouts of the
same stuff, which means 6 times the disk space, since SVN keeps around the .svn
directories). Ouch!
"""

from gump.model import Workspace, Repository, Module, Project, Jar, Path
from gump.model.util import get_project_directory, check_failure, check_skip
from gump.model.util import mark_previous_build
import os
import shutil
import copy

GUMP_STORAGE_DIRNAME=".gump-persist"

def copytree(source=None, target=None, excludes=[]):
    """Naive non-performant copytree utility.
    
    TODO: replace with something efficient (like rsync.py from gump2)."""
    if os.path.exists(target):
        shutil.rmtree(target)
    shutil.copytree(source, target)
    for x in excludes:
        fullpath = os.path.join(target, x)
        if os.path.exists(fullpath):
            shutil.rmtree(fullpath)
        
class ShelfBasedPersistenceHelper:
    def __init__(self, shelf, log):
        self.shelf = shelf
        self.log = log
        
    def store_previous_builds(self, workspace):
        for project in workspace.projects.values():
            if check_failure(project) or\
               check_skip(project) or \
               hasattr(project, "use_atts_when_stopping_to_use_previous_build"):
                    continue
                
            self.log.debug(
"Project %s built okay, storing as the new 'last successful build'..." % project)
            self.store_previous_build(project)
    
    def store_previous_build(self, project):
        if getattr(project, "failed", False):
            return

        # check there's no problematic references...
        for output in project.outputs:
            if isinstance(output, Jar): # relative path is ok...
                continue
            if isinstance(output, Path): # relative path is ok...
                continue
            
            # eg a Classdir is not allowed...
            raise "Can't store this kind of output (%s)!" % output
        
        # okay we can shelve this...
        self.log.debug("Storing previous build for %s..." % project)
        storeable_project = self.extract_storeable_project(project)
        mark_previous_build(storeable_project)
        
        # save files...
        self.store_previous_build_files(storeable_project)
        
        # now disconnect the rest of the model tree so we don't save it.
        storeable_project.module = None
        self.shelve_project(storeable_project)
        
    def extract_storeable_project(self, oldproject):
        # create a project referencing private copies of most stuff
        oldmodule = oldproject.module
        oldrepository = oldmodule.repository
        oldworkspace = oldrepository.workspace
        
        newworkspace = Workspace(oldworkspace.name, oldworkspace.workdir)
        newrepository = Repository(oldworkspace, oldrepository.name,
                                   oldrepository.title, oldrepository.home_page,
                                   oldrepository.cvsweb, oldrepository.redistributable)
        newmodule = Module(newrepository, oldmodule.name, oldmodule.url, oldmodule.description)
        newproject = Project(newmodule, oldproject.name, oldproject.path, oldproject.homedir)
        
        # and now we built that tree, note we set the reference to the module to null,
        # right before saving, circumverting all the checks in the model. So none of the
        # above except newproject is actually stored! Heh.
        # only right before saving....newproject.module = None
        
        # store only names of dependencies
        newproject.shelf_dependencies = []
        for relationship in oldproject.dependencies:
            newproject.shelf_dependencies.append(relationship.dependency.name)
        
        for output in oldproject.outputs:
            # these should not hold references to other parts of the tree...
            newproject.add_output(output)
        
        dontadd = ["module", "name", "path", "homedir", "dependencies", "dependees", "outputs", \
                   "commands", "shelf_dependencies", "has_stale_prereqs", "failure_cause", "stale_prereqs"]
        for x in dir(oldproject):
            if x in dontadd:
                continue
            if x.startswith("_"):
                continue
            if self.is_special_previous_build_attr(x):
                continue
            att = getattr(oldproject, x)
            if callable(att):
                continue
            setattr(newproject, x, att)
        
        return newproject
    
    def store_previous_build_files(self, project):
        currentpath = os.path.join(get_project_directory(project))
        if os.path.exists(currentpath):
            storage_path = os.path.join(currentpath, GUMP_STORAGE_DIRNAME)
    
            self.log.debug("Saving %s files into %s..." % (project, storage_path))
            
            copytree(source=currentpath, target=storage_path, excludes=[GUMP_STORAGE_DIRNAME])
            
            project.original_path = project.path
            project.path = os.path.join(project.path, GUMP_STORAGE_DIRNAME)
        else:
            self.log.debug("Not saving %s files -- none exist!" % project)
    
    def shelve_project(self, storeable_project):
        self.shelf[str(storeable_project.name)] = storeable_project
    
    def load_previous_build(self, project):
        project.previous_build = self.shelf[str(project.name)]
        
        # and include in the "new" tree
        #project.previous_build.module = project.module
        #ws = project.module.repository.workspace
        
        # The below causes the topsort to fail -- the number of indegrees
        # changes improperly. ouch!
        # and link up dependencies
        #for depname in project.previous_build.shelf_dependencies:
            # note we create a situation here where an "old" project seems to depend
            # on a "new" one. This can sort-of be detected by the dependee belonging
            # to a different workspace, except we just changed that, above! So, lets
            # flag this dependency as "one from the past", at least...
            #if ws.projects.has_key(depname):
            #    project.previous_build.add_dependency(ws.projects[depname])
            #    setattr(project.previous_build.dependencies[-1], "previous_build", True)
            #else:
            #    self.log.warn(
#"Previous build %s depends on project %s, which no longer exists! We're going to try and ignore this..." % (
    #project.previous_build, depname))

    def has_previous_build(self, project):
        """Determine if information from a previous build was stored for this project."""
        
        currentpath = os.path.join(get_project_directory(project))
        storage_path = os.path.join(currentpath, GUMP_STORAGE_DIRNAME)
        
        files_available = os.path.exists(storage_path)
        shelved = self.shelf.has_key(project.name)
        return files_available and shelved
    
    def is_special_previous_build_attr(self, name):
        return name in ["delete_atts_when_stopping_to_use_previous_build",
                        "use_atts_when_stopping_to_use_previous_build",
                        "previous_build"]
    
    def is_not_a_previous_build_attr(self, name):
        return name in ["module", "dependencies", "dependees"]
    
    def use_previous_build(self, project):
        # algorithm should check this!
        assert self.has_previous_build(project)
        
        self.log.debug("Using previous build for %s" % project)
        
        # get stuff from the shelf
        self.load_previous_build(project)

        # if the "previous build" "failed" we'll not attempt to use it
        # note that we'd be dealing with a silly algorithm -- we shouldn't be
        # storing failed builds...
        if getattr(project.previous_build, "failed", False):
            return
        
        if hasattr(project, "use_atts_when_stopping_to_use_previous_build"):
            # use_previous_build() seemingly was already active on this build
            return
    
        # we'll replace all current members with the "old" members
        import inspect
        newmembers = inspect.getmembers(project)
        oldmembers = inspect.getmembers(project.previous_build)
        
        # remember...
        project.use_atts_when_stopping_to_use_previous_build = newmembers
    
        # we'll delete all current members that weren't there before
        temporarily_delete_attrs = []
        for (newname, newvalue) in newmembers:
            if self.is_not_a_previous_build_attr(newname):
                continue
            found_in_old = False
            for (oldname, oldvalue) in oldmembers:
                if oldname == newname:
                    found_in_old = True
                    break
            
            if not found_in_old and not self.is_special_previous_build_attr(newname):
                delattr(project, newname)
        
        # we'll have to remove the members on the old project but not
        # on the new one
        temporarily_add_attrs = []
        for (oldname, oldvalue) in oldmembers:
            if self.is_not_a_previous_build_attr(newname):
                continue
            found_in_new = False
            for (newname, newvalue) in newmembers:
                if newname == oldname:
                    found_in_new = True
                    break
            
            if not found_in_new and not self.is_special_previous_build_attr(oldname):
                temporarily_add_attrs += oldname
        
        # the "failed" member is a special case since we set it below
        if not hasattr(project, "failed"):
            temporarily_add_attrs += "failed"
        
        # remember...
        project.delete_atts_when_stopping_to_use_previous_build = temporarily_add_attrs
    
        # move all old project members to the new one
        for (name, value) in oldmembers:
            if self.is_not_a_previous_build_attr(newname):
                continue
            if self.is_special_previous_build_attr(name):
                continue
            setattr(project, name, value)
            
        # unmark failure as a sanity check (we checked for it above)
        project.failed = False
        
    def stop_using_previous_build(self, project):
        if not hasattr(project, "use_atts_when_stopping_to_use_previous_build"):
            # use_previous_build() seemingly wasn't active on this build
            return
        
        # these were the temporary ones
        attlist = project.delete_atts_when_stopping_to_use_previous_build
        for attname in attlist:
            if is_special_previous_build_attr(name):
                # safety. This won't happen if use_previous_build() is used
                continue
            delattr(project, attname)
        
        # these were the actual values
        for (name,value) in project.use_atts_when_stopping_to_use_previous_build:
            if is_special_previous_build_attr(name):
                # safety. This won't happen if use_previous_build() is used
                continue
            setattr(project, name, value)
        
        # get rid of the remembered stuff
        if hasattr(project, "delete_atts_when_stopping_to_use_previous_build"):
            del project.delete_atts_when_stopping_to_use_previous_build
        if hasattr(project, "use_atts_when_stopping_to_use_previous_build"):
            del project.use_atts_when_stopping_to_use_previous_build
