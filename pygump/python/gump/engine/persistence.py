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

#    Information from previous projects can be stored using the store_previous_build()
#    method. It can be used in place of the "current build" using use_previous_build()
#    if has_previous_build() shows there actually was a build stored, and then everything
#    can be restored to normal using stop_using_previous_build().

from gump.model.util import get_project_directory
import os

def has_previous_build(project):
    """Determine if information from a previous build was stored for this project."""
    return hasattr(project, "previous_build")


def store_previous_build(project):
    import copy
    
    stored_project = copy.deepcopy(project) # TODO problem here!!!!
    
    if getattr(project, "failed", False):
        return
    
    for output in project.outputs:
        if isinstance(output, Homedir):
            store_previous_build_homedir(project, output)
            continue
        if isinstance(output, Jar):
            store_previous_build_jar(project, output)
            continue
        
        raise "Can't store this kind of output (%s)!" % output

# TODO make module out of all this, make this configurable
import shutil
storage_dir = os.path.join("work", "previous_build_storage")
if not os.path.exists(storage_dir):
  os.makedirs(storage_dir)

def store_previous_build_homedir(project, homedir):
    homedir_path = os.path.join(get_project_directory(project), homedir.directory)
    homedir_storage_path = os.path.join(storage_dir, homedir_path)
    shutil.copytree(homedir_path, homedir_storage_path)

def is_special_previous_build_attr(name):
    return name == "delete_atts_when_stopping_to_use_previous_build" or \
           name == "use_atts_when_stopping_to_use_previous_build" or \
           name == "previous_build"

def use_previous_build(project):
    # if the "previous build" "failed" we'll not attempt to use it
    if getattr(project.previous_build, "failed", False):
        return
    
    if hasattr(project, "use_atts_when_stopping_to_use_previous_build"):
        # use_previous_build() seemingly was already active on this build
        return

    # we'll replace all current members with the "old" members
    import inspect
    members = inspect.getmembers(project)
    oldmembers = inspect.getmembers(project.previous_build)
    
    # remember...
    project.use_atts_when_stopping_to_use_previous_build = members

    # we'll delete all current members that weren't there before
    temporarily_delete_attrs = []
    for (newname, newvalue) in members:
        found_in_old = False
        for (oldname, oldvalue) in oldmembers:
            if oldname == newname:
                found_in_old = True
                break
        
        if not found_in_old and not is_special_previous_build_attr(attname):
            delattr(project, attname)
    
    # we'll have to remove the members on the old project but not
    # on the new one
    temporarily_add_attrs = []
    for (oldname, oldvalue) in oldmembers:
        found_in_new = False
        for (newname, newvalue) in newmembers:
            if newname == oldname:
                found_in_new = True
                break
        
        if not found_in_new and not is_special_previous_build_attr(attname):
            temporarily_add_attrs += oldname
    
    # the "failed" member is a special case since we set it below
    if not hasattr(project, "failed"):
        temporarily_add_attrs += "failed"
    
    # remember...
    project.delete_atts_when_stopping_to_use_previous_build = temporarily_add_attrs

    # move all old project members to the new one
    for (name, value) in oldmembers:
        if is_special_previous_build_attr(name):
            continue
        setattr(project, name, value)
        
    # unmark failure as a sanity check (we checked for it above)
    project.failed = False
    
    
def stop_using_previous_build(project):
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
