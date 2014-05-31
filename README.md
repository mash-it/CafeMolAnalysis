CafeMolAnalysis: Analysis Tools for CafeMol
====

Analysis Tools for [CafeMol](www.cafemol.org), a Coarse-Grained biomolecular simulation software.

Operating Environment
----

* Python 2.7.6
* CafeMol 2.1

Dependency
---

* numpy (>1.8.1)
* matplotlib (>1.3.1)


Installation
----

1) make PYTHONPATH to ./lib

```
$ cd ./lib
$ export PYTHONPATH=$PYTHONPATH:`pwd`
```

or copy/link to a directory that is in your PYTHONPATH

2) make PATH to ./bin or copy/link files to a directory that is in your PATH

cafeplot.py
----

Visualization of *.ts file

```
# step-qscore plot
cafeplot.py example.ts

# step-etot plot
cafeplot.py example.ts -y etot

# histogram of etot
cafeplot.py example.ts -y etot -b 100

# output as png image
cafeplot.py example.ts -o output.png
```

contactmap.py
----

Making contactmap from dcd file

Make contactmap movie (a series of images) along trajectory

```
cafeplot.py movie example.dcd -n 100 -o output/
```

dcdedit.py
----

Edit DCD file

```
# reduce frames to 1/10
dcdedit.py input.dcd 

# convert to movie file (series of PDB format)
dcdedit.py input.dcd -o output.movie
```

