## Makefile

## Enumerations are inaccessible in binaries and so in ctypes.
## Dumping their values needs to be done outside of ctypes.  It uses
## gdb, and it needs a debugging-enabled binary.

GFBIN=~/opt/gfarm/bin/gfwhere

enums::
	gdb --batch --command=dump-errcode.gdb --args $(GFBIN) > xxx0
	sed -e 's/^[^=]*= //' < xxx0 > xxx1
	awk '/^[A-Z].*/{printf "%s = ", $$0} /^[0-9].*/{print}' < xxx1 > xxx2
	mv xxx2 gfarm-errcode.txt
