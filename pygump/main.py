#!/usr/bin/env python

#
#   Copyright 2003-2004 The Apache Software Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# $Header: $

"""

  This is the command line entrypoint into pygump.
  
  It parses the environment variables, command line arguments and
  some workspace settings and populates an options object with what
  it finds. With this, it starts up the main gump engine.
  
  Additionally, this module has some pretty much self-contained logging
  and error handling. In the event of severe problems, it'll send e-mail
  to the administrator configured in the workspace for this machine.
"""

import os
import sys
import time
from xml.dom import minidom
import smtplib

# for log messages...
SEP = "------------------------------------------------------------------------------\n"
GUMP_VERSION = '3.0-alpha-1'

# log levels
DEBUG = 5
INFO = 4
WARNING = 3
ERROR = 2
CRITICAL = 1

class Logger:
    """
    Very basic "bootstrap" logger to use before getting at a real logger from
    the logging package. Does react to the most basic form of the commands sent
    to the logging.Logger class so it can be replaced at any time by one of
    those.
    """
    
    def __init__(self, logdir, level=DEBUG, console_level=INFO):
        self.level = level
        self.console_level = console_level
        
        if self.console_level >= DEBUG:
            print "DEBUG: logdir is " + logdir

        if not os.path.isdir(logdir): os.mkdir(logdir)
        self.logdir = logdir

        rundatetime = time.strftime('%Y%m%d_%H%M%S')
        filename = 'gump_log_' + rundatetime + '.txt'
        self.filename = os.path.abspath(os.path.join(logdir,filename))
        self.target = open(self.filename, 'w', 0)
    
    def __del__(self):
        self.close()
    
    def close(self):
        self.target.close()
    
    def log(self, level, msg):
        if level == DEBUG: self.debug(msg)
        if level == INFO: self.debug(msg)
        if level == WARNING: self.debug(msg)
        if level == ERROR: self.debug(msg)
        if level == CRITICAL: self.debug(msg)
    
    def debug(self, msg):
        message = 'DEBUG: %s\n' % (msg)
        if self.console_level >= DEBUG:
            print message,
        if self.level >= DEBUG:
            self.target.write(message);
    
    def info(self, msg):
        message = 'INFO: %s\n' % (msg)
        if self.console_level >= INFO:
            print message,
        if self.level >= INFO:
            self.target.write(message);
    
    def warning(self, msg):
        message = 'WARNING: %s\n' % (msg)
        if self.console_level >= WARNING:
            print message,
        if self.level >= WARNING:
            self.target.write(message);
    
    def error(self, msg):
        message = 'ERROR: %s\n' % (msg)
        if self.console_level >= ERROR:
            print message,
        if self.level >= ERROR:
            self.target.write(message);
    
    def exception(self, msg):
        info = sys.exc_info()
        self.error(msg)

        import traceback
        from StringIO import StringIO
        buf = StringIO()
        traceback.print_exception( info[0], info[1], info[2], file=buf)
        self.error(buf.getvalue())
        buf.close()


    def critical(self, msg):
        message = 'CRITICAL: %s\n' % (msg)
        if self.console_level >= CRITICAL:
            print message,
        if self.level >= CRITICAL:
            self.target.write(message);

class GumpConfigError(Exception):
    pass

class GumpEnvironmentError(Exception):
    pass

def check_version():
    """
    Raises exception if python version < 2.3.
    """
    (major, minor, micro, releaselevel, serial) = sys.version_info
    if not major >=2 and minor >= 3:
        raise GumpEnvironmentError, 'CRITICAL: Gump requires Python 2.3 or above. The current version is %s.' % sys.version()
        
def parse_workspace(filename, options):
    """
    Converts the workspace file to a minidom tree and extract some info to
    put into the options instance. It doesn't merge in the profile or anything
    like that, that is left up to the engine.
    """
    domtree             = minidom.parse(filename)
    w                   = domtree.getElementsByTagName('workspace').item(0)
    options.name        = w.getAttribute('name')

    # Extract the base directory
    # don't get this from workspace, we need it sooner than that
    # options.basedir     = w.getAttribute('basedir')
    # options.basepath    = os.path.abspath(basedir)

    # determine which user is doing stuff
    user = "gump"
    try:
        from getpass import getuser
        user = getuser()
    except:
        pass

    # Mail reporting
    # unused options.private     = w.getAttribute('private')
    options.mailserver  = w.getAttribute('mailserver') or 'localhost'
    options.mailport    = w.getAttribute('mailport') or 25
    options.mailto      = w.getAttribute('administrator') 
    options.mailfrom    = w.getAttribute('email') or "%s@%s" % (user, options.hostname)

    # log (site) location(s)
    options.logurl      = w.getAttribute('logurl') 
    # don't get this from workspace, we need it sooner than that
    # options.logdir      = w.getAttribute('logdir') or os.path.join(basepath,'log')

    # clean up
    w.unlink()

def svn_update(log, options):
    """
    Updates pygump itself from SVN.
    """
    command = "sh -c 'svn update --non-interactive "
    if not options.debug: command += "-q " # suppress output
    svnlogfile = os.path.join( options.logdir, "svnuplog.txt" )
    
    command += os.path.join(options.homedir,'pygump')
    
    command += " >" + svnlogfile + " 2>&1'"

    try:
        result = os.system(command)
        if not os.name == 'dos' and not os.name == 'nt':
            result = (((result & 0xFF00) >> 8) & 0xFF)
            
        if result: # any not 0 is bad...
            msg = "An error occurred while self-updating pygump from svn"
            log.error( msg + ":")
            log.target.write(SEP); print SEP,
            
            svnlog=open(svnlogfile,'r')
            line = svnlog.readline()
            while line:
                log.target.write(line); print line,
                line = svnlog.readline()
    
            svnlog.close()
            log.target.write(SEP); print SEP,
            raise GumpEnvironmentError, msg
    finally:
        os.remove(svnlogfile)

def send_email(toaddr,fromaddr,subject,data,server,port=25):
    """
    Utility method for sending out e-mails.
    """
    rawdata = "Date: %s\r\nFrom: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s"	\
           	% (	time.strftime('%d %b %Y %H:%M:%S', time.gmtime()),
           	    fromaddr, toaddr,	subject,	data)
    # Attach to the SMTP server to send....
    #
    server = smtplib.SMTP(server,port)
    #server.set_debuglevel(1)
    server.sendmail(fromaddr, toaddr, rawdata)
    server.quit()

def send_error_email(Exception,details,options,log):
    """
    Send an error report by e-mail.
    """
    if options.mailserver and options.mailport and options.mailto and options.mailfrom:
        subject="Fatal error during pygump run [%s: %s]" % (options.hostname, options.name)
        body="""An unexpected error occurred during the pygump run on
%s (start time: %s, workspace: %s).

The reported exception:
------------------------------------------------------------------------------
%s: %s
------------------------------------------------------------------------------
More information may be available at:
    %s

The full run log of this run:
------------------------------------------------------------------------------
%s
------------------------------------------------------------------------------"""
        
        # get logfile contents
        logbody = ""
        logfile = None
        try:
            log.target.close(); log.target = None
            logfile = open(log.filename, 'r')
            line = logfile.readline()
            while line:
                logbody += line
                line = logfile.readline()
            
            logfile.close()
            log.target = open(log.filename, 'w', 0)
        except Exception, details:
            if not log.target:
                log.target = open(log.filename, 'w', 0)
            log.exception("Exception occurred reading log file")
            if logfile: logfile.close()
            if logbody == "":
                logbody = "ERROR: unable to read logfile!"
        
        # construct full body
        body = body % (options.hostname, options.starttime, options.name,
                       Exception, details, options.logurl, logbody)
        
        # send it off
        send_email(options.mailfrom, options.mailto, subject, body, options.mailserver,
                   options.mailport)
    else:
        raise GumpConfigError, "Insufficient information in the workspace for sending e-mail."


def start_engine(log,options):
    """
    Fire up the core pygump engine to do its thing.
    """
    from gump import engine
    engine.main(options)

def main():
    """
    The entrypoint into pygump. Extracts information and options from the arguments
    and environment variables, starts basic core utilities, then delegates to the
    main engine.
    """
    
    # we need python 2.3
    check_version()

    # get basic settings from environment variables
    _homedir = _hostname = _envfile = _workdir = _pythoncmd = _javahome = _projects = None
    try:
        envfile   = os.environ["GUMP_ENV_FILE"]
        pythoncmd = os.environ["GUMP_PYTHON"]
        javahome  = os.environ["JAVA_HOME"]

        _homedir   = os.environ["GUMP_HOME"]
        _hostname  = os.environ["GUMP_HOSTNAME"]
        try:
            _workdir   = os.environ["GUMP_WORKDIR"]
        except:
            _workdir = os.path.join(_homedir, "pygump", "work")
            
        try:
            _projects  = os.environ["GUMP_PROJECTS"]
        except:
            pass
    except Exception, details:
        print "ERROR: environment not setup properly. Please run pygump using the 'gump' script only."
        print "ERROR: The reported exception:"
        print "ERROR: %s: %s" % (Exception, details)
    
    # and some basic settings calculated from those
    _logdir        = os.path.join(_workdir, "log")
    _workspace     = os.path.join(_homedir, "metadata", "%s.xml" % (_hostname))
    
    # get basic settings from commandline arguments
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--debug",
                      action="store_true",
                      default=False)
    parser.add_option("--homedir",
                      action="store",
                      default=_homedir)
    parser.add_option("--hostname",
                      action="store",
                      default=_hostname)
    parser.add_option("-p",
                      "--project",
                      action="append",
                      dest="projects",
                      default=_projects)
    parser.add_option("--workdir",
                      action="store",
                      default=_workdir)
    parser.add_option("--logdir",
                      action="store",
                      default=_logdir)
    parser.add_option("-w",
                      "--workspace",
                      action="store",
                      default=_workspace)
    parser.add_option("--no-updates",
                      action="store_true",
                      dest="no_updates",
                      default=False)
    options, args = parser.parse_args()
    
    options.starttime = time.strftime('%d %b %Y %H:%M:%S', time.localtime())
    options.starttimeutc = time.strftime('%d %b %Y %H:%M:%S', time.gmtime())
    
    # create logger
    log = Logger(options.logdir)
    try:
        if options.debug:
            log.level = DEBUG
    
        # print some basic debug info...
        log.info("Pyump version %s starting..." % (GUMP_VERSION) )
        log.info("  (the detailed log is written to %s)" % (log.filename) )
        log.debug('  - hostname           : ' + options.hostname)
        log.debug('  - homedir            : ' + options.homedir)
        log.debug('  - current time       : ' + options.starttime)
        log.debug('  - current time (UTC) : ' + options.starttimeutc)
        log.debug('  - python version     : ' + sys.version)
        log.debug('  - python command     : ' + pythoncmd)
        
        log.debug('  - environment variables:')
        for (key, val) in os.environ.items():
            log.debug('      ' + key + '="' + val + '"')
        log.debug('')
        log.debug('  - command line arguments:')
        log.debug('      %s' % (sys.argv))
    
        # validate options and arguments
        if not hasattr(options, "projects"):
            log.debug("No projects to build set, defaulting to 'all'")
            options.projects = ["all"]
        if not os.path.exists(options.workspace):
            log.error("Workspace not found: %s." % options.workspace)
            sys.exit(1)
        
        # get some more options from the workspace
        parse_workspace(options.workspace, options)

        try:
            # self-update
            if not options.no_updates:
                svn_update(log, options)
                
            # finally: fire us up!
            start_engine(log, options)
            log.info("Run completed!")
        except Exception, details:
            # this is not good. Send e-mail to the admin, complaining rather loudly.
            log.exception("an uncaught exception occurred")
            try:
                send_error_email(Exception, details, options, log)
            except Exception, details:
                log.exception("Unable to send e-mail to administrator")
                pass
            
            sys.exit(1)
    finally:
        try:
            log.close()
        except:
            pass
    
    sys.exit(0)
