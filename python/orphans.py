#!/usr/bin/python
"""
	Look for obsolete installed packages, cvs checkouts, and build
	directories.
"""

from xml.sax import parse
from xml.sax.handler import ContentHandler
from glob import glob
import os

class Workspace(ContentHandler):
    cvsdir = None
    jardir = None
    pkgdir = None
    logdir = None
    basedir = None
    modules=[]
    packages=[]
    def startElement(self, name, attrs):
	if name == 'workspace':
	    attrs=dict(attrs)
            self.pkgdir = attrs['pkgdir']
            self.cvsdir = attrs['cvsdir']
            self.basedir = attrs['basedir']
            self.jardir = attrs['jardir']
            self.logdir = attrs['logdir']
	if name == 'module':
	    attrs=dict(attrs)
	    self.modules.append(attrs['name'])
	if name == 'project':
	    attrs=dict(attrs)
	    if 'home' in attrs and attrs['home'].find(self.pkgdir) ==0:
		self.packages.append(attrs['home'].replace('\\','/'))

workspace=Workspace()
parse(open('work/merge.xml'),workspace)

# orphan packages
for dir in glob(workspace.pkgdir+'/*'):
    if not dir.replace('\\','/') in workspace.packages:
	if os.path.isdir(dir): print dir.replace('/',os.sep)

# orphan cvs checkouts
for dir in glob(workspace.cvsdir+'/*'):
    if dir.endswith('Entries') or dir.endswith('Entries.log'): continue
    if not dir[len(workspace.cvsdir)+1:] in workspace.modules:
	if os.path.isdir(dir): print dir.replace('/',os.sep)

# orphan builds
for dir in glob(workspace.basedir+'/*'):
    if not dir[len(workspace.basedir)+1:] in workspace.modules:
        dir=dir.replace('/',os.sep)
	if dir==workspace.basedir.replace('/',os.sep)+os.sep+"dist": continue
	if dir==workspace.jardir.replace('/',os.sep): continue
	if dir==workspace.logdir.replace('/',os.sep): continue
	if dir==workspace.cvsdir.replace('/',os.sep): continue
	if os.path.isdir(dir): print dir

