#!/usr/bin/env python3
## retirefile.py -*-Coding: us-ascii-unix;-*-
## Copyright (C) 2020-2021 RIKEN

"""retirefile.py removes files when they are stable in Gfarm.  It,
working with gfpcopy as a pair, fulfills the move-operation.  It
removes the source files after copying them to a remote file system.
It takes source and destination directories, where the source is in a
local filesystem and the destination in Gfarm.  It enumerates files in
the source and removes them if their replicas have been created in the
destination.  It does not follow symbolic links, because gfpcopy
copies symbolic links as they are (symbolic links).  Note that Gfarm
spontaneously creates extraneous replicas and it will confuse judging
the replica count, so that replicas may not yet be created in distant
sites."""

## Minimal Usage:
## retirefile.py --so ~/opt/gfarm/lib/libgfarm.so --verbose \
##   srcdir /home/hpNNNNNN/hpciNNNNNN/dstdir
## Or:
## exec(open("./retirefile.py").read())

## This assumes Python3.5 and later.  (for Python3.5) This avoids
## "with" on the value returned by os.scandir().  The uses of
## os.scandir() here consume all the entries, and it works fine with
## 3.6 and later.

import types
import os
import sys
import time
import argparse
import datetime
import traceback
import gfarm

dryrun = False

"""An option to skip unlinking local files."""

ignore_links = False

"""An option to ignore symbolic links.  It corresponds to the -k
option of gfpcopy."""

be_verbose = False

"""An option to message when unlinking local files."""

print_summary = False

"""An option to print operation summary."""

time_to_stabilize = (30.0 * 60.0)

"""A time in seconds to allow removal of local files.  It needs to
wait for a while, because the time is unspecified when back-ups of
metadata are taken."""

time_drift = 5.0

"""A time in seconds of a tolerance to compare mtimes whether a
local/remote file is not considered as modified.  gfpcopy sets the
mtime, and a near-zero value is acceptable.  But, the conversion from
a tv value to a float may use different routines for local and remote
files."""

class GfarmException(Exception):
    def __init__(self, cc_):
        self.cc = cc_

def verbose_message(s):
    if (be_verbose):
        print(s, file=sys.stdout)
    else:
        pass
    return None

def warning_message(s):
    print(s, file=sys.stdout)
    return None

## Operation summary information.

summary_counters = types.SimpleNamespace()
summary_counters.retire_begin = None
summary_counters.retire_end = None
summary_counters.removed = 0
summary_counters.skipped = 0
summary_counters.unremovable = 0
summary_counters.missing = 0
summary_counters.gfarm_error = 0
summary_counters.state_unobtainable = 0
summary_counters.directories = None

def dump_summary():
    print(("retire_time: " + str(summary_counters.retire_begin)
           + " -- " + str(summary_counters.retire_end)),
          file=sys.stdout)
    if (summary_counters.directories != None):
        for (s, d) in summary_counters.directories:
            print(("directory_pair: " + str(s) + " to " + str(d)),
                  file=sys.stdout)
    print(("removed_files: " + str(summary_counters.removed)),
          file=sys.stdout)
    print(("skipped_files: " + str(summary_counters.skipped)),
          file=sys.stdout)
    print(("unremovable_files: " + str(summary_counters.unremovable)),
          file=sys.stdout)
    print(("missing_files_in_remote: " + str(summary_counters.missing)),
          file=sys.stdout)
    print(("general_gfarm_errors: " + str(summary_counters.gfarm_error)),
          file=sys.stdout)
    print(("unknown_state_files: " + str(summary_counters.state_unobtainable)),
          file=sys.stdout)
    pass

## (stat.st_mtime is float).

def check_condition(path, lst, nc, rst, message=True):
    """Checks the condition of removing a source file.  Note that gfpcopy
    sets mtime.  It uses ctime for the oldness test."""
    now = time.time()
    mtimel = lst.st_mtime
    mtimer = gfarm.timespec_to_float(rst.st_mtimespec)
    ctimer = gfarm.timespec_to_float(rst.st_ctimespec)
    replicas_created = (rst.st_ncopy >= nc)
    sufficiently_old = ((ctimer + time_to_stabilize) < now)
    mtime_unmodified = (abs(mtimer - mtimel) <= time_drift)
    if (message):
        verbose_message(
            "[OK] "
            + str(path)
            + " size=" + str(rst.st_size)
            + " ncopy=" + str(rst.st_ncopy) + "/" + str(nc)
            + " ctime=" + time.strftime('%H:%M:%S', time.gmtime(ctimer))
            + " mtime=" + time.strftime('%H:%M:%S', time.gmtime(mtimer))
            + " replicas_created=" + str(replicas_created)
            + ", " + "sufficiently_old=" + str(sufficiently_old)
            + ", " + "mtime_unmodified=" + str(mtime_unmodified))
    else:
        pass
    return ((not dryrun)
            and (replicas_created and sufficiently_old and mtime_unmodified))

def retire(src, dst):
    """Removes files in the source if they have replicas.  It takes a pair
    of source and destination directories.  It treats regular files
    and symbol links in the same way (when os.DirEntry.is_file).  Note
    os.scandir allows to remove found files safely."""
    verbose_message("[OK] " + "Retiring: " + src + " to " + dst)
    some_missing = False
    ##with os.scandir(src) as entries:
    entries = os.scandir(src)
    for di in entries:
            if (di.is_symlink() and ignore_links):
                pass
            elif (di.is_file(follow_symlinks=False) or di.is_symlink()):
                name = di.name
                path = os.path.join(dst, name)
                lst = di.stat()
                try:
                    (rst, cc) = gfarm.stat(path)
                    if (cc == gfarm.GFARM_ERR_NO_SUCH_FILE_OR_DIRECTORY):
                        warning_message(
                            "Skipping a local file: " + str(name)
                            + ": " + gfarm.error_string(cc))
                        some_missing = (some_missing | True)
                        summary_counters.missing += 1
                    elif (cc != gfarm.GFARM_ERR_NO_ERROR):
                        summary_counters.gfarm_error += 1
                        raise GfarmException(cc)
                    else:
                        ##raise_if_error(cc)
                        (nc, cc) = gfarm.get_ncopy(path)
                        if (cc == gfarm.GFARM_ERR_NO_SUCH_OBJECT):
                            warning_message(
                                "No replica setting found: " + str(name)
                                + ": " + gfarm.error_string(cc))
                            summary_counters.state_unobtainable += 1
                        elif (cc != gfarm.GFARM_ERR_NO_ERROR):
                            summary_counters.gfarm_error += 1
                            raise GfarmException(cc)
                        elif (check_condition(path, lst, nc, rst)):
                            try:
                                os.unlink(di.path)
                                verbose_message("[OK] Unlink: " + str(di.path)
                                                + " size=" + str(rst.st_size))
                                summary_counters.removed += 1
                            except Exception as x:
                                warning_message("Unlink failed: "
                                                + str(di.path))
                                summary_counters.unremovable += 1
                        else:
                            summary_counters.skipped += 1
                            pass
                except GfarmException:
                    pass
            else:
                pass
    return some_missing

def retire_pair(src0, dst0):
    some_missing = False
    cc = retire(src0, dst0)
    some_missing = (some_missing or cc)
    ##with os.scandir(src0) as entries:
    entries = os.scandir(src0)
    names = [di.name for di in entries
                 if (di.is_dir(follow_symlinks=False))]
    for n in names:
        src1 = os.path.join(src0, n)
        dst1 = os.path.join(dst0, n)
        cc = retire_pair(src1, dst1)
        some_missing = (some_missing or cc)
    return some_missing

def retire_list(pairs):
    gfarm.initialize()
    gfarm.enable_stat_cache()
    some_missing = False
    for (s, d) in pairs:
        cc = retire_pair(s, d)
        some_missing = (some_missing or cc)
    gfarm.terminate()
    if (some_missing):
        warning_message("Some missing files in remote")
    else:
        pass
    return some_missing

if __name__ == "__main__":
    p = argparse.ArgumentParser(description='''
retirefile.py removes local files when they are stable remotely after
copying them via gfpcopy.  Typical usage is: retirefile.py --so
~/opt/libgfarm.so --verbose srcdir /home/hpNNNNNN/hpciNNNNNN/dstdir.
''')
    p.add_argument('directories', metavar='directory-pair',
                   type=str, nargs='+',
                   help='source/destination directory pair')
    p.add_argument('--so', dest='so', type=str, action='store',
                   default="libgfarm.so",
                   help='use the so file instead of libgfarm.so')
    p.add_argument('--verbose', dest='be_verbose', action='store_const',
                   const=True, default=False,
                   help='verbosity')
    p.add_argument('--summary', dest='print_summary', action='store_const',
                   const=True, default=False,
                   help='print summary')
    p.add_argument('--dryrun', dest='dryrun', action='store_const',
                   const=True, default=False,
                   help='dryrun')
    p.add_argument('--ignore-links', dest='ignore_links', action='store_const',
                   const=True, default=False,
                   help='do not remove symbolic links')
    args = p.parse_args()
    directories = args.directories
    so = args.so
    be_verbose = args.be_verbose
    print_summary = args.print_summary
    dryrun = args.dryrun
    ignore_links = args.ignore_links
    if (len(directories) == 0):
        p.print_help()
        sys.exit(1)
    elif ((len(directories) % 2) != 0):
        print("Directories are not in pairs.", file=sys.stdout)
        sys.exit(1)
    else:
        some_missing = False
        some_expection = False
        summary_counters.retire_begin = datetime.datetime.now()
        try:
            gfarm.load(so)
            pairs = list(zip(directories[0::2], directories[1::2]))
            summary_counters.directories = pairs
            some_missing = retire_list(pairs)
        except Exception as x:
            print(traceback.format_exc())
            some_expection = True
            ##print(str(ex))
            ##sys.exit(1)
        summary_counters.retire_end = datetime.datetime.now()
        if (print_summary):
            dump_summary()
        if ((not some_missing) and (not some_expection)):
            sys.exit(0)
        else:
            sys.exit(1)
