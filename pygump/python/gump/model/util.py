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

"""This module defines contracts closely related to the object model."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

from os.path import abspath
from os.path import join
import os

from gump.model import ModelObject, Error, Dependency, CvsModule, SvnModule, ExceptionInfo, Classdir, Jar, \
     DEPENDENCY_INHERIT_ALL, DEPENDENCY_INHERIT_HARD, DEPENDENCY_INHERIT_JARS, DEPENDENCY_INHERIT_RUNTIME

UPDATE_TYPE_CHECKOUT="checkout"
UPDATE_TYPE_UPDATE="update"

def get_jar_path(workdir, jar):
    """Determine the path to a Jar."""
    return join(get_project_home_directory(workdir, jar.project),jar.name)

def get_project_home_directory(workdir, project):
    """Determine the home directory for a project."""
    return join(get_project_directory(workdir, project),project.homedir)

def get_project_directory(workdir, project):
    """Determine the base directory for a project."""
    return join(get_module_directory(workdir, project.module),project.path)

def get_module_directory(workdir, module):
    """Determine the base directory for a module."""
    return join(get_repository_directory(workdir,module.repository),module.name)

def get_repository_directory(workdir, repository):
    """Determine the base directory for a repository."""
    return join(get_workspace_directory(workdir,repository.workspace),repository.name)

def get_workspace_directory(workdir, workspace):
    """Determine the base directory for a workspace."""
    return abspath(join(workdir,workspace.name))

def mark_failure(model_element, cause):
    """Mark a model element as "failed"."""
    assert isinstance(model_element, ModelObject)
    model_element.failed = True
    if not hasattr(model_element, "failure_cause"):
        model_element.failure_cause = []
    model_element.failure_cause.append(cause)

def check_failure(model_element):
    """Determine whether a model element has "failed"."""
    assert isinstance(model_element, ModelObject)
    return getattr(model_element, "failed", False)

def get_failure_causes(model_element):
    """Get an array of "failure" "causes"."""
    assert isinstance(model_element, ModelObject)
    assert getattr(model_element, "failed", False)
    assert len(getattr(model_element, "failure_cause", [])) > 0

    return model_element.failure_cause

def get_cause_for_cause(cause):
    """Get whatever "caused" this "cause" (the "parent" cause).
    
    Returns only the *first* parent cause, not all of them. Returns
    None if there's no "parent" "cause"."""
    if isinstance(cause, Dependency):
        cause = cause.dependency

    if not isinstance(cause, ModelObject) \
       or not len(getattr(cause, "failure_cause", [])) > 0:
        return None
    
    return cause.failure_cause[0]

def get_root_cause(model_element):
    """Digs into a model element "blame" stack to find the "root" "cause".

    Returns an array containing a trace of all the different causes, starting
    with the main cause and ending with the "root" cause."""
    assert isinstance(model_element, ModelObject)

    if isinstance(model_element, Dependency):
        model_element = model_element.dependency

    if not hasattr(model_element, "failure_cause"):
        return []
    
    cause = model_element.failure_cause[0]
    trace = [cause]
    while True:
        parent_cause = get_cause_for_cause(cause)
        if parent_cause:
            if isinstance(parent_cause, Dependency):
                parent_cause = parent_cause.dependency

            if parent_cause in trace:
                # something is seriously screwed up here -- there's
                # a cyclic "cause". Now what? We'll assume that whatever
                # code is calling us is not really prepared to handle
                # something like that. For now we'll raise an exception.
                # I don't think we'll see this in practice -- its a
                # programming error within gump
                raise Error, "Impossible to find root cause as there's a cycle!"
            cause = parent_cause
            trace.append(cause)
        else:
            break
    
    return trace

def mark_skip(model_element):
    """Mark a model element as "should be skipped"."""
    model_element.skip = True

def check_skip(model_element):
    """Determine whether a model element "should be skipped"."""
    return getattr(model_element, "skip", False)

def mark_whether_module_was_updated(module):
    """Mark a module as "updated" if it was."""
    # checkout means we did in fact update
    if hasattr(module, "update_type"):
        if module.update_type == UPDATE_TYPE_CHECKOUT and not getattr(module, "failed", False):
            module.was_updated = True
        
    # no checkout, so an update. Might have had no effect. Check.
    if hasattr(module, "update_log") and not hasattr(module, "was_updated"):
        log = module.update_log.strip()

        # a non empty cvs log message means we did in fact update
        if isinstance(module, CvsModule):
            if len(log) > 0:
                module.was_updated = True
        
        # a svn log message always has a line "At revision ...."
        # if there's other lines with content it means we did in
        # fact update
        if isinstance(module, SvnModule):
            log.replace('\r\n', '\n')
            log.replace('\r', '\n')
            lines = log.split('\n')
            if len(lines) > 1:
                module.was_updated = True

def check_module_update_failure(module):
    """Determine whether a module "update" "failed"."""
    return getattr(module, "update_exit_status", False)

def store_exception(model_object, type, value, traceback):
    """Save exception information with a model element."""
    if not hasattr(model_object, 'exceptions'):
        model_object.exceptions = []
    model_object.exceptions.append(ExceptionInfo(type, value, traceback))

        
def calculate_classpath(workdir, project, recurse=True, runtimeonly=False):
    """This ugly beast of a method looks at a project and its dependencies and
    builds a classpath and a bootclasspath based on its <work/> directives
    and its <depend/> directives."""
    classpath = []
    bootclasspath = []

    # Ant requires to be told about a compiler
    if os.environ.has_key('JAVA_HOME'):
        classpath.append(os.path.join(os.environ['JAVA_HOME'],'lib','tools.jar'))
    
    # Any internal build outputs
    for classdir in [output for output in project.outputs if isinstance(output, Classdir)]:
        classpath.append(classdir.path)
    
    # Build outputs from dependencies
    for relationship in project.dependencies:
        dependency = relationship.dependency
        
        # keep track of visited outputs so we don't
        # process them twice
        visited_outputs = []
        
        for info in relationship.dependencyInfo:
            if runtimeonly and not info.runtime:
                continue

            filter_by_id = info.specific_output_ids and len(info.specific_output_ids) > 0
        
            for output in [o for o in dependency.outputs if o not in visited_outputs]:
                visited_outputs.append(o)
                
                # exclude unspecified outputs
                if filter_by_id and not output.id in info.specific_output_ids:
                        continue

                # calculate path to this output
                path = None
                if isinstance(output, Classdir):
                    path = output.path
                if isinstance(output, Jar):
                    path = get_jar_path(workdir,output)
                
                # actually add the path
                if output.add_to_bootclass_path:
                    bootclasspath.append(path)
                else:
                    classpath.append(path)
                    
                # now the fun begins. If we're doing inheritance, we're
                # going to recurse. If we're not doing "jars" or "outputs"
                # inheritance, we're going to do it once. Otherwise, we'll
                # keep doing it until we're no longer doing "jars"
                # inheritance. Sheesh!
                # Oh, and finally, there's another special case for inheriting
                # only the "runtime" dependencies.
                if recurse:
                    if info.inherit == DEPENDENCY_INHERIT_ALL or info.inherit == DEPENDENCY_INHERIT_HARD:
                        (inheritedclasspath, inheritedbootclasspath) = get_classpath(workdir, dependency, recurse=False)
                        classpath.extend(inheritedclasspath)
                        bootclasspath.extend(inheritedbootclasspath)
                    
                    if info.inherit == DEPENDENCY_INHERIT_JARS:
                        (inheritedclasspath, inheritedbootclasspath) = get_classpath(workdir, dependency, recurse=True)
                        classpath.extend(inheritedclasspath)
                        bootclasspath.extend(inheritedbootclasspath)
                    
                    if info.inherit == DEPENDENCY_INHERIT_RUNTIME:
                        (inheritedclasspath, inheritedbootclasspath) = get_classpath(workdir, dependency, recurse=False, runtimeonly=True)
                        classpath.extend(inheritedclasspath)
                        bootclasspath.extend(inheritedbootclasspath)
                        
    
    return (classpath, bootclasspath)