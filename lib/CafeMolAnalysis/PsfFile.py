#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

class PsfFile:
	def __init__(self, filename):
		self.filename = filename
		self.file = open(filename, "r")
		self.read()
	
	def read(self):
		self.atoms = []
		self.bonds = []
		state = ""

		for line in self.file:
			items = line.split()
			if len(items) > 1 and items[1].rstrip(":") == "!NATOM":
				state = "ATOM"
			elif len(items) > 1 and items[1].rstrip(":") == "!NBOND": 
				state = "BOND"
			elif state == "ATOM":
				self.atoms.append(self.read_atom(line))
			elif state == "BOND":
				self.bonds += self.read_bond(line)
			else:
				print("Unknown Line: {}".format(line.rstrip("\n")))

		print("read {} and get {} atoms and {} bonds"
			.format(self.filename, len(self.atoms), len(self.bonds)))

	
	def read_atom(self, line):
		callback = {
			 "atomid": int(line[0:8])
			,"segname": line[8:11].rstrip(" ").lstrip(" ")
			,"resid": int(line[11:15])
			,"resname": line[15:23].rstrip(" ").lstrip(" ")
			,"atomname": line[23:29].rstrip(" ").lstrip(" ")
			,"atomtype": line[29:35].rstrip(" ").lstrip(" ")
			,"charge": float(line[39:50])
			,"mass": float(line[50:64])
		}
		return callback
	
	def read_bond(self, line):
		items = [ int(a) for a in line.split()]
		return [(items[0], items[1]), (items[2], items[3]), (items[4], items[5])]

