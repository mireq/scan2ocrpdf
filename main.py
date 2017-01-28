# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math
import sys

import cv2
import numpy as np
from PIL import Image
from tesserocr import PyTessBaseAPI, PSM


SHOW_RESULTS = False


def detect_angle(image):
	WORK_IMAGE_SIZE = (1024, 1024)
	MAX_ANGLE = 10

	#image = Image.open(input_filename).convert('L')
	image = image.convert('L')
	image.thumbnail(WORK_IMAGE_SIZE)
	cv_image = np.asarray(image, dtype=np.uint8)
	cv_image = cv2.adaptiveThreshold(cv_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 201, 5)
	cv2.bitwise_not(cv_image, cv_image);

	lines = cv2.HoughLinesP(
		cv_image,
		rho=1,
		theta=np.pi / 180,
		threshold=100,
		minLineLength=cv_image.shape[1] / 2,
		maxLineGap=20
	)

	draw_lines = cv_image
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
			image = image.crop((x_crop, y_crop, image.width - x_crop, image.height - y_crop))
	return image


def main():
	image = Image.open(sys.argv[1]).convert('RGBA')
	image = deskew_image(image)
	image.show()
	#with PyTessBaseAPI(psm=PSM.AUTO_OSD) as api:
	#	image = Image.open("/dev/shm/pdf_tmp/text.png")
	#	api.SetImage(image)
	#	api.Recognize()
	#	layout = api.AnalyseLayout()
	#	orientation, direction, order, deskew_angle = layout.Orientation()
	#	print ("Orientation: {:d}".format(orientation))
	#	print ("WritingDirection: {:d}".format(direction))
	#	print ("TextlineOrder: {:d}".format(order))
	#	print ("Deskew angle: {:.4f}".format(deskew_angle))



if __name__ == "__main__":
	main()
