# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from tesserocr import PyTessBaseAPI, PSM, PT, RIL, iterate_level


class Page(object):
	blocks = []


class Block(object):
	bounding_box = None
	image = None
	paragraphs = []


class Paragraph(object):
	bounding_box = None
	lines = []


class TextLine(object):
	bounding_box = None
	words = []


class Font(object):
	bold = False
	italic = False
	underline = False
	monospace = False
	serif = False
	pointsize = 0
	id = 0


class Word(object):
	bounding_box = None
	confidence = 0.0
	symbols = []

	def __init__(self):
		self.font = Font()


class Symbol(object):
	bounding_box = None
	confidence = 0.0
	image = None
	text = ''


class Analyzer(object):
	lang = None

	TEXT_TYPES = set([PT.FLOWING_TEXT, PT.HEADING_TEXT, PT.PULLOUT_TEXT, PT.VERTICAL_TEXT, PT.CAPTION_TEXT])

	def __init__(self):
		super(Analyzer, self).__init__()
		kwargs = {}
		if self.lang is not None:
			kwargs['lang'] = self.lang
		self.api = PyTessBaseAPI(psm=PSM.AUTO_OSD, **kwargs)

	def analyze_image(self, image):
		page = Page()

		self.api.SetImage(image)
		self.api.Recognize()
		iterator = self.api.GetIterator()
		page.blocks = self.__decode_blocks(iterator, image)

		return page

	def close(self):
		self.api.End()

	def __decode_blocks(self, iterator, image):
		blocks = []
		for tesseract_block in iterate_level(iterator, RIL.BLOCK):
			block = Block()
			block.bounding_box = tesseract_block.BoundingBox(RIL.BLOCK)
			if not tesseract_block.GetUTF8Text(RIL.BLOCK):
				block.image = tesseract_block.GetImage(RIL.BLOCK, 0, image)
				blocks.append(block)
				continue
			block.paragraphs = self.__decode_paragraphs(iterator)
			blocks.append(block)
		return blocks

	def __decode_paragraphs(self, iterator):
		paragraphs = []
		for tesseract_paragraph in iterate_level(iterator, RIL.PARA):
			paragraph = Paragraph()
			paragraph.bounding_box = tesseract_paragraph.BoundingBox(RIL.PARA)
			paragraph.lines = self.__decode_lines(iterator)
			paragraphs.append(paragraph)
			if iterator.IsAtFinalElement(RIL.BLOCK, RIL.PARA):
				break
		return paragraphs

	def __decode_lines(self, iterator):
		lines = []
		for tesseract_line in iterate_level(iterator, RIL.TEXTLINE):
			line = TextLine()
			line.bounding_box = tesseract_line.BoundingBox(RIL.TEXTLINE)
			line.words = self.__decode_words(iterator)
			lines.append(line)
			if iterator.IsAtFinalElement(RIL.PARA, RIL.TEXTLINE):
				break
		return lines

	def __decode_words(self, iterator):
		words = []
		for tesseract_word in iterate_level(iterator, RIL.WORD):
			font_attributes = tesseract_word.WordFontAttributes()
			word = Word()
			word.bounding_box = tesseract_word.BoundingBox(RIL.WORD)
			word.confidence = float(tesseract_word.Confidence(RIL.WORD)) / 100.0
			word.symbols = self.__decode_symbols(iterator)
			word.font.bold = font_attributes['bold']
			word.font.italic = font_attributes['italic']
			word.font.underline = font_attributes['underlined']
			word.font.monospace = font_attributes['monospace']
			word.font.serif = font_attributes['serif']
			word.font.pointsize = font_attributes['pointsize']
			word.font.id = font_attributes['font_id']
			words.append(word)
			if iterator.IsAtFinalElement(RIL.TEXTLINE, RIL.WORD):
				break
		return words

	def __decode_symbols(self, iterator):
		symbols = []
		for tesseract_symbol in iterate_level(iterator, RIL.SYMBOL):
			symbol = Symbol()
			symbol.bounding_box = tesseract_symbol.BoundingBox(RIL.SYMBOL)
			symbol.confidence = float(tesseract_symbol.Confidence(RIL.SYMBOL)) / 100.0
			symbol.text = tesseract_symbol.GetUTF8Text(RIL.SYMBOL)
			symbol.image = tesseract_symbol.GetBinaryImage(RIL.SYMBOL)

			symbols.append(symbol)
			if iterator.IsAtFinalElement(RIL.WORD, RIL.SYMBOL):
				break
		return symbols
