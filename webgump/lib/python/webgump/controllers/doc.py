#!/usr/bin/env python
import webgump
from webgump.util.log import Logger
from webgump.util.template import TemplateEngine

from gump.util.mysql import Database

from mod_python import apache
import os
from rfc822 import formatdate

DEFAULT_PAGE_NAME="index.xml"

def view(req, settings):
    log = Logger(req, name="controllers.doc")
    dblog = Logger(req, name="webgump.db")
    db = Database(dblog,settings["db_host"], settings["db_user"],
                  settings["db_password"],settings["db_name"])
    
    page = DEFAULT_PAGE_NAME
    if "page" in settings:
        page = settings["page"]
    
    docroot = settings["DOCUMENTATION_ROOT"]
    pagepath = os.path.abspath(os.path.join(docroot, page))
    log.debug("Looking for documentation page '%s'" % pagepath)
    if not pagepath.startswith(docroot):
        raise webgump.SecurityError, "Requested page '%s' is illegal!" % page
    
    if not os.path.exists(pagepath) or not os.path.isfile(pagepath):
        raise webgump.Error, "Requested page '%s' cannot be found!" % page
    
    if not os.access(pagepath, os.R_OK):
        raise webgump.SecurityError, "Access denied to page '%s'!" % page
    
    f = False
    try:
        try:
            lastmodified = os.path.getmtime(pagepath)
            req.mtime = lastmodified
            req.content_type = "text/html"
            
            #TODO: implement fancy templating, xml transformation, and other other
            # stuff here. Maybe even interface with cocoon :-). Hahahah.
        
            f = open(pagepath, mode='r')
            for line in f:
                req.write(line)
            
            return apache.OK
        except IOError:
            raise webgump.Error, "Error reading requested page '%s'!" % page
    finally:
        if f:
            try:
                f.close()
            except:
                pass
