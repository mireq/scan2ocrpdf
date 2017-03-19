# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

import PIL.ImageOps
import imagehash
import numpy as np


def hash_to_number(hash_value):
	return np.frombuffer(np.packbits(hash_value.hash, axis=1).tobytes(), dtype=np.uint64)[0] #pylint: disable=no-member


class Font(object):
	def __init__(self):
		self.__symbol_images = {}


	def add_symbol(self, symbol):
		symmbol_image = PIL.ImageOps.invert(symbol.image.convert('L')).convert('1')
		symbol_hash = hash_to_number(imagehash.phash(symmbol_image))
		actual_image = self.__symbol_images.get((symbol.text, symbol_hash))
		if actual_image is None:
			actual_image = symbol.image.convert('I')
		else:
			if actual_image.size[0] < symbol.image.size[0] or actual_image.size[1] < symbol.image.size[1]:
				print("resize")
		self.__symbol_images[(symbol.text, symbol_hash)] = actual_image


class FontGenerator(object):
	def __init__(self):
		self.__fonts = defaultdict(Font)

	def add_symbol(self, symbol):
		self.__fonts[(symbol.font.id, symbol.font.pointsize)].add_symbol(symbol)
