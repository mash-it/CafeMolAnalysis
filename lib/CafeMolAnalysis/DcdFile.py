#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
import struct
from struct import pack, unpack
import numpy as np

THRESHOLD_OF_CONTACT = 1.2 # native contact

class DcdFile:
	def __init__(self, filename):
		self.f = open(filename, "rb")

		# validate file
		self.f.seek(4)
		signiture = unpack("4s", self.f.read(4))[0]
		if signiture != "CORD":
			raise RuntimeError("The DCD file is broken. File Signiture: {}".format(signiture))

		self.read_header_structure()
		self.read_header()

	def read_header_structure(self):
		""" read block structure of header """	

		self.f.seek(0)
		blocksize = []
		pointer_to_block = [4]

		for i in range(3):
			bsize = unpack("i", self.f.read(4))[0]
			self.f.seek(bsize, 1)
			bsize_confirm = unpack("i", self.f.read(4))[0]

			if bsize != bsize_confirm:
				raise RuntimeError("Invalid header structure")

			blocksize.append(bsize)
			pointer_to_block.append(self.f.tell())

		self.blocksize = blocksize
		self.pointer_to_block = pointer_to_block

	def read_header_raw(self):
		self.f.seek(0)
		return self.f.read(self.pointer_to_block[3])
	
	def write_header(self):
		blocks = []

		# first block
		blocks.append(pack("4s9if10i",
			"CORD",
			self.header["frames"],
			self.header["istart"],
			self.header["interval"],
			self.header["steps"],
			self.header["units"],
			0,0,0,0,
			self.header["delta"],
			0,0,0,0,0,0,0,0,0,
			self.header["nver"]))

		# second block
		lines = len(self.header['description'].split("\n"))
		blocks.append(pack("i{}s".format(lines * 80),
			lines,
			self.header['description']))

		# third block
		blocks.append(pack("i", self.natoms))

		callback = b""
		for block in blocks:
			size = pack("i", len(block))
			callback += size + block + size

		return callback

	def read_header(self):
		callback = {}

		# first block
		self.f.seek(self.pointer_to_block[0])

		data = unpack("4s9if10i", self.f.read(self.blocksize[0]))

		header = {
			 "frames": data[1]
			,"istart": data[2]
			,"interval": data[3]
			,"steps": data[4]
			,"units": data[5]
			,"delta": data[10]
			,"nver": data[20]
		}

		# second block
		self.f.seek(self.pointer_to_block[1])
		self.f.seek(4,1) # skip blocksize

		# number of lines in description
		n_lines = unpack("i", self.f.read(4))[0]
		linesize = 80

		description = []

		for i in range(n_lines):
			description.append(unpack("{}s".format(linesize), self.f.read(linesize))[0])

		header["description"] = "\n".join(description)

		# third block
		self.f.seek(self.pointer_to_block[2])
		self.f.seek(4,1) # skip blocksize
		self.natoms = unpack("i", self.f.read(4))[0]

		header["natoms"] = self.natoms

		self.header = header
		return header
	
	def show_header(self):
		for key in self.header.keys():
			print("{key:^13s}: {value}".format(key=key, value=self.header[key]))

	def read_frame_raw(self, frame):
		try:
			self.f.seek(self.pointer_to_block[3] + frame * 12 * (self.natoms + 2))
		except struct.error:
			raise RuntimeError("{}-th frame does not exist in the dcd file.".format(frame))

		return self.f.read(12 * (self.natoms + 2))

	def read_frame(self, frame):
		try:
			self.f.seek(self.pointer_to_block[3] + frame * 12 * (self.natoms + 2))
			self.f.seek(4, 1)
			x = unpack("f" * self.natoms, self.f.read(4 * self.natoms))
			self.f.seek(8, 1)
			y = unpack("f" * self.natoms, self.f.read(4 * self.natoms))
			self.f.seek(8, 1)
			z = unpack("f" * self.natoms, self.f.read(4 * self.natoms))
		except struct.error:
			raise RuntimeError("{}-th frame does not exist in the dcd file.".format(frame))

		return np.array((x,y,z)).T
	
	def write_pdb(self, frame, psf):
		callback = ""
		for atom in psf.atoms:
			crd = self.read_frame(frame)
			callback += "ATOM  {serial:5d} {atomname:4s}{altLoc:1s}{resName:3s} {chainID:1s}{resSeq:4d}{iCode:1s}   {x:8.3f}{y:8.3f}{z:8.3f}\n".format(
				 serial = atom['atomid']
				,atomname = atom['atomname']
				,altLoc = ""
				,resName = atom['resname']
				,chainID = "A"
				,resSeq = atom['resid']
				,iCode = ""
				,x = crd[atom['atomid']-1][0]
				,y = crd[atom['atomid']-1][1]
				,z = crd[atom['atomid']-1][2]
			)
		return callback

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

