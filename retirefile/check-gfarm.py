## check-gfarm.py -*-Coding: us-ascii-unix;-*-

"""Check the Gfarm python binding.  It just calls some routines."""

## Usage instruction:
##
## This script modifies the "remote" directory.  It creates files and
## directories named "aho[0-5]"
##
## (1) Check the Gfarm configuration: Check metadb_server_host,
## metadb_server_port, and metadb_server_list are set appropriately.
##
## (2) Prepare a remote test file:
## $ gfreg -p -v LICENSE gfarm:///home/hpNNNNNN/hpciNNNNNN/LICENSE
##
## (3) Run this script (interactively):
## $ python3
## >>> so="/usr/lib/x86_64-linux-gnu/libgfarm.so"
## >>> remote="/home/hpNNNNNN/hpciNNNNNN"
## >>> exec(open("./check-gfarm.py").read())
##
## It is moderately OK, if it ends without an exception.
##
## (4) Check the returned values:
## >>> ri
## >>> nn

import os
import gfarm

gfarm.load(so)
gfarm.initialize()
gfarm.enable_stat_cache()

##
## Take info on "LICENSE".
##

f0 = str(os.path.join(remote, "LICENSE"))
bpath = os.path.join(remote, "LICENSE").encode(coding)

flags = (gfarm.GFS_REPLICA_INFO_INCLUDING_DEAD_HOST
         | gfarm.GFS_REPLICA_INFO_INCLUDING_DEAD_COPY)

(ri, cc) = gfarm._gfs_replica_info_by_name(bpath, flags)
assert cc == 0
(st, cc) = gfarm.stat(f0)
assert cc == 0
(nc, cc) = gfarm.get_ncopy(f0)
assert cc == 0

##
## Copy, rename some files.
##

p0 = os.path.join(remote, "aho0")
p1 = os.path.join(remote, "aho1")
p2 = os.path.join(remote, "aho2")
p3 = os.path.join(remote, "aho3")
p4 = os.path.join(remote, "aho4")
p5 = os.path.join(remote, "aho5")

cc = gfarm.link(f0, p0)
assert cc == 0
cc = gfarm.link(f0, p1)
assert cc == 0
cc = gfarm.link(f0, p2)
assert cc == 0
cc = gfarm.mkdir(p3, 0o0755)
assert cc == 0
cc = gfarm.rename(p2, p4)
assert cc == 0
cc = gfarm.rename(p3, p5)
assert cc == 0

##
## List files.
##

nn = [n for (n,i,t) in gfarm.listdir(remote)]

##
## Remove some files.
##

cc = gfarm.unlink(p0)
assert cc == 0
cc = gfarm.unlink(p1)
assert cc == 0
## Expect an error for the next.
cc = gfarm.unlink(p2)
assert cc == 2
cc = gfarm.unlink(p4)
assert cc == 0
cc = gfarm.rmdir(p5)
assert cc == 0

gfarm.terminate()
