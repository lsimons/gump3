#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/Attic/logic.py,v 1.27 2003/10/16 21:35:00 ajack Exp $
# $Revision: 1.27 $
# $Date: 2003/10/16 21:35:00 $
#
# ====================================================================
#
# The Apache Software License, Version 1.1
#
# Copyright (c) 2003 The Apache Software Foundation.  All rights
# reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. The end-user documentation included with the redistribution, if
#    any, must include the following acknowlegement:
#       "This product includes software developed by the
#        Apache Software Foundation (http://www.apache.org/)."
#    Alternately, this acknowlegement may appear in the software itself,
#    if and wherever such third-party acknowlegements normally appear.
#
# 4. The names "The Jakarta Project", "Alexandria", and "Apache Software
#    Foundation" must not be used to endorse or promote products derived
#    from this software without prior written permission. For written
#    permission, please contact apache@apache.org.
#
# 5. Products derived from this software may not be called "Apache"
#    nor may "Apache" appear in their names without prior written
#    permission of the Apache Group.
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
# ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# ====================================================================
#
# This software consists of voluntary contributions made by many
# individuals on behalf of the Apache Software Foundation.  For more
# information on the Apache Software Foundation, please see
# <http://www.apache.org/>.


"""
  This is the logic gump applies to the model in order to perform tasks.
"""

import os.path
import os
import sys
import logging
import types
from string import split
from fnmatch import fnmatch

from gump import log, load
from gump.launcher import Cmd, Parameters
from gump.conf import dir, default, handleArgv
from gump.model import Workspace, Module, Project
from gump.context import *
from gump.tools import listDirectoryAsWork

###############################################################################
# Initialize
###############################################################################


###############################################################################
# Classes
###############################################################################


# :TODO: Migrate more code to this
class GumpSet:
    """ Contains the primary works sets -- to save recalculating and
    passing so many individual things around """
    def __init__(self, pexpr='*', projects=None, sequence=None, modules=None ):
        self.projectexpression=pexpr
        
        #
        # Requested Projects
        #
        if not projects:
            self.projects=getProjectsForProjectExpression(pexpr)
        else:
            self.projects = projects
        
        #
        # Project Build Sequence
        #
        if not sequence:
            self.sequence=getBuildSequenceForProjects(self.projects)
        else:
            self.sequence=sequence
            
        #
        # Module List
        #
        if not modules:
            self.modules=getModulesForProjectList(self.sequence)
        else:
            self.modules=modules
            
    
###############################################################################
# Functions
###############################################################################
def isAllProjects(pexpr):
    return pexpr=='all' or pexpr=='*'
    
def isFullGumpSet(set):
    return isAllProjects(set.projectexpression)
        
def getGumpSetForProjectExpression(expr):
  return GumpSet(expr)

def getModuleNamesForProjectExpression(expr):
  return getModuleNamesForProjectList(getProjectsForProjectExpression(expr))
  
def getModuleNamesForProjectList(projects):
  modules=[]
  for module in getModulesForProjectList(projects):
    if not module.name in modules: modules.append(module.name)
  modules.sort()
  return modules

def getModulesForProjectExpression(expr):
  return getModulesForProjectList(getProjectsForProjectExpression(expr))
  
def getModulesForProjectList(projects):
  modules=[]
  for project in projects:
    if Module.list.has_key(project.module):
        module=Module.list[project.module]
        if not module in modules: modules.append(module)
  modules.sort()
  return modules
  
def getProjectsForProjectExpression(expr):
  """ Return a list of projects matching this expression"""
  projects=[]
  for project in Project.list.values():
    try:
      # does this name match
      for pattern in expr.split(','):
        if pattern=="all": pattern='*'
        if fnmatch(project.name,pattern): break
      else:
        # no match, advance to the next name
        continue
      projects.append(project)
    except:
      pass
  projects.sort()
  return projects
  
def getPackagedProjectContexts(context):
  """ Return a list of projects installed as packages """
  projects=[]
  for project in Project.list.values():
    if isPackaged(project):
        projects.append(context.getProjectContextForProject(project))
  return projects
        
        
#
# We have a potential clash betweeb the <project package attribute and
# the <project <package element. The former indicates a packages install
# the latter the (Java) package name for the project contents. As such
# we test the attribute for type.
#
def isPackaged(project):
    return type(project.package) in types.StringTypes
    
def getBuildSequenceForProjects(projects):
    """Determine the build sequence for a given list of projects."""
    todo=[]
    result=[]
    for project in projects:
      project.addToTodoList(todo)
      while todo:
        # one by one, remove the first ready project and append it to the result
        for project in todo:
          if project.isReady(todo):
            todo.remove(project)
            if project.ant or project.script: 
                if not project in result:
                    result.append(project)
            break
        else:
          # we have a circular dependency, remove all innocent victims
            while todo:
                for project in todo:
                  if not project.isPrereq(todo):
                    todo.remove(project)
                    break
            else:
              loop=", ".join([project.name for project in todo])
              raise "circular dependency loop: " + str(loop)
              
    return result

def getBuildCommand(workspace,module,project,context):

    # get the ant element (if it exests)
    ant=project.ant

    # get the script element (if it exists)
    script=project.script

    if not (script or ant):
      log.info('   Not building ' + project.name + ' (no <ant/> or <script/> specified)')
      return None

    if script and script.name:
        return getScriptCommand(workspace,module,project,script,context)
    else:
        return getAntCommand(workspace,module,project,ant,context)
        
        
#
# Build an ANT command for this project
#        
def getAntCommand(workspace,module,project,ant,context):
    
    # The ant target (or none == ant default target)
    target= ant.target or ''
    
    # The ant build file (or none == build.xml)
    buildfile = ant.buildfile or ''
    
    #
    # Where to run this:
    #
    #	The module src directory (if exists) or Gump base
    #	plus:
    #	The specifier for ANT, or nothing.
    #
    basedir = os.path.normpath(os.path.join(module.srcdir or dir.base,ant.basedir or ''))
    
    #
    # Build a classpath (based upon dependencies)
    #
    classpath=getClasspath(project,workspace,context)
    
    #
    # List properties
    #
    properties=getAntProperties(workspace,ant)
   
    #
    # Run java on apache Ant...
    #
    cmd=Cmd(context.javaCommand,'build_'+module.name+'_'+project.name,\
            basedir,{'CLASSPATH':classpath})
    cmd.addParameter('org.apache.tools.ant.Main')  
    
    #
    # Allow ant-level debugging...
    #
    if context.debug:
        cmd.addParameter('-debug')  
        
    #
    #	This sets the *defaults*, a workspace could override them.
    #
    cmd.addPrefixedParameter('-D','build.sysclasspath','only','=')
    cmd.addPrefixedParameter('-D','java.awt.headless','true','=')
    
    # These are module level plus project level
    cmd.addNamedParameters(properties)
    
    # Pass the buildfile
    if buildfile: cmd.addParameter('-f',buildfile)
    
    # End with the target...
    if target: cmd.addParameter(target)
    
    return cmd

def getScriptCommand(workspace,module,project,script,context):
    basedir=os.path.normpath(os.path.join(module.srcdir or dir.base,script.basedir or ''))

    # Add .sh  or .bat as appropriate to platform
    scriptfullname=script.name
    if not os.name == 'dos' and not os.name == 'nt':
        scriptfullname += '.sh'
    else:
        scriptfullname += '.bat'
        
    scriptfile=os.path.normpath(os.path.join(basedir, scriptfullname))
    classpath=getClasspath(project,workspace,context)

    return Cmd(scriptfile,'buildscript_'+module.name+'_'+project.name,\
            basedir,{'CLASSPATH':classpath})

#
# An annotated path has a path entry, plus the context
# of the contributor (i.e. project of Gump.)
#
class AnnotatedPath:
    """Contains a Path plus optional 'contributor' """
    def __init__(self,path,context=None):
        self.path=path
        self.context=context
        
    def __repr__(self):
        return self.path
        
    def __str__(self):
        return self.path
        
    def __eq__(self,other):
        return self.path == other.path and self.context == other.context
                
    def __cmp__(self,other):
        cmp = self.path < other.path
        if not cmp: cmp = self.context < other.context
        return cmp
        
#
# Return a list of the outputs this project generates
#    
def getOutputsList(project, pctxt): 
    outputs=[]
    for i in range(0,len(project.jar)):
        # :TODO: Hack to avoid a crash, don't know why it is needed...
        if project.jar[i].path:
            jar=os.path.normpath(project.jar[i].path)
            outputs.append(AnnotatedPath(jar,pctxt))        
            
    return outputs
                 
#
# Does this project generate outputs (currently JARs)
#                  
def hasOutputs(project,pctxt):
    return (len(getOutputsList(project,pctxt)) > 0)


#
# Maybe this is dodgy (it is inefficient) but we need some
# way to get the sun tools for a javac compiler for ant and
# I don't know a more portable way.
#
# When we get closer to done perhaps strip out the tools only, 
# and not allow the users classpath to pollute ours...
#
def getSystemClasspathList():
    try:
        syscp=os.environ['CLASSPATH']
    except:
        syscp=''
    return split(syscp,os.pathsep)

# :TODO: Runtime?
#
# BOOTCLASSPATH?
def getClasspathList(project,workspace,context):
  """Get a TOTAL classpath for a project (including it's dependencies)"""
  
  # Start with the system classpath (later remove this)
  classpath=getSystemClasspathList()

  # Context for this project
  pctxt=context.getProjectContextForProject(project)

  # Add this project's work directories
  srcdir=Module.list[project.module].srcdir
  for work in project.work:
      path=None
      if work.nested:
          path=os.path.normpath(os.path.join(srcdir,work.nested))
      elif work.parent:
          path=os.path.normpath(os.path.join(workspace.basedir,work.parent))
      else:
          log.error("<work element without nested or parent attributes on " \
              + project.name + " in " + project.module)
    
      if path:
          classpath.append(AnnotatedPath(path,pctxt))

  # Append dependent projects (including optional)
  visited=[]
  
  # Does it have any depends?
  if project.depend:
    # For each
    for depend in project.depend:
        classpath += getDependOutputList(depend,context,visited)  
              
  # Same as above, but for optional...
  if project.option:    
    for option in project.option:
        classpath += getDependOutputList(option,context,visited)
      
  return classpath

#
# :TODO: Runtime Dependncy?
#
def getDependOutputList(depend,context,visited):      
  """Get a classpath of outputs for a project (including it's dependencies)"""            
   
  # Don't loop...
  if depend in visited:
      return []
  visited.append(depend)
          
  #
  # Check we can get the project...
  #
  projectname=depend.project
  if not Project.list.has_key(projectname):
      if projectname:
          log.error("Unknown project (in acquiring classpath) " + projectname )
      return []
      
  # 
  classpath=[]

  #
  # Context for this project...
  #
  project=Project.list[projectname]
  pctxt=context.getProjectContextForProject(project)
  
  #
  # Are we asking for runtime dependencies only?
  #
  runtime=depend.runtime
  
  #
  # Append JARS for this project
  #
  # Note: This checks "id" in "<depend ids="
  for jar in depend.jars():
    classpath.append(AnnotatedPath(jar.path,pctxt)) 

  #
  # inherit='ALL' or 'HARD'
  # or inherit the runtime ones...
  #
  deepCopy=determineDeepCopy(depend)

  if deepCopy or runtime:      
      # Append sub-projects outputs
      if project.depend:
          for subdepend in project.depend:        
            if not runtime or subdepend.inherit=="runtime":      
                classpath += getDependOutputList(subdepend,context,visited)
  
      # Append optional sub-project's output (that may not exist)
      if project.option:
          for suboption in project.option:
            if not runtime or suboption.inherit=="runtime":      
                classpath += getDependOutputList(suboption,context,visited)

  return classpath
  
def determineDeepCopy(depend):
    """Determine if we ought deepCopy to inherit"""
    deep=0
    inherit=depend.inherit
    # :TODO: The 'jars' is a temporary hack.
    if inherit == 'all' or inherit=='hard' or inherit=='jars':
        deep=1
    return deep
    
# BOOTCLASSPATH?
def getClasspath(project,workspace,context):
  return os.pathsep.join(getSimpleClasspathList(getClasspathList(project,workspace,context)))

def getSimpleClasspathList(cp):
    """ Return simple string list """
    classpath=[]
    for p  in cp:
        if isinstance(p,AnnotatedPath):
            classpath.append(p.path)
        else:
            classpath.append(p)
    return classpath
            
  
def getAntProperties(workspace,ant):
  """Get properties for a project"""
  properties=Parameters()
  for property in workspace.property+ant.property:
    properties.addPrefixedNamedParameter('-D',property.name,property.value,'=')
  return properties

def preprocessContext(workspace,context=GumpContext()):

    # Check the workspace
    if not workspace.version >= workspace.ws_version:
        message='Workspace version ['+workspace.version+'] below expected [' + setting.ws_version + ']'
        context.addWarning(message)
        log.warning(message)   
        
    #
    # Check each project...
    #
    for project in Project.list.values():
                        
        projectOk=1
        pctxt = context.getProjectContextForProject(project)
        
        # If so far so good, check packages
        if isPackaged(project):
            
            pctxt.addInfo("This is a packaged project, location: " + str(project.home))
                        
            #
            # Check the package was installed correctly...
            #
            outputsOk=1
            for i in range(0,len(project.jar)):
                jarpath=project.jar[i].path
                if jarpath:
                    if not os.path.exists(jarpath):
                        pctxt.propagateErrorState(STATUS_FAILED,REASON_PACKAGE_BAD)
                        outputsOk=0
                        projectOk=0
                        pctxt.addError("Missing Packaged Jar: " + str(jarpath))
                        log.error("Missing Jar [" + str(jarpath) + "] on *packaged* [" + pctxt.name + "]")
    
            if outputsOk:
                pctxt.status=STATUS_COMPLETE
                pctxt.reason=REASON_PACKAGE
                
            #
            # List them, why not...
            #
            listDirectoryAsWork(pctxt,project.home,'list_package_'+project.name)                
        else:         
            # Check Dependencies Exists:
            for depend in project.depend:
                if not Project.list.has_key(depend.project):
                    pctxt.propagateErrorState(STATUS_FAILED,REASON_CONFIG_FAILED)
                    projectOk=0
                    pctxt.addError("Bad Dependency. Project: " + depend.project + " unknown to *this* workspace")
                    log.error("Missing Dependency [" + depend.project + "] on [" + pctxt.name + "]")
        
            # Check Dependencies Exists:
            for option in project.option:
                if not Project.list.has_key(option.project):
                    pctxt.addWarning("Bad Dependency. Project: " + option.project + " unknown to *this* workspace")
                    log.warn("Missing Dependency [" + option.project + "] on [" + pctxt.name + "]")        
    
    #
    # Check each module...
    #
    for module in Module.list.values():
        moduleOk=1
        mctxt = context.getModuleContextForModule(module)
        
        # A module which contains only packaged projects might as
        # well be considered complete, no need to update from CVS
        # since we won't be building.
        # :TODO: Ought we hack this as *any* not all???
        packageCount=0
        allPackaged=1
        for project in module.project:
            if not isPackaged(project):
                allPackaged=0  
            else:
                mctxt.addInfo('Packaged Project: ' + project.name)
                packageCount+=1
                
        # Must be one to be all
        if not packageCount: allPackaged=0
    
        # Give this module a second try, and since some are packaged
        # check if the others have no outputs, then call them good.
        if packageCount and not allPackaged:
            allPackaged=1
            for project in module.project:
                if not isPackaged(project):
                    pctxt=context.getProjectContextForProject(project)    
                    if not hasOutputs(project,pctxt):
                        # 
                        # Honorary package (allow folks to only mark the main
                        # project in a module as a package, and those that do
                        # not product significant outputs (e.g. test projects)
                        # will be asssumed to be packages.
                        # 
                        pctxt.status=STATUS_COMPLETE
                        pctxt.reason=REASON_PACKAGE
                        packageCount+=1
                    else:    
                        allPackaged=0  
                        if packageCount:
                            mctxt.addWarning("Incomplete \'Packaged\' Module. Project: " + \
                                    project.name + " is not packaged")  
               
        # If packages module, accept it... 
        if allPackaged:
            mctxt.status=STATUS_COMPLETE
            mctxt.reason=REASON_PACKAGE
            mctxt.addInfo("\'Packaged\' Module. (Packaged projects: " + \
                                    str(packageCount) + '.)')   
                        
# static void main()
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)

  args = handleArgv(sys.argv)
  ws=args[0]
  ps=args[1]
  
  context=GumpContext()
  
  # get parsed workspace definition
  workspace=load(ws, context)
  
  projects=getPackagedProjectContexts(context)
  print "Packaged Projects : " + str(len(projects))
  for p in projects: print "Packaged Project " + str(p.name)
    
  printSeparator()
  
  projects=getProjectsForProjectExpression(ps)
  print "Resolved Projects : " + str(len(projects))
  for p in projects: print "Project " + str(p.name)
  modules=getModulesForProjectExpression(ps)
  print "Resolved Modules : " + str(len(modules))
  for m in modules: print "Module " + str(m.name) + " : " + str(m.cvs.repository)
  
  projects=getBuildSequenceForProjects(getProjectsForProjectExpression(ps))
  print "Resolved Project Tree : " + str(len(projects))
  for p in projects: print "Project " + str(p.name)
  modules=getModulesForProjectList(projects)
  print "Resolved Module Tree : " + str(len(modules))
  for m in modules: print "Module " + str(m.name) + " : " + str(m.cvs.repository)
  
  printSeparator()
  
  preprocessContext(workspace, context)
  
  from gump.document import documentText
  
  documentText(workspace, context, ps)

