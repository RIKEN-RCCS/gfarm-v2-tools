#!/bin/ksh

## move-files.sh -- A simple script to use gfpcopy and retirefile.py.
## The destination directory must exit, because it creates a mutexing
## file (actually a directory) in the destination.  It outputs
## messages to a logging file and the logger.  The environment variable
## "GFLIB" is used to specify the place of "libgfarm.so".

log="ftp.debug"

##
## Check the arguments and the environment setting.
##

if [ "$#" -ne 2 ]; then
    echo "Usage: ksh move-files.sh local remote"
    exit 1
fi
if [ -z "${GFLIB}" ]; then
    lib=""
else
    lib="--so ${GFLIB}"
fi

src=$1
dst=$2
dir=`basename $1`
mutex=gfarm://${dst}/${dir}/_move_files_in_progress_

##
## Take a mutex on the remote directory.
##

if ! gfmkdir ${mutex} > /dev/null 2>&1; then
    echo "Mutexing failed.  Some other move-files.sh running."
    exit 1
fi
trap "gfrmdir ${mutex}; trap - EXIT; exit" INT TERM EXIT

docopy() {
    date +"%Y-%m-%dT%H:%M:%S%z"
    gfpcopy -P ${src} gfarm://${dst}
    retirefile.py ${lib} --verbose --summary ${src} ${dst}/${dir}
}

##
## Do moving.
##

docopy 2>&1 | tee >(logger -p ${log})
