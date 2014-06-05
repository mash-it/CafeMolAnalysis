#!/bin/bash

# clear
rm test/output/*

# set PATH
export PATH=$PATH:`pwd`/bin
export PYTHONPHAT=$PYTHONPATH:`pwd`/lib

# cafeplot
cafeplot.py test/input/test.ts -o test/output/cafeplot-normal.png
cafeplot.py test/input/test.ts -y go -b 10 -o test/output/cafeplot-hist.png

# contactmap
contactmap.py movie test/input/test.dcd -n 10 -o test/output/ --force

# dcdedit
dcdedit.py test/input/test.dcd -o test/output/dcdedit-dcd2movie.movie
dcdedit.py test/input/test.dcd -e thin -n 10 -o test/output/dcdedit-thin.dcd
dcdedit.py test/input/test.dcd -e head -n 10 -o test/output/dcdedit-head.dcd
dcdedit.py test/input/test.dcd -e tail -n 10 -o test/output/dcdedit-tail.dcd

echo ""
echo "------------------------------"
echo ""

cd test/output/

ngcount=0

for x in *
do
	if cmp $x ../compare/$x > /dev/null; then
		echo OK > /dev/null
	else
		ngcount=$(($ngcount + 1))
		echo NG $x
	fi
done

echo ""

if [ $ngcount == 0 ]
then
	echo "all OK"
else
	echo $ngcount "NG detected"
fi

#TODO: detect python error
