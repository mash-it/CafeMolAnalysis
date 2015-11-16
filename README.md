CafeMolAnalysis: Analysis Tools for CafeMol
====

Analysis Tools for [CafeMol](www.cafemol.org), a Coarse-Grained biomolecular simulation software.

Operating Environment
----

* Python 2.7.6
* CafeMol 2.1

Dependent Libraries
---

* numpy (>1.8.1)
* matplotlib (>1.3.1)
* pandas (>0.14.0)


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
contactmap.py movie example.dcd -n 100 -o output/
```

dcdedit.py
----

Edit DCD file

```
# reduce frames to 1/10
dcdedit.py input.dcd -e thin -n 10 -o thin.dcd

# get initial 100 frames
dcdedit.py input.dcd -e head -n 100 -o head.dcd

# get last 100 frames
dcdedit.py input.dcd -e tail -n 100 -o tail.dcd

# convert to movie file (series of PDB format)
dcdedit.py input.dcd -o output.movie
```

DcdFile
----

```python
from CafeMolAnalysis import DcdFile, NinfoFile, PsfFile

dcd = DcdFile('sample.dcd')
ninfo = NinfoFile('sample.ninfo')
natcont = ninfo.get_natcont()
psf = PsfFile('sample.psf')

# get header
dcd.read_header()

# get coordinates in a snapshot
frame = 100
dcd.read_frame(frame)

# output pdb file of a snapshot
frame = 200
open("output.pdb").write(dcd.write_pdb(frame, psf))

# get contactmap 
frame = 0
contactmap = dcd.get_contactmap(0, natcont) # numpy 2D array
```



