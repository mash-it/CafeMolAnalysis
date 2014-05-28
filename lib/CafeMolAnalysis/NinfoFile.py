#!/usr/bin/env python
# -*- coding:utf-8 -*-

class NinfoFile:
	def __init__(self, filename):
		self.file = open(filename, "r")

	def get_natcont(self):
		natcont = []
		
		self.file.seek(0)
		for line in self.file:
			items = line.split()
			if len(items) > 0 and items[0] == "contact":
				natcont.append({
					 "icon": int(items[1])
					,"imp1": int(items[4])
					,"imp2": int(items[5])
					,"go_nat": float(items[8])
				})
		
		return natcont
	
