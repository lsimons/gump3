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
 A gump environment (i.e. what tools are available in this machine's
 environment, and so forth).
"""

import os.path
import sys
from types import NoneType
from fnmatch import fnmatch

from gump import log

from gump.core.config import *

from gump.util.note import Annotatable
from gump.util.work import *

import gump.util.process.command
import gump.util.process.launcher

from gump.util.tools import *

from gump.core.model.state import *
from gump.core.model.propagation import *

from gump.tool.integration.depot import *
    
###############################################################################
# Classes
###############################################################################

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
        
        self.checked = False
        self.set = False
    	
        self.noMono = False
        self.noNAnt = False    
        self.noMaven = False    	 
        self.noDepot = False    	
        self.noSvn = False    	
        self.noCvs = False   
        self.noP4 = False   
        self.noJava = False
        self.noJavac = False
        self.noMake = False    
        
        self.javaProperties = None
    
        # GUMP_HOME
        self.gumpHome = None
        
        # JAVACMD can override this, see checkEnvironment
        self.javaHome = None
        self.javaCommand = 'java'
        self.javacCommand = 'javac'
        
        # DEPOT_HOME
        self.depotHome = None
        
        # Timezone and offset from UTC
        self.timezone = time.tzname
        self.timezoneOffset = time.timezone
        
    def checkEnvironment(self,exitOnError=False):
        """ 
        Check things that are required/optional 
        """
        
        if self.checked: return
    
        # Check for directories
        
        self._checkEnvVariable('GUMP_HOME')                
        self.gumpHome = os.environ['GUMP_HOME']
            
        # JAVA_CMD can be set (perhaps for JRE verse JDK)
        if os.environ.has_key('JAVA_CMD'):        
            self.javaCommand  = os.environ['JAVA_CMD']
            self.addInfo('JAVA_CMD environmental variable setting java command to ' + self.javaCommand )      

        # JAVAC_CMD can be set (perhaps for JRE verse JDK)
        if os.environ.has_key('JAVAC_CMD'):        
            self.javacCommand  = os.environ['JAVAC_CMD']
            self.addInfo('JAVAC_CMD environmental variable setting javac command to ' + self.javacCommand )      
    
        self._checkEnvVariable('JAVA_HOME')
                
        if os.environ.has_key('JAVA_HOME'):        
            self.javaHome  = os.environ['JAVA_HOME']
            self.addInfo('JAVA_HOME environmental variable setting java home to ' + self.javaHome )      
                
        if not self.noMaven and not self._checkEnvVariable('MAVEN_HOME',False): 
            self.noMaven=True
            self.addWarning('MAVEN_HOME environmental variable not found, no maven builds.')
            
        if not self.noDepot and not self._checkEnvVariable('DEPOT_HOME',False): 
            self.noDepot=True
            self.addWarning('DEPOT_HOME environmental variable not found, no depot downloads.')
        
        self.depotHome = getDepotHome(False)
            
        # Check for executables
        
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
          
        if not self.noP4 and not self._checkExecutable('p4','-V',False):
            self.noP4=True
            self.addWarning('"p4" command not found, no Perforce repository updates')
          
        if not self.noDepot and \
            not self._checkExecutable(getDepotUpdateCmd(),'-version',False,False,'check_depot_update'): 
            self.noDepot=True
            self.addWarning('"depot update" command not found, no package downloads')
        
        if not self.noMaven and \
            not self._checkExecutable('maven','--version',False,False,'check_maven'): 
            self.noMaven=True
            self.addWarning('"maven" command not found, no Maven builds')
       
        if not self.noNAnt and \
            not self._checkExecutable('NAnt','-help',False,False,'check_NAnt'): 
            self.noNAnt=True
            self.addWarning('"NAnt" command not found, no NAnt builds')
       
        if not self.noMono and \
            not self._checkExecutable('mono','--help',False,False,'check_mono'): 
            self.noMono=True
            self.addWarning('"Mono" command not found, no Mono runtime')
       
        if not self.noMake and \
            not self._checkExecutable('make','--help',False,False,'check_Make'): 
            self.noMake=True
            self.addWarning('"make" command not found, no make builds')
       
        self.checked = True
        
        self.changeState(STATE_SUCCESS)
        
    def setEnvironment(self):
        """ 
        Set things that are required 
        """
        
        if self.set: return
        
        # Blank the CLASSPATH
        os.environ['CLASSPATH'] = ''
  
        self.set=True
        
    def getGumpHome(self):
        # Ensure we've determined the Gump Home
        self.checkEnvironment()    
        return self.gumpHome
        
    def getJavaHome(self):
        # Ensure we've determined the Java Home
        self.checkEnvironment()    
        return self.javaHome
        
    def getJavaProperties(self):
        """
        Ask the JAVA instance what it's system properties are, 
        primarily so we can log/display them (for user review).
        """
        
        if not isinstance(self.javaProperties,NoneType):
            return self.javaProperties

        # Ensure we've determined the Java Compiler to use
        self.checkEnvironment()
        
        if self.noJavac: 
            log.error("Can't obtain Java properties since Java Environment was not found")
            return {}

        import commands, re

        JAVA_SOURCE = dir.tmp + '/sysprop.java'

        source = open(JAVA_SOURCE,'w')
        source.write("""
          import java.util.Enumeration;
          public class sysprop {
            public static void main(String [] args) {
              Enumeration e = System.getProperties().propertyNames();
              while (e.hasMoreElements()) {
                String name = (String) e.nextElement();
                System.out.println(name + ": " + System.getProperty(name));
              }
            }
          }
        """)
        source.close()
    
        cmd = self.javacCommand + " " + JAVA_SOURCE
        os.system(cmd)
        os.unlink(JAVA_SOURCE)
    
        cmd = self.javaCommand + ' -cp ' + dir.tmp + ' sysprop'
        result = commands.getoutput(cmd)
        self.javaProperties = dict(re.findall('(.*?): (.*)', result))
        JAVA_CLASS = JAVA_SOURCE.replace('.java','.class')
        if os.path.exists(JAVA_CLASS): os.unlink(JAVA_CLASS)

        for (name,value) in self.javaProperties.items():
            log.debug("Java Property: " + name + " => " + value)

        return self.javaProperties

    def _checkExecutable(self,command,options,mandatory,logOutput=False,name=None):
        ok = False
        try:
            if not name: name = 'check_'+command
            cmd = gump.util.process.command.getCmdFromString(command+" "+options,name)
            result = execute(cmd)
            ok = result.isOk()
            if ok:
                log.warning('Detected [' + command + ' ' + options + ']')   
            else:
                log.warning('Failed to detect [' + command + ' ' + options + ']')   
        except Exception, details:
            ok = False
            log.error('Failed to detect [' + command + ' ' + options + '] : ' + str(details))
            result = None
       
        # Update 
        self.performedWork(CommandWorkItem(WORK_TYPE_CHECK,cmd,result))
        
        if not ok and mandatory:
            print
            print "Unable to detect/test mandatory [" + command+ "] in path:"
            for p in sys.path:
                print "  " + str(os.path.abspath(p))
            sys.exit(EXIT_CODE_MISSING_UTILITY)
        
        # Store the output
        if logOutput and result.output:
            out = tailFileToString(result.output,10)
            self.addInfo(name + ' produced: \n' + out)
            
        return ok
    
    def _checkEnvVariable(self,env,mandatory=True):
        ok = False
        try:
            ok = os.environ.has_key(env)
            if not ok:
                log.info('Failed to find environment variable [' + env + ']')
        
        except Exception, details:
            ok = False
            log.error('Failed to find environment variable [' + env + '] : ' + str(details))
    
        if not ok and mandatory:
            print
            print "Unable to find mandatory [" + env + "] in environment:"
            for e in os.environ.keys():
                try:
                    v = os.environ[e]
                    print "  " + e + " = " + v
                except:
                    print "  " + e 
            sys.exit(EXIT_CODE_BAD_ENVIRONMENT)
    
        return ok
        
    def getJavaCommand(self):
        return self.javaCommand
        
    def getTimezone(self):
        return self.timezone
        
    def getTimezoneOffset(self):
        return self.timezoneOffset
        
if __name__ == '__main__':
    env = GumpEnvironment()
    env.checkEnvironment()
    env.getJavaProperties()
