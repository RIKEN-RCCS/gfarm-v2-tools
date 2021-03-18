## gfarm.py -*-Coding: us-ascii-unix;-*-
## Copyright (C) 2020-2021 RIKEN

"""A Python3 binding for Gfarm's libgfarm.so (version 2.7.17).  It
supports only a very small subset of the library.  The constants and
structures hardcoded are specific to the version.  They should be
updated for other versions.  This library is used in the sequence of
load, initialize, call some operations, and then terminate.  It passes
strings such as path names via latin-1 to libgfarm.  When latin-1 is
not appropriate, modify the variable "name_coding" appropriately.  The
low level routines return a pair of a value and an error code.  On
errors, the value is None.  They do not report serious errors but
raise assertion errors."""

## This library treats the Gfarm's nanosecond timestamp as an unsigned
## field, that is different from the original definition.  It is to
## check the range of the nanosecond timestamp.  See the "tv_nsec"
## field.

## This library does not follow the coding of file names in
## os.fsdecode() and os.fsencode().

import ctypes
import sys
import pathlib
import time
##import warnings
##import inspect
##import traceback

__version__ = "2021-02-11"
expected_gfarm_version = b"2.7.17"

version = None
so_name = None
gfso = None

##
## File name coding.
##

## It is used when passing byte strings to python and vice versa.
## Usually "utf-8" or "latin-1".  utf-8 cannot be used with arbitrary
## byte strings, but latin-1 can be used with 8bit strings.

name_coding = "latin-1"
##name_coding = "utf-8"

_c_void_p = ctypes.c_void_p
_c_ubyte = ctypes.c_ubyte
_c_bool = ctypes.c_bool
_c_char = ctypes.c_char
_c_int = ctypes.c_int
_c_ushort = ctypes.c_ushort
_c_uint = ctypes.c_uint
_c_long = ctypes.c_long
_c_uint8 = ctypes.c_uint8
_c_uint32 = ctypes.c_uint32
_c_uint64 = ctypes.c_uint64
_c_double = ctypes.c_double
_c_size_t = ctypes.c_size_t

_c_string = ctypes.c_char_p
_c_uchar = _c_ubyte
_c_int32 = _c_int
_c_int64 = _c_long

_c_pointer = ctypes.POINTER(ctypes.c_char)
_c_string_p = ctypes.POINTER(_c_string)
_c_size_t_p = ctypes.POINTER(_c_size_t)
_c_pointer_p = ctypes.POINTER(_c_pointer)
##_c_void_p_p = ctypes.POINTER(_c_void_p)
## Null return values for ctypes.restype:
##_c_null_pointer_value = _c_pointer()

##
## Error code of libgfarm.
##

GFARM_ERR_NO_ERROR = 0
GFARM_ERR_OPERATION_NOT_PERMITTED = 1
GFARM_ERR_NO_SUCH_FILE_OR_DIRECTORY = 2
GFARM_ERR_NO_SUCH_PROCESS = 3
GFARM_ERR_INTERRUPTED_SYSTEM_CALL = 4
GFARM_ERR_INPUT_OUTPUT = 5
GFARM_ERR_DEVICE_NOT_CONFIGURED = 6
GFARM_ERR_ARGUMENT_LIST_TOO_LONG = 7
GFARM_ERR_EXEC_FORMAT = 8
GFARM_ERR_BAD_FILE_DESCRIPTOR = 9
GFARM_ERR_NO_CHILD_PROCESS = 10
GFARM_ERR_RESOURCE_TEMPORARILY_UNAVAILABLE = 11
GFARM_ERR_NO_MEMORY = 12
GFARM_ERR_PERMISSION_DENIED = 13
GFARM_ERR_BAD_ADDRESS = 14
GFARM_ERR_BLOCK_DEVICE_REQUIRED = 15
GFARM_ERR_DEVICE_BUSY = 16
GFARM_ERR_ALREADY_EXISTS = 17
GFARM_ERR_CROSS_DEVICE_LINK = 18
GFARM_ERR_OPERATION_NOT_SUPPORTED_BY_DEVICE = 19
GFARM_ERR_NOT_A_DIRECTORY = 20
GFARM_ERR_IS_A_DIRECTORY = 21
GFARM_ERR_INVALID_ARGUMENT = 22
GFARM_ERR_TOO_MANY_OPEN_FILES_IN_SYSTEM = 23
GFARM_ERR_TOO_MANY_OPEN_FILES = 24
GFARM_ERR_INAPPROPRIATE_IOCTL_FOR_DEVICE = 25
GFARM_ERR_TEXT_FILE_BUSY = 26
GFARM_ERR_FILE_TOO_LARGE = 27
GFARM_ERR_NO_SPACE = 28
GFARM_ERR_ILLEGAL_SEEK = 29
GFARM_ERR_READ_ONLY_FILE_SYSTEM = 30
GFARM_ERR_TOO_MANY_LINKS = 31
GFARM_ERR_BROKEN_PIPE = 32
GFARM_ERR_NUMERICAL_ARGUMENT_OUT_OF_DOMAIN = 33
GFARM_ERR_RESULT_OUT_OF_RANGE = 34
GFARM_ERR_ILLEGAL_BYTE_SEQUENCE = 35
GFARM_ERR_RESOURCE_DEADLOCK_AVOIDED = 36
GFARM_ERR_FILE_NAME_TOO_LONG = 37
GFARM_ERR_DIRECTORY_NOT_EMPTY = 38
GFARM_ERR_NO_LOCKS_AVAILABLE = 39
GFARM_ERR_FUNCTION_NOT_IMPLEMENTED = 40
GFARM_ERR_OPERATION_NOW_IN_PROGRESS = 41
GFARM_ERR_OPERATION_ALREADY_IN_PROGRESS = 42
GFARM_ERR_SOCKET_OPERATION_ON_NON_SOCKET = 43
GFARM_ERR_DESTINATION_ADDRESS_REQUIRED = 44
GFARM_ERR_MESSAGE_TOO_LONG = 45
GFARM_ERR_PROTOCOL_WRONG_TYPE_FOR_SOCKET = 46
GFARM_ERR_PROTOCOL_NOT_AVAILABLE = 47
GFARM_ERR_PROTOCOL_NOT_SUPPORTED = 48
GFARM_ERR_OPERATION_NOT_SUPPORTED = 49
GFARM_ERR_ADDRESS_FAMILY_NOT_SUPPORTED_BY_PROTOCOL_FAMILY = 50
GFARM_ERR_ADDRESS_ALREADY_IN_USE = 51
GFARM_ERR_CANNOT_ASSIGN_REQUESTED_ADDRESS = 52
GFARM_ERR_NETWORK_IS_DOWN = 53
GFARM_ERR_NETWORK_IS_UNREACHABLE = 54
GFARM_ERR_CONNECTION_ABORTED = 55
GFARM_ERR_CONNECTION_RESET_BY_PEER = 56
GFARM_ERR_NO_BUFFER_SPACE_AVAILABLE = 57
GFARM_ERR_SOCKET_IS_ALREADY_CONNECTED = 58
GFARM_ERR_SOCKET_IS_NOT_CONNECTED = 59
GFARM_ERR_OPERATION_TIMED_OUT = 60
GFARM_ERR_CONNECTION_REFUSED = 61
GFARM_ERR_NO_ROUTE_TO_HOST = 62
GFARM_ERR_TOO_MANY_LEVELS_OF_SYMBOLIC_LINK = 63
GFARM_ERR_DISK_QUOTA_EXCEEDED = 64
GFARM_ERR_STALE_FILE_HANDLE = 65
GFARM_ERR_IDENTIFIER_REMOVED = 66
GFARM_ERR_NO_MESSAGE_OF_DESIRED_TYPE = 67
GFARM_ERR_VALUE_TOO_LARGE_TO_BE_STORED_IN_DATA_TYPE = 68
GFARM_ERR_AUTHENTICATION = 69
GFARM_ERR_EXPIRED = 70
GFARM_ERR_PROTOCOL = 71
GFARM_ERR_UNKNOWN_HOST = 72
GFARM_ERR_CANNOT_RESOLVE_AN_IP_ADDRESS_INTO_A_HOSTNAME = 73
GFARM_ERR_NO_SUCH_OBJECT = 74
GFARM_ERR_CANT_OPEN = 75
GFARM_ERR_UNEXPECTED_EOF = 76
GFARM_ERR_GFARM_URL_PREFIX_IS_MISSING = 77
GFARM_ERR_TOO_MANY_JOBS = 78
GFARM_ERR_FILE_MIGRATED = 79
GFARM_ERR_NOT_A_SYMBOLIC_LINK = 80
GFARM_ERR_IS_A_SYMBOLIC_LINK = 81
GFARM_ERR_UNKNOWN = 82
GFARM_ERR_INVALID_FILE_REPLICA = 83
GFARM_ERR_NO_SUCH_USER = 84
GFARM_ERR_CANNOT_REMOVE_LAST_REPLICA = 85
GFARM_ERR_NO_SUCH_GROUP = 86
GFARM_ERR_GFARM_URL_USER_IS_MISSING = 87
GFARM_ERR_GFARM_URL_HOST_IS_MISSING = 88
GFARM_ERR_GFARM_URL_PORT_IS_MISSING = 89
GFARM_ERR_GFARM_URL_PORT_IS_INVALID = 90
GFARM_ERR_FILE_BUSY = 91
GFARM_ERR_NOT_A_REGULAR_FILE = 92
GFARM_ERR_IS_A_REGULAR_FILE = 93
GFARM_ERR_PATH_IS_ROOT = 94
GFARM_ERR_INTERNAL_ERROR = 95
GFARM_ERR_DB_ACCESS_SHOULD_BE_RETRIED = 96
GFARM_ERR_TOO_MANY_HOSTS = 97
GFARM_ERR_GFMD_FAILED_OVER = 98
GFARM_ERR_BAD_INODE_NUMBER = 99
GFARM_ERR_BAD_COOKIE = 100
GFARM_ERR_INSUFFICIENT_NUMBER_OF_FILE_REPLICAS = 101
GFARM_ERR_CHECKSUM_MISMATCH = 102
GFARM_ERR_CONFLICT_DETECTED = 103
GFARM_ERR_INVALID_CREDENTIAL = 104
GFARM_ERR_NO_FILESYSTEM_NODE = 105
GFARM_ERR_DIRECTORY_QUOTA_EXISTS = 106
GFARM_ERR_NUMBER = 107

##
## File permissions.  The lowest 9 bits are as posix.
##

GFARM_S_ALLPERM = 0o0007777
GFARM_S_ISUID = 0o0004000
GFARM_S_ISGID = 0o0002000
GFARM_S_ISTXT = 0o0001000
GFARM_S_IFMT = 0o0170000
GFARM_S_IFDIR = 0o0040000
GFARM_S_IFREG = 0o0100000
GFARM_S_IFLNK = 0o0120000

def GFARM_S_ISDIR(m):
    return ((m & GFARM_S_IFMT) == GFARM_S_IFDIR)

def GFARM_S_ISREG(m):
    return ((m & GFARM_S_IFMT) == GFARM_S_IFREG)

def GFARM_S_ISLNK(m):
    return ((m & GFARM_S_IFMT) == GFARM_S_IFLNK)

def GFARM_S_IS_PROGRAM(m):
    retrun (GFARM_S_ISREG(m) and (m & 0o0111) != 0)

def GFARM_S_IS_SUGID_PROGRAM(m):
    return ((m & (GFARM_S_ISUID|GFARM_S_ISGID)) != 0
            and GFARM_S_IS_PROGRAM(m))

##
## Options to gfs_replica_info_by_name.
##

GFS_REPLICA_INFO_INCLUDING_DEAD_HOST = 1
GFS_REPLICA_INFO_INCLUDING_INCOMPLETE_COPY = 2
GFS_REPLICA_INFO_INCLUDING_DEAD_COPY = 4

##
## State checking.
##

class UninitializedError(Exception):
    pass

def assert_active_context():
    """Checks if libgfarm is initialized to avoid SEGV, because most
    library routines fail when not called between initialize and
    terminate."""
    ctxp = _c_void_p.in_dll(gfso, "gfarm_ctxp")
    if (ctxp.value == None):
        raise UninitializedError()

def abst_path(path):
    """Returns a PurePath for a string representation, after checking a
    path string is from the root."""
    p = pathlib.PurePath(path)
    assert p.is_absolute()
    return p

##
## Loading libgfarm.
##

def load(so = "libgfarm.so"):
    """Loads a libgfram.so."""
    global so_name, gfso, version

    so_name = so
    gfso = ctypes.CDLL(so_name)

    gfso.gfarm_version.argtypes = []
    gfso.gfarm_version.restype = _c_string

    version = gfso.gfarm_version()
    if (expected_gfarm_version != version):
        print(("Warning libgfarm version mismatch:"
               + " version=" + str(version)
               + " expected=" + str(expected_gfarm_version)),
              file=sys.stderr)
    else:
        pass

    gfso.free.argtypes = [_c_void_p]
    gfso.free.restype = None

    gfso.gfarm_initialize.argtypes = [_c_pointer, _c_pointer]
    gfso.gfarm_initialize.restype = _c_int

    gfso.gfarm_terminate.argtypes = []
    gfso.gfarm_terminate.restype = _c_int

    gfso.gfarm_error_string.argtypes = [_c_int]
    gfso.gfarm_error_string.restype = _c_string

    gfso.gfs_replica_info_by_name.argtypes = [_c_string, _c_int, _c_void_p]
    gfso.gfs_replica_info_by_name.restype = _c_int

    gfso.gfs_replica_info_number.argtypes = [_c_void_p]
    gfso.gfs_replica_info_number.restype = _c_int
    gfso.gfs_replica_info_nth_host.argtypes = [_c_void_p, _c_int]
    gfso.gfs_replica_info_nth_host.restype = _c_string
    gfso.gfs_replica_info_nth_gen.argtypes = [_c_void_p, _c_int]
    gfso.gfs_replica_info_nth_gen.restype = _c_uint64
    gfso.gfs_replica_info_nth_is_incomplete.argtypes = [_c_void_p, _c_int]
    gfso.gfs_replica_info_nth_is_incomplete.restype = _c_int
    gfso.gfs_replica_info_nth_is_dead_host.argtypes = [_c_void_p, _c_int]
    gfso.gfs_replica_info_nth_is_dead_host.restype = _c_int
    gfso.gfs_replica_info_nth_is_dead_copy.argtypes = [_c_void_p, _c_int]
    gfso.gfs_replica_info_nth_is_dead_copy.restype = _c_int

    gfso.gfarm_realpath_by_gfarm2fs.argtypes = [_c_string, _c_string_p]
    gfso.gfarm_realpath_by_gfarm2fs.restype = _c_int

    gfso.gfs_stat_cached.argtypes = [_c_string, _c_gfs_stat_p]
    gfso.gfs_stat_cached.restype = _c_int
    gfso.gfs_lstat_cached.argtypes = [_c_string, _c_gfs_stat_p]
    gfso.gfs_lstat_cached.restype = _c_int

    gfso.gfs_getxattr_cached.argtypes = [_c_string, _c_string, _c_pointer,
                                         _c_size_t_p]
    gfso.gfs_getxattr_cached.restype = _c_int
    gfso.gfs_lgetxattr_cached.argtypes = [_c_string, _c_string, _c_pointer,
                                          _c_size_t_p]
    gfso.gfs_lgetxattr_cached.restype = _c_int

    gfso.gfs_opendir_caching.argtypes = [_c_string, _c_pointer_p]
    gfso.gfs_opendir_caching.restype = _c_int
    gfso.gfs_readdir.argtypes = [_c_pointer, _c_gfs_dirent_p_p]
    gfso.gfs_readdir.restype = _c_int
    gfso.gfs_closedir.argtypes = [_c_pointer]
    gfso.gfs_closedir.restype = _c_int

    gfso.gfs_stat_cache_enable.argtypes = [_c_int]
    gfso.gfs_stat_cache_enable.restype = None
    gfso.gfarm_xattr_caching_pattern_add.argtypes = [_c_string]
    gfso.gfarm_xattr_caching_pattern_add.restype = _c_int

    gfso.gfs_link.argtypes = [_c_string, _c_string]
    gfso.gfs_link.restype1 = _c_int
    gfso.gfs_unlink.argtypes = [_c_string]
    gfso.gfs_unlink.restype1 = _c_int

    gfso.gfs_mkdir.argtypes = [_c_string, _c_gfarm_mode_t]
    gfso.gfs_mkdir.restype1 = _c_int
    gfso.gfs_rmdir.argtypes = [_c_string]
    gfso.gfs_rmdir.restype1 = _c_int

    gfso.gfs_rename.argtypes = [_c_string, _c_string]
    gfso.gfs_rename.restype1 = _c_int
    return None

##
## Initialization/termination.
##

def initialize():
    """(See Gfarm)."""
    cc = gfso.gfarm_initialize(None, None)
    assert cc == GFARM_ERR_NO_ERROR
    return cc

def terminate():
    """(See Gfarm)."""
    cc = gfso.gfarm_terminate()
    assert cc == GFARM_ERR_NO_ERROR
    return cc

def error_string(cc):
    """Returns a string for an error code."""
    return (gfso.gfarm_error_string(cc)).decode("latin-1")

##
## Replica information.
##

## gfs_replica_info is an opaque structure defined in
## "gfs_replica_info.c".  They have accessors.

##struct gfs_replica_info {
##      gfarm_int32_t n;
##      char **hosts;
##      gfarm_uint64_t *gens;
##      gfarm_int32_t *flags;
##};

def _gfs_replica_info_by_name(path, flags):
    """Returns information of a replica of a path as a tuple
    (host,generation,flags).  The path be a byte string, flags be an
    ioring of GFS_REPLICA_INFO_XXX."""
    assert_active_context()
    r = _c_pointer()
    cc = gfso.gfs_replica_info_by_name(path, flags, ctypes.byref(r))
    assert cc == GFARM_ERR_NO_ERROR
    if (cc != GFARM_ERR_NO_ERROR):
        return (None, cc)
    else:
        try:
            n = gfso.gfs_replica_info_number(r)
            host_generation_flags = [
                (gfso.gfs_replica_info_nth_host(r, i),
                 gfso.gfs_replica_info_nth_gen(r, i),
                 [gfso.gfs_replica_info_nth_is_incomplete(r, i) != 0,
                  gfso.gfs_replica_info_nth_is_dead_host(r, i) != 0,
                  gfso.gfs_replica_info_nth_is_dead_copy(r, i) != 0])
                for i in range(n)]
        finally:
            gfso.gfs_replica_info_free(r)
    return (host_generation_flags, cc)

def _gfarm_realpath_by_gfarm2fs(path):
    """???."""
    assert_active_context()
    pathx = _c_string()
    cc = gfso.gfarm_realpath_by_gfarm2fs(path, ctypes.byref(pathx))
    if (cc == GFARM_ERR_NO_ERROR):
        (pathx, cc)
    else:
        (path, cc)

##
## File stat operations.
##

## File stat and opendir operations have cached/uncached variants.
## Actual caching can be turned on/off by gfs_stat_cache_enable.

##typedef gfarm_int64_t gfarm_time_t;
##struct gfarm_timespec {
##        gfarm_time_t tv_sec;
##        gfarm_int32_t tv_nsec;
##};

_c_gfarm_time_t = _c_int64
_c_gfarm_nsec_t = _c_uint32

class _c_gfarm_timespec(ctypes.Structure):
    """struct gfarm_timespec."""
    _fields_ = [
        ("tv_sec", _c_gfarm_time_t),
        ("tv_nsec", _c_gfarm_nsec_t)]

    def __init__(self):
        return

    def __str__(self):
        sec = getattr(self, "tv_sec")
        return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(sec))

def _check_nsec(v):
    assert v < 1000000000, "bad nsec range"
    return v

def timespec_to_float(tv):
    return (getattr(tv, "tv_sec") + _check_nsec(getattr(tv, "tv_nsec")) * 1e-9)

##typedef gfarm_int64_t gfarm_off_t;
##typedef gfarm_uint64_t gfarm_ino_t;
##typedef gfarm_uint32_t gfarm_mode_t;
##struct gfs_stat {
##        gfarm_ino_t st_ino;
##        gfarm_uint64_t st_gen;
##        gfarm_mode_t st_mode;
##        gfarm_uint64_t st_nlink;
##        char *st_user;
##        char *st_group;
##        gfarm_off_t st_size;
##        gfarm_uint64_t st_ncopy;
##        struct gfarm_timespec st_atimespec;
##        struct gfarm_timespec st_mtimespec;
##        struct gfarm_timespec st_ctimespec;
##};

_c_gfarm_off_t = _c_int64
_c_gfarm_ino_t = _c_uint64
_c_gfarm_mode_t = _c_uint32

##os.stat_result(st_mode=%d, st_ino=%d, st_dev=%d, st_nlink=%d,
##st_uid=%d, st_gid=%d, st_size=%d, st_atime=%d, st_mtime=%d,
##st_ctime=%d)

class _c_gfs_stat(ctypes.Structure):
    """struct gfs_stat."""
    _fields_ = [
        ("st_ino", _c_gfarm_ino_t),
        ("st_gen", _c_uint64),
        ("st_mode", _c_gfarm_mode_t),
        ("st_nlink", _c_uint64),
        ("st_user", _c_string),
        ("st_group", _c_string),
        ("st_size", _c_gfarm_off_t),
        ("st_ncopy", _c_uint64),
        ("st_atimespec", _c_gfarm_timespec),
        ("st_mtimespec", _c_gfarm_timespec),
        ("st_ctimespec", _c_gfarm_timespec)]

    def __init__(self):
        return

_c_gfs_stat_p = ctypes.POINTER(_c_gfs_stat)

## gfmd may return on "GFM_PROTO_FSTAT" {GFARM_ERR_NO_ERROR,
## GFARM_ERR_OPERATION_NOT_PERMITTED, GFARM_ERR_BAD_FILE_DESCRIPTOR,
## GFARM_ERR_NO_MEMORY}.

def _gfs_stat_cached(path, aboutlink = False):
    """(See Gfarm)."""
    assert_active_context()
    st = _c_gfs_stat()
    if (aboutlink):
        cc = gfso.gfs_lstat_cached(path, ctypes.byref(st))
    else:
        cc = gfso.gfs_stat_cached(path, ctypes.byref(st))
    assert (cc == GFARM_ERR_NO_ERROR
            or cc == GFARM_ERR_OPERATION_NOT_PERMITTED
            or cc == GFARM_ERR_NO_SUCH_FILE_OR_DIRECTORY)
    if (cc == GFARM_ERR_NO_ERROR):
        return (st, cc)
    else:
        return (None, cc)

def stat(path, aboutlink = False):
    """Returns a gfs_stat/gfs_lstat value.  It returns None if the
    operation failed.  It uses gfs_lstat if the optional argument is
    true."""
    p = abst_path(path)
    s = str(p).encode(name_coding)
    (st, cc) = _gfs_stat_cached(s, aboutlink)
    return (st, cc)

##
## X-attributes.
##

GFARM_EA_NCOPY = (b"gfarm." + b"ncopy")
GFARM_EA_REPATTR = (b"gfarm." + b"replicainfo")
GFARM_EA_DIRECTORY_QUOTA = (b"gfarm." + b"directory_quota")

def _gfs_getxattr_cached(path, attr, aboutlink = False):
    """().  It returns a byte string or None when no attributes are
    associated to the path (when libfarm returns
    GFARM_ERR_NO_SUCH_OBJECT)."""
    assert_active_context()
    limit = 128
    v = ctypes.create_string_buffer((limit + 1))
    size = _c_size_t(limit)
    if (aboutlink):
        cc = gfso.gfs_lgetxattr_cached(path, attr, v, ctypes.byref(size))
        assert (cc == GFARM_ERR_NO_ERROR or cc == GFARM_ERR_NO_SUCH_OBJECT)
    else:
        cc = gfso.gfs_getxattr_cached(path, attr, v, ctypes.byref(size))
        assert (cc == GFARM_ERR_NO_ERROR or cc == GFARM_ERR_NO_SUCH_OBJECT)
    if (cc == GFARM_ERR_NO_ERROR):
        return (v[0:size.value], cc)
    else:
        return (None, cc)

## bytes(path, name_coding) does not work (?).

def getxattr_loop(path, attr, aboutlink):
    s = str(path).encode(name_coding)
    (a, cc) = _gfs_getxattr_cached(s, attr, aboutlink)
    if (a != None):
        return (a.decode(name_coding), cc)
    elif (cc == GFARM_ERR_NO_SUCH_OBJECT):
        p = path.parent
        if (p == s):
            (None, cc)
        else:
            return getxattr_loop(p, attr, aboutlink)
    else:
        return (None, cc)

def getxattr(path, attr, aboutlink = False):
    """Calls gfs_getxattr_cached for the path and its parents until it
    finds an attribute or reaches the root.  It returns a string or
    None when an attribute is not found."""
    p = abst_path(path)
    return getxattr_loop(p, attr, aboutlink)

def get_ncopy(path, aboutlink = False):
    """Returns an ncopy attribute value (it is a requested count of
    replicas).  It calls gfs_getxattr_cached."""
    (n, cc) = getxattr(path, GFARM_EA_NCOPY, aboutlink)
    if (n != None):
        return (int(n), cc)
    else:
        return (None, cc)

##gfs_lsetxattr
##gfs_setxattr
##gfs_lremovexattr
##gfs_removexattr

##
## Directory scanning.
##

## The routines treat a structure gfs_dir as opaque.

##define GFS_MAXNAMLEN 255
##struct gfs_dirent {
##      gfarm_ino_t d_fileno;
##      unsigned short d_reclen;
##      unsigned char d_type;
##      unsigned char d_namlen;
##      char d_name[GFS_MAXNAMLEN + 1];
##};

GFS_MAXNAMLEN = 255

class _c_gfs_dirent(ctypes.Structure):
    """struct gfs_dirent."""
    _fields_ = [
        ("d_fileno", _c_gfarm_ino_t),
        ("d_reclen", _c_ushort),
        ("d_type", _c_uchar),
        ("d_namlen", _c_uchar),
        ("d_name", _c_char * (GFS_MAXNAMLEN + 1))]

    def __init__(self):
        return

_c_gfs_dirent_p = ctypes.POINTER(_c_gfs_dirent)
_c_gfs_dirent_p_p = ctypes.POINTER(_c_gfs_dirent_p)

class _dir():
    """A structure to hold an opaque structure returned by
    gfs_opendir_caching to make it reclaimed."""
    def __init__(self, dcc):
        (d_, cc_) = dcc
        self.d = d_
        self.cc = cc_
        return
    def __del__(self):
        ##print("_dir.__del__()")
        if (self.d != None):
            _gfs_closedir(self.d)
            self.d = None
        else:
            pass

def _gfs_opendir_caching(path):
    """Calls gfs_opendir_caching.  It returns an opaque structure, which
    will usually be stored in _dir."""
    assert_active_context()
    d = _c_pointer()
    cc = gfso.gfs_opendir_caching(path, ctypes.byref(d))
    assert cc == GFARM_ERR_NO_ERROR
    if (cc == GFARM_ERR_NO_ERROR):
        return (d, cc)
    else:
        return (None, cc)

def _gfs_readdir(d):
    """Calls gfs_readdir and returns a gfs_dirent structure or None."""
    assert_active_context()
    p = _c_gfs_dirent_p()
    cc = gfso.gfs_readdir(d, ctypes.byref(p))
    assert cc == GFARM_ERR_NO_ERROR
    if (p):
        return (p.contents, cc)
    else:
        return (None, cc)

def _gfs_closedir(d):
    """(See Gfarm)."""
    assert_active_context()
    cc = gfso.gfs_closedir(d)
    assert cc == GFARM_ERR_NO_ERROR
    return (None, cc)

def listdir(path):
    """Lists directory entries like os.listdir(path), but returns tuples
    of (name,ino,type).  It returns a generator."""
    p = abst_path(path)
    s = str(p).encode(name_coding)
    dx = _dir(_gfs_opendir_caching(s))
    if (dx.d == None):
        return None
    else:
        while True:
            (e, cc) = _gfs_readdir(dx.d)
            if (e != None):
                n = e.d_name[0:e.d_namlen].decode(name_coding)
                yield (n, e.d_fileno, e.d_type)
            else:
                del(dx)
                return None

##
## Control to file stat operations.
##

## Cached or uncached variants of stat and opendir are enabled by
## gfs_stat_cache_enable.

def _gfs_stat_cache_enable(v):
    """(See Gfarm)."""
    assert_active_context()
    gfso.gfs_stat_cache_enable(v)
    return GFARM_ERR_NO_ERROR

def _gfarm_xattr_caching_pattern_add(s):
    """(See Gfarm)."""
    assert_active_context()
    cc = gfso.gfarm_xattr_caching_pattern_add(s)
    assert cc == GFARM_ERR_NO_ERROR
    return cc

def enable_stat_cache():
    """Enables stat caching by calling gfs_stat_cache_enable(1) and
    gfarm_xattr_caching_pattern_add for GFARM_EA_NCOPY and
    GFARM_EA_REPATTR."""
    _gfs_stat_cache_enable(1)
    _gfarm_xattr_caching_pattern_add(GFARM_EA_NCOPY)
    _gfarm_xattr_caching_pattern_add(GFARM_EA_REPATTR)
    return None

##
## File operations (removing).
##

def _gfs_link(src, dst):
    """(See Gfarm)."""
    assert_active_context()
    cc = gfso.gfs_link(src, dst)
    assert (cc == GFARM_ERR_NO_ERROR
            or cc == GFARM_ERR_OPERATION_NOT_PERMITTED
            or cc == GFARM_ERR_ALREADY_EXISTS)
    return cc

def _gfs_unlink(path):
    """"(See Gfarm)."""
    assert_active_context()
    cc = gfso.gfs_unlink(path)
    assert (cc == GFARM_ERR_NO_ERROR
            or cc == GFARM_ERR_OPERATION_NOT_PERMITTED
            or cc == GFARM_ERR_NO_SUCH_FILE_OR_DIRECTORY
            or cc == GFARM_ERR_IS_A_DIRECTORY)
    return cc

def link(src, dst):
    """Calls gfs_link."""
    p0 = abst_path(src)
    s0 = str(p0).encode(name_coding)
    p1 = abst_path(dst)
    s1 = str(p1).encode(name_coding)
    cc = _gfs_link(s0, s1)
    return cc

def unlink(path):
    """Calls gfs_unlink."""
    p = abst_path(path)
    s = str(p).encode(name_coding)
    cc = _gfs_unlink(s)
    return cc

def _gfs_mkdir(path, mode):
    """(See Gfarm)."""
    assert_active_context()
    cc = gfso.gfs_mkdir(path, mode)
    assert (cc == GFARM_ERR_NO_ERROR
            or cc == GFARM_ERR_OPERATION_NOT_PERMITTED
            or cc == GFARM_ERR_ALREADY_EXISTS)
    return cc

def _gfs_rmdir(path):
    """(See Gfarm)."""
    assert_active_context()
    cc = gfso.gfs_rmdir(path)
    ##print(cc)
    assert (cc == GFARM_ERR_NO_ERROR
            or cc == GFARM_ERR_OPERATION_NOT_PERMITTED
            or cc == GFARM_ERR_NO_SUCH_FILE_OR_DIRECTORY
            or cc == GFARM_ERR_NOT_A_DIRECTORY)
    return cc

def mkdir(path, mode):
    """ Calls gfs_mkdir."""
    p = abst_path(path)
    s = str(p).encode(name_coding)
    cc = _gfs_mkdir(s, mode)
    return cc

def rmdir(path):
    """ Calls gfs_rmdir."""
    p = abst_path(path)
    s = str(p).encode(name_coding)
    cc = _gfs_rmdir(s)
    return cc

def _gfs_rename(src, dst):
    """(See Gfarm)."""
    assert_active_context()
    cc = gfso.gfs_rename(src, dst)
    assert (cc == GFARM_ERR_NO_ERROR
            or cc == GFARM_ERR_OPERATION_NOT_PERMITTED
            or cc == GFARM_ERR_NO_SUCH_FILE_OR_DIRECTORY)
    return cc

def rename(src, dst):
    """ Calls gfs_rename."""
    p0 = abst_path(src)
    s0 = str(p0).encode(name_coding)
    p1 = abst_path(dst)
    s1 = str(p1).encode(name_coding)
    cc = _gfs_rename(s0, s1)
    return cc

## Copyright (C) 2020-2021 RIKEN
## This library is distributed WITHOUT ANY WARRANTY.  This library can be
## redistributed and/or modified under the terms of the BSD 2-Clause License.
