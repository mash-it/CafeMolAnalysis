#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

# python default modules
import sys, argparse, time, os
from itertools import combinations
import multiprocessing as mp

# third-party modules
import numpy as np
import matplotlib.pyplot as plt

# modules by mash-it
from CafeMolAnalysis import DcdFile, NinfoFile

parser = argparse.ArgumentParser()
parser.add_argument("mode", type=str, help="output mode (movie or dmat)")
parser.add_argument("input", type=str, help="dcd file (need ninfo file in same dir)")
parser.add_argument("--ninfo", type=str, help="ninfo file (guess if no specification)")
parser.add_argument("-i", "--init", type=int, help="initial frame to write", default=0)
parser.add_argument("-l", "--last", type=int, help="last frame to write")
parser.add_argument("-f", "--freq", type=int, help="frequency of frames to output")
parser.add_argument("-n", "--number", type=int, help="total number of frames to output")
parser.add_argument("-o", "--output", type=str, help="name of directory for output img")
parser.add_argument("-p", "--process", type=int, help="number of process for parallel (dmat)")
parser.add_argument("--force", action='store_true', help='execute without confirm')
parser.add_argument("--dpi", type=float, help="dpi of output image", default=60)
args = parser.parse_args()

if args.mode == "movie" and args.output == None:
	raise TypeError("Please specify output directory by -o or --output")

inppath, inpfile = os.path.split(args.input)
inppath += "./"

inpfile = os.path.basename(args.input)
filehead = inpfile.rstrip(".dcd")

outpath = os.path.dirname(args.output.rstrip("/")+"/")

if outpath != "":
	outpath += "/"

# native contacts
if args.ninfo == None:
	args.ninfo = os.path.splitext(args.input)[0] + ".ninfo"
natcont = NinfoFile( args.ninfo ).get_natcont()

print("Open {}: {} Native Contacts".format(args.ninfo, len(natcont)))

# Trajectory File
dcd = DcdFile( args.input )
dcdhead = dcd.read_header()

print("Open {}: {} Frames".format(args.input, dcdhead["frames"]))

# define frames to read
if args.last == None:
	args.last = dcd.read_header()["frames"]

if args.number:
	if args.freq:
		sys.stderr.write("WARNING: Both freq (-f) and number (-n) is specified, so freq will be ignored.\n\n")
	#raise RuntimeError("Please specify only one of freq (-f) or number (-n).")
	freq = int(( args.last - args.init ) / args.number)
	frames = range(args.init, args.last, freq )
elif args.freq:
	frames = range(args.init, args.last + 1, args.freq )
else:
	raise RuntimeError("Please specify freq (-f) or number (-n).")

# confirm when too many files
if not args.force:
	print("This procedure will read {} frames. Continue? [y]/n:".format(len(frames)), end=" ")
	while True:
		ans = raw_input()
		if ans in ['y', 'Y']:
			break
		if ans in ['n', 'N']:
			sys.exit(1)
		print ("Please enter y or n.")
	
# make contactmap movie
if args.mode == "movie":
	# contactmap of native structure 
	contactmap_native = np.zeros((dcd.natoms + 1, dcd.natoms + 1))
	for cont in natcont:
		imp1, imp2 = cont["imp1"], cont["imp2"]
		contactmap_native[imp1, imp2] = 1
	
	# contactmap for each frame in dcd
	for frame in frames:
		contactmap = dcd.get_contactmap(frame, natcont)
		
		qscore = contactmap.sum() / len(natcont)
		print ("step {step:10d}: {cont:4d}/{ncont:4d} contacts"
			.format(step=frame*dcdhead["interval"], cont=int(contactmap.sum()), ncont=len(natcont)))
		
		fig = plt.figure()
		ax = fig.add_subplot(111)
		ax.set_title("{filehead}: {frame} frame (Q = {qscore:5.3f})"
			.format(filehead = filehead, frame = frame, qscore = qscore))
		ax.matshow(- contactmap + contactmap_native * 2)
		plt.savefig("{output}/{frame:06d}"
			.format(output = args.output, frame=frame), dpi=args.dpi)
		plt.close()

# make distance matrix
if args.mode == "dmat" and not args.process:
	START = time.time()
	contactmap = np.array([ dcd.get_contactmap(frame, natcont) for frame in frames ])

	dmat = np.zeros([len(frames), len(frames)])

	for i,j in combinations(range(len(frames)), r=2):
		dmat[i,j] = np.absolute(contactmap[i] - contactmap[j]).sum()

	dmat += dmat.T

	END = time.time()
	print("serial:", END - START)
	
	cax = plt.matshow(dmat)
	plt.colorbar(cax)
	plt.show()

if args.mode == "dmat" and args.process:
	START = time.time()

	contactmap = np.array([ dcd.get_contactmap(frame, natcont) for frame in frames ])

	# define subprocess for multiprocessing
	def subcalc(p):
		subdmat = np.zeros([len(frames), len(frames)])
		for (i,j) in p:
			subdmat[i,j] = np.absolute(contactmap[i] - contactmap[j]).sum()
		return subdmat
	
	# divide task equally
	task = list(combinations(range(len(frames)),r=2) )
	splitpos = [ i * len(task) for i in range(args.process) ]

	subtasks = []
	for i in range(args.process):
		ini, fin = None, None
		if i != 0:
			ini = len(task) * i / args.process
		if i != args.process - 1:
			fin = len(task) * (i+1) / args.process
		subtasks.append( task[ini : fin] )
	
	pool = mp.Pool(args.process)
	callback = pool.map(subcalc, subtasks)
	dmat = np.sum(callback, axis=0)
	
	dmat += dmat.T

	END = time.time()
	print("parallel", END - START)

	
	cax = plt.matshow(dmat)
	plt.colorbar(cax)
	plt.show()

