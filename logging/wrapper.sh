#!/bin/bash

## A command wrapper with logging to syslog.  This does not work with
## KSH.

log="ftp.debug"
echo HPCI-ACCESS "$0" "$*" | /bin/logger -p ${log}
exec ./tee2 "$@" \
     3> >(trap '' INT QUIT; exec /bin/logger -p ${log})
