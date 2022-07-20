#!/bin/ksh -x

# Usage: make-index.sh source-directory

# This makes a file list as lines of "size file-name".  It then groups
# the files by the sum of the sizes by calling "group-files.awk".  It
# strips the directory prefix (by using "%P" in printf).

# Examples
# make-index.sh source-directory > index.txt

if [ "$#" -ne 1 ]; then
    echo "Usage: ksh $0 source-directory"
    exit 1
fi

find "$1" -xdev -type f -printf "%s %P\n" \
     | awk -M -f $(dirname $0)/group-files.awk
