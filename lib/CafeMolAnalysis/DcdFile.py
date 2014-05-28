#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
import struct
from struct import unpack
import numpy as np

POINTER_TO_NUMBER_OF_ATOMS = 428
POINTER_TO_COORDINATES = 436

THRESHOLD_OF_CONTACT = 1.2 # native contact

class DcdFile:
	def __init__(self, filename):
		self.f = open(filename, "rb")

		# validate file
		self.f.seek(4)
		signiture = unpack("4s", self.f.read(4))[0]
		if signiture != "CORD":
			raise RuntimeError("The DCD file is broken. File Signiture: {}".format(signiture))

		# number of atoms: which needed to read coords 
		# (other header info are not needed to read coords)
		self.f.seek(POINTER_TO_NUMBER_OF_ATOMS)
		self.natoms = unpack("i", self.f.read(4))[0] 
	
	def read_header(self):
		callback = {}

		# first block
		self.f.seek(0)
		blocksize = unpack("i", self.f.read(4))[0]

		data = unpack("4s9if10i", self.f.read(blocksize))

		callback = {
			 "frames": data[1]
			,"istart": data[2]
			,"interval": data[3]
			,"steps": data[4]
			,"units": data[5]
			,"delta": data[10]
		}

		return callback

	def read_frame(self, frame):
		try:
			self.f.seek(POINTER_TO_COORDINATES + frame * 12 * (self.natoms + 2))
	
			self.f.seek(4, 1)
			x = unpack("f" * self.natoms, self.f.read(4 * self.natoms))
			self.f.seek(8, 1)
			y = unpack("f" * self.natoms, self.f.read(4 * self.natoms))
			self.f.seek(8, 1)
			z = unpack("f" * self.natoms, self.f.read(4 * self.natoms))
		except struct.error:
			raise RuntimeError("{}-th frame does not exist in the dcd file.".format(frame))

		return np.array((x,y,z)).T
	
	"""
	def get_reg_frames(self, init = 0, last = None, freq = 1, number = None):
		
		if not last:
			last = self.read_header()["frames"]

		if not number:
			if not type(freq) == int:
				raise TypeError("freq must be integer ({} given)".format(type(freq)))
			if freq <= 0:
				raise ValueError("freq must be larger than 1.")

			return range(init, last+1, freq)

		if number:
			if not type(number) == int:
				raise TypeError("number must be integer ({} given)".format(type(number)))
			if number <= 0:
				raise ValueError("number must be larger than 1.")
			if number > last - init:
				raise ValueError("number is larger than frames in the range.")

			freq = int(( last - init ) / number )
			return range( init, last, freq )
	"""

	def get_contactmap(self, frame, natcont):
		""" format of natconts: [{"imp1":int, "imp2":int, "go_nat":float}] """
		crd = self.read_frame(frame)

		# add dummy particle to collect index of mass point
		dummy = np.array([[np.nan]*3])
		crd = np.concatenate([dummy, crd])

		contactmap = np.zeros((self.natoms + 1, self.natoms + 1))

		for cont in natcont:
			imp1, imp2 = cont["imp1"], cont["imp2"]
			distance = np.sqrt(((crd[imp1] - crd[imp2])**2).sum())
			if distance / cont["go_nat"] < THRESHOLD_OF_CONTACT:
				contactmap[imp1, imp2] = 1

		return contactmap

