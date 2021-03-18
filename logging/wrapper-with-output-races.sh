#!/bin/bash -x

## A command wrapper with logging to syslog.

log="user.err"
echo HPCI-ACCESS "$*" | /bin/logger -p ${log}
exec 1> >(trap '' INT QUIT; exec /bin/tee >(exec /bin/logger -p ${log}))
exec 2> >(trap '' INT QUIT; exec /bin/tee >(exec /bin/logger -p ${log}) 1>&2)
"$@"
exec 1>&-
exec 2>&-
wait
