# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from jinja2 import Environment, PackageLoader, select_autoescape


env = Environment(
	loader=PackageLoader('scan2ocrpdf', 'templates'),
	autoescape=select_autoescape(['html', 'xml'])
)
