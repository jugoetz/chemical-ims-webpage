#!/bin/bash

# This script needs to be located in <django_source_dir>/utilities/ to work properly
# Run the database update of chemical-ims-webpage by calling the management command parseexpereact

# get the django project directory and cd to its child 'utilities/
PROJECT_DIR="$( dirname "$( dirname "${BASH_SOURCE[0]}" )" )"
cd "$PROJECT_DIR/utilities/" || exit 1

# activate venv
source ../../.venv/bin/activate

# execute task
python download_expereact_data.py

# deactivate venv
deactivate
