#!/usr/bin/env python
#
# $Header:  1.7 2003/05/10 18:20:36 nicolaken Exp $
# $Revision: 1.7 $
# $Date: 2003/05/10 18:20:36 $
#
# ====================================================================
#
# The Apache Software License, Version 1.1
#
# Copyright (c) 2004 The Apache Software Foundation.  All rights
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
  This is the commandline entrypoint into Python Gump,
  used *primarily* by nightly cron jobs.
  
  It updates Gump (from CVS) to ensure it (itself) is 
  latest, does some environment twiddling, and runs the
  main gump/integration.py. Bit more twiddling with 
  outputs afterwards...

"""

import os.path
import os
import sys
import socket
import time


LINE=' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - GUMP'

def runCommand(command,args='',dir=None,outputFile=None):
    """ Run a command, and check the result... """
    
    #    
    originalCWD=None
    if dir:     
        originalCWD=os.getcwd()
        cwdpath=os.path.abspath(dir)
        try:
            log.write('Executing with CWD: [' + dir + ']\n')    
            if not os.path.exists(cwdpath): os.makedirs(dir)
            os.chdir(cwdpath)
        except Exception, details :
            # Log the problem and re-raise
            log.write('Failed to create/change CWD [' + cwdpath + ']. Details: ' + str(details) + '\n')
            return 0
              
    try:
        
        #
        if not outputFile:
            outputFile='out.tmp'
        
        fullCommand = command + ' ' + args + ' >' + outputFile + ' 2>&1'    
        log.write('Execute : ' + fullCommand + '\n')
       
        #
        # Execute Command & Calculate Exit Code
        #
        systemReturn=os.system(fullCommand)
        
        if not os.name == 'dos' and not os.name == 'nt':
            waitcode=systemReturn
        
            #
            # The return code (from system = from wait) is (on Unix):
            #
            #	a 16 bit number
            #	top byte	=	exit status
            #	low byte	=	signal that killed it
            #
            exit_code=(((waitcode & 0xFF00) >> 8) & 0xFF)
        
        else:
            exit_code=systemReturn
    
        if os.path.exists(outputFile):
            if os.path.getsize(outputFile) > 0:
                catFile(log,outputFile)            
            os.remove(outputFile)
        
        log.write('Exit Code : ' + `exit_code`)
    
    finally:
        if originalCWD: os.chdir(originalCWD)
      
    return exit_code

def catFile(output,file,title=None):
    """ Cat a file to a stream... """
    if title:
        output.write(LINE + '\n')    
        output.write(title + '\n\n')
        
    input=open(file,'r')
    line = input.readline()
    while line:
        output.write(line)
        # Next...
        line = input.readline()
        
# Enable a log
logFile='gumpy.log'
log=open(logFile,'w')

result=0
        
try:

    try:
        
        # Process Environment
        hostname = socket.gethostname()

        log.write('- GUMP run on host   : ' + hostname + '\n')
        log.write('- GUMP run @         : ' + time.strftime('%d %b %y %H:%M:%S', time.gmtime()) + '\n')
        log.write('- GUMP run by Python : ' + `sys.version` + '\n')
        log.write('- GUMP run on OS     : ' + `os.name` + '\n')
        log.write('- GUMP run in env    : \n')
        
        for envkey in os.environ.keys():
            envval=os.environ[envkey]
            log.write('   ' + envkey + ' -> [' + envval + ']\n')
        
        workspaceName = hostname + '.xml'
        if os.environ.has_key('GUMP_WORKSPACE'):        
            workspaceName = os.environ['GUMP_WORKSPACE'] + '.xml'
            
        projectsExpr='*'
        if os.environ.has_key('GUMP_PROJECTS'):        
            projectsExpr = os.environ['GUMP_PROJECTS']            


        #
        # Add Gump to Python Path...
        #
        pythonPath=''
        if os.environ.has_key('PYTHONPATH'):
            pythonPath=os.environ['PYTHONPATH']
            pythonPath+=os.pathsep
        pythonPath+=str(os.path.abspath(os.path.join(os.getcwd(),'python')))
        log.write(' - GUMP PYTHONPATH  :  ' + pythonPath + '\n')
        os.environ['PYTHONPATH']=pythonPath

        #
        # Update Gump from CVS
        #	
        cvsExit = 0
        if not os.environ.has_key('GUMP_NO_CVS_UPDATE'):
            cvsExit = runCommand('cvs -q update -dP')
        else:
            log.write('CVS update skipped per environment setting.\n')
        if cvsExit:
            result=1
            
        # :TODO: Is this a CVS thing, or a Gump historical thing?
        #
        if os.path.exists('.timestamp'): 
            os.remove('.timestamp')            
    
        if not result:
            #
            #
            # Process command line
            #
            args=''
            for arg in sys.argv[1:]:
                if args: args += ' '
                args += arg    
        
            iargs = '-w ' + workspaceName + ' ' + projectsExpr + args
  
            #
            # Run the main Gump...
            #    
            integrationExit = runCommand('python gump/integrate.py', iargs, 'python')
            if integrationExit:
                result=1

            # Copy outputs (especially forrest) into log...


    except KeyboardInterrupt:    
        log.write('Terminated by user interrupt...\n')
        result = 1
    
finally:
    # Close the log
    log.close()
    
    if 1 or result:
        # Cat log if failed...
        catFile(sys.stdout, logFile, 'The Gump log...')

# bye!
sys.exit(result)