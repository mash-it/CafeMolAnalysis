#!/usr/bin/env python
# -*- coding: utf-8 -*-

# todo: multimodel, multiunits in one PDB file

class PdbFile:
	def __init__(self, filename):
		self.filename = filename
		self.file = open(filename)
	
	def read_atoms(self):
		self.file.seek(0)
		self.atoms = []
		for line in self.file:
			if len(line) > 4 and line[0:4] == "ATOM":
				self.atoms.append(self.read_atomline(line))
	
	def read_atomline(self, line):
		# to avoid IndexError
		line += " " * 80

		columns = [
			 ("serial", 7,11, int)
			,("atomname", 13,16, str)
			,("altLoc", 17,17, str)
			,("resName", 18,20, str)
			,("chainID", 22,22, str)
			,("resSeq", 23,26, int)
			,("iCode", 27,27, str)
			,("x", 31,38, float)
			,("y", 39,46, float)
			,("z", 47,53, float)
			,("occupancy", 55,60, float)
			,("tempFactor", 61,66, float)
			,("element", 77,78, str)
			,("charge", 79,80, str)
		]

		atom = {}
		for c in columns:
			try:
				atom[c[0]] = c[3](line[c[1]-1: c[2]])
			except ValueError:
				pass
				
		return atom

