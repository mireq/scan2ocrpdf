# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math

import cv2
import numpy as np
from PIL import Image


SHOW_RESULTS = False


def detect_angle(image):
	WORK_IMAGE_SIZE = (1024, 1024)
	MAX_ANGLE = 8

	image = image.convert('L')
	image.thumbnail(WORK_IMAGE_SIZE)
	cv_image = np.asarray(image, dtype=np.uint8)
	cv_image = cv2.adaptiveThreshold(cv_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 5)
	cv2.bitwise_not(cv_image, cv_image)

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
		cv2.bitwise_not(draw_lines, draw_lines)

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
