#!/usr/bin/python
"""
Generate the merged XML description of the workspace
"""

import os.path,os,sys
from gumpcore import *
from gumpconf import *

#########################################################################
#                     Dump the object module as XML                     #
#########################################################################

def xmlize(nodeName,object,f,indent='',delta='  '):
  from xml.sax.saxutils import escape
  import types

  attrs=[nodeName]
  elements=[]
  text=''
  encoding='latin-1'

  # iterate over the object properties
  for name in object.__dict__:
    if name.startswith('__') and name.endswith('__'): continue
    var=getattr(object,name)

    # avoid nulls, metadata, and methods
    if not var: continue
    if isinstance(var,types.TypeType): continue
    if isinstance(var,types.MethodType): continue

    # determine if the property is text, attribute, or element
    if name=='@text':
        text=var
    elif isinstance(var,types.StringTypes):
        attrs.append('%s="%s"' % (name,escape(var)))
    else:
        elements.append((name,var))

  # format for display
  if not elements:
    # use compact form for elements without children
    if text.strip():
      f.write( '%s<%s>%s</%s>\n' % (indent,' '.join(attrs).encode(encoding),
        text.strip().encode(encoding),nodeName))
    else:
      f.write( '%s<%s/>\n' % (indent,' '.join(attrs).encode(encoding)))
  else:
   # use full form for elements with children
   f.write( '%s<%s>\n' % (indent,' '.join(attrs).encode(encoding)))
   newindent=indent+delta
   for (name,var) in elements:
     if isinstance(var,list):
       # multiple valued elements
       for e in var: xmlize(name,e,f,newindent,delta)
     elif isinstance(var,Single):
       # single valued elements
       xmlize(name,var.delegate,f,newindent,delta)
   f.write( '%s</%s>\n' % (indent,nodeName.encode(encoding)))


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

  workspace=load(ws)

  try:
    f=open(dir.work+'/'+default.merge, 'w')
    xmlize('workspace',workspace,f)
  finally:
    # Since we may exit via an exception, close fp explicitly.
    if f:
      f.close()





