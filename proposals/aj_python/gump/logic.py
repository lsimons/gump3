#!/usr/bin/python
"""
  This is the logic gump applies to the model in order to perform tasks.
"""

import os.path
import os
import sys
import logging
from string import split
from fnmatch import fnmatch

from gump import log, load
from gump.launcher import Cmd, Parameters
from gump.conf import dir, default, handleArgv
from gump.model import Workspace, Module, Project

###############################################################################
# Initialize
###############################################################################


###############################################################################
# Functions
###############################################################################
def getModulesForProjectExpression(expr):
  return getModulesForPorjectList(getProjectsForProjectExpression(expr))
  
def getModulesForProjectList(projects):
  modules=[]
  for project in projects:
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
  
def getPackagedProjects(expr):
  """ Return a list of projects installed as packages """
  projects=[]
  for project in Project.list.values():
    if project.package:
        projects.append(project)
    
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
            if project.ant or project.script: result.append(project)
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

def getBuildCommand(workspace,module,project):

    # get the ant element (if it exests)
    ant=project.ant

    # get the script element (if it exists)
    script=project.script

    if not (script or ant):
      log.info('   Not building this project! (no <ant/> or <script/> specified)')
      return None

    if script and script.name:
        return getScriptCommand(workspace,module,project,script)
    else:
        return getAntCommand(workspace,module,project,ant)
        
def getAntCommand(workspace,module,project,ant):
    target= ant.target or ''

    basedir = os.path.normpath(os.path.join(module.srcdir or dir.base,ant.basedir or ''))
    classpath=getClasspath(project)
    properties=getAntProperties(workspace,ant)
   
    cmd=Cmd('java','ant_'+module.name+'_'+project.name,basedir,{'CLASSPATH':classpath})
    cmd.addParameter('org.apache.tools.ant.Main')    
    cmd.addPrefixedParameter('-D','build.sysclasspath','only','=')
    cmd.addNamedParameters(properties)
    # build file?
    if target: cmd.addParameter(target)
    
    return cmd

def getScriptCommand(workspace,module,project,script):
    basedir=os.path.normpath(os.path.join(module.srcdir or dir.base,script.basedir or ''))

    # Add .sh  or .bat as appropriate to platform
    scriptfullname=script.name
    if not os.name == "nt":
        scriptfullname += '.sh'
    else:
        scriptfullname += '.bat'
    scriptfile=os.path.normpath(os.path.join(basedir, scriptfullname))
    classpath=getClasspath(project)

    return Cmd(scriptfile,'script_'+module.name+'_'+project.name,basedir,{'CLASSPATH':classpath})
    

#
# Maybe this is dodgy (it is inefficient) but we need some
# way to get the sun tools for a javac compiler for ant...
#
def getSystemClasspathList():
    try:
        syscp=os.environ['CLASSPATH']
    except:
        syscp=''
    return split(syscp,os.pathsep)

# :TODO:
# Ought convert to project context to take into consideration
# those dependencies which are failed
#
# BOOTCLASSPATH?
def getClasspathList(project):
  """Get classpath for a project (including it's dependencies)"""
  classpath=getSystemClasspathList()
  
  # start with the work directories
  srcdir=Module.list[project.module].srcdir
  for work in project.work:
      classpath.append(os.path.normpath(os.path.join(srcdir,work.nested)))

  for depend in project.depend:
    for jar in depend.jars():
      classpath.append(jar.path) 
  
  # :TODO: Check Exist...
  for option in project.option:
    for jar in option.jars():
      classpath.append(jar.path)
      
  return classpath
  
# BOOTCLASSPATH?
def getClasspath(project):
  return os.pathsep.join(getClasspathList(project))

  
def getAntProperties(workspace,ant):
  """Get properties for a project"""
  properties=Parameters()
  for property in workspace.property:#+ant.property:
    properties.addPrefixedNamedParameter('-D',property.name,property.value,'=')
  return properties
  
# static void main()
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)

  args = handleArgv(sys.argv)
  ws=args[0]
  ps=args[1]
  
  # get parsed workspace definition
  workspace=load(ws)
  
  projects=getProjectsForProjectExpression(ps)
  print "Resolved Projects : " + str(len(projects))
  for p in projects: print "Project " + str(p.name)
  modules=getModulesForProjectExpression(ps)
  print "Resolved Modules : " + str(len(modules))
  for m in modules: print "Module " + str(m.name) + " : " + str(m.cvs.repository)

