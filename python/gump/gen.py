#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/Attic/gen.py,v 1.1 2003/04/28 20:27:48 leosimons Exp $
# $Revision: 1.1 $
# $Date: 2003/04/28 20:27:48 $
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
Generate the merged XML description of the workspace.

Not even sure if this is needed!!!
"""

import os.path,os,sys,logging
from gump import *
from gump.conf import *

# init logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG) #set verbosity to show all messages of severity >= DEBUG

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
    ws=default.workspace

  workspace=load(ws)

  try:
    f=open( default.merge, 'w')
    xmlize('workspace',workspace,f)
  finally:
    # Since we may exit via an exception, close fp explicitly.
    if f:
      f.close()





