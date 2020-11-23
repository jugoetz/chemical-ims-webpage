#!/bin/bash

# This script needs to be located/executed in <django_source_dir>/utilities/ to work properly
# It assumes that the venv django runs in is located in the same directory as the django source directory
# Run the database update for sqlite3 database of chemical-ims-webpage by calling updateFromExpereact.py

# activate venv
source ../../.venv/bin/activate

# execute python script
cd ../chemical-ims-webpage/inventorymanagement/ || exit 1
python updateFromExpereact.py

# deactivate venv
deactivate
