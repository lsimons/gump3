#!/usr/bin/env python
import os
from ezt import Template

class TemplateEngine:
    def __init__(self, template_root):
        self.template_root = template_root

    def render_template(self, template, target, data):
        if isinstance(template, Template):
            template.generate(target, data)
        else:
            self.get_template(template).generate(target, data)

    def get_template(self, name):
        templatefile = os.path.abspath(os.path.join(self.template_root, "%s.ezt" % name))
        template = Template(templatefile)
        return template
