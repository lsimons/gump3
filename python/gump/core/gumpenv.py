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

 A gump environment
 
"""

import os.path
import sys
from fnmatch import fnmatch

from gump import log

from gump.core.config import *

from gump.utils.note import Annotatable
from gump.utils.work import *
from gump.utils.launcher import *
from gump.utils.tools import *

from gump.model.state import *
from gump.model.propagation import *
    
###############################################################################
# Classes
###############################################################################

# Local time zone, in offset from UTC
TZ='%+.2d:00' % (-time.timezone/3600)

class GumpEnvironment(Annotatable,Workable,Propogatable):

    def __init__(self):
        Annotatable.__init__(self)
        Workable.__init__(self)
        Propogatable.__init__(self)
        Stateful.__init__(self)
        
        #
    	# Set to true if not found, see checkEnvironment
    	#
    	self.checked=False
    	
    	self.noForrest=False    
    	self.noMaven=False    	
    	self.noUpdate=False    	
    	self.noTimeout=False
    	self.noSvn=False    	
    	self.noCvs=False    	
        self.noJavaHome=False
        self.noClasspath=False
        self.noJava=False
        self.noJavac=False
        self.noPGrep=False
        self.javaProperties=False
    	
    	#
    	# JAVACMD can override this, see checkEnvironment
    	#
        self.javaCommand = 'java'
        
        #
        # Offset from UTC
        #
        self.timezoneOffset=TZ
        
    def checkEnvironment(self,exitOnError=False):
        """ Check Things That are Required """
        
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
        #	FORREST_HOME?
    
        if not self.noJavaHome and not self.checkEnvVariable('JAVA_HOME',False):    
            self.noJavaHome=1    
            self.addWarning('JAVA_HOME environmental variable not found. Might not be needed.')
                
        if not self.noClasspath and not self.checkEnvVariable('CLASSPATH',False):
            self.noClasspath=1    
            self.addWarning('CLASSPATH environmental variable not found. Might not be needed.')
                
        if not self.noForrest and not self.checkEnvVariable('FORREST_HOME',False): 
            self.noForrest=1
            self.addWarning('FORREST_HOME environmental variable not found, no xdoc output.')
                
        if not self.noMaven and not self.checkEnvVariable('MAVEN_HOME',False): 
            self.noMaven=1
            self.addWarning('MAVEN_HOME environmental variable not found, no maven builds.')
            
        #
        # Check for executables:
        #
        #	java
        #	javac (for bootstrap ant & beyond)
        #	cvs
        #
        #	forrest (for documentation)
        #
        self.checkExecutable('env','',False)

        if not self.noJava and not self.checkExecutable(self.javaCommand,'-version',exitOnError,1):
            self.noJava=1
            self.noJavac=1

        if not self.noJavac and not self.checkExecutable('javac','-help',False):
            self.noJavac=1

        if not self.noJavac and not self.checkExecutable('java com.sun.tools.javac.Main','-help',False,False,'check_java_compiler'):
            self.noJavac=1

        if not self.noCvs and not self.checkExecutable('cvs','--version',False):
            self.noCvs=1
            self.addWarning('"cvs" command not found, no CVS repository updates')
        
        if not self.noSvn and not self.checkExecutable('svn','--version',False):
            self.noSvn=1
            self.addWarning('"svn" command not found, no SVN repository updates')
        
        if not self.noForrest and not self.checkExecutable('forrest','-projecthelp',False): 
            self.noForrest=1
            self.addWarning('"forrest" command not found, no xdoc output')
        
        if not self.noTimeout:
            if	not self.checkExecutable('timeout','60 env',False): 
                self.noTimeout=1
                self.addWarning('"timeout" command not found, no in-line command time outs')
            else:
                setting.timeoutCommand=1
            
        if not self.noUpdate and \
            not self.checkExecutable('python update.py','-version',False,False,'check_depot_update'): 
            self.noUpdate=1
            self.addWarning('"update.py" command not found, no package downloads')
        
        if not self.noMaven and \
            not self.checkExecutable('maven','--version',False,False,'check_maven'): 
            self.noMaven=1
            self.addWarning('"maven" command not found, no Maven builds')
        
        if not self.noPGrep and not self.checkExecutable('pgrep','-help',False): 
            self.noPGrep=1
            self.addWarning('"pgrep" command not found, no process clean-ups can occur')        
    
    
        self.checked=1
        
        self.changeState(STATE_SUCCESS)
    
    def getJavaProperties(self):
        if self.javaProperties: return self.javaProperties

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
        os.unlink(JAVA_SOURCE.replace('.java','.class'))

        for (name,value) in self.javaProperties.items():
            log.debug("Java Property: " + name + " => " + value)

        return self.javaProperties

    def checkExecutable(self,command,options,mandatory,logOutput=False,name=None):
        ok=False
        try:
            if not name: name='check_'+command
            cmd=getCmdFromString(command+" "+options,name)
            result=execute(cmd)
            ok=result.state==CMD_STATE_SUCCESS 
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
    
    def checkEnvVariable(self,env,mandatory=1):
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
