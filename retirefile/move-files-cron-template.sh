#!/bin/ksh -x

## A script template to run by cron.

## It runs as a fixed user (for example "somelocal"), and switches
## accounts of Gfarm using map-files.  Thus, it requires source
## directories are readable/writable by that user.  It needs to
## prepare files "gfarm2rc_hpciNNNNNN", "gf_mapfile_hpciNNNNNN", and
## "gf_secret_hpciNNNNNN" for each account in Gfarm.

## Contents of "gfarm2rc_hpciNNNNNN":
## |auth disable gsi *
## |auth disable gsi_auth *
## |auth enable sharedsecret *
## |local_user_map gf_mapfile_hpciNNNNNN
## |shared_key_file gf_secret_hpciNNNNNN

## Contents of "gf_mapfile_hpciNNNNNN":
## |hpciNNNNNN somelocal

docopy() {
    id=${1}
    conf=gfarm2rc_${1}
    src=${2}
    dst=${3}
    dir=`basename ${2}`
    date
    echo ${conf}
    export GFARM_CONFIG_FILE=${conf}
    gfpcopy -P ${src} gfarm://${dst}
    retirefile.py --verbose --summary ${src} ${dst}/${dir}
}

filter() {
    tee -a log.txt | grep -v '^\[OK\]'
}

PATH=$HOME/bin:$PATH
docopy hpci000000 some/gomi0 /home/hpNNNNNN/hpci000000 2>&1 | filter
docopy hpci111111 some/gomi1 /home/hpNNNNNN/hpci111111 2>&1 | filter
docopy hpci222222 some/gomi2 /home/hpNNNNNN/hpci222222 2>&1 | filter
