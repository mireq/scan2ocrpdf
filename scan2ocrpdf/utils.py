# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import errno
import os


def makedirs(path):
	try:
		os.makedirs(path)
	except OSError as exception:
		if exception.errno != errno.EEXIST or not os.path.isdir(path):
			raise
