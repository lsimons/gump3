#!/usr/bin/python
"""
        Look for obsolete installed packages, cvs checkouts, and build
        directories.
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

  print
  print ' ----- Build sequence for ' + projectname + ' -----'
  print

  # for all the projects that this project depends upon, show relevant infos
  for project in build_sequence:
    
    # get the module object given the module name,
    # which is gotten from the project
    module=Module.list[project.module]

    print ' ----------- '+ module.name + ':' + project.name + ' ----------- '

    # get the ant element
    ant=project.ant

    if ant:  
      if ant.target:
        print ' ANT TARGET '
        print '   ',ant.target
      else:
        print ' ANT TARGET '
        print '   [default]'    

    # get the script element
    script=project.script

    if script:
      print ' BUILD WITH SCRIPT '
      print '   ?', script

    if not (script or ant):
      print ' THIS PROJECT IS NOT TO BE BUILT '
      
    print ' SRCDIR'
    print '   ',os.path.normpath(os.path.join(module.srcdir,ant.basedir or ''))

    print ' CLASSPATH'          #FIXME (nicolaken) has to use this too
    for depend in project.depend:#+project.option:
      p=Project.list[depend.project]
      srcdir=Module.list[p.module].srcdir

      for jar in p.jar:
        print '  ',os.path.normpath(os.path.join(srcdir,jar.name))

    print
    print ' PROPERTIES'                #FIXME (nicolaken) it's not necessarily there
    for property in workspace.property:#+ant.property:
      print '  ',property.name,'=',property.value

    print
    print ' ------------------------------------------------------- '
    print    

  
# static void main()
if __name__=='__main__':
  # cd into the base Gump dir; all dirs are relative to it
  os.chdir(dir.base)
    
  # load commandline args or use default values
  if len(sys.argv)>1 :
    ws=sys.argv[1]
  else:
    ws=default.workspace
    
  if len(sys.argv)>2 :
    ps=sys.argv[2]
  else:
    ps=default.project    

  workspace=load(ws)
  dumpDeps(workspace, ps);          
  sys.exit(0)
