#!/bin/bash

## A wrapper for gfpcopy with logging to syslog.  See wrapper.sh for
## general usage.

log="ftp.debug"
echo HPCI-ACCESS "$0" "$*" | /bin/logger -p ${log}
exec ./tee2 gfpcopy -P "$@" \
     3> >(trap '' INT QUIT; exec /bin/logger -p ${log})
