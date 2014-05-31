#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
dcdedit.py by Mashiho Ito.

reduce frames to 1/10 
	$ dcdedit.py original.dcd -f 10 -o reduced.dcd

convert to movie file (series of PDB format; need psf file)
	$ dcdedit.py example.dcd -o example.movie

"""

from __future__ import print_function

import argparse

# modules by mash-it
from CafeMolAnalysis import DcdFile, PsfFile

parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, help="input dcd file")
parser.add_argument("--psf", type=str, help="input psf file (need when output movie file)")
parser.add_argument("-o", "--output", type=str, help="output dcd file", required=True)
parser.add_argument("-f", "--freq", type=int, help="frequency to output", default=1)
args = parser.parse_args()

dcd = DcdFile(args.input)

# --------------------------------------------------
#   validate input/output file
# --------------------------------------------------
extension = args.output.split(".")[-1]

if not extension in ["dcd", "movie"]:
	raise RuntimeError("Invalid output file type: it has to be dcd or movie.")

if extension == "movie":
	if args.psf:
		psf = PsfFile(args.psf)
	else:
		psf = PsfFile(args.input.rstrip("dcd") + "psf")
	#raise RuntimeError("Need psf file (--psf) to write movie file.")

# --------------------------------------------------
#   write dcd file
# --------------------------------------------------
if extension == "dcd":
	ofile = open(args.output, "wb")
	ofile.write(dcd.read_header_raw())
	#TODO: rewrite frames in dcd header
	
	for frame in range(0, dcd.header['frames'], args.freq):
		ofile.write(dcd.read_frame_raw(frame))
	
	ofile.close()

# --------------------------------------------------
#   write movie file
# --------------------------------------------------
if extension == "movie":
	ofile = open(args.output, "w")
	for frame in range(0, dcd.header['frames'], args.freq):
		ofile.write("<<<<    {}\n".format(frame * dcd.header["interval"]))
		ofile.write("<<\n")
		ofile.write(dcd.write_pdb(frame, psf))
		ofile.write(">>\n>>>>\nEND\n\n")

