# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from .jinja2 import env
from .utils import makedirs


class AnalyzedPageDebugGenerator(object):
	def __init__(self, debug_dir):
		self.debug_dir = debug_dir
		self.__dest_dir = None

	def generate(self, page, image, image_path):
		if not self.__debugging_enabled():
			return
		self.__make_dest_dir(image_path)
		self.__generate_html_output(page, image)

	def __debugging_enabled(self):
		return self.debug_dir is not None

	def __make_dest_dir(self, image_path):
		self.__dest_dir = os.path.join(self.debug_dir, os.path.basename(image_path))
		makedirs(self.__dest_dir)
		makedirs(os.path.join(self.__dest_dir, 'images'))

	def __generate_html_output(self, page, image):
		print(page, image)
		template = env.get_template('analyzed_page_debug.html')
		result = template.render(**self.__get_template_context()) # pylint: disable=no-member
		with open(os.path.join(self.__dest_dir, 'page.html'), 'w') as f:
			f.write(result)

	def __get_template_context(self):
		return {}
