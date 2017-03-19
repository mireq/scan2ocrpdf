# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import os
from collections import namedtuple

from .generator import FontGenerator
from .jinja2 import env
from .utils import makedirs


AnalyzePageRequest = namedtuple('AnalyzePageRequest', ['page', 'image', 'image_path'])


def write_template(template_name, output_name, dest_dir, context):
	template = env.get_template(template_name)
	result = template.render(**context) # pylint: disable=no-member
	with open(os.path.join(dest_dir, output_name), 'w') as f:
		f.write(result)


class AnalyzedPageDebugGenerator(object):
	def __init__(self, debug_dir):
		self.debug_dir = debug_dir
		self.request = None
		self.__font_generator = FontGenerator()
		self.__dest_dir = None

	def generate(self, page, image, image_path):
		self.request = AnalyzePageRequest(page, image, image_path)
		if not self.__debugging_enabled():
			return
		self.__make_dest_dir()
		self.__extract_images()
		self.__generate_glyphs()
		self.__generate_html_output()

	def __debugging_enabled(self):
		return self.debug_dir is not None

	def __make_dest_dir(self):
		self.__dest_dir = os.path.join(self.debug_dir, os.path.basename(self.request.image_path))
		makedirs(self.__dest_dir)
		makedirs(os.path.join(self.__dest_dir, 'images'))
		makedirs(os.path.join(self.__dest_dir, 'css'))
		makedirs(os.path.join(self.__dest_dir, 'js'))
		makedirs(os.path.join(self.__dest_dir, 'fonts'))

	def __extract_images(self):
		for symbol in self.request.page.symbols:
			image_hash = hashlib.md5(symbol.image.tobytes()).hexdigest()
			symbol.image_path = os.path.join('images', image_hash + '.png')
			symbol.image.save(os.path.join(self.__dest_dir, symbol.image_path))

	def __generate_glyphs(self):
		for symbol in self.request.page.symbols:
			self.__font_generator.add_symbol(symbol)

	def __generate_html_output(self):
		context = self.__get_template_context()
		write_template('analyzed_page_debug.html', 'page.html', self.__dest_dir, context)
		write_template('css/page.css', 'page.css', os.path.join(self.__dest_dir, 'css'), context)
		write_template('js/inspector.js', 'inspector.js', os.path.join(self.__dest_dir, 'js'), context)
		write_template('js/utils.js', 'utils.js', os.path.join(self.__dest_dir, 'js'), context)

	def __get_template_context(self):
		return {
			'title': os.path.basename(self.request.image_path),
			'page': self.request.page,
		}
