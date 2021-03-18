#!/bin/ksh
. test-common.sh
checksetting
gfpcopy -v gomi "gfarm://ms-0.r-ccs.riken.jp:601${GFDIR}"
