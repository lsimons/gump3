#!/usr/bin/env python
import os
import sys
import imp

from mod_python import apache
from mod_python import util

from webgump.util import log
from webgump.util.log import Logger
from webgump.util import bust_cache

import webgump

DEBUG = True
#DEBUG = False

class Handler:
    def __init__(self, req):
        """A new handler is created by mod_python on every request."""
        self.status = None
        self.req = req
        
        if DEBUG:
            self.log = Logger(req, level=log.DEBUG, name="webgump.handler")
        else:
            self.log = Logger(req, level=log.INFO, name="webgump.handler")

    def handle(self, req):
        """This is the main delegation method that reads in config and then
        fires up a controller."""
        req.content_type = "text/html"
        try:
            self._settings()
            action = self._get_action()
            self.status = action(self.req, self.settings)
        except webgump.SecurityError, msg:
            self.req.status = apache.HTTP_BAD_REQUEST
            bust_cache(self.req)

            self.req.write("<p style=\"color: red\"><strong>%s</strong></p>" % msg)
            self.log.exception("Naughty client!", doNotLogToWebPage=True)
            return apache.OK
        except webgump.Error, msg:
            self.req.status = apache.HTTP_INTERNAL_SERVER_ERROR
            bust_cache(self.req)

            self.req.write("<p><strong>%s</strong></p>" % msg)
            self.log.exception("Internal error!", doNotLogToWebPage=True)
            return apache.OK
        except IOError:
            self.req = None
            self.log.error("Client is gone.")
            return apache.OK
        except:
            try:
                # sufficiently advanced controllers should ideallly do their own
                # exception handling and recovery. This is a minimal failsafe.
                self.req.write("<p><strong>An unexpected problem has occurred!</strong></p>")
                self.log.exception("Uncaught exception!")
            except:
                pass
        
        #self._debug_info()
    
        if self.status:
            return self.status
        else:
            return apache.OK
    
    def _settings(self):
        """Set defaults, then load config file, then set some more settings based
        on the mod_python provided environment."""
        self.req.add_common_vars()
        self.settings = {
            'DEBUG': DEBUG,
            'PAGE_TITLE': "Front Page",
            'db_host': "localhost",
            'db_user': "webgump",
            'db_password': "webgump",
            'db_name': "webgump"
        }
        for key,val in self.req.subprocess_env.items():
            self.settings[key] = val

        self.settings['TEMPLATE_ROOT'] = \
            os.path.abspath(os.path.join(self.settings['DOCUMENT_ROOT'], "../templates"))
        self.settings['DOCUMENTATION_ROOT'] = \
            os.path.abspath(os.path.join(self.settings['DOCUMENT_ROOT'], "../xdocs"))

        query_vars = util.parse_qs(self.req.subprocess_env["QUERY_STRING"])
        self.settings['HTTP_GET_VARS'] = query_vars
        for key,val in query_vars.items():
            if key in self.settings:
                raise webgump.SecurityError, "Illegal query parameter '%s'!" % key
            val.reverse()
            self.settings[key] = val[0]
            val.reverse()
    
    def _get_action(self):
        """Determine the controller to fire up."""
        controller = self.settings['controller'] or "home"
        action = self.settings['action'] or "view"
        self.log.debug("Executing %s::%s()" % (controller,action))
        try:
            module = _find_controller_module(controller)
        except:
            e = sys.exc_info()
            raise e[0], "Unable to find controller '%s': %s" % (controller, e[1]), e[2]
        
        if module and hasattr(module, action):
            method = getattr(module, action)
            if callable(method):
                return method
            else:
                raise "Action '%s' of controller '%s' not callable" % (action, controller)
        else:
            raise "No action '%s' available in controller '%s'" % (action, controller)   
        
    def _debug_info(self):
        """Write basic environment information to the web page."""
        try:
            if DEBUG:
                self.req.write("<hr/><p><strong>DEBUG INFO</strong></p>\n")
                self.req.write("<p><em>Webapp Settings</em></p>\n<pre>")
                for (key,val) in self.settings.items():
                    self.req.write("%s: %s\n" % (key,val))
                self.req.write("</pre>")
        except:
            pass


def _find_controller_module(controller):
    """Finds and loads a module within lsdblog.controllers based on the provided
    controller name."""
    import webgump.controllers
    
    modulename = "webgump.controllers.%s" % controller
    module = None
    try:
        module = sys.modules[modulename]
    except KeyError:
        n = "webgump"
        (f1,p,d) = imp.find_module(n)
        try:
            m = imp.load_module(n,f1,p,d)
            p = m.__path__
            n = "controllers"
            (f2,p,d) = imp.find_module(n,p)
            try:
                m = imp.load_module(n,f2,p,d)
                p = m.__path__
            
                (f3,p,d) = imp.find_module(controller, p)
                try:
                    module = imp.load_module(controller, f3, p, d)
                finally:
                    if f3:
                        f3.close()
            finally:
                if f2:
                    f2.close()
        finally:
            if f1:
                f1.close()
    return module
