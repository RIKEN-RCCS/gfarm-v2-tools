#!/usr/bin/awk -M -f

# USAGE: awk -M -f group-files.awk < list-of-files > grouped-list-of-files

# This groups a list of lines "size file-name" as the sum of the sizes
# is below the limit (not exactly below when a single line exceeds the
# limit).  Groups are separated by lines "nnnn", where "nnnn" are four
# digits numbers starting by "0000" and ending with "nnnn" for the
# number of groups.  The "-M" option to AWK is for using bignums.

BEGIN { 
    limit = (25 * 1024 * 1024 * 1024)
    #limit = (200 * 1024)
    printf("%04d\n", no)
    no++
}
{
    if (sum != 0 && sum + $1 >= limit) {
	sum = 0
	printf("%04d\n", no)
	no++
    }
    sum += $1
    print $0
}
END {
    printf("%04d\n", no)
}
