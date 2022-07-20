# Logging

Make command outputs logged to syslog, trivially.

## Problem: Random interleaving of outputs

Outputs on the stdout/stderr are randomly interleaved using tee(1).
Moreover, placing wait(1) does not guarantee a completion of tee(1),
and that causes a next shell prompt to appear before the outputs on
the stdout/stderr.

```
#!/bin/bash
exec 1> >(tee >(logger))
exec 2> >(tee >(logger) 1>&2)
"$@"
exec 1>&-
exec 2>&-
wait
```

## tee2.c - a variant of tee(1) for stdout and stderr

tee2(1) duplicates command outputs to fd=1,3 and fd=2,4 that are
passed by the caller.  tee2(1) immediately copies the outputs on the
stdout to fd=1,3 and the stderr to fd=2,4, and it may likely keep the
ordering of the outputs.  The example below passes the stdout outputs
to the logger while the terminal outputs are not disturbed.

```
#!/bin/bash
tee2 "$@" 3> >(logger)
```

tee2(1) makes a report when a subprocess is killed by a signal.

## Setting of syslog (CentOS 6)

wrapper.sh and hpci-gfpcopy.sh may use the facility "ftp.debug".
Generating messages in /var/log/messages is avoided by using the
lowest "debug" level.

Place a file in "/etc/rsyslog.d" and restart the service.

```
# cat /etc/rsyslog.d/hpcigfarm.conf
ftp.debug                /var/log/hpcigfarm
```

```
# /sbin/service rsyslog restart
```
