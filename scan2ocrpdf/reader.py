# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from PIL import Image

from .deskew import deskew_image
from .exceptions import UserException


class ReadError(UserException):
	pass


class Reader(object):
	def __init__(self, deskew=False):
		self.deskew = deskew

	def read_image(self, path):
		try:
			image = Image.open(path).convert('RGBA')
		except (FileNotFoundError, OSError, IOError) as e:
			raise ReadError(str(e))
		if self.deskew:
			image = deskew_image(image)
		return image
