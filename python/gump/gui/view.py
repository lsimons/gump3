#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/gui/view.py,v 1.5 2004/03/08 22:28:09 ajack Exp $
# $Revision: 1.5 $
# $Date: 2004/03/08 22:28:09 $
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
import logging, logging.config

from xml.sax import parse
from xml.sax.handler import ContentHandler

# http://wxpython.org/
from wxPython.wx import *

from gump import log
from gump.config import dir, default
from gump.utils.xmlutils import xmlize
from gump.utils.commandLine import handleArgv
from gump.model.module import Module
from gump.model.project import Project
from gump.model.workspace import Workspace
from gump.model.loader import WorkspaceLoader
from gump.engine import GumpEngine
from gump.gumprun import GumpSet

###############################################################################
# Initialize
###############################################################################

###############################################################################
# Main App
###############################################################################

class gumpview(wxApp):
    
  # model
  mySubs=None
  items=None
  build_sequence=None
  history=[]

  # item IDs:
  menu_BACK=10001 
  menu_UPDATE=10002
  menu_GEN=10003
  menu_RUN=10004
  menu_CONSOLE=10005
  menu_HELP=10006
  
  # view
  frame=None
  tree=None
  list=None
  data=None
  logsplitter=None
  logview=None
  mainsplit=None

  # action views
  toolbar=None
  runbutton=None
  
  # tree index
  mItem={}
  pItem={}

  def OnInit(self):
    
    # The main frame
    self.frame = wxFrame(NULL, -1, "Gump Workspace Viewer")

    # Create our toolbar
    self.frame.toolbar = self.frame.CreateToolBar(wxTB_HORIZONTAL |
                                        wxNO_BORDER | wxTB_FLAT )

    self.frame.toolbar.AddSimpleTool(self.menu_BACK,
                                     wxBitmap("gump/gui/images/back.bmp",
                                              wxBITMAP_TYPE_BMP),
                                     "Back")
  
    self.frame.toolbar.AddSeparator()

    self.frame.toolbar.AddSimpleTool(self.menu_UPDATE,
                                     wxBitmap("gump/gui/images/update.bmp",
                                              wxBITMAP_TYPE_BMP),
                                     "Update from VCS")
                                     
    self.frame.toolbar.AddSimpleTool(self.menu_GEN,
                                     wxBitmap("gump/gui/images/gen.bmp",
                                              wxBITMAP_TYPE_BMP),
                                     "Generate XML merged descriptor")
                                     
    self.frame.toolbar.AddSimpleTool(self.menu_RUN,
                                     wxBitmap("gump/gui/images/run.bmp",
                                              wxBITMAP_TYPE_BMP),
                                     "Run")

    self.frame.toolbar.AddSeparator()


    self.frame.toolbar.AddCheckTool(self.menu_CONSOLE,
                                     wxBitmap("gump/gui/images/console.bmp",
                                              wxBITMAP_TYPE_BMP),
                                     shortHelp="Toggle this")
    
    self.frame.toolbar.AddSimpleTool(self.menu_HELP,
                                     wxBitmap("gump/gui/images/help.bmp",
                                              wxBITMAP_TYPE_BMP),
                                     "Help")
    
    self.frame.toolbar.Realize()
        
    # layout
    self.logsplitter = wxSplitterWindow(self.frame,-1,style=wxSP_NOBORDER )    
    self.mainsplit = wxSplitterWindow(self.logsplitter,-1,style=wxSP_NOBORDER)
    split2 = wxSplitterWindow(self.mainsplit,-1,style=wxSP_NOBORDER)
    notebook = wxNotebook(split2, -1, style=wxCLIP_CHILDREN )
    
    #notebook images
    notebookil = wxImageList(16, 16)
    idx_referenced = notebookil.Add(wxImage("gump/gui/images/referenced.bmp").ConvertToBitmap())
    idx_dependencies = notebookil.Add(wxImage("gump/gui/images/dependencies.bmp").ConvertToBitmap())
    idx_prereqs = notebookil.Add(wxImage("gump/gui/images/prereqs.bmp").ConvertToBitmap())
    idx_classpath = notebookil.Add(wxImage("gump/gui/images/classpath.bmp").ConvertToBitmap())
    idx_property = notebookil.Add(wxImage("gump/gui/images/property.bmp").ConvertToBitmap())    
    idx_exports = notebookil.Add(wxImage("gump/gui/images/exports.bmp").ConvertToBitmap())    
    notebook.AssignImageList(notebookil)
    #self.SetImageList(self.il, wxIMAGE_LIST_SMALL)

    # panes
    self.list=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxNO_BORDER )
    self.dependencies=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxNO_BORDER )
    self.prereqs=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxNO_BORDER )
    self.classpath=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxNO_BORDER )
    self.property=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxNO_BORDER )
    self.exports=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxNO_BORDER )

    self.data=wxTextCtrl(split2,-1,style=wxTE_MULTILINE)

    self.logview=GumpLogView(self.logsplitter)

    self.tree=wxTreeCtrl(self.mainsplit,-1)
    
    # attach the panes to the frame
    self.logsplitter.SplitHorizontally(self.mainsplit, self.logview)
    self.mainsplit.SplitVertically(self.tree, split2)
    notebook.AddPage(self.list, 'referenced')
    notebook.SetPageImage(0, idx_referenced)
    notebook.AddPage(self.dependencies, 'dependencies')
    notebook.SetPageImage(1, idx_dependencies)
    notebook.AddPage(self.prereqs, 'prereqs')
    notebook.SetPageImage(2, idx_prereqs)
    notebook.AddPage(self.classpath, 'classpath')
    notebook.SetPageImage(3, idx_classpath)
    notebook.AddPage(self.property, 'property')
    notebook.SetPageImage(4, idx_property)
    notebook.AddPage(self.exports, 'exports')
    notebook.SetPageImage(5, idx_exports)
    
    split2.SplitHorizontally(notebook, self.data)
    self.SetTopWindow(self.frame)
    self.logsplitter.Unsplit(self.logview)
    self.frame.Show(true)

    # resize
    self.logsplitter.SetMinimumPaneSize(20)
    self.mainsplit.SetMinimumPaneSize(20)
    split2.SetMinimumPaneSize(20)
    self.logsplitter.SetSashPosition(350,true)
    self.mainsplit.SetSashPosition(250,true)
    split2.SetSashPosition(130)

    # wire up the events
    EVT_TREE_SEL_CHANGED(self, self.tree.GetId(), self.selectTree)
    
    EVT_LIST_ITEM_SELECTED(self, self.list.GetId(), self.selectProject)
    EVT_LIST_ITEM_SELECTED(self, self.dependencies.GetId(), self.selectProject)
    EVT_LIST_ITEM_SELECTED(self, self.prereqs.GetId(), self.selectProject)
    
    EVT_KEY_UP(self, self.OnKeyUp)

    EVT_MENU(self, self.menu_BACK, self.backAction)
    EVT_MENU(self, self.menu_UPDATE,  self.updateAction )
    EVT_MENU(self, self.menu_GEN,  self.genAction )
    EVT_MENU(self, self.menu_RUN,  self.runAction )
    EVT_TOOL(self, self.menu_CONSOLE, self.consoleAction)
    #        EVT_TOOL(self, 50, self.OnToolClick)
    EVT_MENU(self, self.menu_HELP, self.helpAction)
    
    return true

  # list all modules and their projects
  def load(self,files):
      
    #tree images
    treeil = wxImageList(16, 16)
    idx_workspace = treeil.Add(wxImage("gump/gui/images/workspace.bmp").ConvertToBitmap())
    idx_module = treeil.Add(wxImage("gump/gui/images/module.bmp").ConvertToBitmap())
    idx_module_ex = treeil.Add(wxImage("gump/gui/images/module_ex.bmp").ConvertToBitmap())    
    idx_project = treeil.Add(wxImage("gump/gui/images/project.bmp").ConvertToBitmap())
    idx_project_ex = treeil.Add(wxImage("gump/gui/images/project_ex.bmp").ConvertToBitmap())
    self.tree.AssignImageList(treeil)
    
    root = self.tree.AddRoot(files[0])
    self.tree.SetItemImage(root, idx_workspace, wx.wxTreeItemIcon_Normal)
    self.tree.SetItemImage(root, idx_workspace, wx.wxTreeItemIcon_Expanded)
    self.tree.SetItemImage(root, idx_workspace, wx.wxTreeItemIcon_SelectedExpanded)
    
    # Load (and complete) the workspace
    self.workspace = (WorkspaceLoader()).load(files[0])
    
    # Build the view tree of modules/projects
    for module in self.workspace.getSortedModules():
      name=module.getName()
      parent=self.mItem[name]=self.tree.AppendItem(root,name)
      self.tree.SetPyData(parent,module)
      self.tree.SetItemImage(parent, idx_module ,    wx.wxTreeItemIcon_Normal)
      self.tree.SetItemImage(parent, idx_module_ex , wx.wxTreeItemIcon_Expanded)
      self.tree.SetItemImage(parent, idx_module_ex , wx.wxTreeItemIcon_Selected)
      self.tree.SetItemImage(parent, idx_module_ex,  wx.wxTreeItemIcon_SelectedExpanded)
      for project in module.getSortedProjects():
        proj=self.pItem[project.getName()]=self.tree.AppendItem(parent,project.getName())
        self.tree.SetPyData(self.pItem[project.name],project)
        self.tree.SetItemImage(proj, idx_project ,    wx.wxTreeItemIcon_Normal)
        self.tree.SetItemImage(proj, idx_project_ex , wx.wxTreeItemIcon_Selected)
      
    self.tree.Expand(root)

  def OnKeyUp(self,event):
    if event.GetKeyCode()==WXK_BACK:
      self.backAction(event)

    if event.GetKeyCode()==WXK_F5:
      self.runAction(event)


  # back action
  def backAction(self,event):
    if len(self.history)>1:
      self.history.pop()
      self.showProject(self.history[-1])
    
  # updates CVS
  def updateAction(self,event):
    print "INUPDATE "
    if self.history[-1]:
      project=self.history[-1].name 
    else:
       project='all'
    
    print "INUPDATE " + project
    updateThread(self.workspace,project).Start()
    
  # run the selected project xml gen
  def genAction(self,event):
    genThread(self.workspace).Start()
    
  # run the selected project
  def runAction(self,event):
    if not self.history: return
    project=self.history[-1]
    if not project.ant: return

    compileThread(project,self).Start()

  # help action
  def helpAction(self,event):
    self.msgbox("TODO")

  # help action
  def consoleAction(self,event):
   if self.logsplitter.IsSplit():
     self.logsplitter.Unsplit(self.logview)
   else:
     self.logsplitter.SplitHorizontally(self.mainsplit, self.logview)
     self.logview.SetColumnWidth(0,wxLIST_AUTOSIZE_USEHEADER)
     self.logview.Show()
    
  # select a single feed and display titles from each item
  def selectTree(self, event):
    project=self.tree.GetPyData(event.GetItem())
    if project and isinstance(project,Project):
      if not self.history or self.history[-1]<>project:
        self.showProject(project)
        self.history.append(project)

  def showProject(self,project):
    if self.history: self.history[-1]['xmldata']=self.data.GetValue()
    self.frame.SetTitle(project.name)

    # gather a list of projects which reference this project
    self.items=[]
    for dependency in project.getDependees():
        self.items.append(dependency.getOwnerProject().getName())

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
    self.data.Clear()
    #if project.xmldata:
    #  self.data.AppendText(project.xmldata)
    #else:
    #  self.data.AppendText(xmlize('project',project))
    #  self.data.ShowPosition(0)
    
    self.data.AppendText(project.getXMLData())
    self.data.ShowPosition(0)

    # gather a list of project dependencies unrolled to build
    run=GumpSet(self.workspace,project.getName())
    self.build_sequence = run.getProjectSequence()
    
    # display the project dependencies
    self.dependencies.DeleteAllItems()
    if not self.dependencies.GetColumn(0):
      self.dependencies.InsertColumn(0, 'Build sequence')

    i=0
    for build in self.build_sequence:
      row=self.dependencies.InsertStringItem(i,build.getName())
      self.dependencies.SetItemData(row,i)
      for jar in build.getJars():
        if jar.path and not os.path.exists(jar.getPath()):
          self.dependencies.SetItemBackgroundColour(row,wxRED)
      i+=1

    self.dependencies.SetColumnWidth(0,wxLIST_AUTOSIZE_USEHEADER)

    # display the prereqs
    self.prereqs.DeleteAllItems()
    if not self.prereqs.GetColumn(0):
      self.prereqs.InsertColumn(0, 'Prerequisites')

    i=0
    for dependency in project.getDependencies():
      prereq=dependency.getProject()
      #if prereq.ant or prereq.script: continue
      row=self.prereqs.InsertStringItem(i,prereq.getName())
      for jar in prereq.getJars():
        if not os.path.exists(jar.getPath()):
          self.prereqs.SetItemBackgroundColour(row,wxRED)
      i+=1

    self.prereqs.SetColumnWidth(0,wxLIST_AUTOSIZE_USEHEADER)

    # display the classpath
    self.classpath.DeleteAllItems()
    if not self.classpath.GetColumn(0):
      self.classpath.InsertColumn(0, 'Path')

    (classpath, bootclasspath)=project.getClasspathLists()
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

    # display what jars this project produces
    self.exports.DeleteAllItems()
    if not self.exports.GetColumn(0):
      self.exports.InsertColumn(0, 'Exports')

    for i in range(0,len(project.jar)):
      jar=project.jar[i].path
      if jar:
        row=self.exports.InsertStringItem(i,jar)
        if not os.path.exists(jar):
          self.exports.SetItemBackgroundColour(row,wxRED)
      else:
        self.msgbox('Invalid element: ' + xmlize('jar',project.jar[i]))

    self.exports.SetColumnWidth(0,wxLIST_AUTOSIZE_USEHEADER)

  # show the xml description for a single item
  def selectProject(self, event):
    projname=event.GetEventObject().GetItem(event.GetIndex(),0).GetText()
    project=self.workspace.getProject(projname)
    self.showProject(project)
    self.history.append(project)

    # expand the associated module and select the project
    self.tree.Expand(self.mItem[project.module])
    self.tree.SelectItem(self.pItem[project.name])

  # make sure that the tree items don't outlive the view
  def unload(self):
    self.mItem.clear()
    self.pItem.clear()

  # display a modal dialog box
  def msgbox(self,message,title="Warning"):
    log.error(title + ": "+message)
    if not self.logview.IsShown():
      dlg=wxMessageDialog(None, message, title, wx.wxOK)
      dlg.ShowModal()
      dlg.Destroy()

class ViewHandler(logging.Handler):

    view = None

    """
    A handler class which logs in this view .
    """    
    def __init__(self, logview):
        """
        Initializes the handler
        """
        logging.Handler.__init__(self)
        self.view = logview
        
    def emit(self, record):
        """
        Emit a record.
        """
        
        msg = "%s\n" % self.format(record)
        self.view.add(msg, record)
        
class GumpSplashScreen(wxSplashScreen):
  def __init__(self):
    bmp = wxImage("gump/gui/images/gump.bmp").ConvertToBitmap()
    wxSplashScreen.__init__(self, bmp,
                            wxSPLASH_CENTRE_ON_SCREEN|wxSPLASH_TIMEOUT,
                            4000, None, -1,
                            style = wxSIMPLE_BORDER|wxFRAME_NO_TASKBAR|wxSTAY_ON_TOP)
    wxYield()
        
class GumpLogView(wxListCtrl):

    def __init__(self, parent):
        wxListCtrl.__init__(self, parent, -1,
                            style=wxLC_REPORT|wxLC_VIRTUAL|wxLC_HRULES|wxLC_VRULES)
        self.log = []
        self.logmsg = []
        
        self.il = wxImageList(16, 16)
        self.idx_critical = self.il.Add(wxImage("gump/gui/images/fatal.bmp").ConvertToBitmap())
        self.idx_error = self.il.Add(wxImage("gump/gui/images/error.bmp").ConvertToBitmap())
        self.idx_warning = self.il.Add(wxImage("gump/gui/images/warning.bmp").ConvertToBitmap())
        self.idx_info = self.il.Add(wxImage("gump/gui/images/info.bmp").ConvertToBitmap())
        self.idx_debug = self.il.Add(wxImage("gump/gui/images/debug.bmp").ConvertToBitmap())
        self.SetImageList(self.il, wxIMAGE_LIST_SMALL)
 
        self.attr_critical = wxListItemAttr()
        self.attr_critical.SetBackgroundColour("dark red")
        self.attr_error = wxListItemAttr()
        self.attr_error.SetBackgroundColour("red")
        self.attr_warning = wxListItemAttr()
        self.attr_warning.SetBackgroundColour("yellow")
        self.attr_info = wxListItemAttr()
        self.attr_info.SetBackgroundColour("white")
        self.attr_debug = wxListItemAttr()
        self.attr_debug.SetBackgroundColour("light blue")
        
        self.InsertColumn(0, "Message")

        self.SetItemCount(0)

        EVT_LIST_ITEM_ACTIVATED(self, self.GetId(), self.OnItemActivated)

    def add(self, message, record):
      self.log.insert(0,record)
      self.logmsg.insert(0,message)
      self.SetItemCount(len(self.log))

    def OnItemActivated(self, event):
        txt = self.logmsg[event.m_itemIndex]
        title = self.log[event.m_itemIndex].levelname
        dlg=wxMessageDialog(None, txt, title, wx.wxOK)
        dlg.ShowModal()
        dlg.Destroy()

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    #---------------------------------------------------
    # These methods are callbacks for implementing the
    # "virtualness" of the list...  It 
    # determines the text, attributes and/or image based
    # on values from the data source
    
            #record.name
            #record.msg
            #record.args
            #record.levelname 
            #record.levelno
            #record.pathname
            #record.filename
            #record.module
            #record.exc_info
            #record.lineno 
            #record.created 
            #record.msecs
            #record.relativeCreated
            #record.thread

        
    def OnGetItemText(self, item, col):
        return self.logmsg[item].strip()

    def OnGetItemImage(self, item):
        currentLogLevel = self.log[item].levelno
        if currentLogLevel == logging.CRITICAL:
            return self.idx_critical
        elif currentLogLevel == logging.ERROR:
            return self.idx_error
        elif currentLogLevel == logging.WARN:
            return self.idx_warning
        if currentLogLevel == logging.INFO:
            return self.idx_info
        elif currentLogLevel == logging.DEBUG:
            return self.idx_debug
        else:
            return None

    def OnGetItemAttr(self, item):
        currentLogLevel = self.log[item].levelno
        if currentLogLevel == logging.CRITICAL:
            return self.attr_critical
        elif currentLogLevel == logging.ERROR:
            return self.attr_error
        elif currentLogLevel == logging.WARN:
            return self.attr_warning
        if currentLogLevel == logging.INFO:
            return self.attr_info
        elif currentLogLevel == logging.DEBUG:
            return self.attr_debug
        else:
            return None

class genThread:
  def __init__(self,workspace):
    self.workspace=workspace
  def Start(self):
    self.running = 1
    thread.start_new_thread(self.Run,())
  def Stop(self):
    self.running = 0
  def Run(self):      
    f=open( default.merge, 'w')
    try:
      xmlize('workspace',self.workspace,f)
    finally:
      # Since we may exit via an exception, close fp explicitly.
      f.close()

class updateThread:
  def __init__(self,workspace,project):
    self.workspace=workspace
    self.project=project
  def Start(self):
    self.running = 1
    thread.start_new_thread(self.Run,())
  def Stop(self):
    self.running = 0
  def Run(self):
    update(self.workspace,self.project)

class compileThread:
  def __init__(self,project,view):
    self.project=project
    self.view=view
  def Start(self):
    self.running = 1
    thread.start_new_thread(self.Run,())
  def Stop(self):
    self.running = 0
  def Run(self):
    module=Module.list[self.project.module]

    os.chdir(os.path.join(module.srcdir,self.project.ant.basedir or ''))
    os.environ['CLASSPATH']=os.pathsep.join(default.classpath+self.project.classpath())
    cmd="java org.apache.tools.ant.Main"
    for property in self.view.workspace.property+self.project.ant.property:
      cmd+=" -D"+property.name+"="+property.value
    if self.project.ant.buildfile: cmd+=" -f "+self.project.ant.buildfile 
    if self.project.ant.target: cmd+=" "+self.project.ant.target

    (stdout,stdin)=popen2.popen2(cmd + ' 2>&1')
    stdin.close()
    self.view.data.Clear()
    while self.running:
      line = stdout.readline()
      if not line: break
      self.view.data.AppendText(line)
    self.view.showProject(self.project)

if __name__ == '__main__':

  # init logging and add specific Gui handler
  logging.config.fileConfig("gump/logconf.ini")
  
  # load app
  app = gumpview(0)
  GumpSplashScreen().Show()

  #add app-specific log handler
  logger = logging.getLogger("")
  logger.setLevel(logging.DEBUG)
  lh = ViewHandler(app.logview)
  logger.addHandler(lh)

  # loadspecified or default workspace
  (args,options) = handleArgv(sys.argv,0)
  app.load([args[0]])

  # start app
  app.MainLoop()

  # dipose app
  app.unload()
