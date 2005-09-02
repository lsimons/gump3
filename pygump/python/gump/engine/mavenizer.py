import os, sys
from xml import dom
from xml.dom import minidom
from gump.engine.modeller import _find_element_text
from gump.util.io import VFS

slash = os.sep

def _parse_maven_projects( module_node, download_func, get_vfs):
        """Looks for <project type="maven"> and converts those."""
        #create maven DOM
	try:
		maven_node = _resolve_maven_import( module_node.getAttribute('href'), download_func )
		#parse DOM creating new gumped-maven file 
		#then return file location to be used instead
		#of original maven file
		gumped_maven_href = _parse_maven_file(maven_node, download_func, get_vfs, module_node.getAttribute( 'goal' ))
		return gumped_maven_href
	except:
		print 'maven parse error'
		return '-1'
        
    
def _parse_maven_file( project, download_func, get_vfs, maven_build_goal ):
	"""
	/****************************\
	|   MAVEN PLUGIN FOR GUMP3   |
	\****************************/

	This version of gump will directly bootstrap maven so that a maven 
	project file is added to the gump workspace.  There are still several
	open issues in this project.


	***setting up a maven project***

	In your module description you need to add type=.maven. to the end of 
	that tag.
	EX:
	<module name="db-torque">
	  <url  href="http://db.apache.org/torque/"/>
	  <description>
	    Java based build tool
	  </description>
	  <project href="project.xml" type="maven"/> 
	</module>
	If any specific maven goals need to be added to the build a 
	goal=.maven_goal. may also be added.
	EX:
	<project href="maven_test.xml" type="maven" goal=.jar./> 
	Of course you will need ant and maven in the project build.


	***Setting up maven gump id dependencies***

	Currently there is a mismatch between maven and gump ids(see 
	wiki.apache.org/gump).  The fix right now is a mapping between these 
	mismatches that can be found in gump/util/mavenToGump.conf.  When new
	mismatches are discovered they should be added to this file(follow 
	format already in file).


	***How it works***

	When loader.py is creating the dom tree from the workspace, it checks 
	for the type=.maven. flag.  If one is found mavenizer.py is called.  
	First the maven file will be opened using _resolve_maven_imports.   
	Once the dom is created, a check is made for any extend file included
	in the maven project(maven projects may be defined over more than one 
	project).  _parse_maven_file goes through the maven project descriptor 
	gathering all the information needed/given to create a gump descriptor.
	Once completed a new gumped_maven_project.xml file is created.  This 
	may eventually be all internal but for now it is a visible file that 
	you can check once the gump run is complete.  During the creation of 
	this file any ID mismatch's are handled.  Once creation is complete the
	file is saved and closed, with the file location being passed back to 
	loader.py.  Loader.py then uses that file instead of the original maven
	descriptor to create the gump tree.  When .do-builds is passed by 
	command line the maven-plugin (similar to the ant plugin) is called to 
	build any maven project.

	*Note: mavenizer.py and the maven plugin for gump3 were originally 
	implemented by Justin Merz as the Google 2005 summer of code project.
	"""

	#deal with extended maven projects
	extend = 0;
	hasExtend = _find_element_text(project, "extend")
	if ( hasExtend ):
		extend = 1;
		project_ex = _resolve_maven_import( hasExtend, download_func )
	#get maven id
        id = _find_element_text(project, "id")
	if not id and extend:
        	id = _find_element_text(project_ex, "id")
        #get maven group id
	groupid = _find_element_text(project, "groupId")
	if not groupid and extend:
        	groupid = _find_element_text(project_ex, "groupId")
        name = "%s-%s" % (groupid,id)
	filename = "gumped_%s.xml" % name
	#TODO get module name
	modulename = "module_name"
	#get title
        title = _find_element_text(project, "title")
	if not title and extend:
        	title = _find_element_text(project_ex, "title")
	#get NAG
	nag = _find_element_text(project, "nagEmailAddress")
	if not nag and extend:
        	nag = _find_element_text(project_ex, "nagEmailAdress")
        #get url
	url = _find_element_text(project, "url")
	if not url and extend:
        	url = _find_element_text(project_ex, "url")
	#get repository info	
	cvsweb = _find_element_text(project.getElementsByTagName("repository").item(0), "url")
        #get description
	description = _find_element_text(project, "description")
	if not description and extend:
		description = _find_element_text(project_ex, "description")
        #more repository info
	repository = _find_element_text(project, "gumpRepositoryId")
	if not repository and extend:
		repository = _find_element_text(project_ex, "gumpRepositoryId")
        if not repository:
            # create repository and module
            connection = _find_element_text(project.getElementsByTagName("repository").item(0), "connection")
            connection = connection[4:] # get rid of "scm:"
            provider = connection[:connection.index(':')] # "cvs" or "svn" or "starteam"
            if provider.upper() == "cvs".upper():
                repository2 = connection[connection.index(':')+1:]
                parts = repository2.split(':')
		method = parts[0]	
		user = parts[1][:parts[1].index('@')]
		host = parts[1][parts[1].index('@')+1:]
                path = parts[2]
                module = parts[3]
	# get dependencies
	dependencies = project.getElementsByTagName("dependency");
	if not dependencies and extend:
		dependencies = project_ex.getElementsByTagName("dependency");
	package = _find_element_text(project, "package")
	if not package and extend:
		package = _find_element_text(project_ex, "package")
	#maven build info
	hasBuild = 0
	if _find_element_text(project, "build") or _find_element_text(project_ex, "build"):
		hasBuild = 1
	buildInfo = "<maven "
	# TODO work on this call path
	#sourceDir = _find_element_text(project, "sourceDirectory")
	#if not sourceDir and extend:
	#	sourceDir = _find_element_text(project_ex, "sourceDirectory")
	#if sourceDir:
	#	buildInfo += 'basedir="%s" ' % sourceDir
	target = maven_build_goal
	if target:
		buildInfo += 'target="%s" ' % target
	buildInfo += '/>'
	map = build_map_ID()
	
	#find root of metadata/ where data is coming from
	home_dir = get_vfs
	mavenfile = open("%s%s%s" % (home_dir, slash, filename), "w")
	mavenfile.write( '<?xml version="1.0" encoding="UTF-8"?> \n' )
	mavenfile.write( license() )
	mavenfile.write( '  <project name="%s">\n\n' % name)
	if url:
		mavenfile.write( '    <url href="%s"/>\n' % url );
	if description:
		mavenfile.write( '    <description>\n')
		mavenfile.write( '      %s \n' % description)
		mavenfile.write( '    </description>\n\n')
#	if modulename:
#		mavenfile.write( '    <module name="%s">\n\n' % modulename)
	if hasBuild:
		mavenfile.write( '    %s\n\n' % buildInfo )
	if package:
		mavenfile.write( '    <package>%s</package>\n' % package )
	if repository:
		mavenfile.write( '    <repository name="%s"/>\n\n' % repository)
	elif repository2:
		mavenfile.write( '    <repository name="%s" type="%s">\n' % ( module, provider ))
		mavenfile.write( '      <title>%s</title>\n' % module )
		if cvsweb:
			mavenfile.write( '      <cvsweb>%s</cvsweb>\n' % cvsweb )
		mavenfile.write( '      <redistributable/>\n\n' )
		if host:
			mavenfile.write( '      <hostname>%s</hostname>\n' % host )
		if method:
			mavenfile.write( '      <method>%s</method>\n' % method )
		if user:
			mavenfile.write( '      <user>%s</user>\n' % user )
			mavenfile.write( '      <password>%s</password>\n' % user)
		if path:
			mavenfile.write( '      <path>%s</path>\n' % path )
		mavenfile.write( '    </repository>\n\n')
	mavenfile.write( '    <depend project="maven"/>\n')
	for dependency in dependencies:
		depend = _find_element_text( dependency, "artifactId" )
		if map:
			depend = map_ID( depend, map )
		if depend:
			mavenfile.write( '    <depend project="%s"/>\n' % depend)
	mavenfile.write( ' \n')
	if nag:
		mavenfile.write( '    <nag from="Gump Integration Build &lt;general@gump.apache.org&gt;" to="%s"/>\n\n' % nag); 
	mavenfile.write( ' \n')
	mavenfile.write( '  </project>\n')
	mavenfile.close()
                            
	return filename
    
def _resolve_maven_import( href, download_func):
	#opens maven files for reading
	try:
		stream = download_func(href)
		maven_dom = minidom.parse(stream)
		maven_dom.normalize()
		return maven_dom
	except:
		print "found maven file %s, but could not open!" % href

def build_map_ID():
	#open config file, set up dictonary
	try:
		mycwd = os.getcwd()
		IDfile = open("%s%spython%sgump%sutil%smavenToGump.conf" % (mycwd, slash, slash, slash, slash) , "r")
		relation = IDfile.readline()
		parts = relation.split(',')
		IDmap = { parts[0]:parts[1][1:parts[1].index(':')] }
		while( relation ):
			parts = relation.split(',')
			IDmap[parts[0]] = parts[1][1:parts[1].index(':')]
			relation = IDfile.readline()
		return IDmap
	except:
		print 'ERROR building maven to gump ID map'
		return 0

def map_ID( artifactID, map ):	
	if map.has_key(artifactID):
		projectID = map[artifactID]
		return projectID
	return artifactID

def license():
	#for printing apache license
	license = '<!-- \n'
	license += '/* \n'
	license += ' * Copyright 2001-2004 The Apache Software Foundation. \n'
	license += ' * \n'
	license += ' * Licensed under the Apache License, Version 2.0 (the "License"); \n'
	license += ' * you may not use this file except in compliance with the License. \n'
	license += ' * You may obtain a copy of the License at \n'
	license += ' * \n'
	license += ' *      http://www.apache.org/licenses/LICENSE-2.0 \n'
	license += ' * \n'
	license += ' * Unless required by applicable law or agreed to in writing, software \n'
	license += ' * distributed under the License is distributed on an "AS IS" BASIS, \n'
	license += ' * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. \n'
	license += ' * See the License for the specific language governing permissions and \n'
	license += ' * limitations under the License. \n'
	license += ' */ \n'
	license += ' --> \n'
	return license
		
