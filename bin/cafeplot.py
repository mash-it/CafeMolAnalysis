#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cafeplot.py by Mashiho Ito.

step-qsocre plot:
	$ cafeplot.py example.ts

step-etot plot:
	$ cafeplot.py example.ts -y etot

multi-unit plot:
	$ cafeplot.py example.ts --unit all,1,2

histogram of etot:
	$ cafeplot.py example.ts -y etot -b 100

output png image:
	$ cafeplot.py example.ts -o output.png

"""

from __future__ import print_function

from CafeMolAnalysis import TsFile
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("input", type=str, help="input ts file")
parser.add_argument("-x", type=str, help="X-axis (default: step)", default="step")
parser.add_argument("-y", type=str, help="Y-axis (default: qscore)", default="qscore")
parser.add_argument("-b", "--bins", type=int, help="number of bins (Histogram Mode)")
parser.add_argument("-t", "--type", type=str, help="type of plot")
parser.add_argument("-o", "--output", type=str, help="output image file")
parser.add_argument("--dpi", type=int, help="resolution of output image", default=120)
parser.add_argument("--title", type=str, help="title of plot")
parser.add_argument("--xlog", action="store_true", help="use log scale in X-axis")
parser.add_argument("--ylog", action="store_true", help="use log scale in Y-axis")
parser.add_argument("--xrange", type=str, help="range of X-axis: float,float")
parser.add_argument("--yrange", type=str, help="range of Y-axis: float,float")
parser.add_argument("-u", "--unit", type=str, help="unit to plot: e.g. all,1,2", default='all')

args = parser.parse_args()

# load matplotlib
# if savefig, use Agg for ssh remote login
if args.output != None:
	import matplotlib
	matplotlib.use("Agg")
import matplotlib.pyplot as plt

# open ts file (not read immediately)
ts = TsFile(args.input, read=False)

units = args.unit.split(",")

# --------------------------------------------------
# 	set plot type
# --------------------------------------------------
plottype = {
	 'line'   : '-'
	,'dot'    : ','
	,'point'  : '.'
	,'cross'  : 'x'
	,'circle' : 'o'
}

if args.type == None:
	if args.x == "step":
		args.type = "line"
	else:
		args.type = "point"
		
if args.type in plottype:
	args.type = plottype[args.type]

if args.title == None:
	plt.title(args.input)
else:
	plt.title(args.title)

# --------------------------------------------------
# 	plot (normal mode)
# --------------------------------------------------
if args.bins == None:
	# if two or more lines set legend
	for unit in units:
		ts.read(unit=unit)
		# plot (normal mode)
		plt.plot(ts.frame[args.x], ts.frame[args.y], args.type, label=unit)
		plt.xlabel(args.x)
		plt.ylabel(args.y)

	# legend (Q-score)
	if len(units) > 1:
		plt.legend(loc='best')

	# range (Q-score)
	if args.x == "qscore":
		plt.xlim([0,1])
	if args.y == "qscore":
		plt.ylim([0,1])

# --------------------------------------------------
# 	plot (histogram mode)
# --------------------------------------------------

if args.bins != None:
	bins = args.bins
	minY, maxY = ts.frame[args.y].min(), ts.frame[args.y].max()
	delta = (maxY - minY) / bins
	inis = [ minY+ x*(maxY-minY)/bins for x in range(bins) ]
	if args.xrange:
		xbound = args.xrange.split(",")
		condition = lambda x: x > float(xbound[0]) and x < float(xbound[1])
		plt.hist( filter(condition, ts.frame[args.y]), bins )
	else:
		plt.hist( ts.frame[args.y], bins )
	plt.xlabel(args.y)
	plt.ylabel("Freq")

# --------------------------------------------------
# 	adjust range and scale
# --------------------------------------------------

if args.xlog:
	plt.xscale("log")
if args.ylog:
	plt.yscale("log")

if args.xrange:
	xbound = args.xrange.split(",")
	xmin = float(xbound[0])
	xmax = float(xbound[1])
	plt.xlim([xmin,xmax])

if args.yrange:
	ybound = args.yrange.split(",")
	ymin = float(ybound[0])
	ymax = float(ybound[1])
	plt.ylim([ymin,ymax])

plt.grid()

# --------------------------------------------------
# 	output to window or file
# --------------------------------------------------
if args.output == None:
	plt.show()
else:
	plt.savefig(args.output, dpi=args.dpi)

