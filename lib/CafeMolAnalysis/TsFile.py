#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import numpy as np
from pandas import DataFrame

class TsFile:
	maxwarn = 5
	def __init__(self, filename, read=True):
		self.filename = filename
		self.file = open(self.filename)

		# set header
		self.set_header()

		if read:
			self.read()
	
	def set_header(self):
		self.file.seek(0)

		for line in self.file:
			items = line.split()
			if len(items) > 0 and items[0][0:5] == "#unit":
				break

		self.columns = items[1:]

		self.warn = 0

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
		self.table = []
		self.file.seek(0)

		i = 0

		while True:
			try:
				self.readline(unit)
				i += 1
			except StopIteration:
				#print("read {} lines from {} and finish to read.".format(i, self.filename))
				break
			if i >= line:
				print("read {} lines from {}.".format(i, self.filename))
				break

		self.table = np.array(self.table)
		self.frame = DataFrame(self.table, columns = self.columns)
		self.frame['step'] = self.frame['step'].apply(int)

	def getTP(self, rcoord, conditions):
		""" get Transition Path between two state """
		isA = conditions[0]
		isB = conditions[1]

		A_arrive = B_arrive = A_stay = B_stay = 0

		# get initial state
		for val in self.frame[rcoord]:
			if isA(val):
				last_state = 'A'
				break
			if isB(val):
				last_state = 'B'
				break

		AtoB = []
		BtoA = []
		waitingA = []
		waitingB = []

		for i, p in self.frame.iterrows():
			now = p['step']

			# back or stay A
			if isA(p[rcoord]) and last_state == "A":
				A_leave = now
				
			# arrive A
			if isA(p[rcoord]) and last_state == "B":
				BtoA.append(now - B_leave)
				waitingB.append(B_leave - B_arrive)

				A_arrive = A_leave = now
				last_state = "A"
				
			# arrive B
			if isB(p[rcoord]) and last_state =="A":
				B_arrive = B_leave = now
				last_state = "B"
				AtoB.append(now - A_leave)
				waitingA.append(A_leave - A_arrive)

			# back or stay B
			if isB(p[rcoord]) and last_state =="B":
				B_leave = now

		"""
		# old version
		for i, p in self.frame.iterrows():
			if isA(p[rcoord]):
				A_last = p['step']
				if last_state == 'B':
					# B to A transition
					BtoA.append( (B_last, p['step']) )
					last_state = 'A'

			if isB(p[rcoord]):
				B_last = p['step']
				if last_state == 'A':
					# A to B transition
					AtoB.append( (A_last, p['step']) )
					last_state = 'B'
		"""

		return (AtoB, BtoA, waitingA, waitingB)

	def close(self):
		self.file.close()

