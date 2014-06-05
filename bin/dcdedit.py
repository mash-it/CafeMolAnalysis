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

edittype = ["thin", "head", "tail"]

parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, help="input dcd file")
parser.add_argument("--psf", type=str, help="input psf file (need when output movie file)")
parser.add_argument("-e", "--edit", type=str, help=" | ".join(edittype))
parser.add_argument("-o", "--output", type=str, help="output dcd file", required=True)
parser.add_argument("-n", type=int, help="frequency to output")
args = parser.parse_args()

dcd = DcdFile(args.input)
nframes = dcd.header['frames']

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
#   make iterator of frames, rewrite header
# --------------------------------------------------

if args.edit and not(args.n):
	raise RuntimeError("number argument (-n) must be input for editting.")

if args.edit == None:
	frames = range(0, nframes)

elif args.edit == "thin":
	frames = range(0, nframes, args.n)
	dcd.header["frames"] = len(frames)
	dcd.header["interval"] *= args.n
	dcd.header["delta"] *= args.n

elif args.edit == "head":
	frames = range(args.n)
	dcd.header["frames"] = args.n
	dcd.header["steps"] = args.n * dcd.header["interval"]

elif args.edit == "tail":
	frames = range(nframes-args.n, nframes)
	dcd.header["frames"] = args.n
	dcd.header["steps"] = args.n * dcd.header["interval"]

else:
	raise RuntimeError("edit mode (-e) must be {}.".format( ", ".join(edittype)))

# --------------------------------------------------
#   write dcd file
# --------------------------------------------------
if extension == "dcd":
	ofile = open(args.output, "wb")
	ofile.write(dcd.write_header())
	
	for frame in frames:
		ofile.write(dcd.read_frame_raw(frame))
	
	ofile.close()

# --------------------------------------------------
#   write movie file
# --------------------------------------------------
if extension == "movie":
	ofile = open(args.output, "w")
	for frame in frames:
		ofile.write("<<<<    {}\n".format(frame * dcd.header["interval"]))
		ofile.write("<<\n")
		ofile.write(dcd.write_pdb(frame, psf))
		ofile.write(">>\n>>>>\nEND\n\n")

