#!/usr/bin/python
"""
        Graphic GUI to navigate a Gump workspace
"""

import sys
from xml.sax import parse
from xml.sax.handler import ContentHandler

# http://wxpython.org/
from wxPython.wx import *

from gumpcore import load,Module,Project
from gen import xmlize
from gumpconf import *

class gumpview(wxApp):
  # model
  mySubs=None
  items=None
  build_sequence=None

  # view
  tree=None
  list=None
  data=None

  # tree index
  mItem={}
  pItem={}

  def OnInit(self):
    # layout
    frame = wxFrame(NULL, -1, "Gump Workspace Viewer")
    split1 = wxSplitterWindow(frame,-1)
    split2 = wxSplitterWindow(split1,-1)
    notebook = wxNotebook(split2, -1, style=wxCLIP_CHILDREN)

    # panes
    self.tree=wxTreeCtrl(split1,-1)
    self.list=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxSUNKEN_BORDER)
    self.dependencies=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxSUNKEN_BORDER)
    self.data=wxTextCtrl(split2,-1,style=wxTE_MULTILINE)

    # attach the panes to the frame
    split1.SplitVertically(self.tree, split2)
    notebook.AddPage(self.list, 'referenced')
    notebook.AddPage(self.dependencies, 'dependencies')
    split2.SplitHorizontally(notebook, self.data)
    self.SetTopWindow(frame)
    frame.Show(true)

    # resize
    split1.SetMinimumPaneSize(20)
    split2.SetMinimumPaneSize(20)
    split1.SetSashPosition(300,true)
    split2.SetSashPosition(200)

    # wire up the events
    EVT_TREE_SEL_CHANGED(self, self.tree.GetId(), self.selectTree)
    EVT_LIST_ITEM_SELECTED(self, self.list.GetId(), self.selectItem)
    EVT_LIST_ITEM_SELECTED(self, self.dependencies.GetId(), self.selectItem2)
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

  # select a single feed and display titles from each item
  def selectTree(self, event):
    self.showProject(self.tree.GetPyData(event.GetItem()))

  def showProject(self,project):
    if not project or not isinstance(project,Project): return

    # gather a list of projects which reference this project
    self.items=[]
    for parent in Project.list.values():
      list=parent.depend+parent.option
      if parent.ant: list+=parent.ant.depend
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
    self.build_sequence = project.buildSequence()

    # display the project dependencies
    self.dependencies.DeleteAllItems()
    if not self.dependencies.GetColumn(0):
      self.dependencies.InsertColumn(0, 'Build sequence')

    for i in range(0,len(self.build_sequence)):
      row=self.dependencies.InsertStringItem(i,self.build_sequence[i].name)
      self.dependencies.SetItemData(row,i)

    self.dependencies.SetColumnWidth(0,wxLIST_AUTOSIZE_USEHEADER)


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

if __name__ == '__main__':
  app = gumpview(0)
  app.load(sys.argv[1:] or [default.workspace])
  app.MainLoop()
  app.unload()
