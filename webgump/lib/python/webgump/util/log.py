#!/usr/bin/env python
import time
import sys

from mod_python import apache

# log levels
DEBUG = apache.APLOG_DEBUG      #7
INFO = apache.APLOG_INFO        #6
WARNING = apache.APLOG_WARNING  #4
ERROR = apache.APLOG_ERR        #3
CRITICAL = apache.APLOG_CRIT    #2
NONE = -1000

LOG_LEVEL_NAMES = {
    DEBUG:'DEBUG',
    INFO:'INFO',
    WARNING:'WARNING',
    ERROR:'ERROR',
    CRITICAL:'CRITICAL'
}

class Logger:
    """Simple logger similar to PEP 249 that logs to an apache error log."""
    def __init__(self, req=None, level=DEBUG, printLevel=ERROR, name=None):
        self.req = req
        if req:
            self.error_func = req.log_error
        else:
            self.error_func = apache.log_error
        self.level = level
        self.printLevel = printLevel
        self.name = name


    def log(self, level, msg):
        try:
            logToWebPage = self.req and level <= self.printLevel
            if logToWebPage: self.req.write("<pre>\n")
            
            if self.name:
                for line in msg.split("\n"):
                    self.error_func("[%s] %s" % (self.name, line), level)
                    if logToWebPage: self.req.write("[%s] %s: %s\n" % (self.name, LOG_LEVEL_NAMES[level], line))
            else:
                for line in msg.split("\n"):
                    self.error_func(msg, level)
                    if logToWebPage: self.req.write("%s: %s\n" % (LOG_LEVEL_NAMES[level], line))
                    
            if logToWebPage: self.req.write("</pre>\n")
        except IOError:
            # probably a client is "gone"
            pass
    
    def debug(self, msg):
        if self.level >= DEBUG:
            self.log(DEBUG, msg);
    
    def info(self, msg):
        if self.level >= INFO:
            self.log(INFO, msg);
    
    def warning(self, msg):
        if self.level >= WARNING:
            self.log(WARNING, msg);
    
    def error(self, msg):
        if self.level >= ERROR:
            self.log(ERROR, msg);
    
    def exception(self, msg):
        info = sys.exc_info()
        import traceback
        from StringIO import StringIO
        buf = StringIO()
        traceback.print_exception( info[0], info[1], info[2], file=buf)
        self.error("%s\n%s" % (msg, buf.getvalue()))

    def critical(self, msg):
        if self.level >= CRITICAL:
            self.log(CRITICAL, msg);

