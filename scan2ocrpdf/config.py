# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import argparse


class ConfigRegistry(object):
	def __init__(self):
		parser = argparse.ArgumentParser(description="Convert series of images to PDF")
		parser.add_argument('--deskew', dest='deskew', action='store_true', help="Deskew images")
		parser.add_argument('-l', '--lang', dest='lang', help="Specify language(s) used for OCR")
		parser.add_argument('--debug-dir', dest='debug_dir', help="Directory to store debug files")
		parser.add_argument('images', metavar='images', nargs='+', help="List of images")
		parser.set_defaults(deskew=False)
		args = parser.parse_args()

		self.deskew = args.deskew
		self.lang = args.lang
		self.debug_dir = args.debug_dir
		self.images = args.images


def get_config():
	if get_config.registry is None:
		get_config.registry = ConfigRegistry()
	return get_config.registry
get_config.registry = None
