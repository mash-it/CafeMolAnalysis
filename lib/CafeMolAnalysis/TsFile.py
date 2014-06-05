#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import numpy as np
from pandas import DataFrame

class TsFile:
	maxwarn = 5
	def __init__(self, filename):
		self.filename = filename
		self.file = open(self.filename)

		# set header
		self.set_header()

		# read body
		self.file.seek(0)
		self.read()
		self.frame = DataFrame(self.table, columns = self.columns)
	
	def set_header(self):
		self.file.seek(0)

		for line in self.file:
			items = line.split()
			if len(items) > 0 and items[0][0:5] == "#unit":
				break

		self.columns = items[1:]

		self.warn = 0
		self.table = []

	def readline(self, unit = "all"):
		line = self.file.readline()

		if not line:
			# file is end
			raise StopIteration()

		if (line[0] == "#") and (line.split()[0] == "#" + unit):
			items = line.split()

			try:
				self.table.append(map(float,items[1:]))

			except ValueError:
				# show WARING if it contain invalid value (e.g. ********* )

				if self.warn < self.maxwarn:
					print ("It could not convert string to float:", file=sys.stderr)
					print (line, file=sys.stderr)

				self.warn += 1

	def read(self, line = float("inf"), unit = "all"):
		i = 0

		while True:
			try:
				self.readline(unit)
				i += 1
			except StopIteration:
				print("read {} lines from {} and finish to read.".format(i, self.filename))
				break
			if i >= line:
				print("read {} lines from {}.".format(i, self.filename))
				break

		self.table = np.array(self.table)

	def close(self):
		self.file.close()

