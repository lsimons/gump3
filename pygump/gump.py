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
        if not os.path.isdir(logdir): os.mkdir(logdir)
        self.logdir = logdir
        self.level = level
        self.console_level = console_level

        rundatetime = time.strftime('%d%m%Y_%H%M%S')
        filename = 'gump_log_' + runDateTime + '.txt'
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
        if self.level >= DEBUG:
            self.target.write(message);
        if self.console_level >= DEBUG:
            print message
    
    def info(self, msg):
        message = 'INFO: %s\n' % (msg)
        if self.level >= INFO:
            self.target.write(message);
        if self.console_level >= INFO:
            print message
    
    def warning(self, msg):
        message = 'WARNING: %s\n' % (msg)
        if self.level >= WARNING:
            self.target.write(message);
        if self.console_level >= WARNING:
            print message
    
    def error(self, msg):
        message = 'ERROR: %s\n' % (msg)
        if self.level >= ERROR:
            self.target.write(message);
        if self.console_level >= ERROR:
            print message

    def critical(self, msg):
        message = 'CRITICAL: %s\n' % (msg)
        if self.level >= CRITICAL:
            self.target.write(message);
        if self.console_level >= CRITICAL:
            print message

def check_version():
    """
    Prints error message and exits if python version < 2.3.
    """
    (major, minor, micro, releaselevel, serial) = sys.version_info
    if not major >=2 and minor >= 3:
        print 'CRITICAL: Gump requires Python 2.3 or above. The current version is %s.' % sys.version()
        exit(1)
        
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

    # Mail reporting
    options.private     = w.getAttribute('private')
    options.mailserver  = w.getAttribute('mailserver') or 'localhost'
    options.mailport    = w.getAttribute('mailport') or 25
    options.mailto      = w.getAttribute('administrator') 
    options.mailfrom    = w.getAttribute('email') 

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
    command = "svn update --non-interactive "
    svnlogfile = os.path.join( options.logdir, "svnuplog.txt" )
    if not options.debug: command += "-q" # suppress output
    
    command += os.path.join(options.homedir,'pygump')
    
    command += "2>&1 > " + svnlogfile

    try:
        result = os.system(command)
        if result: # any not 0 is bad...
            msg = "An error occurred while self-updating pygump from svn"
            log.error( msg + ":")
            log.target.write(SEP)
            
            svnlog=open(svnlogfile,'r')
            line = svnlog.readline()
            while line:
                log.target.write(line)
                line = input.readline()
    
            svnlog.close
            log.target.write(SEP)
            raise RuntimeError, msg
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

def send_error_email(Exception,details,log):
    """
    TODO. Send an error report by e-mail.
    """

def start_engine(log,options):
    """
    TODO. Fire up the core pygump engine to do its thing.
    """
    pass

def main():
    """
    The entrypoint into pygump. Extracts information and options from the arguments
    and environment variables, starts basic core utilities, then delegates to the
    main engine.
    """
    
    # we need python 2.3
    check_version()

    # get basic settings from environment variables
    _homedir = _hostname = _envfile = _workdir = _pythoncmd = _javahome = None
    try:
        envfile   = os.environ["GUMP_ENV_FILE"]
        pythoncmd = os.environ["GUMP_PYTHON"]
        javahome  = os.environ["JAVA_HOME"]

        _homedir   = os.environ["GUMP_HOME"]
        _hostname  = os.environ["GUMP_HOSTNAME"]
        _workdir   = os.environ["GUMP_WORKDIR"]
        _projects  = os.environ["GUMP_PROJECTS"]
    except:
        print "pygump: environment not setup properly. Please run pygump using the 'gump' script only."
    
    # and some basic settings calculated from those
    _logdir        = os.path.join(_workdir, "/log")
    _workspace     = os.path.join(_homedir, "pygump", "metadata", "%s.xml" % (_hostname))
    
    # get basic settings from commandline arguments
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--debug",
                      action="store_true",
                      default=False)
    parser.add_option("-h",
                      "--homedir",
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
    parser.add_option("--logfile",
                      action="store",
                      default=_logdir)
    parser.add_option("-w",
                      "--workspace",
                      action="store",
                      default=_workspace)
    parser.add_option("--no-updates",
                      action="store_false",
                      dest="do_updates",
                      default=True)
    options, args = parser.parse_args()
    
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
        log.debug('  - current time       : ' + time.strftime('%d %b %Y %H:%M:%S', time.localtime()))
        log.debug('  - current time (UTC) : ' + time.strftime('%d %b %Y %H:%M:%S', time.gmtime()))
        log.debug('  - python version     : ' + sys.version)
        log.debug('  - python command     : ' + pythoncmd)
        
        log.debug('  - environment variables:')
        for (key, val) in os.environ.items():
            log.debug('      ' + envkey + '="' + envval + '"\n')
        log.debug('')
        log.debug('  - command line arguments:')
        log.debug('      %s' % (sys.argv))
    
        # validate options and arguments
        if not hasattr(options, "projects") or len(options.projects) == 0:
            log.debug("No projects to build set, defaulting to 'all'")
            options.projects = ["all"]
        if not os.path.exists(options.workspace):
            log.error("Workspace not found: %s." % options.workspace)
            exit(1)
        
        # get some more options from the workspace
        parse_workspace(options.workspace, options)

        try:
            # self-update
            if(options.do_updates):
                svn_update(log, options)
                
            # finally: fire us up!
            start_engine(log, options)
        except Exception, details:
            # this is not good. Send e-mail to the admin, complaining rather loudly.
            log.error("gump: an uncaught exception occurred: " + details)
            try:
                send_error_email(Exception, details, log)
            except Exception, details:
                log.error("gump: additionally, an error occurred sending an e-mail about that exception: " + details)
                pass
            
            exit(1)
    finally:
        try:
            log.close()
        except:
            pass
