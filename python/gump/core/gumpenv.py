#!/usr/bin/python


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

 A gump environment (i.e. what tools are available in this machines
 environment, and so forth).
 
"""

import os.path
import sys
from types import NoneType
from fnmatch import fnmatch

from gump import log

from gump.core.config import *

from gump.utils.note import Annotatable
from gump.utils.work import *

import gump.process.command
import gump.process.launcher

from gump.utils.tools import *

from gump.model.state import *
from gump.model.propagation import *

from gump.integration.depot import *
    
###############################################################################
# Classes
###############################################################################

# Local time zone, in offset from UTC
TZ='%+.2d:00' % (-time.timezone/3600)

class GumpEnvironment(Annotatable,Workable,Propogatable):
    """
    	Represents the environment that Gump is running within.
    	
    	What environment variables are set, what tools are 
    	available, what Java command to use, etc.
    	
    """

    def __init__(self):
        Annotatable.__init__(self)
        Workable.__init__(self)
        Propogatable.__init__(self)
        Stateful.__init__(self)
        
        #
    	# Set to true if not found, see checkEnvironment
    	#
    	self.checked=False
    	
    	self.noMaven=False    	 
    	self.noDepot=False    	
    	self.noUpdate=False    
    	self.noSvn=False    	
    	self.noCvs=False    	
        self.noJavaHome=False
        self.noClasspath=False
        self.noJava=False
        self.noJavac=False
        self.noPGrep=False
        
        self.javaProperties=None
    
    	# JAVACMD can override this, see checkEnvironment
        self.javaCommand = 'java'
        
        # DEPOT_HOME
        self.depotHome = None
        
        # Offset from UTC
        self.timezoneOffset=TZ
        
    def checkEnvironment(self,exitOnError=False):
        """ 
        Check Things That are Required 
        """
        
        if self.checked: return
    
        #
        # :TODO: Complete this, it ought be an important early warning...
        #
    
    
        #:TODO: Take more from runAnt.py on:
        # - ANT_OPTS?
        # - How to ensure lib/tools.jar is in classpath
        # - Others?
    
        #
        #	Directories...
    
    
        #
        # JAVACMD can be set (perhaps for JRE verse JDK)
        #
        if os.environ.has_key('JAVACMD'):        
            self.javaCommand  = os.environ['JAVACMD']
            self.addInfo('JAVACMD environmental variable setting java command to ' \
                + self.javaCommand )
    
    
        #	Envs:
        #	JAVA_HOME for bootstrap ant?
        #	CLASSPATH
    
        if not self.noJavaHome and not self._checkEnvVariable('JAVA_HOME',False):    
            self.noJavaHome=True    
            self.addWarning('JAVA_HOME environmental variable not found. Might not be needed.')
                
        if not self.noClasspath and not self._checkEnvVariable('CLASSPATH',False):
            self.noClasspath=True    
            self.addWarning('CLASSPATH environmental variable not found. Might not be needed.')
                
        if not self.noMaven and not self._checkEnvVariable('MAVEN_HOME',False): 
            self.noMaven=True
            self.addWarning('MAVEN_HOME environmental variable not found, no maven builds.')
            
        if not self.noDepot and not self._checkEnvVariable('DEPOT_HOME',False): 
            self.noDepot=True
            self.addWarning('DEPOT_HOME environmental variable not found, no depot downloads.')
        
        self.depotHome  = getDepotHome(False)
            
        #
        # Check for executables:
        #
        #	java
        #	javac (for bootstrap ant & beyond)
        #	cvs
        #	svn
        #
        self._checkExecutable('env','',False)

        if not self.noJava and not self._checkExecutable(self.javaCommand,'-version',exitOnError,1):
            self.noJava=True
            self.noJavac=True

        if not self.noJavac and not self._checkExecutable('javac','-help',False):
            self.noJavac=True

        if not self.noJavac and not self._checkExecutable('java com.sun.tools.javac.Main','-help',False,False,'check_java_compiler'):
            self.noJavac=True

        if not self.noCvs and not self._checkExecutable('cvs','--version',False):
            self.noCvs=True
            self.addWarning('"cvs" command not found, no CVS repository updates')
        
        if not self.noSvn and not self._checkExecutable('svn','--version',False):
            self.noSvn=True
            self.addWarning('"svn" command not found, no SVN repository updates')
          
        if not self.noUpdate and \
            not self._checkExecutable(getDepotUpdateCmd(),'-version',False,False,'check_depot_update'): 
            self.noUpdate=True
            self.addWarning('"update.py" command not found, no package downloads')
        
        if not self.noMaven and \
            not self._checkExecutable('maven','--version',False,False,'check_maven'): 
            self.noMaven=True
            self.addWarning('"maven" command not found, no Maven builds')
        
        if not self.noPGrep and not self._checkExecutable('pgrep','-help',False): 
            self.noPGrep=True
            self.addWarning('"pgrep" command not found, no process clean-ups can occur')        
    
        self.checked=True
        
        self.changeState(STATE_SUCCESS)
    
    def getJavaProperties(self):
        if not isinstance(self.javaProperties,NoneType): 
            return self.javaProperties

        # Ensure we've determined the Java Compiler to use
        self.checkEnvironment()
        
        if self.noJavac: return {}

        import commands, re

        JAVA_SOURCE = dir.tmp + '/sysprop.java'

        source=open(JAVA_SOURCE,'w')
        source.write("""
          import java.util.Enumeration;
          public class sysprop {
            public static void main(String [] args) {
              Enumeration e=System.getProperties().propertyNames();
              while (e.hasMoreElements()) {
                String name = (String)e.nextElement();
                System.out.print(name + ": ");
                System.out.println(System.getProperty(name));
              }
            }
          }
        """)
        source.close()
    
        os.system('javac ' + JAVA_SOURCE)
        os.unlink(JAVA_SOURCE)
    
        cmd=self.javaCommand + ' -cp ' + dir.tmp + ' sysprop'
        self.javaProperties = \
	        dict(re.findall('(.*?): (.*)', commands.getoutput(cmd)))
        JAVA_CLASS=JAVA_SOURCE.replace('.java','.class')
        if os.path.exists(JAVA_CLASS):
            os.unlink(JAVA_CLASS)

        for (name,value) in self.javaProperties.items():
            log.debug("Java Property: " + name + " => " + value)

        return self.javaProperties

    def _checkExecutable(self,command,options,mandatory,logOutput=False,name=None):
        ok=False
        try:
            if not name: name='check_'+command
            cmd=gump.process.command.getCmdFromString(command+" "+options,name)
            result=execute(cmd)
            ok=result.isOk()
            if not ok:
                log.info('Failed to detect [' + command + ']')   
        except Exception, details:
            ok=False
            log.error('Failed to detect [' + command + '] : ' + str(details))
            result=None
       
        # Update 
        self.performedWork(CommandWorkItem(WORK_TYPE_CHECK,cmd,result))
        
        if not ok and mandatory:
            banner()
            print
            print " Unable to detect/test mandatory [" + command+ "] in path (see next)."
            for p in sys.path:
                print "  " + str(os.path.abspath(p))
            sys.exit(EXIT_CODE_MISSING_UTILITY)
        
        # Store the output
        if logOutput and result.output:
            out=tailFileToString(result.output,10)
            self.addInfo(name + ' produced: \n' + out)
            
        return ok
    
    def _checkEnvVariable(self,env,mandatory=True):
        ok=False
        try:
            ok=os.environ.has_key(env)
            if not ok:
                log.info('Failed to find environment variable [' + env + ']')
        
        except Exception, details:
            ok=False
            log.error('Failed to find environment variable [' + env + '] : ' + str(details))
    
        if not ok and mandatory:
            banner()
            print
            print " Unable to find mandatory [" + env + "] in environment (see next)."
            for e in os.environ.keys():
                try:
                    v=os.environ[e]
                    print "  " + e + " = " + v
                except:
                    print "  " + e 
            sys.exit(EXIT_CODE_BAD_ENVIRONMENT)
    
        return ok
        
    def getJavaCommand(self):
        return self.javaCommand
        
    def getTimezoneOffset(self):
        return self.timezoneOffset
        
if __name__ == '__main__':
  env = GumpEnvironment()
  env.checkEnvironment()
  env.getJavaProperties()
