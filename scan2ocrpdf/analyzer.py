# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from PIL import Image
from tesserocr import PyTessBaseAPI, PSM, PT, RIL, iterate_level
from itertools import chain


class Size(object):
	width = 0
	height = 0

	def __init__(self, width, height):
		self.width = width
		self.height = height


class BoundingBox(object):
	x1 = 0
	y1 = 0
	width = 0
	height = 0

	@property
	def x2(self):
		return self.x1 + self.width

	@property
	def y2(self):
		return self.y1 + self.height

	@staticmethod
	def from_size(x1, y1, width, height):
		instance = BoundingBox()
		instance.x1 = x1
		instance.y1 = y1
		instance.width = width
		instance.height = height
		return instance

	@staticmethod
	def from_coordinates(x1, y1, x2, y2):
		width = x2 - x1
		height = y2 - y1
		return BoundingBox.from_size(x1, y1, width, height)

	def relative_to(self, other):
		return BoundingBox.from_size(self.x1 - other.x1, self.y1 - other.y1, self.width, self.height)


class Page(object):
	blocks = []
	size = None

	@property
	def paragraphs(self):
		return chain(*(block.paragraphs for block in self.blocks))

	@property
	def lines(self):
		return chain(*(paragraph.lines for paragraph in self.paragraphs))

	@property
	def words(self):
		return chain(*(line.words for line in self.lines))

	@property
	def symbols(self):
		return chain(*(word.symbols for word in self.words))


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
	text = ''

	def __init__(self):
		self.font = Font()


class Symbol(object):
	bounding_box = None
	confidence = 0.0
	image = None
	text = ''


class Analyzer(object):
	TEXT_TYPES = set([PT.FLOWING_TEXT, PT.HEADING_TEXT, PT.PULLOUT_TEXT, PT.VERTICAL_TEXT, PT.CAPTION_TEXT])

	def __init__(self, lang=None):
		super(Analyzer, self).__init__()
		kwargs = {}
		if lang is not None:
			kwargs['lang'] = lang
		self.api = PyTessBaseAPI(psm=PSM.AUTO_OSD, **kwargs)

	def analyze_image(self, image):
		page = Page()

		self.api.SetImage(image)
		self.api.Recognize()
		iterator = self.api.GetIterator()
		page.blocks = self.__decode_blocks(iterator, image)
		page.size = Size(*image.size)

		return page

	def close(self):
		self.api.End()

	def __decode_blocks(self, iterator, image):
		blocks = []
		for tesseract_block in iterate_level(iterator, RIL.BLOCK):
			block = Block()
			block.bounding_box = BoundingBox.from_coordinates(*tesseract_block.BoundingBox(RIL.BLOCK))
			if not tesseract_block.GetUTF8Text(RIL.BLOCK).strip():
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
			paragraph.bounding_box = BoundingBox.from_coordinates(*tesseract_paragraph.BoundingBox(RIL.PARA))
			paragraph.lines = self.__decode_lines(iterator)
			paragraphs.append(paragraph)
			if iterator.IsAtFinalElement(RIL.BLOCK, RIL.PARA):
				break
		return paragraphs

	def __decode_lines(self, iterator):
		lines = []
		for tesseract_line in iterate_level(iterator, RIL.TEXTLINE):
			line = TextLine()
			line.bounding_box = BoundingBox.from_coordinates(*tesseract_line.BoundingBox(RIL.TEXTLINE))
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
			word.bounding_box = BoundingBox.from_coordinates(*tesseract_word.BoundingBox(RIL.WORD))
			word.confidence = float(tesseract_word.Confidence(RIL.WORD)) / 100.0
			word.text = tesseract_word.GetUTF8Text(RIL.WORD)
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
			symbol.bounding_box = BoundingBox.from_coordinates(*tesseract_symbol.BoundingBox(RIL.SYMBOL))
			symbol.confidence = float(tesseract_symbol.Confidence(RIL.SYMBOL)) / 100.0
			symbol.text = tesseract_symbol.GetUTF8Text(RIL.SYMBOL)
			symbol.image = tesseract_symbol.GetBinaryImage(RIL.SYMBOL).convert('1', dither=Image.NONE)
			symbols.append(symbol)
			if iterator.IsAtFinalElement(RIL.WORD, RIL.SYMBOL):
				break
		return symbols
