#!/bin/bash

# This script needs to be located/executed in <django_source_dir>/utilities/ to work properly
# Backup the sqlite3 database of chemical-ims-webpage to folder ~/chemborrowsys/database_backup
# Delete backups after 30 days

CURRENTDATE=$(date +%Y-%m-%d)
# copy db to backup folder
cp ../db.sqlite3 ~/chemborrowsys/database_backup/
cd ~/chemborrowsys/database_backup || exit 1
# tar-gz the database copy
tar -czf backup_${CURRENTDATE}.tar.gz db.sqlite3
# remove the database copy
rm db.sqlite3
# remove the backup from 30 days ago
DELETEDATE=$(date --date="${dataset_date} -30 day" +%Y-%m-%d)
rm backup_${DELETEDATE}.tar.gz
