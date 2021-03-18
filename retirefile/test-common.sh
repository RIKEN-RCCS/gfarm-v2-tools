## Common routines for test.

## Checks the setting for test.  Test scripts require variables GFLIB
## and GFDIR.  GFLIB is a path to "libgfarm.so", and GFDIR is a path
## in the remote directory.  Files are created in the remote directory
## "${GFDIR}/gomi".  For example,
## export GFDIR=/home/hpNNNNNN/hpciNNNNNN
## export GFLIB=${HOME}/lib/libgfarm.so

checksetting() {
if [ -z "${GFDIR}" -o -z "${GFLIB}" ]; then
    echo "Set GFDIR as a target directory and GFLIB as a path to libgfarm.so"
    exit 1
fi
}
