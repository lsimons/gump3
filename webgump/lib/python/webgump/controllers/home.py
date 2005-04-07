#!/usr/bin/env python
from webgump.util.template import TemplateEngine
from gump.util.mysql import Database
from webgump.util.log import Logger

def view(req, settings):
    req.content_type = "text/html"
    
    dblog = Logger(req, name="webgump.db")
    db = Database(dblog,settings["db_host"], settings["db_user"],
                  settings["db_password"],settings["db_name"])
    
    (affected, rows) = db.execute('SELECT * FROM test;')
    content = []
    for row in rows:
        content.append(row["content"])
    
    settings["content"] = content
    settings["log"] = Logger(req, name="webgump.ezt")
    template = "view"
    template_engine = TemplateEngine(settings['TEMPLATE_ROOT'])
    try:
        template_engine.render_template(template, req, settings)
    except:
        req.write("<p><strong>Error occurred rendering template '%s':</strong></p>\n" % template)
        raise
