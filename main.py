# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

import scan2ocrpdf.debug


SHOW_RESULTS = False


def draw_block(draw, bbox, fill=None, outline=None):
	draw.rectangle(((bbox[0], bbox[1]), (bbox[2], bbox[3])), fill=fill, outline=outline)


def main():
	config = scan2ocrpdf.get_config()
	reader = scan2ocrpdf.Reader(deskew=config.deskew)
	analyzer = scan2ocrpdf.Analyzer(lang=config.lang)
	analyzed_page_debug_generator = scan2ocrpdf.debug.AnalyzedPageDebugGenerator(debug_dir=config.debug_dir)

	try:
		for image_path in config.images:
			image = reader.read_image(image_path)
			page = analyzer.analyze_image(image)
			analyzed_page_debug_generator.generate(page, image, image_path)
	except scan2ocrpdf.UserException as e:
		sys.stderr.write(str(e))
	finally:
		analyzer.close()


if __name__ == "__main__":
	main()
