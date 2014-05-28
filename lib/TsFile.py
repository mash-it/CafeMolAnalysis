#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

class TsFile:
	maxwarn = 5
	def __init__(self, filename):
		self._filename = filename
		self._file = open(self._filename)
		self.set_vars()

	def set_vars(self):

		self.warn = 0

		self.step = []
		self.tempk = []
		self.radg = []
		self.etot = []
		self.velet = []
		self.qscore = []
		self.rmsd = []
		self.local = []
		self.go = []
		self.repul = []
	
		self.data = {
			 "step"    : self.step
			,"tempk"   : self.tempk
			,"radg"    : self.radg
			,"etot"    : self.etot
			,"velet"   : self.velet
			,"qscore"  : self.qscore
			,"rmsd"    : self.rmsd
			,"local"   : self.local
			,"go"      : self.go
			,"repul"   : self.repul
		}

	def readline(self, unit = "all"):
		line = self._file.readline()

		if line == "":
			# file is end
			raise StopIteration()

		if (line[0] == "#") and (line.split()[0] == "#" + unit):
			items = line.split()
			try:
				# Check appendable all data
				int(items[1]), float(items[2]), float(items[3]), float(items[4]), float(items[5])
				float(items[6]), float(items[7]), float(items[8]), float(items[9]), float(items[10])				

				# execute appending if ValueError not exist
				self.step.append  ( int(items[ 1]) )
				self.tempk.append ( float(items[ 2]) )
				self.radg.append  ( float(items[ 3]) )
				self.etot.append  ( float(items[ 4]) )
				self.velet.append ( float(items[ 5]) )
				self.qscore.append( float(items[ 6]) )
				self.rmsd.append  ( float(items[ 7]) )
				self.local.append ( float(items[ 8]) )
				self.go.append    ( float(items[ 9]) )
				self.repul.append ( float(items[10]) )

			except ValueError:
				# show WARING if it contain invalid value (e.g. ********* )
				if self.warn < self.maxwarn:
					print ("Could not convert string to float:", file=sys.stderr)
					print (line, file=sys.stderr)
					self.warn += 1

	def read(self, count = 0):
		if count > 0:
			self.read_n_points(count)
		else:
			self.read_whole()

	def read_whole(self, unit = "all"):
		i = 0
		flag = True
		while flag:
			try:
				self.readline(unit)
				i += 1
			except StopIteration:
				break
		print("read {} lines from {}".format(i, self._filename))
	
	def read_n_points(self, n, unit="all"):
		i = 0
		while len(self.step) < n:
			i += 1
			if self.readline(unit) == False:
				break

		print ("read {} lines and end file".format(i))

	def close(self):
		self._file.close()

