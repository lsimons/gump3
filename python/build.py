#!/usr/bin/python
"""
        This is the entrypoint into gump. It at the moment basically
        calls gumpcore.load() to get the workspace, then dumps
        information about what it should be doing to stdout.

        The main thing to do here is to clone dumpDeps to create a
        build() method which executes the appropriate script
        (probably only ant at the moment; would be nice to have
        support for maven) for each of the dependencies.        
"""


import os.path,os,sys
from gumpcore import *
from gumpconf import *

# dump all dependencies to build a project to the output
def dumpDeps(workspace, projectname):

  # get the project object given the project name
  project=Project.list[projectname]

  print 'PROJECTS TO BUILD:'

  # resolve the build sequence of the specified project
  build_sequence = dependencies(projectname, project.depend)

  # synchronize
  syncWorkDir( workspace, build_sequence )

  # build
  buildProjects( workspace, projectname, project, build_sequence )  
   

def syncWorkDir( workspace, build_sequence ):
  print
  print ' ----- Synchronizing work directories with sources-----'
  print

  # copy the raw project materials from source to work dir (hopefully using rsync, cp is fallback)
  for project in build_sequence:
    module=Module.list[project.module];
    sourcedir = os.path.normpath(os.path.join(workspace.cvsdir,module.name)) # todo allow override
    destdir = os.path.normpath(os.path.join(workspace.basedir,module.name))

    if not workspace.sync:
      workspace.sync = default.syncCommand
    execString = workspace.sync + ' ' + sourcedir + ' ' + destdir

    #if default.debug:
    print 'Synchronizing:', execString
    # TODO: don't just brag about it!
    #exec( execString )

def buildProjects( workspace, projectname, project, build_sequence ):
  print
  print ' ----- Build sequence for ' + projectname + ' -----'
  print

  # restore classpath when done
  try:
    oldPath = os.environ['CLASSPATH']
  except:
    oldPath = ''

  # for all the projects that this project depends upon, show relevant infos
  for project in build_sequence:

    # get the module object given the module name,
    # which is gotten from the project
    module=Module.list[project.module]

    print ' ----------- '+ module.name + ':' + project.name + ' ----------- '

    # get the ant element
    ant=project.ant

    if ant:
      target=''

      # debug info      
      if ant.target:
        print ' ANT TARGET '
        print '   ',ant.target
        target = ant.target
      else:
        print ' ANT TARGET '
        print '   [default]'

    # get the script element
    script=project.script

    if script:
      print ' BUILD WITH SCRIPT '
      print '   ', script.name

    if not (script or ant):
      print ' THIS PROJECT IS NOT TO BE BUILT '
      
    print ' SRCDIR'
    buildbasedir = os.path.normpath(os.path.join(module.srcdir,ant.basedir or ''))
    print '   ',buildbasedir

    print ' CLASSPATH'          #FIXME (nicolaken) has to use this too
    classpath=''
    for depend in project.depend:#+project.option:
      p=Project.list[depend.project]
      srcdir=Module.list[p.module].srcdir

      for jar in p.jar:
        classpath = classpath + os.path.normpath(os.path.join(srcdir,jar.name)) + ';'
        print '  ',os.path.normpath(os.path.join(srcdir,jar.name))

    print
    print ' PROPERTIES'                #FIXME (nicolaken) it's not necessarily there
    for property in workspace.property:#+ant.property:
      print '  ',property.name,'=',property.value

    print ' ------------------------------------------------------- '
    print

    if ant:
      execString=default.antCommand + ' ' + target
      print 'Building using ant!'
      print '    cd', buildbasedir
      print '    export CLASSPATH=' + classpath
      print '   ', execString

      # TODO: don't just brag about it!
      #os.environ['CLASSPATH']=classpath
      #os.chdir( buildbasedir )
      #exec( execString )

    if script:
      scriptfile = os.path.normpath(os.path.join(module.srcdir, script.name))
      print 'Building using ant!'
      print '    cd', buildbasedir
      print '    export CLASSPATH=' + classpath
      print '   ', scriptfile

      # TODO: don't just brag about it!
      #os.environ['CLASSPATH']=classpath
      #os.chdir( buildbasedir )
      #exec( scriptfile )
      
    print
    print ' ------------------------------------------------------- '
    print

  os.environ['CLASSPATH'] = oldPath


# static void main()
if __name__=='__main__':
  # -----------DISABLED-----------
  # use all absolutized pathnames
  # ------------------------------
  # cd into the base Gump dir; all dirs are relative to it
  #os.chdir(dir.base)
    
  # load commandline args or use default values
  if len(sys.argv)>1 :
    ws=sys.argv[1]
  else:
    ws=gumpPath(default.workspace)
    
  if len(sys.argv)>2 :
    ps=sys.argv[2]
  else:
    ps=default.project    

  # get parsed workspace definition
  workspace=load(ws)
  # print info on the definition
  dumpDeps(workspace, ps);          
  sys.exit(0)
