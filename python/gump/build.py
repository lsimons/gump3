#!/usr/bin/python
"""
  This is the commandline entrypoint into gump.

  It at the moment basically
  calls gump.load() to get the workspace, then dumps
  information about what it should be doing to stdout.

  The main thing to do here is to clone dumpDeps to create a
  build() method which executes the appropriate script
  (probably only ant at the moment; would be nice to have
  support for maven) for each of the dependencies.
"""

import os.path
import os
import sys
import logging

from gump import load, buildSequence
from gump.conf import dir, default, handleArgv
from gump.model import Workspace, Module, Project

###############################################################################
# Initialize
###############################################################################

# base gump logger
log = logging.getLogger(__name__)

###############################################################################
# Functions
###############################################################################

def run(workspace, projectname):
  """dump all dependencies to build a project to the output"""

  # if the project is not there, exit with error
  if projectname not in Project.list:
    print
    print "The project '"+projectname+"' is not defined in the workspace."
    sys.exit(1)

  # get the project object given the project name
  project=Project.list[projectname]

  log.info('PROJECTS TO BUILD:')

  # resolve the build sequence of the specified project
  try:
    todo=[]
    project.addToTodoList(todo)
    todo.sort()
    build_sequence = buildSequence(todo)
    for tproject in build_sequence:
      log.info('   ' + tproject.name)
  except:
    message=str(sys.exc_type)
    if sys.exc_value: message+= ": " + str(sys.exc_value)
    log.error(message)
    return 1 # exit status

  # synchronize
  syncWorkDir( workspace, build_sequence )

  # build
  return buildProjects( workspace, projectname, project, build_sequence )


def syncWorkDir( workspace, build_sequence ):
  """copy the raw project materials from source to work dir (hopefully using rsync, cp is fallback)"""

  log.info('')
  log.info('--- Synchronizing work directories with sources')
  log.info('')

  for project in build_sequence:
    module=Module.list[project.module];
    sourcedir = os.path.normpath(os.path.join(workspace.cvsdir,module.name)) # todo allow override
    destdir = os.path.normpath(os.path.join(workspace.basedir,module.name))

    if not workspace.sync:
      workspace.sync = default.syncCommand
    execString = workspace.sync + ' ' + sourcedir + ' ' + destdir

    log.debug('Synchronizing: ' + execString)
    # TODO: don't just brag about it!
    #exec( execString )

  log.debug('')
  log.info('-----------------------------------------------')
  log.debug('')


def buildProjects( workspace, projectname, project, build_sequence ):
  """actually perform the build of the specified project and its deps"""

  log.info('')
  log.info('--- Building: ' + projectname + ' and dependencies')
  log.info('')

  # to restore classpath when done
  try:
    oldPath = os.environ['CLASSPATH']
  except:
    oldPath = ''

  # build all projects this project depends upon, then the project itself
  for project in build_sequence:

    # get the module object given the module name,
    # which is gotten from the project
    module=Module.list[project.module]

    log.info(' ------ Building: '+ module.name + ':' + project.name)

    # get the ant element
    ant=project.ant

    if ant:
      target=''

      # debug info
      if ant.target:
        log.info('   Using ant for build...TARGET: ' + ant.target)
        target = ant.target
      else:
        log.info('   Using ant for build...TARGET: [default]')

    # get the script element
    script=project.script

    if script:
      log.info('   Using a script to build...script: ' + script.name)

    if not (script or ant):
      log.info('   Not building this project! (no <ant/> or <script/> specified)')

    buildbasedir = os.path.normpath(os.path.join(module.srcdir,ant.basedir or ''))
    log.debug('   SRCDIR:' + buildbasedir)

    classpath=[]
    for depend in project.depend+project.option:
      for jar in depend.jars():
        classpath.append(jar.path)
    classpath=os.pathsep.join(classpath)
    log.debug('   CLASSPATH:' + classpath)

    properties=''
    for property in workspace.property:#+ant.property:
      properties = properties + '-D%s=%s' % (property.name,property.value)
    log.debug('   PROPERTIES:' + properties)

    log.debug(' ------------------------------------------------------- ')

    if ant:
      execString=default.antCommand + ' ' + target
      log.debug('Building using ant!')
      log.debug('    cd' +  buildbasedir)
      log.debug('    export CLASSPATH=' + classpath)
      log.debug('   ' + execString)

      # TODO: don't just brag about it!
      #os.environ['CLASSPATH']=classpath
      #os.chdir( buildbasedir )
      #exec( execString )

    if script:
      scriptfile = os.path.normpath(os.path.join(module.srcdir, script.name))
      log.debug('Building using a script!')
      log.debug('    cd', buildbasedir)
      log.debug('    export CLASSPATH=' + classpath)
      log.debug('   ', scriptfile)

      # TODO: don't just brag about it!
      #os.environ['CLASSPATH']=classpath
      #os.chdir( buildbasedir )
      #exec( scriptfile )

    log.debug('')
    log.info(' ------------------------------------------------------- ')
    log.debug('')

  os.environ['CLASSPATH'] = oldPath

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
  # run gump
  result = run(workspace, ps);

  # bye!
  sys.exit(result)
