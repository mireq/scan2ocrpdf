# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw
from tesserocr import PyTessBaseAPI, PSM, RIL, iterate_level


SHOW_RESULTS = False


def detect_angle(image):
	WORK_IMAGE_SIZE = (1024, 1024)
	MAX_ANGLE = 8

	image = image.convert('L')
	image.thumbnail(WORK_IMAGE_SIZE)
	cv_image = np.asarray(image, dtype=np.uint8)
	cv_image = cv2.adaptiveThreshold(cv_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 5)
	cv2.bitwise_not(cv_image, cv_image);

	lines = cv2.HoughLinesP(
		cv_image,
		rho=1,
		theta=np.pi / 180,
		threshold=100,
		minLineLength=cv_image.shape[1] / 2,
		maxLineGap=20
	)

	if lines is None or lines.shape[0] < 10:
		return 0

	draw_lines = None
	if SHOW_RESULTS:
		#draw_lines = np.full_like(cv_image, 0)
		draw_lines = np.asarray(image, dtype=np.uint8)
		cv2.bitwise_not(draw_lines, draw_lines);

	total_vect = [0, 0]
	for line in lines:
		line = line[0]
		point1 = (line[0], line[1])
		point2 = (line[2], line[3])
		angle = math.atan2(point2[0] - point1[0], point2[1] - point1[1]) * 180 / math.pi
		if angle > 180:
			angle = angle - 180
		if (angle > MAX_ANGLE and angle < 90 - MAX_ANGLE) or (angle > 90 + MAX_ANGLE and angle < 180 - MAX_ANGLE):
			continue
		vect = (point2[0] - point1[0], point2[1] - point1[1])
		if angle < 90 - MAX_ANGLE or angle > 90 + MAX_ANGLE:
			if vect[1] > 0:
				vect = (vect[1], -vect[0])
			else:
				vect = (-vect[1], vect[0])
		total_vect[0] += vect[0]
		total_vect[1] += vect[1]
		if SHOW_RESULTS:
			cv2.line(draw_lines, point1, point2, (255, 0, 0))

	rot = math.atan2(total_vect[0], total_vect[1]) * 180 / math.pi
	corrective_angle = rot - 90.0

	if SHOW_RESULTS:
		cv2.imshow("gray image", draw_lines)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	return corrective_angle


def deskew_image(image, crop=True):
	angle = detect_angle(image)
	if angle != 0:
		image = image.rotate(-angle, resample=Image.BICUBIC)
		if crop:
			ratio = abs(math.tan(math.radians(angle)))
			x_crop = ratio * image.height / 2
			y_crop = ratio * image.width / 2
			if x_crop < image.width // 2 and y_crop < image.height // 2:
				image = image.crop((x_crop, y_crop, image.width - x_crop, image.height - y_crop))
	return image


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
