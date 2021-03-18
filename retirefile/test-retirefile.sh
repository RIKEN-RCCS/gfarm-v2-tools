#!/bin/ksh

## Test retirefile.py.  The scripts are called in steps.  Steps (1)
## and (2) clean the local and remote directories.  Step (3) makes
## files to copy in the local directory "gomi".  Step (4) copies files
## via gfpcopy.  Step (5) lists remote files to check Step (4).  Step
## (6) runs retirefile.py.  Files are only removed when Step (6) is
## run after 30 minutes.

## (0) $ export GFDIR=/home/hpNNNNNN/hpciNNNNNN
## (0) $ export GFLIB=${HOME}/lib/libgfarm.so
## (1) $ rm -fr gomi
## (2) $ sh test-clean-test-files.sh
## (3) $ sh test-make-test-files.sh
## (4) $ sh test-copy-by-gfpcopy.sh
## (5) $ sh test-list-test-files.sh
## (6) $ sh test-retirefile.sh

. test-common.sh
checksetting
python3 retirefile.py --verbose --so ${GFLIB} gomi ${GFDIR}/gomi
