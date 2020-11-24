#!/bin/bash

# This script needs to be located/executed in <django_source_dir>/utilities/ to work properly
# It assumes that the venv django runs in is located in the same directory as the django source directory
# Run the database update for sqlite3 database of chemical-ims-webpage by calling updateFromExpereact.py

# get script directory and make it pwd
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR || exit 1

# activate venv
source ../../.venv/bin/activate

# execute python script
cd ../inventorymanagement/ || exit 1
python updateFromExpereact.py

# deactivate venv
deactivate
