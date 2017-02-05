# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from tesserocr import PyTessBaseAPI, PSM, PT, RIL, iterate_level


class Page(object):
	blocks = []


class Block(object):
	bounding_box = None
	image = None


class Analyzer(object):
	TEXT_TYPES = set([PT.FLOWING_TEXT, PT.HEADING_TEXT, PT.PULLOUT_TEXT, PT.VERTICAL_TEXT, PT.CAPTION_TEXT])

	def __init__(self):
		super(Analyzer, self).__init__()
		self.api = PyTessBaseAPI(psm=PSM.AUTO_OSD)

	def analyze_image(self, image):
		page = Page()

		self.api.SetImage(image)
		self.api.Recognize()
		iterator = self.api.GetIterator()
		page.blocks = self.__decode_blocks(iterator, image)
		#for tesseract_block in iterate_level(iterator, RIL.BLOCK):
		#	block = Block()
		#	block.bounding_box = tesseract_block.BoundingBox(RIL.BLOCK)
		#	block.block_type = tesseract_block.BlockType()
		#	if not block.block_type in self.TEXT_TYPES:
		#		block.image = tesseract_block.GetImage(RIL.BLOCK, 0, image)
		#	for tesseract_para in iterate_level(iterator, RIL.PARA):
		#		for tesseract_textline in iterate_level(iterator, RIL.TEXTLINE):
		#			for tesseract_word in iterate_level(iterator, RIL.WORD):
		#				for symbol in iterate_level(iterator, RIL.SYMBOL):
		#					if iterator.IsAtFinalElement(RIL.WORD, RIL.SYMBOL):
		#						break
		#				if iterator.IsAtFinalElement(RIL.TEXTLINE, RIL.WORD):
		#					break
		#			if iterator.IsAtFinalElement(RIL.PARA, RIL.TEXTLINE):
		#				break
		#		if iterator.IsAtFinalElement(RIL.BLOCK, RIL.PARA):
		#			break

		return page

	def close(self):
		self.api.End()

	def __decode_blocks(self, iterator, image):
		blocks = []
		for tesseract_block in iterate_level(iterator, RIL.BLOCK):
			print(tesseract_block.GetUTF8Text(RIL.BLOCK))
			block = Block()
			block.bounding_box = tesseract_block.BoundingBox(RIL.BLOCK)
			if not tesseract_block.BlockType() in self.TEXT_TYPES:
				block.image = tesseract_block.GetImage(RIL.BLOCK, 0, image)
			blocks.append(block)
		return blocks
