#!/usr/bin/python
"""
	Gump core functionality. It contains a sax dispatcher tool, a dependency
	walker, and an object model (GOM) which is built from an xmlfile using
	the sax dispatcher.

	The idea is that a subclass of GumpBase is used for each of the various
	xml tags which can appear in a gump profile, with a saxdispatcher
	generating a tree of GumpBase objects from the profile, dynamically
	merging as it finds href references.

	You can then use the dependencies() method to get an ordered, flat vector
	of the projects in the profile.
"""

import os.path, os, time, urllib, urlparse, shutil, string, os.path
from xml.sax import parse
from xml.sax.handler import ContentHandler
from gumputil import *
from gumpconf import *
  
#########################################################################
#	  SAX Dispatcher Mechanism                                          #
#########################################################################

# a stack of active xml elements
class SAXDispatcher(ContentHandler):
  def __init__(self,file,name,cls):
    self.topOfStack=DocRoot(name,cls)
    self.elementStack=[self.topOfStack]
    parse(file,self)
    self.docElement=self.topOfStack.element
    
  def startElement (self, name, attrs):
    if self.topOfStack: self.topOfStack=self.topOfStack.startElement(name,attrs)
    self.elementStack.append(self.topOfStack);
    
  def characters(self, string):
    if self.topOfStack: self.topOfStack.characters(string)
    
  def endElement (self, name):
    del self.elementStack[-1]
    self.topOfStack=self.elementStack[-1]

# Run a file through a saxdispatcher, building a GOM in memory from
# the xml file. Return the generated GOM
def load(file):
  if not os.path.exists(file):
    gumpMessage('Error',
                'workspace '+file+' not found',
                '  You need to specify a valid workspace for Gump to run\n'
                '  If you are new to Gump, simply copy minimal-workspace.xml\n'
                '  to a file with the name of your computer (mycomputer.xml)\n'
                '  and rerun this program.'
                )

    raise IOError, 'workspace '+file+' not found'
    
  workspace=SAXDispatcher(file,'workspace',Workspace).docElement
  workspace.complete()
  for module in Module.list.values(): module.complete(workspace)
  for project in Project.list.values(): project.complete(workspace)
  return workspace

#########################################################################
#		  Base classes for the Gump object model		#
#                                                                       #
# This is actually where most of the logic and complexity is handled,   #
# allowing the actual model to be rather simple and compact. All        #
# elements of the GOM should extend GumpBase or a subclass of GumpBase. #
#########################################################################
# Base class for the entire Gump object model.  Attributes become
# properties.  Characters become the string value of the element.
#
# An internal attribute with name '@text' is used for storing all
# the characters (as opposed to xml elements and xml attributes).
class GumpBase(object):
  def __init__(self,attrs):
    # parse out '@@DATE@@'
    for (name,value) in attrs.items():
      self.__dict__[name]=value.replace('@@DATE@@',default.date)
      
    # setup internal character field
    if not '@text' in self.__dict__: self.init()
    self.__dict__['@text']=''
  
  def startElement(self, name, attrs):
    # possibility to customize behaviour based on
    # type of the element
    # TODO: can this difference just go here?
    try:
      attr=self.__getattribute__(name)
      if isinstance(attr,Single): return attr(attrs)
      if isinstance(attr,Multiple): return attr(attrs)
    except:
      # print self.__class__, name
      pass

  
  def characters(self,string):
    self.__dict__['@text']+=string

  
  def __setitem__(self,name,value): 
    self.__dict__[name]=value

  
  def __getitem__(self,name): 
    if name in self.__dict__: return self.__dict__[name]

  
  def __getattr__(self,name): 
    pass

  
  def __str__(self): 
    return self.__dict__['@text'].strip()

  
  def init(self):
    pass

# Document root: workspaces and targets of hrefs
class DocRoot(GumpBase):
  
  def __init__(self,name,cls):
    GumpBase.__init__(self,{})
    self.name=name
    self.cls=cls
    self.element=None

  
  def startElement(self, name, attrs):
    if name<>self.name: 
      raise "Incorrect element, expected %s, found %s" % (self.name,name)
    self.element=self.cls(attrs)
    return self.element

# Named elements (e.g., project,module,repository).  Supports href and
# maintains a list of elements.  Duplicate names get merged.  Classes
# declared of this type must declare a static list property.
class Named(GumpBase):
  def __new__(cls,attrs):
    href=attrs.get('href')
    
    if href: 
      newHref=gumpCache(href)
      if default.debug: print 'opening: ' + newHref + '\n'
      element=SAXDispatcher(open(newHref),cls.__name__.lower(),cls).docElement
    else:
      name=attrs.get('name')      
      try:
          element=cls.list[name]
      except:
          element=GumpBase.__new__(cls,attrs)
      if name: cls.list[name]=element
    return element

# properties which are only ever expected to hold a single value 
class Single(object):
  def __init__(self,cls=GumpBase):
    self.delegate=None
    self.cls=cls


  def __call__(self,attrs):
    if self.delegate: 
      self.delegate.__dict__.update(dict(attrs))
    else:
      self.delegate=self.cls(attrs)
    return self.delegate


  def __getattr__(self,name):
    if self.delegate: 
      try:
        return self.delegate.__getattribute__(name)
      except:
        return self.delegate[name]


  def __str__(self):
    if self.delegate: return self.delegate.__str__()
    return ''


  def __nonzero__(self):
    return self.delegate

# properties which can hold multiple instances
class Multiple(list):
  def __init__(self,cls=GumpBase):
    list.__init__(self)
    self.cls=cls


  def __call__(self,attrs):
    result=self.cls(attrs)
    self.append(result)
    return result

#########################################################################
#			    Gump Object Model
#
#                                                                       #
# All intelligence and functionality is provided in the base classes    #
# above, allowing the actual model to be rather simple and compact.     #
#########################################################################

# represents a <workspace/> element
class Workspace(GumpBase):
  def init(self): 
    self.property=Multiple(Property)
    self.project=Multiple(Project)
    self.module=Multiple(Module)
    self.repository=Multiple(Repository)
    self.profile=Multiple(Profile)

  # provide default elements when not defined in xml
  def complete(self):
    if not self['banner-image']:
      self['banner-image']="http://jakarta.apache.org/images/jakarta-logo.gif"
    if not self['banner-link']: self['banner-link']="http://jakarta.apache.org"
    if not self.logdir: self.logdir=self.basedir+"/log"
    if not self.cvsdir: self.cvsdir=self.basedir+"/cvs"
    if not self.pkgdir: self.pkgdir=self.basedir
    if self.deliver:
      if not self.scratchdir: self.scratchdir=self.basedir+"/scratch"

# represents a <profile/> element
class Profile(Named):
  list={}

  def init(self): 
    self.project=Multiple(Project)
    self.module=Multiple(Module)
    self.repository=Multiple(Repository)

# represents a <module/> element
class Module(Named):
  list={}

  def init(self): 
    self.cvs=Single()
    self.url=Single()
    self.description=Single()
    self.redistributable=Single()
    self.project=Multiple(Project)

  # provide default elements when not defined in xml
  def complete(self,workspace):
    self.srcdir=os.path.join(str(workspace.basedir),self.srcdir or self.name)
    for project in self.project: 
      if not project.module: project.module=self.name

# represents a <repository/> element
class Repository(Named):
  list={}

  def init(self): 
    self['home-page']=Single()
    self.title=Single()
    self.cvsweb=Single()
    self.root=Single(RepositoryRoot)
    self.redistributable=Single()

# represents a <root/> element within a <repository/> element
class RepositoryRoot(GumpBase):

  def init(self): 
    self.method=Single()
    self.user=Single()
    self.password=Single()
    self.hostname=Single()
    self.path=Single()

# represents a <project/> element
class Project(Named):
  list={}

  def init(self): 
    self.ant=Single(Ant)
    self.script=Single()
    self.depend=Multiple(Depend)
    self.description=Single()
    self.url=Single()
    self.option=Multiple(Depend)
    self.property=Single(Property)
    self.package=Multiple()
    self.jar=Multiple(Jar)
    self.home=Single(Home)
    self.license=Single()
    self.nag=Multiple(Nag)
    self.javadoc=Single(Javadoc)
    self.junitreport=Single(JunitReport)
    self.work=Multiple(Work)
    self.mkdir=Multiple(Mkdir)
    self.redistributable=Single()

  # provide default elements when not defined in xml
  def complete(self,workspace):

    # compute home directory
    if self.home and isinstance(self.home,Single):
      if self.home.nested:
        srcdir=Module.list[self.module].srcdir
        self.home=srcdir +'/' + self.home.nested

    # complete properties
    if self.ant: self.ant.complete(self)

# represents an <ant/> element
class Ant(GumpBase): 
  def init(self): 
    self.depend=Multiple(Depend)
    self.property=Multiple(Property)
    self.jvmarg=Multiple()

  # provide default elements when not defined in xml
  def complete(self,project):
    for property in self.property: property.complete(project)

# represents a <nag/> element
class Nag(GumpBase): 
  def init(self): 
    self.regexp=Multiple()

# represents a <javadoc/> element
class Javadoc(GumpBase): 
  def init(self): 
    self.description=Multiple()

# represents a <property/> element
class Property(GumpBase): 

  # provide default elements when not defined in xml
  def complete(self,project):
    if self.reference=='home':
      self.value=Project.list[self.project].home
    if self.reference=='srcdir':
      module=Project.list[self.project].module
      self.value=Module.list[module].srcdir


# TODO: set up the below elements with defaults using complete()

# represents a <depend/> element
class Depend(GumpBase): pass

# represents a <description/> element
class Description(GumpBase): pass

# represents a <home/> element
class Home(GumpBase): pass

# represents a <jar/> element
class Jar(GumpBase): pass

# represents a <junitreport/> element
class JunitReport(GumpBase): pass

# represents a <mkdir/> element
class Mkdir(GumpBase): pass

# represents a <work/> element
class Work(GumpBase): pass

#########################################################################
#                     Utility functions                                 #
#########################################################################

# sort project dependencies of a project and returns build sequence
def dependencies(root, #string
         projects, #hashtable
         state = {}, #hashtable
         visiting= [], #stack
         ret = [], #vector
         internalProjects = [],#vector
         indent = ''):

        VISITING = 0
        VISITED = 1
        indent=indent+' '
        state[root] = VISITING
        visiting.append(root)
        project=Project.list[root]

        # Make sure we exist
        if not project:
            print  "Project `" + root + "' does not exist in this project. ";
            visiting.pop();
            if visiting:
                parent = visiting[:];
                print ("\nIt is needed for project `" + parent + "'.");
                raise

        if default.debug:
          print '------------------------- VISITING ' + root
          
        for depend in project.depend:#+project.option:
          cur = depend.project
          print indent + '(' + root + ' -- dep --> ' + cur
          
          try:
            p=Project.list[depend.project]
          except:
            print 'ERROR: Cannot find ' + depend.project
            print '  referenced by ' + project.name
            print '  that has the following dependencies:'
            for dep in project.depend:
              print '   ->' + dep.project
            print
            raise
            
          #print state.keys()
          
          if not state.has_key(cur):
            # Not been visited
            dependencies(cur, projects, state, visiting, ret, internalProjects, indent);
          elif (state[cur] == VISITING):
            # Currently visiting this node, so have a cycle
            print 'Circular exception'
            print 'current node: ' + cur
            print 'visited stack: ' + visiting
            raise


        p = visiting.pop();
        if not (root == p):
            print 'Unexpected internal error: expected to pop ' + root + ' but got ' + p
            raise

        print '------------------------- VISITED ' + root
        state[root] = VISITED

        ret.append(project)

        return ret
      
#########################################################################
#			    Demonstration code				                        #
#########################################################################

if __name__=='__main__':
  print "*** starting ***"
  os.chdir(dir.base)
  workspace=load('rubix.xml')

  print
  print "*** workspace ***"
  print
  print 'basedir:\t', workspace.basedir
  print 'pkgdir:\t\t', workspace.pkgdir
  for property in workspace.property: print 'Property:\t',property.name,property.value

  print
  print "*** JDBC ***"
  print
  jdbc=Project.list['jdbc']
  print 'Package:\t', jdbc.package
  for jar in jdbc.jar: print 'Jar:\t\t', jar.name, jar.id

  print
  print "*** Junit ***"
  print

  junit=Module.list['junit']
  print 'Description:\t', junit.description
  print 'Url:\t\t', junit.url.href
  print 'Cvs:\t\t', junit.cvs.repository

  junit=Project.list['junit']
  print 'Package:\t', junit.package[0]
  for depend in junit.depend: print 'Depend:\t\t',depend.project
  for jar in junit.jar: print 'Jar:\t\t', jar.name, jar.id
  
  print
  print "*** Gump ***"
  print
  gump=Project.list['gump']
  for depend in gump.depend: print 'Depend:\t\t',depend.project
  ant=gump.ant
  for property in ant.property: print 'Property:\t',property.name,property.value
  
  print
  print "*** krysalis-ruper-test ***"
  print
  krysalisrupertest=Project.list['krysalis-ruper-test']
  for depend in krysalisrupertest.depend: print 'Depend:\t\t',depend.project
  ant=krysalisrupertest.ant
  for property in ant.property: print 'Property:\t',property.name,property.value



##
##templateDef = """
##<HTML>
##<HEAD><TITLE>$gump.ant</TITLE></HEAD>
##<BODY>
##
#### this is a single-line Cheetah comment and won't appear in the output
###* This is a multi-line comment and won't appear in the output
##    blah, blah, blah 
##*#
##</BODY>
##</HTML>"""
##nameSpace = {'gump': gump, 'contents': 'Hello World!'}
###t = Template(templateDef, searchList=[nameSpace])
##t = Template(templateDef)
##t.gump=gump
##print t


