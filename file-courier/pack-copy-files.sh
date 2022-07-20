#!/bin/sh

# Usage: pack-copy-files.sh source-directory target-directory temporary-prefix index-file n0 n1

# This archives-then-transfers files in groups from n0 to n1 (n1
# inclusive).  It uses an index-file created by "make-index.sh".
# "source-directory" should be a local directory, and
# "target-directory" should include a remote host prefix.
# "temporary-prefix" is something like /tmp/xxxx, then a temporary
# file will be /tmp/xxxx-0000.zip.  A "temporary-prefix" path should
# be absolte, because it does change-directory to the source-directory
# before calling zip.  "set_-e" lets the process exit on errors.

# Examples
# pack-copy-files.sh /source/somewhere host:/target/elsewhere \
#    /tmp/some-prefix /tmp/index-of-somewhere 0 N

if [ "$#" -ne 6 ]; then
    echo "Usage: ksh $0 source-directory target-directory temporary-prefix index-file n0 n1"
    exit 1
fi

set -e

sourcedirectory="$1"
targetdirectory="$2"
temporaryprefix="$3"
indexfile="$4"
for i in `seq -f '%04g' $5 $6`
do
    echo "zip and copy a group $i ..."
    sh "$(dirname $0)/catalog-files.sh" "${indexfile}" $i \
	| (cd "${sourcedirectory}"; zip -q -@ "${temporaryprefix}-$i")
    rsync -ptgo -P -e ssh "${temporaryprefix}-$i.zip" "${targetdirectory}/"
    rm "${temporaryprefix}-$i.zip"
done
