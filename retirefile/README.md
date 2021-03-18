# Retirefile <!-- -*-Coding: utf-8-unix;-*- -->

## retirefile.py - a Gfarm utility

__retirefile.py__ removes files when they are stable.  It realizes a
move-operation working in a pair with __gfpcopy__.  It is indended to
move scientific data files to a globally available Gfarm filesystem.

Files are copied to the destination by gfpcopy, and then the original
files are removed from the source by retirefile.py.  Removal is
performed after a short duration to allow time for geographically
distant replication that a Gfarm filesystem performs.  retirefile.py
takes a list of even number of directories, paired as the sources and
destinations.

### When a move-operation is used

Usually, gfpcopy is sufficient for manually transferring files.
Errors are simply noticed by the user.  And also, the user can wait
for replicas to stabilize.  On the other hand, a move-operation is
preferred when transferring files in a background like a cron job.  It
simplifies detecting errors (a file remains in the source) and
recovering errors (a work is retried on remaining files).

The work of retirefile.py is simple and can be implemented by
combining commands of Gfarm.  However, secure connections are costly,
but it is tedious to avoid frequent reconnections when combining
commands.  retirefile.py straightforwardly works by connecting once.

### Installation

It does not provide installation procedures.  Copy the files manually.

* Copy "gfarm.py" where python3 can find it.  For example, use
  `python3 -m site --user-site` to find a place to personally use it.
  "gfarm.py" is a module to call "libgfarm.so".
* Copy "retirefile.py" anywhere a shell can find it.  Possibly call
  `chmod +x` on it.

### Usage

* It needs to use the library "libgfarm.so" (Gfarm version
  2.7.17).  It should be visible in some ld paths (LD_LIBRARY_PATH) or
  passed by an option `--so path`.  See the help message of
  retirefile.py.
* It accepts a pair of source and destination directories.  The source
  is in the local filesystem, and the destination is in Gfarm.  It
  does _not_ accept URI of Gfarm, but only accepts simple full paths.
* Recommended locale is C.  It scans local files by Python's os.scandir,
  but passes the names to Gfarm in latin-1.

### Working of retirefile.py

* It scans a local directory, and checks the existence of each file in
  Gfarm.  It considers the copied files in Gfarm are stable when each
  file satisfies the conditions: the file has a replica count that
  equals to the setup count or larger, the file aged for a certain
  period, and the file is not modified after creation.  It just checks
  the mtime and ctime of a file, but does not compare sizes or
  contents.  Note that gfpcopy adjusts mtime of the copied files.
* It does not follow symbolic links, because gfpcopy does not.
* Assumptions:
  * The time epoch (of the filesystem) is the same on the local and
  remote sites.  It means retirefile.py will not work on Windows
  clients.

### File list

* [gfarm.py](gfarm.py) is a Python ctypes interface to libgfarm.so.
* [retirefile.py](retirefile.py) is a file remover.  It calls
  libgfarm.so through gfarm.py.
* [move-files.sh](move-files.sh) is a simple script to use gfpcopy and
  retirefile.py to implement a move-operation.
* [move-files-cron-template.sh](move-files-cron-template.sh) is a
  template for a cron script.  It calls gfpcopy and retirefile.py to
  implement a move-operation.  It switches accounts of Gfarm, and thus
  requires to prepare a set of configurations files of Gfarm.  For
  usage, see the [section](#setup-to-use-move-files-ash) in this
  README file.

### Setup to use move-files-cron-template.sh

__move-files-cron-template.sh__ is a (template) script to implement a
move-operation.  This script runs as a certain local user, but
switches Gfarm accounts by specifying a Gfarm configuration file via
an environment variable.  It needs to prepare some configuration
files.  Gfarm can be accessed via GSI or with shared secrets, but this
section only describes using shared secrets.

* Prepare the Gfarm configuration files for each account on the Gfarm
  destination.  Three files are used for each account.
  * Each "gfarm2rc_*account*" file contains the usual setting for an
    account, but the local_user_map and shared_key_file slots are
    replaced appropriately to point to the local files.
  * Each "gf_mapfile_*account*" file contains a line to map the
    local user to a Gfarm account.
  * Each "gf_secret_*account*" file contains a shared-secret which
    is offered by the user on the Gfarm destination.

For using GSI, "gf_secret_*account*" files are not necessary, but an
X509 certificate needs to be specified via an environment variable.

## License terms

Retirefile is distributed under the BSD 2-Clause License.
