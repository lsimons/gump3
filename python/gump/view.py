#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/Attic/view.py,v 1.8 2003/05/01 02:56:42 rubys Exp $
# $Revision: 1.8 $
# $Date: 2003/05/01 02:56:42 $
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
  Graphic GUI to navigate a Gump workspace
"""

import os
import popen2
import thread
import sys
import logging

from xml.sax import parse
from xml.sax.handler import ContentHandler

# http://wxpython.org/
from wxPython.wx import *

from gump import load, buildSequence, log
from gump.conf import dir, default
from gump.gen import xmlize
from gump.model import Module, Project

classpath=os.environ['CLASSPATH'].split(os.pathsep)

class gumpview(wxApp):
  # model
  mySubs=None
  items=None
  build_sequence=None
  project=None

  # view
  frame=None
  tree=None
  list=None
  data=None

  # tree index
  mItem={}
  pItem={}

  def OnInit(self):
    # layout
    self.frame = wxFrame(NULL, -1, "Gump Workspace Viewer")
    split1 = wxSplitterWindow(self.frame,-1)
    split2 = wxSplitterWindow(split1,-1)
    notebook = wxNotebook(split2, -1, style=wxCLIP_CHILDREN)

    # panes
    self.tree=wxTreeCtrl(split1,-1)
    self.list=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxSUNKEN_BORDER)
    self.dependencies=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxSUNKEN_BORDER)
    self.classpath=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxSUNKEN_BORDER)
    self.property=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxSUNKEN_BORDER)
    self.data=wxTextCtrl(split2,-1,style=wxTE_MULTILINE)

    # attach the panes to the frame
    split1.SplitVertically(self.tree, split2)
    notebook.AddPage(self.list, 'referenced')
    notebook.AddPage(self.dependencies, 'dependencies')
    notebook.AddPage(self.classpath, 'classpath')
    notebook.AddPage(self.property, 'property')
    split2.SplitHorizontally(notebook, self.data)
    self.SetTopWindow(self.frame)
    self.frame.Show(true)

    # resize
    split1.SetMinimumPaneSize(20)
    split2.SetMinimumPaneSize(20)
    split1.SetSashPosition(300,true)
    split2.SetSashPosition(200)

    # wire up the events
    EVT_TREE_SEL_CHANGED(self, self.tree.GetId(), self.selectTree)
    EVT_LIST_ITEM_SELECTED(self, self.list.GetId(), self.selectItem)
    EVT_LIST_ITEM_SELECTED(self, self.dependencies.GetId(), self.selectItem2)
    EVT_KEY_UP(self, self.OnKeyUp)
    return true

  # list all modules and their projects
  def load(self,files):
    root = self.tree.AddRoot(files[0])
    self.workspace = load(files[0])
    names=Module.list.keys()
    names.sort()
    for name in names:
      module=Module.list[name]
      parent=self.mItem[name]=self.tree.AppendItem(root,name)
      self.tree.SetPyData(parent,module)
      for project in module.project:
        self.pItem[project.name]=self.tree.AppendItem(parent,project.name)
        self.tree.SetPyData(self.pItem[project.name],project)

    self.tree.Expand(root)

  def OnKeyUp(self,event):
    if not event.GetKeyCode()==WXK_F5: return
    if not self.project or not self.project.ant: return
    module=Module.list[self.project.module]

    os.chdir(os.path.join(module.srcdir,self.project.ant.basedir or ''))
    os.environ['CLASSPATH']=os.pathsep.join(classpath+self.project.classpath())
    cmd="java org.apache.tools.ant.Main"
    for property in self.workspace.property+self.project.ant.property:
      cmd+=" -D"+property.name+"="+property.value
    if self.project.ant.target: cmd+=" "+self.project.ant.target

    self.data.Clear()
    compileThread(cmd,self.data).Start()
    
  # select a single feed and display titles from each item
  def selectTree(self, event):
    self.showProject(self.tree.GetPyData(event.GetItem()))

  def showProject(self,project):
    if not project or not isinstance(project,Project): return
    self.project=project
    self.frame.SetTitle(project.name)

    # gather a list of projects which reference this project
    self.items=[]
    for parent in Project.list.values():
      list=parent.depend+parent.option
      for depend in list:
        if depend.project==project.name:
          self.items.append(parent.name)

    # display the list, sorted by name
    self.list.DeleteAllItems()
    if not self.list.GetColumn(0):
      self.list.InsertColumn(0, 'Cross Reference')
      self.items.sort()
    for i in range(0,len(self.items)):
      row=self.list.InsertStringItem(i,self.items[i])
      self.list.SetItemData(row,i)

    self.list.SetColumnWidth(0,wxLIST_AUTOSIZE_USEHEADER)

    # display the project definition
    import StringIO
    data = StringIO.StringIO()
    xmlize('project',project,data,)
    self.data.Clear()
    data.seek(0)
    self.data.AppendText(data.read())
    self.data.ShowPosition(0)

    # gather a list of project dependencies unrolled to build
    self.build_sequence = []
    try:
      todo=[]
      project.addToTodoList(todo)
      todo.sort()
      self.build_sequence = buildSequence(todo)
    except:
      message=str(sys.exc_type)
      if sys.exc_value: message+= ": " + str(sys.exc_value)
      dlg=wxMessageDialog(None, message, "Error", wx.wxOK)
      dlg.ShowModal()
      dlg.Destroy()

    # display the project dependencies
    self.dependencies.DeleteAllItems()
    if not self.dependencies.GetColumn(0):
      self.dependencies.InsertColumn(0, 'Build sequence')

    for i in range(0,len(self.build_sequence)):
      row=self.dependencies.InsertStringItem(i,self.build_sequence[i].name)
      self.dependencies.SetItemData(row,i)

    self.dependencies.SetColumnWidth(0,wxLIST_AUTOSIZE_USEHEADER)

    # display the classpath
    self.classpath.DeleteAllItems()
    if not self.classpath.GetColumn(0):
      self.classpath.InsertColumn(0, 'Path')

    classpath=project.classpath()
    for i in range(0,len(classpath)):
      self.classpath.InsertStringItem(i,classpath[i])

    self.classpath.SetColumnWidth(0,wxLIST_AUTOSIZE_USEHEADER)

    # display the properties
    self.property.DeleteAllItems()
    if not self.property.GetColumn(0):
      self.property.InsertColumn(0, 'Name')
      self.property.InsertColumn(1, 'Value')

    i=0
    if project.ant:
      for property in self.workspace.property+project.ant.property:
        self.property.InsertStringItem(i,property.name or '')
        self.property.SetStringItem(i,1,property.value or '')
        i=i+1

    self.property.SetColumnWidth(0,wxLIST_AUTOSIZE_USEHEADER)
    self.property.SetColumnWidth(1,wxLIST_AUTOSIZE_USEHEADER)

  # show the xml description for a single item
  def selectItem(self, event):
    project=Project.list[self.items[event.GetItem().GetData()]]
    self.showProject(project)

    # expand the associated module and select the project
    self.tree.Expand(self.mItem[project.module])
    self.tree.SelectItem(self.pItem[project.name])

  # show the xml description for a single item
  def selectItem2(self, event):
    project=Project.list[self.build_sequence[event.GetItem().GetData()].name]
    self.showProject(project)

    # expand the associated module and select the project
    self.tree.Expand(self.mItem[project.module])
    self.tree.SelectItem(self.pItem[project.name])

  # make sure that the tree items don't outlive the view
  def unload(self):
    self.mItem.clear()
    self.pItem.clear()

class compileThread:
  def __init__(self,cmd,data):
    self.cmd=cmd
    self.data=data
  def Start(self):
    self.running = 1
    thread.start_new_thread(self.Run,())
  def Stop(self):
    self.running = 0
  def Run(self):
    (stdout,stdin)=popen2.popen2(self.cmd + ' 2>&1')
    stdin.close()
    while 1:
      line = stdout.readline()
      if not line: break
      self.data.AppendText(line)

if __name__ == '__main__':
  app = gumpview(0)
  app.load(sys.argv[1:] or [default.workspace])
  app.MainLoop()
  app.unload()
