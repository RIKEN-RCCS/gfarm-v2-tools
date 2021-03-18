#!/bin/ksh
. test-common.sh
checksetting
mkdir -p gomi/d0 gomi/d1
for i in 0 1 2 3 4 5 6 7 8 9; do
	cp ./LICENSE gomi/bsd.$i
	cp ./LICENSE gomi/d0/bsd.$i
	cp ./LICENSE gomi/d1/bsd.$i
done
