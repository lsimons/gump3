#!/usr/bin/env python

# $Header: /home/stefano/cvs/gump/python/gump/Attic/view.py,v 1.27 2003/05/05 09:31:59 nicolaken Exp $
# $Revision: 1.27 $
# $Date: 2003/05/05 09:31:59 $
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

from gump import load, buildSequence, log
from gump.conf import dir, default
from gump.gen import xmlize
from gump.model import Module, Project

# init logging
log = logging.getLogger(__name__)

classpath = os.getenv('CLASSPATH')
if(classpath):
  classpath = classpath.split(os.pathsep)

class gumpview(wxApp):
  # model
  mySubs=None
  items=None
  build_sequence=None
  history=[]

  # item IDs:
  menu_BACK=10001 
  menu_RUN=10002
  menu_CONSOLE=10003
  menu_HELP=10004
  
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
                                     wxBitmap("gump/images/back.bmp",
                                              wxBITMAP_TYPE_BMP),
                                     "Back")
      
    self.frame.toolbar.AddSimpleTool(self.menu_RUN,
                                     wxBitmap("gump/images/run.bmp",
                                              wxBITMAP_TYPE_BMP),
                                     "Run")

    self.frame.toolbar.AddSeparator()


    self.frame.toolbar.AddCheckTool(self.menu_CONSOLE,
                                     wxBitmap("gump/images/console.bmp",
                                              wxBITMAP_TYPE_BMP),
                                     shortHelp="Toggle this")
    
    self.frame.toolbar.AddSimpleTool(self.menu_HELP,
                                     wxBitmap("gump/images/help.bmp",
                                              wxBITMAP_TYPE_BMP),
                                     "Help")
    
    self.frame.toolbar.Realize()
        
    # layout
    self.logsplitter = wxSplitterWindow(self.frame,-1,style=wxSP_NOBORDER )    
    self.mainsplit = wxSplitterWindow(self.logsplitter,-1,style=wxSP_NOBORDER)
    split2 = wxSplitterWindow(self.mainsplit,-1,style=wxSP_NOBORDER)
    notebook = wxNotebook(split2, -1, style=wxCLIP_CHILDREN )

    # panes
    self.tree=wxTreeCtrl(self.mainsplit,-1)
    
    self.list=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxNO_BORDER )
    self.dependencies=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxNO_BORDER )
    self.prereqs=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxNO_BORDER )
    self.classpath=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxNO_BORDER )
    self.property=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxNO_BORDER )
    self.exports=wxListCtrl(notebook,-1,style=wxLC_REPORT|wxNO_BORDER )

    self.data=wxTextCtrl(split2,-1,style=wxTE_MULTILINE)

    self.logview=wxTextCtrl(self.logsplitter,-1,style=wxTE_MULTILINE|wxTE_RICH2)   
    self.logview.SetEditable(False)

    

    # attach the panes to the frame
    self.logsplitter.SplitHorizontally(self.mainsplit, self.logview)
    self.mainsplit.SplitVertically(self.tree, split2)
    notebook.AddPage(self.list, 'referenced')
    notebook.AddPage(self.dependencies, 'dependencies')
    notebook.AddPage(self.prereqs, 'prereqs')
    notebook.AddPage(self.classpath, 'classpath')
    notebook.AddPage(self.property, 'property')
    notebook.AddPage(self.exports, 'exports')
    split2.SplitHorizontally(notebook, self.data)
    self.SetTopWindow(self.frame)
    self.logsplitter.Unsplit(self.logview)
    self.frame.Show(true)

    # resize
    self.logsplitter.SetMinimumPaneSize(20)
    self.mainsplit.SetMinimumPaneSize(20)
    split2.SetMinimumPaneSize(20)
    self.logsplitter.SetSashPosition(350,true)
    self.mainsplit.SetSashPosition(300,true)
    split2.SetSashPosition(130)

    # wire up the events
    EVT_TREE_SEL_CHANGED(self, self.tree.GetId(), self.selectTree)
    
    EVT_LIST_ITEM_SELECTED(self, self.list.GetId(), self.selectProject)
    EVT_LIST_ITEM_SELECTED(self, self.dependencies.GetId(), self.selectProject)
    EVT_LIST_ITEM_SELECTED(self, self.prereqs.GetId(), self.selectProject)
    
    EVT_KEY_UP(self, self.OnKeyUp)

    EVT_MENU(self, self.menu_BACK, self.backAction)
    EVT_MENU(self, self.menu_RUN,  self.runAction )
    EVT_TOOL(self, self.menu_CONSOLE, self.consoleAction)
    #        EVT_TOOL(self, 50, self.OnToolClick)
    EVT_MENU(self, self.menu_HELP, self.helpAction)
    
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
    if event.GetKeyCode()==WXK_BACK:
      self.backAction(event)

    if event.GetKeyCode()==WXK_F5:
      self.runAction(event)


  # back action
  def backAction(self,event):
    if len(self.history)>1:
      self.history.pop()
      self.showProject(self.history[-1])
    
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
     self.logview.Show()
    
  # select a single feed and display titles from each item
  def selectTree(self, event):
    project=self.tree.GetPyData(event.GetItem())
    if project and isinstance(project,Project):
      if not self.history or self.history[-1]<>project:
        self.showProject(project)
        self.history.append(project)

  def showProject(self,project):
    if self.history: self.history[-1]['viewdata']=self.data.GetValue()
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
    self.data.Clear()
    if project.viewdata:
      self.data.AppendText(project.viewdata)
    else:
      self.data.AppendText(xmlize('project',project))
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
      self.msgbox(message, "Error")

    # display the project dependencies
    self.dependencies.DeleteAllItems()
    if not self.dependencies.GetColumn(0):
      self.dependencies.InsertColumn(0, 'Build sequence')

    for i in range(0,len(self.build_sequence)):
      build=Project.list[self.build_sequence[i].name]
      row=self.dependencies.InsertStringItem(i,build.name)
      self.dependencies.SetItemData(row,i)
      for jar in build.jar:
        if jar.path and not os.path.exists(jar.path):
          self.dependencies.SetItemBackgroundColour(row,wxRED)

    self.dependencies.SetColumnWidth(0,wxLIST_AUTOSIZE_USEHEADER)

    # display the prereqs
    self.prereqs.DeleteAllItems()
    if not self.prereqs.GetColumn(0):
      self.prereqs.InsertColumn(0, 'Prerequisites')

    i=0
    for depend in project.depend+project.option:
      prereq=Project.list[depend.project]
      if prereq.ant or prereq.script: continue
      row=self.prereqs.InsertStringItem(i,prereq.name)
      for jar in prereq.jar:
        if not os.path.exists(jar.path):
          self.prereqs.SetItemBackgroundColour(row,wxRED)
      i=i+1

    self.prereqs.SetColumnWidth(0,wxLIST_AUTOSIZE_USEHEADER)

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
    project=Project.list[projname]
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
    if self.logview.IsShown():
      log.error(title + ": "+message)
    else:
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

        #CRITICAL = 50
        #FATAL = CRITICAL
        #ERROR = 40
        #WARN = 30
        #INFO = 20
        #DEBUG = 10
        #NOTSET = 0

        msg = "%s\n" % self.format(record)
        
        textStyle = None;
        
        if(record.levelno == logging.FATAL):
         textStyle = wx.wxTextAttr("YELLOW", "RED")
        elif(record.levelno ==logging.ERROR):     
         textStyle = wx.wxTextAttr("RED", "YELLOW")
        elif(record.levelno == logging.WARN):     
         textStyle = wx.wxTextAttr("RED", "GRAY")
        elif(record.levelno == logging.INFO):     
         textStyle = wx.wxTextAttr("BLACK", "WHITE")
        elif(record.levelno == logging.DEBUG):    
         textStyle = wx.wxTextAttr("GRAY", "WHITE")
        else:
         textStyle = wx.wxTextAttr("WHITE", "BLACK")
         
        self.view.SetDefaultStyle( textStyle ) 

        self.view.AppendText(msg)
        
        
class GumpSplashScreen(wxSplashScreen):
  def __init__(self):
    bmp = wxImage("gump/images/gump.bmp").ConvertToBitmap()
    wxSplashScreen.__init__(self, bmp,
                            wxSPLASH_CENTRE_ON_SCREEN|wxSPLASH_TIMEOUT,
                            4000, None, -1,
                            style = wxSIMPLE_BORDER|wxFRAME_NO_TASKBAR|wxSTAY_ON_TOP)
    wxYield()
        
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
    os.environ['CLASSPATH']=os.pathsep.join(classpath+self.project.classpath())
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
  lh = ViewHandler(app.logview)
  logger.addHandler(lh)
  
  # loadspecified or default workspace
  app.load(sys.argv[1:] or [default.workspace])

  # start app
  app.MainLoop()

  # dipose app
  app.unload()
