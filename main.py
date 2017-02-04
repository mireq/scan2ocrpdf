# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

from PIL import Image, ImageDraw
from tesserocr import PyTessBaseAPI, PSM, RIL, iterate_level

from scan2ocrpdf import deskew_image


SHOW_RESULTS = False


def draw_block(draw, bbox, fill=None, outline=None):
	draw.rectangle(((bbox[0], bbox[1]), (bbox[2], bbox[3])), fill=fill, outline=outline)


def main():
	image = Image.open(sys.argv[1]).convert('RGBA')
	image = deskew_image(image)
	overlay = Image.new('RGBA', image.size, (255,255,255,0))
	draw = ImageDraw.Draw(overlay)
	with PyTessBaseAPI(psm=PSM.AUTO_OSD) as api:
		api.SetImage(image)
		api.Recognize()
		iterator = api.GetIterator()
		for block in iterate_level(iterator, RIL.BLOCK):
			for para in iterate_level(iterator, RIL.PARA):
				for word in iterate_level(iterator, RIL.WORD):
					for symbol in iterate_level(iterator, RIL.SYMBOL):
						confidence = max((symbol.Confidence(RIL.SYMBOL) / 100.0) * 4.0 - 3.0, 0.0)
						red = 255
						green = 255
						if confidence > 0.5:
							red = int(((1.0 - confidence) * 2.0) * 255)
						if confidence < 0.5:
							green = int((confidence * 0.5) * 255)
						draw_block(draw, block.BoundingBox(RIL.SYMBOL), fill=(red,green,0,192), outline=(128,128,128,255))
						if iterator.IsAtFinalElement(RIL.WORD, RIL.SYMBOL):
							break
					draw_block(draw, block.BoundingBox(RIL.WORD), outline=(0,0,255,255))
					if iterator.IsAtFinalElement(RIL.PARA, RIL.WORD):
						break
				draw_block(draw, block.BoundingBox(RIL.PARA), outline=(255,255,0,255))
				if iterator.IsAtFinalElement(RIL.BLOCK, RIL.PARA):
					break
			draw_block(draw, block.BoundingBox(RIL.BLOCK), outline=(255,0,0,255))
	out = Image.alpha_composite(image, overlay)
	out.show()

	#	layout = api.AnalyseLayout()
	#	orientation, direction, order, deskew_angle = layout.Orientation()
	#	print ("Orientation: {:d}".format(orientation))
	#	print ("WritingDirection: {:d}".format(direction))
	#	print ("TextlineOrder: {:d}".format(order))
	#	print ("Deskew angle: {:.4f}".format(deskew_angle))



if __name__ == "__main__":
	main()
