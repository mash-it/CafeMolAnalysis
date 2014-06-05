#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
	drip: Analysis Tools for CafeMol 
"""

import sys

dependency = []
try:
	import numpy
except ImportError:
	dependency.append("numpy")
	
try:
	import matplotlib
except ImportError:
	dependency.append("matplotlib")

try:
	import pandas
except ImportError:
	dependency.append("pandas")

if len(dependency) > 0:
	raise RuntimeError("The following required modules can not be import: {}".format(", ".join(dependency)))

from TsFile import TsFile
from PsfFile import PsfFile
from PdbFile import PdbFile
from DcdFile import DcdFile
from NinfoFile import NinfoFile

