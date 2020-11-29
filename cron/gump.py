#!/usr/bin/env python

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

  This is the commandline entrypoint into Apache Gump, 
  used *primarily* by nightly cron jobs.

  It updates Gump (from svn) to ensure it (itself) is 
  latest, does some environment twiddling, and runs the
  main gump/integration.py. Bit more twiddling with 
  outputs afterwards...

"""

import os.path
import os
import sys
import socket
import time
import signal
import smtplib
from xml.dom import minidom

LINE = ' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - GUMP'

GUMP_VERSION = '2.0.2-alpha-0003'

def ignoreHangup(_signum):
    pass

def runCommand(command, args = '', dir = None, outputFile = None):
    """ Run a command, and check the result... """

    #
    originalCWD = None
    if dir:
        originalCWD = os.getcwd()
        cwdpath = os.path.abspath(dir)
        try:
            log.write('Executing with CWD: [' + dir + ']\n')
            if not os.path.exists(cwdpath):
                os.makedirs(dir)
            os.chdir(cwdpath)
        except Exception as details :
            # Log the problem and re-raise
            log.write('Failed to create/change CWD [' + cwdpath + \
                          ']. Details: ' + str(details) + '\n')
            return 0

    try:

        #
        if not outputFile:
            outputFile = 'out.txt'

        fullCommand = command + ' ' + args + ' >' + outputFile + ' 2>&1'
        log.write('Execute : ' + fullCommand + '\n')

        #
        # Execute Command & Calculate Exit Code
        #
        systemReturn = os.system(fullCommand)

        if not os.name == 'dos' and not os.name == 'nt':
            waitcode = systemReturn

            #
            # The return code (from system = from wait) is (on Unix):
            #
            #    a 16 bit number
            #    top byte    =    exit status
            #    low byte    =    signal that killed it
            #
            exit_code = (((waitcode & 0xFF00) >> 8) & 0xFF)

        else:
            exit_code = systemReturn

        if os.path.exists(outputFile):
            if os.path.getsize(outputFile) > 0:
                catFile(log, outputFile)
            os.remove(outputFile)

        if exit_code:
            log.write('Process Exit Code : ' + repr(exit_code) + '\n')

    finally:
        if originalCWD:
            os.chdir(originalCWD)

    return exit_code

def catFile(output, file, title = None):
    """ Cat a file to a stream... """
    if title:
        output.write(LINE + '\n')
        output.write(title + '\n\n')

    input = open(file, 'r')
    line = input.readline()
    while line:
        output.write(line)
        # Next...
        line = input.readline()

def sendEmail(toaddr, fromaddr, subject, data, server, port = 25):
    rawdata = "Date: %s\r\nFrom: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" \
                % (     time.strftime('%d %b %Y %H:%M:%S', time.gmtime()), 
                    fromaddr, toaddr,   subject,        data)
    try:
        #
        # Attach to the SMTP server to send....
        #
        server = smtplib.SMTP(server, port)
        #server.set_debuglevel(1)
        server.sendmail(fromaddr, toaddr, rawdata)
        server.quit()

    except Exception as details:
        print ('Failed to send mail: ' + str(details))

def writeRunLogEntry(entry):
    # Enable a run log
    runlogFileName = 'gump_runlog.txt'
    runlogFile = os.path.abspath(os.path.join('log', runlogFileName))
    runlog = None
    try:
        runlog = open(runlogFile, 'a', 0) # Unbuffered...
        try:
            runlog.write(time.strftime('%d %b %Y %H:%M:%S'))
            runlog.write(' : ')
            runlog.write(repr(os.getpid()))
            runlog.write(' : ')
            runlog.write(entry)
            runlog.write('\n')
        except Exception as details:
            print ('Failed to write to runlog : ' + str(details))
    finally:
        if runlog:
            runlog.close()


def establishLock(lockFile):

    failed = 0
    info = ''
    if 'posix' == os.name:
        import fcntl

        try:
            lock = open(lockFile, 'a + ')
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except:
            failed = 1
            info = ', and is locked.'

    else:
        if os.path.exists(lockFile):
            failed = 1

        # Write this PID into a lock file
        lock = open(lockFile, 'w')

    if failed:
        writeRunLogEntry('False Start. The lock file [%s] exists%s' % \
                             (lockFile, info))

        print ("""The lock file [%s] exists%s. 
Either Gump is still running, or it terminated very abnormally.
Please resolve this (waiting or removing the lock file) before retrying.
        """ % (lockFile, info))
        sys.exit(1)

    # Leave a mark...
    lock.write(repr(os.getpid()))
    lock.flush()

    return lock

def releaseLock(lock, lockFile):

    if 'posix' == os.name:
        import fcntl
        try:
            fcntl.flock(lockFile.fileno(), fcntl.LOCK_UN)
        except:
            pass

    # Close it, so we can dispose of it
    lock.close()

    # Others might be blocked on this
    try:
        os.remove(lockFile)
    except:
        # Somehow another could delete this, even if locked...
        pass


def tailFile(file, lines, _eol = None, _marker = None):
    """ Return the last N lines of a file as a list """
    taillines = []
    try:
        o = None
        try:
            # Read lines from the file...
            o = open(file, 'r')
            line = o.readline()

            size = 0
            while line:
                # Store the lines
                taillines.append(line)

                # But dump any before 'lines'
                size = len(taillines)
                if size > lines:
                    del taillines[0:(size-lines)]
                    size = len(taillines)

                # Read next...
                line = o.readline()

        finally:
            if o:
                o.close()
    except Exception as details:
        print ('Failed to tail :' + file + ' : ' + str(details))

    return taillines

def tailFileToString(file, lines, eol = None, marker = None):
    return "".join(tailFile(file, lines, eol, marker))

def run_prepost_script(env_var, script_type):
    """
    runs a local PRE or POST script if the corresponding environment
    variable has been specified and the script exists.
    """
    if os.environ.has_key(env_var):
        pp_script = os.environ[env_var]
        if not os.path.exists(pp_script):
            pp_script = os.path.join(start_dir, pp_script)
        if os.path.exists(pp_script):
            pp_name = os.path.basename(pp_script)
            pp_exit = runCommand(pp_script,
                                 outputFile = os.path.join(".",
                                                           pp_name + ".out")
                                 )
            if pp_exit:
                return 1
        else:
            log.write('No %s script [%s].\n' % (script_type, pp_script))
    return 0

def doRun():
    # Starting up...
    writeRunLogEntry('Apache Gump(tm) Start-up. Arguments [%s]' % sys.argv)

    # Allow a lock
    lockFile = os.path.abspath('gump.lock')
    lock = establishLock(lockFile)

    # Set the signal handler to ignore hangups
    try:
        # Not supported by all OSs
        # :TODO: Does the variable signal.SIG_HUP even exist? Test
        # this code on Linux w/o the try/except.
        signal.signal(signal.SIG_HUP, ignoreHangup)
    except:
        pass



    hostname = 'Unknown'
    workspaceName = 'Unknown'
    wsName = 'Unknown'

    mailserver = None
    mailport = None
    mailfrom = None
    mailto = None
    logurl = None
    logdir = None

    args = sys.argv
    result = 0
    svnExit = -1
    integrationExit = -1

    try:

        try:

            # Process Environment
            hostname = socket.gethostname()

            log.write('- GUMP run on host   : ' + hostname + '\n')
            log.write('- GUMP run @         : ' + \
                          time.strftime('%d %b %Y %H:%M:%S',
                                        time.localtime()) + '\n')
            log.write('- GUMP run @  UTC    : ' + \
                          time.strftime('%d %b %Y %H:%M:%S',
                                        time.gmtime()) + '\n')
            log.write('- GUMP run by Python : ' + repr(sys.version) + '\n')
            log.write('- GUMP run by Python : ' + repr(sys.executable) + '\n')
            log.write('- GUMP run by Gump   : ' + GUMP_VERSION + '\n')
            log.write('- GUMP run on OS     : ' + repr(os.name) + '\n')
            log.write('- GUMP run in env    : \n')

            for envkey in os.environ.keys():
                envval = os.environ[envkey]
                log.write('      ' + envkey + ' -> [' + envval + ']\n')

            # Workspace is the hostname, unless overridden
            workspaceName = os.path.abspath('metadata/' + hostname + '.xml')
            if os.environ.has_key('GUMP_WORKSPACE'):
                workspaceName = os.environ['GUMP_WORKSPACE'] + '.xml'
            if len(args)>2 and args[1] in ['-w', '--workspace']:
                workspaceName = args[2]
                del args[1:3]
            workspacePath = workspaceName

            projectsExpr = 'all'
            if os.environ.has_key('GUMP_PROJECTS'):
                projectsExpr = os.environ['GUMP_PROJECTS']
            if len(args)>1:
                projectsExpr = args[1]
                del args[1:2]

            # Check version information
            (major, minor, _micro, _releaselevel, _serial) = sys.version_info
            if not major >= 2 and minor >= 3:
                raise RuntimeError('Gump requires Python 2.3 or above. [' \
                                       + sys.version() + ']')

            # Nope, can't find the workspace...
            if not os.path.exists(workspacePath):
                raise RuntimeError('\n  No workspace at ' 
                                   + str(workspacePath) + 
                  '!\n  Maybe you need to check out the metadata from svn?\n' + 
                  '  See the file metadata/FILLME for more information...')

            #
            # Process the workspace...
            #
            ws = minidom.parse(workspacePath)
            workspaceElementList = ws.getElementsByTagName('workspace')
            if not workspaceElementList.length == 1:
                # LSD: this is kinda lame way to parse this
                #      better to just validate against a DTD
                raise RuntimeError('Need one (only) <workspace> tag. Found ' + \
                           repr( workspaceElementList.length) + '.')
            wsw = workspaceElementList.item(0)
            wsName = wsw.getAttribute('name')
            # Extract the base directory
            baseDir = wsw.getAttribute('basedir')
            basePath = os.path.abspath(baseDir)
            # Mail reporting
            private = wsw.getAttribute('private')
            mailserver = wsw.getAttribute('mailserver') or 'mail.apache.org'
            mailport = wsw.getAttribute('mailport') or 25
            mailto = wsw.getAttribute('administrator') 
            mailfrom = wsw.getAttribute('email') 
            # Log (site) location(s)
            logurl = wsw.getAttribute('logurl')
            logdir = wsw.getAttribute('logdir') or os.path.join(basePath, 'log')
            # Extract the mail server/address
            ws.unlink()

            log.write('- GUMP base directory : ' + baseDir + '\n')
            log.write('- GUMP base path      : ' + str(basePath) + '\n')
            if mailserver and not private:
                log.write('- GUMP mail server    : ' + mailserver + '\n')
            if mailport and not private:
                log.write('- GUMP mail port      : ' + str(mailport) + '\n')
            if mailfrom:
                log.write('- GUMP mail from      : ' + mailfrom + '\n')
            if mailto:
                log.write('- GUMP mail to        : ' + mailto + '\n')
            if logurl:
                log.write('- GUMP log is @       : ' + logurl + '\n')
            if logdir:
                log.write('- GUMP log is @       : ' + logdir + '\n')

            # Add Gump to Python Path...
            pythonPath = ''
            if os.environ.has_key('PYTHONPATH'):
                pythonPath = os.environ['PYTHONPATH']
                pythonPath += os.pathsep
            pythonDir = str(os.path.abspath(os.path.join(os.getcwd(),
                                                         'python')))
            pythonPath += pythonDir
            log.write(' - GUMP PYTHONPATH  :  ' + pythonPath + '\n')
            os.environ['PYTHONPATH'] = pythonPath


            # Wipe all *.pyc from the pythonPath (so we don't
            # have old code lying around as compiled zombies)
            for root, _dirs, files in os.walk(pythonDir):
                for name in files:
                    if name.endswith('.pyc'):
                        fullname = os.path.join(root, name)
                        # log.write('- Remove PYC : ' + fullname + '\n')
                        os.remove(fullname)

            # Update Gump code from SVN
            if not os.environ.has_key('GUMP_NO_SVN_UPDATE') and \
                not os.environ.has_key('GUMP_NO_SCM_UPDATE'):
                svnExit = runCommand('svn', 'update --non-interactive')
            else:
                log.write('SVN update skipped per environment setting.\n')
                svnExit = 0
            if svnExit:
                result = 1

            if os.path.exists('.timestamp'): 
                os.remove('.timestamp')

            if run_prepost_script('HOST_LOCAL_PRE_RUN', 'pre-run'):
                result = 1

            if not result:
                # Process/build command line
                iargs = '-w ' + workspaceName + ' ' + projectsExpr + ' ' + \
                    ' '.join(args[1:])

                # Allow a check not an integrate
                check = 0
                if '--check' in args:
                    check = 0

                #
                # Run the main Gump...
                #
                command = 'bin/integrate.py'
                if check:
                    command = 'bin/check.py'
                integrationExit = runCommand(sys.executable + ' ' + command,
                                             iargs)
                if integrationExit:
                    result = 1

            if not result:
                if run_prepost_script('HOST_LOCAL_POST_RUN', 'post-run'):
                    result = 1

        except KeyboardInterrupt:
            log.write('Terminated by user interrupt...\n')
            result = 1
            raise

        except:
            log.write('Terminated unintentionally...\n')
            result = 1
            raise

    finally:
        # Close the log
        log.close()

        releaseLock(lock, lockFile)

        logTitle = 'Apache Gump Logfile'
        if result:
            logTitle = 'Problem running Apache Gump [%s]' % wsName

        # Publish logfile
        published = False
        if logdir:
            publishedLogName = 'gump_log.txt'
            publishedLogFile = os.path.abspath(os.path.join(logdir,
                                                            publishedLogName))
            if '--xdocs' in args:
                publishedLogFile = os.path.abspath(
                                    os.path.join(
                                        os.path.abspath(
                                            os.path.join(logdir, 'content'), 
                                        logFileName)))

            try:
                publishedLog = open(publishedLogFile, 'w', 0) # Unbuffered...
                catFile(publishedLog, logFile, logTitle)
                publishedLog.close()
                published = True
            except Exception as details:
                print 'Failed to publish log file. ', str(details)
                published = False
        else:
            print 'Unable to publish log file.'

        if result:
            # Cat to screen (if running to screen)
            tty = False
            try:
                tty = sys.stdout.isatty()
            except:
                pass
            if tty or not published:
                catFile(sys.stdout, logFile, logTitle)

            if mailserver and mailport and mailto and mailfrom:
                mailData = 'There is a problem with run \'%s\' (%s)' % \
                    (wsName, runDateTime)
                if published and logurl:
                    mailData += ', location : ' + logurl + '\n'
                else:
                    mailData += ', at : ' + hostname + ':' + workspaceName + \
                        '\n'

                #
                try:
                    maxTailLines = 50
                    tailData = tailFileToString(logFile, maxTailLines)

                    if published and logurl:
                        mailData += '------------------------------------------------------------\n' 
                        mailData += 'The log ought be at:\n'
                        mailData += '   '
                        logFileUrl = logurl
                        if not logFileUrl.endswith('/'): 
                            logFileUrl += '/'
                        logFileUrl += publishedLogName
                        mailData += logFileUrl
                        mailData += '\n'

                    mailData += '------------------------------------------------------------\n'
                    mailData += 'The last (up to) %s lines of the log are :\n' \
                        % maxTailLines
                    mailData += tailData
                except:
                    pass

                # Tack a version on there
                mailData += '--\n'
                mailData += 'Gump Version: '
                mailData += GUMP_VERSION
                mailData += '\n'

                sendEmail(mailto, mailfrom, logTitle, mailData, mailserver,
                          mailport)

            else:
                print 'Unable to mail failure report : ' + \
                    repr([mailserver, mailport, mailto, mailfrom])


    writeRunLogEntry('Complete [%s svn:%s, run:%s]' % \
                         (result, svnExit, integrationExit))

    # bye!
    sys.exit(result)

# Do it! Do it!

# Ensure we start in the correct directory, setting GUMP_HOME
start_dir = os.path.abspath(os.getcwd())
gumpHome = os.path.abspath(os.path.join(os.getcwd(), '..'))
os.environ['GUMP_HOME'] = gumpHome
os.chdir(gumpHome)

# various parts of this file write logs to this dir...
logDir = 'log'
if not os.path.isdir(logDir):
    os.mkdir(logDir)

# Enable a log
runDateTime = time.strftime('%d%m%Y_%H%M%S')
logFileName = 'gump_log_' + runDateTime + '.txt'
logFile = os.path.abspath(os.path.join(logDir, logFileName))
log = open(logFile, 'w', 0) # Unbuffered...

if '--debug' in sys.argv:
    import pdb
    pdb.run('doRun()')
else:
    doRun()
