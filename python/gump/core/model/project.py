#!/usr/bin/env python

# Copyright 2003-2004 The Apache Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

    The model for a 'Project'
    
"""

from time import localtime, strftime, tzname

from gump.model.state import *
from gump.model.object import ModelObject, NamedModelObject
from gump.model.misc import Jar, Assembly, BaseOutput, \
                            Resultable, Positioned, \
                            Mkdir, Delete, JunitReport, Work, \
                            AddressPair
from gump.model.stats import Statable, Statistics
from gump.model.property import Property
from gump.model.builder import Ant,NAnt,Maven,Script
from gump.utils import getIndent
from gump.utils.file import *
from gump.model.depend import *
from gump.utils.note import transferAnnotations, Annotatable
import gump.process.command
from gump.utils.domutils import *


class Project(NamedModelObject, Statable, Resultable, Dependable, Positioned):
    
    UNSET_LANGUAGE=0
    JAVA_LANGUAGE=1
    CSHARP_LANGUAGE=2
    
    LANGUAGE_MAP= {
        'java':JAVA_LANGUAGE,
        'csharp':CSHARP_LANGUAGE
    }

    """ A Single project """
    def __init__(self,name,xml,owner):
    	NamedModelObject.__init__(self,name,xml,owner)
    	
    	Statable.__init__(self)
    	Resultable.__init__(self)
    	Dependable.__init__(self)
    	Positioned.__init__(self)
    	
    	# Navigation
        self.module=None # Module has to claim ownership
        self.workspace=None
    	
    	self.home=None
    	self.basedir=None
    	
    	self.license=None
        
        self.languageType=Project.JAVA_LANGUAGE    	
        
    	self.affectedProjects=[]
        
    	#############################################################
    	#
    	# Sub-Components
    	#
    	self.ant=None
        self.nant=None
    	self.maven=None
    	self.script=None

    	self.works=[]
    	self.mkdirs=[]
    	self.deletes=[]
    	self.reports=[]
        self.notifys=[]
    
        self.url=None
        self.desc=''
        
        self.redistributable=False
        self.packageMarker=None
        self.jvmargs=gump.process.command.Parameters()
        self.packageNames=None
        
    	#############################################################
    	# Outputs (Jars, Assemblies)
    	#
        self.outputs={}      
        
    	#############################################################
    	# Misc
    	#        
        self.honoraryPackage=False        
        self.built=False
        
    def __del__(self):
        NamedModelObject.__del__(self)
        Statable.__del__(self)
        Resultable.__del__(self)
        Dependable.__del__(self)
        Positioned.__del__(self)
        
    def hasNotifys(self):
        """
        Does this project have any notification addresses, and if not
        does the module?
        
        boolean true if some
        """
        if self.notifys: return True
        if self.module: return self.module.hasNotifys()
        return False
        
    def getNotifys(self):
        """
        	Return the list of notification addresses for this project
        	but if none, see if the module has any.
        """
        if not self.notifys: 
            if self.module:
                return self.module.getNotifys()
        return self.notifys
        
    def getArtifactGroup(self):
        """
        What does this projects artifacts group under?
        Ask the module...
        
        Return String
        """
        return self.getModule().getArtifactGroup()
        
    def hasAnt(self):
        if self.ant: return True
        return False
        
    def hasNAnt(self):
        if self.nant: return True
        return False
        
    def hasMaven(self):
        if self.maven: return True
        return False
        
    def hasScript(self):
        if self.script: return True
        return False
    
    def getAnt(self):
        return self.ant
        
    def getNAnt(self):
        return self.nant
        
    def getMaven(self):
        return self.maven
        
    def getScript(self):
        return self.script
    
    def hasUrl(self):
        if self.url or self.getModule().hasUrl(): return True
        return False
            
    def getUrl(self):
        return self.url or self.getModule().getUrl()            
        
    def hasDescription(self):
        if self.desc or self.getModule().hasDescription(): return True
        return False
        
    def getDescription(self):
        return self.desc or self.getModule().getDescription()    
        
    def getLimitedDescription(self, limit=60):
        desc=self.getDescription()    
        if len(desc) > limit:
            desc=desc[:limit]
            desc+='...'        
        return desc
        
    def getMetadataLocation(self):
        return self.metadata or self.getModule().getMetadataLocation()
                     
    def getMetadataViewUrl(self):
        if self.metadata:
            location=self.metadata
            if location.startswith('http'): return location
            # :TODO: Make configurable
            return 'http://cvs.apache.org/viewcvs.cgi/gump/' + location
        return self.getModule().getMetadataViewUrl()
                        
    def getViewUrl(self):
        # :TODO: if a basedir then offset?
        return self.getModule().getViewUrl()
            
    def addOutput(self,output):
        self.outputs[output.getName()]=output
        
    def getOutputCount(self):
        return len(self.outputs)
        
    def hasOutputWithId(self,id):
        return self.outputs.has_key(id)
        
    def hasLicense(self):
        if self.license: return True
        return False
        
    def getLicense(self):
        return self.license
        
    def getDeletes(self): return self.deletes
    def getMkDirs(self): return self.mkdirs
    def getWorks(self): return self.works
        
    def hasOutputs(self):
        if self.outputs: return True
        return False
        
    def getOutputs(self):
        return self.outputs.values()

    def hasAnyOutputs(self):
        """
        Does this project generate outputs (currently JARs)
        """
        return self.hasOutputs() or self.hasLicense()
        
    def hasPackageNames(self):
        if self.packageNames: return True
        return False
        
    def getPackageNames(self):
        return self.packageNames
        
    def getOutputAt(self,index):
        return self.outputs.values()[index]
                
    def isRedistributable(self):
        return self.redistributable or (self.module and self.module.isRedistributable())
        
    def wasBuilt(self):
        """ Was a build attempt made? """
        return self.built
        
    def setBuilt(self,built=True):
        self.built=built
        
    def hasReports(self):
        if self.reports: return True
        return False
        
    def getReports(self):
        return self.reports
        
    def getFOGFactor(self):
        return self.getStats().getFOGFactor()
        
    def getHistoricalOddsOfSuccess(self):
        return self.getStats().getHistoricalOddsOfSuccess()
        
    # Only modules get Modified.
    def getLastModified(self):
        return self.getModule().getStats().getLastModified()  
        
    def countAffectedProjects(self):
        return len(self.affectedProjects)
        
    def getAffectedProjects(self):
        return self.affectedProjects
        
    def addAffected(self,project):
        self.affectedProjects.append(project)
        self.affectedProjects.sort()
        
    def propagateErrorStateChange(self,state,reason,cause,message):
        
        #
        # Mark depend*ee*s as failed for this cause...
        # Warn option*ee*s
        #
        for dependee in self.getDirectDependees():  
    
            # This is a backwards link, so use the owner
            dependeeProject=dependee.getOwnerProject()
        
            if dependee.isOptional():
                dependeeProject.addInfo("Optional dependency " + self.name + " " + message)
            else:
                dependee.addInfo("Dependency " + self.name + " " + message)
                dependeeProject.changeState(STATE_PREREQ_FAILED,reason,cause)
    #
    # We have a potential clash between the <project package attribute and
    # the <project <package element. The former indicates a packages install
    # the latter the (Java) package name for the project contents. 
    #                                      
    def isPackaged(self):
        return self.isPackageMarked() or self.honoraryPackage
    
    def isPackageMarked(self):
        if self.packageMarker: return True
        return False        
        
    def getPackageMarker(self):   
        return self.packageMarker
                  
    def setHonoraryPackage(self,honorary=True):
        self.honoraryPackage=honorary
    
    def isGumped(self):
        return (not self.isPackaged()) and self.hasBuilder()
        
    # provide elements when not defined in xml
    def complete(self,workspace): 
        if self.isComplete(): return

        if not self.inModule():
            self.addWarning("Not in a module")
            return
         
        # :TODO: hacky   
        self.workspace=workspace
        
        # Import overrides from DOM
        transferDomInfo(self.element, self, {})        
    
        # Somebody overrode this as a package
        if self.hasDomAttribute('package'):
            self.packageMarker=self.getDomAttributeValue('package')
        
        # Packaged Projects don't need the full treatment..
        packaged=self.isPackaged()

        # Import any <ant part [if not packaged]
        if self.hasDomChild('ant') and not packaged:
            self.ant = Ant(self.getDomChild('ant'),self)
            
            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.ant, self)
        
        # Import any <nant part [if not packaged]
        if self.hasDomChild('nant') and not packaged:
            self.nant = NAnt(self.getDomChild('nant'),self)
            
            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.nant, self)
        
        # Import any <maven part [if not packaged]
        if self.hasDomChild('maven') and not packaged:
            self.maven = Maven(self.getDomChild('maven'),self)
            
            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.maven, self)
            
        # Import any <script part [if not packaged]
        if self.hasDomChild('script') and not packaged:
            self.script = Script(self.getDomChild('script'),self)
            
            # Copy over any XML errors/warnings
            # :TODO:#1: transferAnnotations(self.xml.script, self)
        
        # Set this up to be the base directory of this project,
        # if one is set
        self.basedir = os.path.abspath(os.path.join(	\
                            self.getModule().getWorkingDirectory() or dir.base,	\
                            self.getDomAttributeValue('basedir','')))
         
        # Compute home directory
        if self.isPackaged():
            # Installed below package directory
            if self.isPackageMarked():
                self.home=os.path.abspath(
                    os.path.join(
                        workspace.pkgdir,
                        self.getDomAttributeValue('package')))
            else:
                self.home=os.path.abspath(workspace.pkgdir)
        elif self.hasDomChild('home'):
            home=self.getDomChild('home')
            if hasDomAttribute(home,'nested'):
                nested=self.expandVariables(
                    getDomAttributeValue(home,'nested'))
                self.home=os.path.abspath(
                    os.path.join(self.getModule().getWorkingDirectory(),
                                    nested))
            elif hasDomAttribute(home,'parent'):
                parent=self.expandVariables(
                    getDomAttributeValue(home,'parent'))
                self.home=os.path.abspath(
                    os.path.join(workspace.getBaseDirectory(),parent))
            else:
                message=('Unable to complete project.home for %s [not nested/parent] : %s') \
                            % (self.name, home)
                self.addError(message)
                log.warning(message)
                self.home=None        
        else:
            if self.module:
                module=self.getModule()    
                self.home=os.path.abspath(module.getWorkingDirectory())
            else:
                self.home=os.path.abspath(
                            os.path.join(
                                workspace.getBaseDirectory(),
                                self.name))
        # Forget how this could be possible...
        #else:
        #    message='Unable to complete project.home for: ' + self.name 
        #    self.addError(message)
        #    self.home=None
        
        
        # The language type java or CSharp or ...
        if self.hasDomAttribute('language'):
            self.setLanguageTypeFromString(self.getDomAttributeValue('language'))
        

        # Extract license 
        if self.hasDomChild('license'):
            license=self.getDomChild('license')
            if hasDomAttribute(license,'name'):
                self.license = getDomAttributeValue(license,'name')
            else:
                self.addError('Missing \'name\' on <license')
        
        #
        # Resolve jars/assemblies/outputs        
        #
        outputTypes={'jar':Jar, 'assembly':Assembly, 'output':BaseOutput}
        
        for (tag, clazz) in outputTypes.iteritems():
            for tdom in self.getDomChildIterator(tag):
                name=self.expandVariables(
                        getDomAttributeValue(tdom,'name'))
                    
                if self.home and name:  
                    output=clazz(name,tdom,self)
                    output.complete()
                    output.setPath(os.path.abspath(os.path.join(self.home,name)))
                    self.addOutput(output)
                else:
                    self.addError('Missing \'name\' on <' + tag)
                
                
        # Fix 'ids' on all Jars/Assemblies/Outputs which don't have them
        if self.hasOutputs():
            if 1 == self.getOutputCount():
                output=self.getOutputAt(0)
                if not output.hasId():
                    self.addDebug('Sole output [' + os.path.basename(output.getPath()) + '] identifier set to project name')
                    output.setId(self.getName())    
            else:
                # :TODO: A work in progress, not sure how
                # we ought 'construct' ids.
                for output in self.getOutputs():
                    if not output.hasId():
                        basename=os.path.basename(output.getPath())
                        newId=basename
                        # Strip off .jar or .lib (note: both same length)
                        if newId.endswith('.jar') or newId.endswith('.lib'):
                            newId=newId[:-4]
                        # Strip off -@@DATE@@
                        datePostfix='-' + str(default.date_s)
                        if newId.endswith(datePostfix):
                            reduction=-1 * len(datePostfix)
                            newId=newId[:reduction]
                        # Assign...
                        self.addDebug('Output [' + basename + '] identifier set to output basename: [' + newId + ']')    
                        output.setId(newId)
        
        # Grab all the work
        for w in self.getDomChildIterator('work'):
            work=Work(w,self)
            work.complete()
            self.works.append(work)

        # Grab all the mkdirs
        for m in self.getDomChildIterator('mkdir'):
            mkdir=Mkdir(m,self)
            mkdir.complete()
            self.mkdirs.append(mkdir)

        # Grab all the deleted
        for d in self.getDomChildIterator('delete'):
            delete=Delete(d,self)
            delete.complete()
            self.deletes.append(delete)

        # Grab all the reports (junit for now)
        if self.hasDomChild('junitreport'):
            junitreport=self.getDomChild('junitreport')
            report=JunitReport(junitreport,self)
            report.complete()
            self.reports.append(report)
            
        # Grab all notifications
        for notifyEntry in self.getDomChildIterator('nag'):
            # Determine where to send
            toaddr=getDomAttributeValue(notifyEntry,'to',workspace.administrator)
            fromaddr=getDomAttributeValue(notifyEntry,'from',workspace.email)   
            self.notifys.append(
                    AddressPair(
                        getStringFromUnicode(toaddr),
                        getStringFromUnicode(fromaddr)))  
        
        # Build Dependencies Map [including depends from <ant|maven/<property/<depend
        if not packaged:
            (badDepends, badOptions) = self.importDependencies(workspace)                        

        # Expand <ant <depends/<properties...
        if self.ant: self.ant.expand(self,workspace)
        if self.maven: self.maven.expand(self,workspace)
        if self.script: self.script.expand(self,workspace)

        if not packaged:
            # Complete dependencies so properties can reference the,
            # completed metadata within a dependent project
            for dependency in self.getDirectDependencies():
                depProject=dependency.getProject()
                if not depProject.isComplete():
                    depProject.complete(workspace)

            self.buildDependenciesMap(workspace)                        
        
        if self.hasDomChild('url'):
            url=self.getDomChild('url')
            self.url=getDomAttributeValue(url,'href')
            
        if self.hasDomChild('description'):
            self.desc=self.getDomChildValue('description')   
    
        for jvmarg in self.getDomChildIterator('jvmarg'):
            if hasDomAttribute(jvmarg,'value'):                
                self.jvmargs.addParameter(getDomAttributeValue(jvmarg,'value'))
            else:
                log.error('Bogus JVM Argument w/ Value')            
            
        #
        # complete properties
        #
        if self.ant: 
            self.ant.complete(self,workspace)
            transferAnnotations(self.ant, self)  
            
        if self.maven: 
            self.maven.complete(self,workspace)
            transferAnnotations(self.maven, self)    
            
        if self.script: 
            self.script.complete(self,workspace)
            transferAnnotations(self.script, self)              
            
        if not packaged:    
            #
            # TODO -- move these back?
            #
            if badDepends or badOptions: 
                for xmldepend in badDepends:
                    self.changeState(STATE_FAILED,REASON_CONFIG_FAILED)
                    self.addError("Bad Dependency. Project: " \
                            + getDomAttributeValue(xmldepend,'project') + " unknown to *this* workspace")

                for xmloption in badOptions:                
                    self.addWarning("Bad *Optional* Dependency. Project: " \
                            + getDomAttributeValue(xmloption,'project') + " unknown to *this* workspace")
        else:
            self.addInfo("This is a packaged project, location: " + self.home)        
                                    
        # Copy over any XML errors/warnings
        # :TODO:#1: transferAnnotations(self.xml, self)  
        
        #if not self.home:
        #    raise RuntimeError, 'A home directory is needed on ' + `self`
        
        # Existence means 'true'
        self.redistributable=self.hasDomChild('redistributable')       
        
        # Store any 'Java Package names'
        for pdom in self.getDomChildIterator('package'):
            packageName=getDomTextValue(pdom)
            if packageName:
                if not self.packageNames:
                    self.packageNames=[]
                if not packageName in self.packageNames:
                    self.packageNames.append(packageName)
                    
        # Close down the DOM...
        self.shutdownDom()       
        
        # Done, don't redo
        self.setComplete(True)

    def importDependencies(self,workspace):        
        badDepends=[]
        # Walk the DOM parts converting
        for ddom in self.getDomChildIterator('depend'):
            dependProjectName=getDomAttributeValue(ddom,'project')
            if workspace.hasProject(dependProjectName):
                dependProject=workspace.getProject(dependProjectName)
                
                # Import the dependency
                dependency=importDomDependency(self, dependProject, ddom, 0)
                                
                # Add a dependency
                self.addDependency(dependency)
            else:
                badDepends.append(ddom)    
                
        # Walk the XML parts converting
        badOptions=[]
        for odom in self.getDomChildIterator('option'):
            optionProjectName=getDomAttributeValue(odom,'project')
            if workspace.hasProject(optionProjectName):
                optionProject=workspace.getProject(optionProjectName)
                                
                # Import the dependency
                dependency=importDomDependency(self, optionProject, odom, 1)
                                
                # Add a dependency
                self.addDependency(dependency)                    
            else:
                badOptions.append(odom)

        return (badDepends, badOptions)
        
    def hasBaseDirectory(self):
        if self.basedir: return True
        return False
        
    def getBaseDirectory(self):
         return self.basedir
         
    def hasHomeDirectory(self):
        if self.home: return True
        return False
        
    def getHomeDirectory(self):
        return self.home
        
    def inModule(self):
        return hasattr(self,'module') and self.module
        
    def setModule(self,module):
        if self.module:
            raise RuntimeError, 'Project [' + self.name + '] already has a module set'
        self.module=module
        
    def getModule(self):
        if not self.inModule(): raise RuntimeError, 'Project [' + self.name + '] not in a module.]'
        return self.module 
        
    def getWorkspace(self):
        return self.workspace
        
    def hasBuilder(self):
        """
        Does this project have a builder?
        """
        hasBuild=0
        # I.e has an <ant or <script element
        if self.ant or self.script or self.maven: hasBuild=1    
        return hasBuild      
        
    def dump(self, indent=0, output=sys.stdout):
        """ 
        Display the contents of this object 
        """
        i=getIndent(indent)
        i1=getIndent(indent+1)
        output.write(i+'Project: ' + self.getName() + '\n')
        NamedModelObject.dump(self, indent+1, output)
                
        if self.isPackageMarked():
            output.write(i1+'Packaged: ' + self.getPackageMarker() + '\n')
        
        Dependable.dump(self,indent,output)
                        
        if self.ant:
            self.ant.dump(indent+1,output)
        if self.maven:
            self.maven.dump(indent+1,output)
        if self.script:
            self.script.dump(indent+1,output)
            
        for work in self.works:
            work.dump(indent+1,output)
            
        for out in self.getOutputs():
            out.dump(indent+1,output)
            
    def getAnnotatedOutputsList(self): 
        """
        Return a list of the outputs this project generates
        """
        outputs=[]
        for output in self.getOutputs():
            path=output.getPath()
            outputs.append(gump.language.path.AnnotatedPath(output.getId(),path,self,None,"Project output"))                    
        return outputs
                        
    def setLanguageTypeFromString(self,lang=None):
        try:
            self.languageType=Project.LANGUAGE_MAP[lang]
        except:
            message='Language %s not in supported %s.' % (lang, Project.LANGUAGE_MAP.keys())
            self.addWarning(message)
            log.warning(message)
            
    def getLanguageType(self):
        return self.languageType
        
    def setLanguageType(self,langType):
        self.languageType=langType

class ProjectStatistics(Statistics):
    """Statistics Holder"""
    def __init__(self,projectName):
        Statistics.__init__(self,projectName)

    def getKeyBase(self):
        return 'project:'+ self.name        

                                                
class ProjectSummary:
    """ Contains an overview """
    def __init__(self,	\
                    projects=0,successes=0,failures=0,	\
                    prereqs=0,noworks=0,packages=0,	\
                    others=0,statepairs=None):
                        
        # Counters
        self.projects=projects
        self.successes=successes
        self.failures=failures
        self.prereqs=prereqs
        self.noworks=noworks
        self.packages=packages
        self.others=others
        self.statepairs=statepairs
        
        # Percentages
        self.overallPercentage=0
        self.successesPercentage=0
        self.failuresPercentage=0
        self.prereqsPercentage=0
        self.noworksPercentage=0
        self.packagesPercentage=0
        self.othersPercentage=0
        
        #
        if not self.statepairs: self.statepairs=[]
        
        self.calculatePercentages()
        
    def addState(self,state):            
        # Stand up and be counted
        if state.isSuccess():
            self.successes+=1
        elif state.isPrereqFailed():
            self.prereqs+=1
        elif state.isFailed():
            self.failures+=1
        elif state.isUnset():
            self.noworks+=1
        elif state.isComplete():
            # :TODO: Accurate?
            self.packages+=1
        else:
            self.others+=1
                
        # One more project...
        self.projects += 1
                
        # Add state, if not already there
        if not state.isUnset() and not state in self.statepairs: \
            self.statepairs.append(state)
        
        self.calculatePercentages()
        
    def addSummary(self,summary):
                 
        self.projects += summary.projects
        
        self.successes += summary.successes
        self.failures += summary.failures
        self.prereqs += summary.prereqs
        self.noworks += summary.noworks
        self.packages += summary.packages
        self.others += summary.others
        
        # Add state pair, if not already there
        for pair in summary.statepairs:
            if not pair.isUnset() and not pair in self.statepairs: \
                self.statepairs.append(pair)
                
        self.calculatePercentages()
        
    def calculatePercentages(self):
        """ Keep counters correct """
        if self.projects > 0:            
            self.successesPercentage=(float(self.successes)*100)/self.projects
            self.failuresPercentage=(float(self.failures)*100)/self.projects
            self.prereqsPercentage=(float(self.prereqs)*100)/self.projects
            self.noworksPercentage=(float(self.noworks)*100)/self.projects
            self.packagesPercentage=(float(self.packages)*100)/self.projects
            self.othersPercentage=(float(self.others)*100)/self.projects
            
            # This is the overall success of a run...
            self.overallPercentage=(float(self.successes + self.packages)*100)/self.projects
            
    def getOverallPercentage(self):
        """ Return the overall success """
        return self.overallPercentage
