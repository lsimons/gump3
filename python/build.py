#!/usr/bin/python
"""
	Look for obsolete installed packages, cvs checkouts, and build
	directories.
"""

import os.path,os,sys
from gumpcore import *
from gumpconf import *

os.chdir(dir.base)
debug=True #False

if len(sys.argv)>1 :
  ws=sys.argv[1]
else:
  ws=default.workspace

if len(sys.argv)>2 :
  pj=sys.argv[2]
else:
  pj=default.project
  
workspace=load(ws)
projectname=pj
project=Project.list[pj]
module=Module.list[project.module]
ant=project.ant

print 'SRCDIR'
print '  ',os.path.normpath(os.path.join(module.srcdir,ant.basedir or ''))

print
print 'CLASSPATH:'
for depend in project.depend+project.option:
  p=Project.list[depend.project]
  srcdir=Module.list[p.module].srcdir

  for jar in p.jar:
    print '  ',os.path.normpath(os.path.join(srcdir,jar.name))

print
print 'PROPERTIES'
for property in workspace.property+ant.property:
  print '  ',property.name,'=',property.value

print 'PROJECTS TO BUILD:'

build_sequence = dependencies(projectname, project.depend)

print
print ' ----- Build sequence for ' + projectname + ' -----'
print
for project in build_sequence:
  print '  ' + project.name


            
sys.exit(0)
