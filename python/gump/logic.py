#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/Attic/logic.py,v 1.41 2003/10/24 18:31:35 ajack Exp $
# $Revision: 1.41 $
# $Date: 2003/10/24 18:31:35 $
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

def hasBuildCommand(project):
    hasBuild=0
    # I.e has an <ant or <script element
    if project.ant or project.script: hasBuild=1    
    return hasBuild


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
    
    # Optional 'verbose' or 'debug'
    verbose=ant.verbose
    debug=ant.debug
    
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
    (classpath,bootclasspath)=getClasspaths(project,workspace,context)
    
    #
    # Get properties
    #
    properties=getAntProperties(workspace,ant)
   
    #
    # Get properties
    #
    jvmargs=getJVMArgs(workspace,ant)
   
    #
    # Run java on apache Ant...
    #
    cmd=Cmd(context.javaCommand,'build_'+module.name+'_'+project.name,\
            basedir,{'CLASSPATH':classpath})
            
    # Set this as a system property. Setting it here helps JDK1.4+
    # AWT implementations cope w/o an X11 server running (e.g. on
    # Linux)
    #    
    cmd.addPrefixedParameter('-D','java.awt.headless','true','=')
    
    #
    # Add BOOTCLASSPATH
    #
    if bootclasspath:
        cmd.addPrefixedParameter('-X','bootclasspath/p',bootclasspath,':')
            
    if jvmargs:
        cmd.addParameters(jvmargs)
            
    cmd.addParameter('org.apache.tools.ant.Main')  
    
    #
    # Allow ant-level debugging...
    #
    if context.debug or debug:
        cmd.addParameter('-debug')  
    if context.verbose or verbose:
        cmd.addParameter('-verbose')  
        
    #
    #	This sets the *defaults*, a workspace could override them.
    #
    cmd.addPrefixedParameter('-D','build.sysclasspath','only','=')
    
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
      
    # Optional 'verbose' or 'debug'
    verbose=script.verbose
    debug=script.debug
       
    scriptfile=os.path.normpath(os.path.join(basedir, scriptfullname))
    (classpath,bootclasspath)=getClasspaths(project,workspace,context)

    cmd=Cmd(scriptfile,'buildscript_'+module.name+'_'+project.name,\
            basedir,{'CLASSPATH':classpath})
    
            
    # Set this as a system property. Setting it here helps JDK1.4+
    # AWT implementations cope w/o an X11 server running (e.g. on
    # Linux)
    #    
    cmd.addPrefixedParameter('-D','java.awt.headless','true','=')
    
    #
    # Add BOOTCLASSPATH
    #
    if bootclasspath:
        cmd.addPrefixedParameter('-X','bootclasspath/p',bootclasspath,':')
                    
    #
    # Allow ant-level debugging...
    #
    if context.debug or debug:
        cmd.addParameter('-debug')  
    if context.verbose or verbose:
        cmd.addParameter('-verbose')  
        
    return cmd

#
# An annotated path has a path entry, plus the context
# of the contributor (i.e. project of Gump.)
#
class AnnotatedPath:
    """Contains a Path plus optional 'contributor' """
    def __init__(self,path,context=None,pcontext=None,note=None):
        self.path=path
        self.context=context
        self.pcontext=pcontext
        self.note=note
        
    def __repr__(self):
        return self.path
        
    def __str__(self):
        return self.path
        
    # Equal if same string
    def __eq__(self,other):
        if not isinstance(other,AnnotatedPath):
            otherPath = other
        else:
            otherPath = other.path             
        return self.path == otherPath
                
    # Equal if same string
    def __cmp__(self,other):
        if not isinstance(other,AnnotatedPath):
            otherPath = other
        else:
            otherPath = other.path                         
        cmp = self.path < otherPath        
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
            outputs.append(AnnotatedPath(jar,pctxt,None,"Project output"))        
            
    return outputs
                 
#
# Does this project generate outputs (currently JARs)
#                  
def hasOutputs(project,pctxt):
    return (len(getOutputsList(project,pctxt)) > 0)
    
#
# Return a (classpath, bootclaspath) tuple for this project
#
def getClasspaths(project,workspace,context):
  #
  # Calculate classpath and bootclasspath
  #
  (classpath, bootclasspath) = getClasspathLists(project,workspace,context)
  
  #
  # Convert path and AnnotatedPath to simple paths.
  #
  (scp, sbcp) = (	getSimpleClasspathList(classpath), \
                      getSimpleClasspathList(bootclasspath) )

  #
  # Join using path separator, and return tuple
  #
  return (os.pathsep.join(scp),os.pathsep.join(sbcp) )

#
# Convert path and AnnotatedPath to simple paths.
# 
def getSimpleClasspathList(cp):
    """ Return simple string list """
    classpath=[]
    for p  in cp:
        if isinstance(p,AnnotatedPath):
            classpath.append(p.path)
        else:
            classpath.append(p)
    return classpath
            


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

#
# Return a tuple of (CLASSPATH, BOOTCLASSPATH) for a project
#
def getClasspathLists(project,workspace,context,debug=0):
  """Get a TOTAL classpath for a project (including it's dependencies)"""

  # Context for this project
  pctxt=context.getProjectContextForProject(project)

  #
  # Do this once only... storing it on the context. Not as nice as 
  # doing it OO (each project context stores it's own, but a step..)
  #
  if hasattr(pctxt,'resolvedClasspath') and \
      hasattr(pctxt,'resolvedBootclasspath') :
      if debug: print "Claspath/Bootclasspath previously resolved..."
      return ( pctxt.resolvedClasspath, pctxt.resolvedBootclasspath )
  
  # Start with the system classpath (later remove this)
  classpath=getSystemClasspathList()
  bootclasspath=[] # :TODO: Get from ?

  #
  # Add this project's work directories (these go into
  # CLASSPATH, never BOOTCLASSPATH)
  #
  srcdir=Module.list[project.module].srcdir
  for work in project.work:
      path=None
      if work.nested:
          path=os.path.abspath(os.path.join(srcdir,work.nested))
      elif work.parent:
          path=os.path.abspath(os.path.join(workspace.basedir,work.parent))
      else:
          log.error("<work element without nested or parent attributes on " \
              + project.name + " in " + project.module)

      if path:
          classpath.append(AnnotatedPath(path,pctxt,None,'Work Entity'))
          if debug: print "Work Entity:   " + path 

  # Append dependent projects (including optional)
  visited=[]
  
  # Does it have any depends? Process all of them...
  if project.depend:
    # For each
    for depend in project.depend:
        (subcp, subbcp) = getDependOutputList(pctxt,project,pctxt,depend,context,visited,0,debug)
        importClasspaths(pctxt,classpath,bootclasspath,subcp,subbcp)
        
  # Same as above, but for optional...
  if project.option:    
    for option in project.option:
        (subocp, subobcp) = getDependOutputList(pctxt,project,pctxt,option,context,visited,0,debug)
        importClasspaths(pctxt,classpath,bootclasspath,subocp,subobcp)   
  
  #
  # Store so we don't do this twice.
  #            
  pctxt.resolvedClasspath = classpath
  pctxt.resolvedBootclasspath = bootclasspath
  
  return (classpath, bootclasspath)

#
# Perform this 'dependency' (mandatory or optional)
#
# 1) Bring in the JARs (or those specified by id in depend ids)
# 2) Do NOT bring in the working entities (directories/jars)
# 3) Bring in the sub-depends (or optional) if inherit='all' or 'hard'
# 4) Bring in the runtime sub-depends if inherit='runtime'
# 5) Also: *** Bring in any depenencies that the dependency inherits ***
#
def getDependOutputList(beneficiary,parent,parentctxt,depend,context,visited,depth=0,debug=0):      
  """Get a classpath of outputs for a project (including it's dependencies)"""            
   
  # Don't loop...
  if depend in visited:  
      beneficiary.addInfo("Duplicated dependency [" + str(depend) + "]")          
      if debug:
        print str(depth) + ") Already Visited : " + str(depend)
        print str(depth) + ") Previously Visits  : "
        for v in visited:
          print str(depth) + ")  - " + str(v)
      return ([],[])
  visited.append(depend)
  if debug:
      print str(depth) + ") Perform : " + str(depend) + " in " + parent.name
          
  #
  # Check we can get the project...
  #
  projectname=depend.project
  if not Project.list.has_key(projectname):
      if projectname:
          beneficiary.addError("Unknown project (in acquiring classpath) [" + projectname \
                  + "] for [" + str(depend) + "]")
      return ([],[])
      
  # 
  #
  #
  classpath=[]
  bootclasspath=[]

  #
  # Context for this dependecy project...
  #
  project=Project.list[projectname]
  pctxt=context.getProjectContextForProject(project)
  
  # The dependency drivers...
  #
  # runtime (i.e. this is a runtime dependency)
  # inherit (i.e. inherit stuff from a dependency)
  #
  runtime=depend.runtime
  inherit=depend.inherit
  if depend.ids:
      ids=depend.ids.split(' ')
  else:
      ids=None
  
  #
  # Explain..
  #
  dependStr=''
  if inherit: 
      if dependStr: dependStr += ', '
      dependStr += 'Inherit:'+str(inherit)
  if runtime: 
      if dependStr: dependStr += ', '
      dependStr += 'Runtime'
      
  #
  # No need to show this, will show later
  #if ids: 
  #    if dependStr: dependStr += ', '
  #    dependStr += 'IDs [' + ', '.join(ids) + ']'
  
  #
  # Append JARS for this project
  #	(respect ids)
  #
  projectIds=[]
  for jar in project.jar:
      # Sote for double checking
      if jar.id: projectIds.append(jar.id)
      # If 'all' or in ids list:
      if (not ids) or (jar.id in ids):   
          if ids: dependStr += ' Id = ' + jar.id
          path=AnnotatedPath(jar.path,pctxt,parentctxt,dependStr) 
          
              # Add to CLASSPATH
          if not jar.type == 'boot':
              if not path in classpath:
                  if debug:   print str(depth) + ') Append JAR : ' + str(path)
                  classpath.append(path)
          else:
              # Add to BOOTCLASSPATH
              if not path in bootclasspath:
                  if debug:   print str(depth) + ') Append *BOOTCLASSPATH* JAR : ' + str(path)
                  bootclasspath.append(path)    

  #
  # Double check
  #
  if ids:
      for id in ids:
          if not id in projectIds:
              # :TODO: This will cause repeats of this message
              # for every dep who tries to use this
              # Gumpy really needs to be OO!!!!
              parentctxt.addWarning("Invalid ID [" + id \
                  + "] for dependency on [" + projectname + "]")

  # Append sub-projects outputs, if inherited
  if project.depend:
      for subdepend in project.depend:        
          #	If the dependency is set to 'all' (or 'hard') we inherit all dependencies
          # If the dependency is set to 'runtime' we inherit all runtime dependencies
          # If the dependent project inherited stuff, we inherit that...
          if    (inherit=='all' or inherit=='hard') \
             or (inherit=='runtime' and subdepend.runtime) \
             or (subdepend.inherit and not subdepend.inherit=='none'):      
              (subcp, subbcp) = getDependOutputList(beneficiary,project,pctxt,subdepend,context,visited,depth+1,debug)
              importClasspaths(beneficiary,classpath,bootclasspath,subcp,subbcp)   
          elif debug:
              print str(depth) + ') Skip : ' + str(subdepend) + ' in ' + project.name

  # Append sub-projects outputs, if inherited
  if project.option:
      for suboption in project.option:   
          # See similar loop above here for logic...
          if    (inherit=='all' or inherit=='hard') \
             or (inherit=='runtime' and suboption.runtime) \
             or (suboption.inherit and not suboption.inherit=='none'):      
              (subocp, subobcp) = getDependOutputList(beneficiary,project,pctxt,suboption,context,visited,depth+1,debug)
              importClasspaths(beneficiary,classpath,bootclasspath,subocp,subobcp)   
          elif debug:
              print str(depth) + ') Skip optional : ' + str(suboption) + ' in ' + project.name

  return (classpath, bootclasspath)
    

#
# Import cp and bcp into classpath and bootclasspath,
# but do not accept duplicates. Report duplicates
#
def importClasspaths(beneficiary,classpath,bootclasspath,cp,bcp):

    # Import the CLASSPATH stuff
    for path in cp:
        if not path in classpath:
            classpath.append(path)
        else:
            beneficiary.addInfo("Duplicated classpath JAR [" + str(path) + "]")                    
              
    # Import the BOOTCLASSPATH stuff
    for bpath in bcp:
        if not bpath in bootclasspath:
            bootclasspath.append(bpath)       
        else:
            beneficiary.addInfo("Duplicated bootclasspath JAR [" + str(bpath) + "]")                        
                
def getJVMArgs(workspace,ant):
  """Get JVM arguments for a project"""
  args=Parameters()
  for jvmarg in ant.jvmarg:
    if jvmarg.value:
        args.addParameter(jvmarg.value)
    else:
        log.error('Bogus JVM Argument')
  return args
  
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
  
  #projects=getPackagedProjectContexts(context)
  #print "Packaged Projects : " + str(len(projects))
  #for p in projects: print "Packaged Project " + str(p.name)
    
  printSeparator()
  print "Project Expression : " + ps
  
  projects=getProjectsForProjectExpression(ps)
  #print "Resolved Projects : " + str(len(projects))
  #for p in projects: print "Project " + str(p.name)
  #modules=getModulesForProjectExpression(ps)
  #print "Resolved Modules : " + str(len(modules))
  #for m in modules: print "Module " + str(m.name) + " : " + str(m.cvs.repository)
  
  #projects=getBuildSequenceForProjects(getProjectsForProjectExpression(ps))
  #print "Resolved Project Tree : " + str(len(projects))
  #for p in projects: print "Project " + str(p.name)
  #modules=getModulesForProjectList(projects)
  #print "Resolved Module Tree : " + str(len(modules))
  #for m in modules: print "Module " + str(m.name) + " : " + str(m.cvs.repository)
  
  printSeparator()
  
  # preprocessContext(workspace, context)
  
  # from gump.document import documentText
  # documentText(workspace, context, ps)
  
  for project in projects:
      (cp,bcp)=getClasspathLists(project,workspace,context,1)
      print "Project : " + project.name 
      for p in cp:
          if isinstance(p,AnnotatedPath):
              pp='Unnamed'
              ppp='Unnamed'
              if p.context: pp=p.context.name
              if p.pcontext: ppp=p.pcontext.name
              print " - " + str(p) + " : " + pp + " : " + ppp + " : " + str(p.note)
          else:
              print " + " + str(p)
              
      for p in bcp:
          if isinstance(p,AnnotatedPath):
              pp='Unnamed'
              ppp='Unnamed'
              if p.context: pp=p.context.name
              if p.pcontext: ppp=p.pcontext.name
              print " - " + str(p) + " : " + pp + " : " + ppp + " : " + str(p.note) + " --- BOOT"
          else:
              print " + " + str(p) + " --- BOOT"
              
      cmd=getBuildCommand(workspace,Module.list[project.module],project,context)
      if cmd:
          cmd.dump()