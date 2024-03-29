#!/bin/ksh

# Usage: catalog-files.sh index-file N

# This enumerates a list of files in the group at N in the index-file
# which is created by "make-index.sh".  "expr 0 + N" is used to ignore
# leading zeros on the 2nd argument.

set -e
indexfile="$1"
blocks=$(printf "%04d" $(expr 0 + $2))
blocke=$(printf "%04d" $(expr 1 + $2))
#sed -n "/^${blocks}\$/,/^${blocke}\$/p" "${indexfile}"
awk "/^${blocks}\$/{flag=1;next}/^${blocke}\$/{exit 0}flag" "${indexfile}" \
    | sed -e 's/^[0-9]* //'
