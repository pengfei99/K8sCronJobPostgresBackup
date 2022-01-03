#!/bin/bash
# pg_cluster_bkp.sh
# This shell script calls pg_dumpall and pipes into the gzip utility, then directs to
# a directory for storage.
# $(date +"%Y_%m_%d") incorporates the current system date into the file name.
# The first arg ($1) is the database user to connect with.
# The second arg ($2) is the host name of the database
# The third arg ($3) is the path of where to put the backup

pg_dumpall -U "$1" -h "$2" | gzip > "$3"/$(date +"%Y_%m_%d")_pg_bck.gz