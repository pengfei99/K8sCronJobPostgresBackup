#!/bin/bash
# pg_bkp.sh
# This script performs a pg_dump, saving the file the specified dir.
# The first arg ($1) is the database user to connect with.
# The second arg ($2) is the host name of the database
# The third arg ($3) is the database name to backup and is included in the file name
# The fourth arg ($4) is the path of where to put the backup
# $(date +"%Y_%m_%d") includes the current system date into the actual file name.

# Notice the -C option in the command so that we can restore if the database happens to be non-existent, without 
# the need to manually create it beforehand. 
pg_dump -U "$1" -h "$2" -C -d "$3" > "$4"/$(date +"%Y_%m_%d")_"$3".sql

# example to run this script
# sh pg_bkp.sh user-pengfei 10.233.30.220 north_wind /home/coder/work/dumps